"""Repo scanner — walk a folder, classify SQL/Tableau/PowerBI files, parse each,
and aggregate table- and column-level lineage.

Pure and DB-free so it is easy to test; the caller (the API) resolves the path
safely and persists the returned result.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .powerbi_parser import parse_powerbi
from .sql_parser import parse_sql
from .tableau_parser import parse_tableau

DEFAULT_SQL_GLOBS = ["**/*.sql"]
DEFAULT_REPORT_GLOBS = ["**/*.twb", "**/*.twbx", "**/*.pbix", "**/*.pbit"]

_TABLEAU_EXTS = {".twb", ".twbx"}
_POWERBI_EXTS = {".pbix", ".pbit"}


def classify(path: Path) -> str | None:
    ext = path.suffix.lower()
    if ext == ".sql":
        return "sql"
    if ext in _TABLEAU_EXTS:
        return "tableau"
    if ext in _POWERBI_EXTS:
        return "powerbi"
    return None


def derive_name(path: Path, base: Path, conventions: list[dict[str, Any]] | None) -> str:
    """Derive an asset display name, applying optional naming-convention regexes."""
    rel = path.relative_to(base).as_posix()
    for conv in conventions or []:
        pattern = conv.get("pattern")
        if not pattern:
            continue
        try:
            m = re.search(pattern, rel)
        except re.error:
            continue
        if m:
            if m.groupdict().get("name"):
                return m.group("name")
            if m.groups():
                return m.group(1)
            return path.stem
    return path.stem


def _collect(base: Path, globs: list[str]) -> list[Path]:
    seen: dict[str, Path] = {}
    for pattern in globs:
        for p in base.glob(pattern):
            if p.is_file():
                seen[str(p)] = p
    return sorted(seen.values(), key=str)


def scan_repo(
    base: str | Path,
    sql_globs: list[str] | None = None,
    report_globs: list[str] | None = None,
    naming_conventions: list[dict[str, Any]] | None = None,
    dialect: str | None = None,
) -> dict[str, Any]:
    base = Path(base)
    sql_globs = sql_globs or DEFAULT_SQL_GLOBS
    report_globs = report_globs or DEFAULT_REPORT_GLOBS

    assets: list[dict[str, str]] = []
    table_edges: dict[tuple[str, str, str], dict[str, str]] = {}
    column_edges: list[dict[str, Any]] = []
    tables: set[str] = set()
    warnings: list[str] = []

    files: list[Path] = []
    for p in _collect(base, sql_globs) + _collect(base, report_globs):
        if classify(p) and p not in files:
            files.append(p)

    for path in files:
        kind = classify(path)
        name = derive_name(path, base, naming_conventions)
        rel = path.relative_to(base).as_posix()
        assets.append({"path": rel, "asset_type": kind, "name": name})
        try:
            if kind == "sql":
                parsed = parse_sql(path.read_text(encoding="utf-8", errors="replace"), dialect=dialect, default_target=name)
            elif kind == "tableau":
                parsed = parse_tableau(str(path), report_name=name, dialect=dialect)
            else:
                parsed = parse_powerbi(str(path), report_name=name, dialect=dialect)
        except Exception as exc:  # noqa: BLE001 - never let one file break the scan
            warnings.append(f"{rel}: {exc}")
            continue

        tables.update(parsed.get("source_tables", []))
        for e in parsed.get("table_edges", []):
            key = (e["source"], e["target"], e["relation"])
            table_edges[key] = {**e, "asset": name}
            tables.add(e["source"])
            tables.add(e["target"])
        for ce in parsed.get("column_edges", []):
            column_edges.append({**ce, "asset": name})
        warnings.extend(f"{rel}: {w}" for w in parsed.get("warnings", []))

    return {
        "assets": assets,
        "table_edges": list(table_edges.values()),
        "column_edges": column_edges,
        "tables": sorted(tables),
        "files": len(files),
        "warnings": warnings,
    }
