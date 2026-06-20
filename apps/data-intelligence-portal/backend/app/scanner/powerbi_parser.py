"""PowerBI report parsing for the repo scanner — best-effort.

`.pbix` / `.pbit` are zip containers. The tabular DataModel in a `.pbix` is a
compressed binary (VertiPaq) we do not decode. Instead we extract what is plainly
readable:
  - `DataMashup` -> the Power Query M (`Formulas/Section1.m`), from which we pull
    native SQL (`Value.NativeQuery`, `Sql.Database(..,[Query=..])`) and table refs,
  - `.pbit` `DataModelSchema` (JSON) -> tables, columns, and measures (DAX as the
    transformation).

All edges target the report. Never raises; always appends a best-effort warning.
"""
from __future__ import annotations

import json
import re
import zipfile
from typing import Any

from .sql_parser import parse_sql

_NATIVE_QUERY = re.compile(r'Value\.NativeQuery\s*\(\s*[^,]+,\s*"((?:[^"\\]|\\.)*)"', re.S)
_SQL_DB_QUERY = re.compile(r'Query\s*=\s*"((?:[^"\\]|\\.)*)"', re.S)
_M_ITEM = re.compile(r'(?:Schema|Item)\s*=\s*"([^"]+)"')


def _decode(raw: bytes) -> str:
    for enc in ("utf-16-le", "utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except Exception:  # noqa: BLE001
            continue
    return raw.decode("utf-8", "replace")


def _extract_mashup_m(raw: bytes) -> str:
    """The DataMashup part wraps a zip; pull Formulas/Section1.m if present."""
    idx = raw.find(b"PK\x03\x04")
    if idx < 0:
        return ""
    import io

    try:
        with zipfile.ZipFile(io.BytesIO(raw[idx:])) as zf:
            name = next((n for n in zf.namelist() if n.lower().endswith("section1.m")), None)
            if name:
                return _decode(zf.read(name))
    except Exception:  # noqa: BLE001
        return ""
    return ""


def _m_text_from_zip(zf: zipfile.ZipFile) -> str:
    chunks = []
    for name in zf.namelist():
        low = name.lower()
        if low.endswith("datamashup") or low.endswith("/datamashup") or low == "datamashup":
            chunks.append(_extract_mashup_m(zf.read(name)))
        elif low.endswith("section1.m"):
            chunks.append(_decode(zf.read(name)))
    return "\n".join(c for c in chunks if c)


def parse_powerbi(path: str, report_name: str, dialect: str | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "source_tables": [],
        "table_edges": [],
        "column_edges": [],
        "warnings": ["powerbi parser is best-effort (binary DataModel not decoded)"],
    }
    src_tables: set[str] = set()
    table_edges: set[tuple[str, str, str]] = set()

    try:
        zf = zipfile.ZipFile(path)
    except Exception as exc:  # noqa: BLE001
        out["warnings"].append(f"powerbi read error: {exc}")
        return out

    with zf:
        # 1) Power Query M (native SQL + table items)
        m_text = ""
        try:
            m_text = _m_text_from_zip(zf)
        except Exception as exc:  # noqa: BLE001
            out["warnings"].append(f"mashup extract error: {exc}")

        for match in list(_NATIVE_QUERY.finditer(m_text)) + list(_SQL_DB_QUERY.finditer(m_text)):
            sql = match.group(1).encode().decode("unicode_escape", "ignore")
            parsed = parse_sql(sql, dialect=dialect, default_target=report_name)
            src_tables.update(parsed["source_tables"])
            out["column_edges"].extend(parsed["column_edges"])
            for s in parsed["source_tables"]:
                table_edges.add((s, report_name, "reads"))
        for item in _M_ITEM.findall(m_text):
            if item:
                src_tables.add(item)
                table_edges.add((item, report_name, "reads"))

        # 2) .pbit DataModelSchema (JSON) — tables, columns, measures (DAX)
        schema_name = next((n for n in zf.namelist() if n.lower().endswith("datamodelschema")), None)
        if schema_name:
            try:
                model = json.loads(_decode(zf.read(schema_name)))
                for table in (model.get("model", {}) or {}).get("tables", []) or []:
                    tname = table.get("name")
                    if tname:
                        src_tables.add(tname)
                        table_edges.add((tname, report_name, "reads"))
                    for measure in table.get("measures", []) or []:
                        expr = measure.get("expression")
                        if isinstance(expr, list):
                            expr = " ".join(expr)
                        out["column_edges"].append(
                            {
                                "source_table": tname,
                                "source_column": None,
                                "target_table": report_name,
                                "target_column": measure.get("name") or "measure",
                                "transformation": expr,
                            }
                        )
            except Exception as exc:  # noqa: BLE001
                out["warnings"].append(f"datamodelschema parse error: {exc}")

    out["source_tables"] = sorted(src_tables)
    out["table_edges"] = [{"source": s, "target": t, "relation": r} for (s, t, r) in sorted(table_edges)]
    return out
