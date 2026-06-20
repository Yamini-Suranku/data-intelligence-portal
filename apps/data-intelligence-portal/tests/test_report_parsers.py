"""Tests for the Tableau and PowerBI report parsers."""
import json
import zipfile

from backend.app.scanner.tableau_parser import parse_tableau
from backend.app.scanner.powerbi_parser import parse_powerbi

TWB = """<?xml version='1.0'?>
<workbook>
  <datasources>
    <datasource name='ds'>
      <connection>
        <relation name='Custom SQL' type='text'>select c.region, sum(s.amt) as rev from raw.sales s join raw.cust c on c.id = s.cust_id group by c.region</relation>
        <relation name='dim' type='table' table='[analytics].[date_dim]'/>
      </connection>
      <column caption='Profit Ratio' name='[Calculation_1]'>
        <calculation class='tableau' formula='[Profit]/[Sales]'/>
      </column>
    </datasource>
  </datasources>
</workbook>
"""


def test_tableau_custom_sql_relations_and_calc(tmp_path):
    twb = tmp_path / "sales.twb"
    twb.write_text(TWB, encoding="utf-8")
    res = parse_tableau(str(twb), report_name="sales")

    assert "raw.sales" in res["source_tables"]
    assert "analytics.date_dim" in res["source_tables"]
    # physical relation reads the report
    assert {"source": "analytics.date_dim", "target": "sales", "relation": "reads"} in res["table_edges"]
    # custom-SQL column lineage
    rev = next(c for c in res["column_edges"] if c["target_column"] == "rev")
    assert rev["source_table"] == "raw.sales"
    # calculated field captured as a transformation
    calc = next(c for c in res["column_edges"] if c["target_column"] == "Profit Ratio")
    assert calc["transformation"] == "[Profit]/[Sales]"


def test_powerbi_pbit_datamodelschema(tmp_path):
    model = {
        "model": {
            "tables": [
                {
                    "name": "Sales",
                    "measures": [{"name": "Total Revenue", "expression": "SUM(Sales[Amount])"}],
                }
            ]
        }
    }
    pbit = tmp_path / "report.pbit"
    with zipfile.ZipFile(pbit, "w") as zf:
        # DataModelSchema is UTF-16-LE JSON in real files
        zf.writestr("DataModelSchema", json.dumps(model).encode("utf-16-le"))

    res = parse_powerbi(str(pbit), report_name="report")
    assert "Sales" in res["source_tables"]
    measure = next(c for c in res["column_edges"] if c["target_column"] == "Total Revenue")
    assert "SUM" in measure["transformation"].upper()
    assert res["warnings"]  # always flags best-effort


def test_powerbi_garbage_file_never_raises(tmp_path):
    bad = tmp_path / "broken.pbix"
    bad.write_bytes(b"not a zip")
    res = parse_powerbi(str(bad), report_name="broken")
    assert res["warnings"]  # reported, no exception
    assert res["source_tables"] == []
