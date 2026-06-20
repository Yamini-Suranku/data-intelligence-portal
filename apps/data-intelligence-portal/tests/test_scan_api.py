"""End-to-end tests for the repo scanner API."""
from fastapi.testclient import TestClient

from backend.app import main

client = TestClient(main.app)

MODEL_SQL = """
create table analytics.customer_spend as
with recent as (select o.amount, o.customer_id from raw.orders o where o.status = 'paid')
select customer_id, sum(amount) as total_spend from recent group by customer_id
"""


def _fixture_repo(tmp_path):
    repo = tmp_path / "analytics"
    (repo / "models").mkdir(parents=True)
    (repo / "models" / "customer_spend.sql").write_text(MODEL_SQL, encoding="utf-8")
    return repo


def test_scan_local_path_produces_table_and_column_lineage(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "SCAN_ROOT", tmp_path)
    _fixture_repo(tmp_path)

    src = client.post("/api/scan/sources", json={"name": "analytics", "path": "analytics", "sql_globs": ["**/*.sql"]})
    assert src.status_code == 201
    source_id = src.json()["id"]

    run = client.post(f"/api/scan/sources/{source_id}/run")
    assert run.status_code == 200
    summary = run.json()
    assert summary["files"] == 1
    assert summary["columns"] >= 2

    # scanned table edge shows up in the lineage graph feed
    data_lineage = client.get("/api/lineage/data").json()
    assert any(e["target"] == "analytics.customer_spend" and e["source"] == "raw.orders" for e in data_lineage)

    # column-level drill-down with transformation
    cols = client.get("/api/lineage/columns", params={"table": "analytics.customer_spend"}).json()
    spend = next(c for c in cols if c["target_column"] == "total_spend")
    assert spend["source_table"] == "raw.orders"
    assert "SUM" in (spend["transformation"] or "").upper()

    # asset recorded
    assets = client.get("/api/scan/assets").json()
    assert any(a["asset_type"] == "sql" and a["name"] == "customer_spend" for a in assets)


def test_scan_source_rejects_path_traversal():
    res = client.post("/api/scan/sources", json={"name": "x", "path": "../../etc"})
    assert res.status_code == 400


def test_readiness_includes_scanner_check():
    body = client.get("/api/readiness").json()
    assert "scanner" in {c["name"] for c in body["checks"]}
