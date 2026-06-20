"""Tableau workbook parsing for the repo scanner.

`.twb` is XML; `.twbx` is a zip containing a `.twb`. We extract:
  - custom SQL (`<relation type='text'>`) -> handed to the SQL parser,
  - physical table relations (`<relation type='table' table='[s].[t]'>`), and
  - calculated fields (`<column><calculation formula=.../></column>`) as
    report-level transformations.

All edges target the report (the workbook). Best-effort; never raises.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from typing import Any

from .sql_parser import parse_sql

_BRACKETS = re.compile(r"[\[\]]")


def _localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _read_twb_xml(path: str) -> str:
    if path.lower().endswith(".twbx"):
        with zipfile.ZipFile(path) as zf:
            twb = next((n for n in zf.namelist() if n.lower().endswith(".twb")), None)
            if not twb:
                raise ValueError("no .twb inside .twbx")
            return zf.read(twb).decode("utf-8", "replace")
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def parse_tableau(path: str, report_name: str, dialect: str | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "source_tables": [],
        "table_edges": [],
        "column_edges": [],
        "warnings": [],
    }
    src_tables: set[str] = set()
    table_edges: set[tuple[str, str, str]] = set()

    try:
        xml = _read_twb_xml(path)
        root = ET.fromstring(xml)
    except Exception as exc:  # noqa: BLE001
        out["warnings"].append(f"tableau read error: {exc}")
        return out

    for el in root.iter():
        tag = _localname(el.tag)
        if tag == "relation":
            rtype = el.get("type")
            if rtype == "text" and (el.text or "").strip():
                parsed = parse_sql(el.text, dialect=dialect, default_target=report_name)
                src_tables.update(parsed["source_tables"])
                out["column_edges"].extend(parsed["column_edges"])
                for e in parsed["table_edges"]:
                    table_edges.add((e["source"], e["target"], e["relation"]))
                out["warnings"].extend(parsed["warnings"])
            elif rtype == "table" and el.get("table"):
                tbl = _BRACKETS.sub("", el.get("table")).strip().strip(".")
                if tbl:
                    src_tables.add(tbl)
                    table_edges.add((tbl, report_name, "reads"))
        elif tag == "column":
            calc = next(
                (c for c in el if _localname(c.tag) == "calculation" and c.get("formula")),
                None,
            )
            if calc is not None:
                out["column_edges"].append(
                    {
                        "source_table": None,
                        "source_column": None,
                        "target_table": report_name,
                        "target_column": el.get("caption") or _BRACKETS.sub("", el.get("name") or "") or "calculated_field",
                        "transformation": calc.get("formula"),
                    }
                )

    out["source_tables"] = sorted(src_tables)
    out["table_edges"] = [{"source": s, "target": t, "relation": r} for (s, t, r) in sorted(table_edges)]
    return out
