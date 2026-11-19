"""
Phase 7 tests: the export to Power BI and the Power BI project (.pbip).

Power BI Desktop cannot run in these tests, so they check everything that can be
checked without it:
  * the export is protected by the quality gate;
  * the exported star schema contains everything needed to reproduce the 19 KPIs
    exactly, using the same filters as the DAX measures;
  * the generated project passes the validator (TMDL, DAX references, relationships,
    report fields and the official Microsoft JSON schemas);
  * the validator catches defects introduced on purpose.
The final check, Power BI = SQL for every KPI (rule K03), is done in Power BI itself
on the Audit & Traceability page and recorded in Phase 9.

Run from the main project folder:
    pytest -v
"""

import csv
import json
import re
import shutil

import pytest

from scripts import build_powerbi_project as builder
from scripts.export_powerbi import export, infer_type
from scripts.generate_data import generate
from scripts.run_kpis import run_kpis
from scripts.run_validations import run_validations
from scripts.validate_powerbi import validate_project


@pytest.fixture(scope="module")
def project(tmp_path_factory):
    """Generate the data, export it and build the Power BI project in a temporary folder."""
    folder = tmp_path_factory.mktemp("powerbi")
    db_path = folder / "aqmi.db"
    planted = generate(db_path, export_dir=None)["planted"]
    validations = run_validations(db_path, report_dir=None, planted=planted)
    kpis = run_kpis(db_path, report_dir=None)
    data_dir = folder / "processed"
    schema = export(db_path, data_dir, validations=validations, kpis=kpis)
    builder.build(folder / "pbip", schema_path=data_dir / "_schema.json", data_folder=str(data_dir) + "/")
    return {"folder": folder, "data": data_dir, "schema": schema, "kpis": kpis, "pbip": folder / "pbip"}


def _load(project, table):
    with open(project["data"] / f"{table}.csv", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


# -----------------------------------------------------------------------------
# 1. Export
# -----------------------------------------------------------------------------
def test_export_writes_the_star_schema(project):
    dims = [t for t in project["schema"] if t.startswith("Dim_")]
    facts = [t for t in project["schema"] if t.startswith("Fact_")]
    assert len(dims) == 9 and len(facts) == 18 and "Model_Info" in project["schema"]
    for table, info in project["schema"].items():
        assert (project["data"] / f"{table}.csv").exists()
        assert info["rows"] > 0, table


def test_export_refuses_data_that_failed_the_quality_gate(project, tmp_path):
    failed = {"gate_passed": False}
    with pytest.raises(RuntimeError):
        export(project["folder"] / "aqmi.db", tmp_path / "out", validations=failed, kpis=project["kpis"])
    assert not (tmp_path / "out").exists()


def test_date_table_covers_the_period_without_gaps(project):
    dates = [r["date"] for r in _load(project, "Dim_Date")]
    assert dates[0] == "2024-11-01" and dates[-1] == "2026-10-31" and len(dates) == len(set(dates)) == 730


def test_keys_of_dimensions_are_unique_and_facts_point_to_them(project):
    for dim, key in [("Dim_Aircraft", "aircraft_id"), ("Dim_Material", "material_id"), ("Dim_Supplier", "supplier_id"),
                     ("Dim_Department", "department_id"), ("Dim_Employee", "employee_id"), ("Dim_Document", "document_id")]:
        keys = [r[key] for r in _load(project, dim)]
        assert len(keys) == len(set(keys)), dim
    for frm, fcol, to, tcol, _ in builder.RELATIONSHIPS:
        if to == "Dim_Date":
            continue
        valid = {r[tcol] for r in _load(project, to)}
        used = {r[fcol] for r in _load(project, frm) if r[fcol] != ""}
        assert used <= valid, f"{frm}.{fcol} -> {to}.{tcol}"


def test_active_date_relationships_stay_inside_the_calendar(project):
    for frm, fcol, to, _, active in builder.RELATIONSHIPS:
        if to == "Dim_Date" and active:
            values = [r[fcol] for r in _load(project, frm) if r[fcol] != ""]
            assert min(values) >= "2024-11-01" and max(values) <= "2026-10-31", f"{frm}.{fcol}"


@pytest.mark.parametrize("values, name, expected", [
    (["1", "2"], "count", "int64"), (["1", "2"], "available_qty", "double"), (["1.5", ""], "x", "double"),
    (["2025-01-31"], "d", "date"), (["2025-01-31 10:00:00"], "t", "dateTime"), (["NC-2025-0001"], "n", "string"),
    (["", ""], "empty", "string")])
def test_column_types(values, name, expected):
    assert infer_type(values, name) == expected


# -----------------------------------------------------------------------------
# 2. The star schema reproduces the 19 KPIs (same filters as the DAX measures)
# -----------------------------------------------------------------------------
def _kpis_from_csv(project):
    I, C, CS = _load(project, "Fact_Incidents"), _load(project, "Fact_CAPA"), _load(project, "Fact_CAPA_Snapshot")
    MO, H = _load(project, "Fact_MaintenanceOrders"), _load(project, "Fact_Holds")
    MM, MV = _load(project, "Fact_MO_Materials"), _load(project, "Fact_InventoryMovements")
    SS, SC, POS = _load(project, "Fact_StockSnapshot"), _load(project, "Fact_StockCounts"), _load(project, "Fact_PO_Snapshot")
    DV, DS = _load(project, "Fact_DocumentVerifications"), _load(project, "Fact_DocumentSnapshot")
    LL = _load(project, "Fact_Lessons")
    asof = _load(project, "Model_Info")[0]["as_of_date"]
    pct = lambda n, d: round(100 * n / d, 1)       # noqa: E731
    completed = [o for o in MO if o["is_cancelled"] == "0" and o["actual_end_date"]]
    due = [c for c in C if c["action_type"] == "CORRECTIVE" and c["is_cancelled"] == "0" and c["due_date"] <= asof]
    closed = [i for i in I if i["status"] == "CLOSED"]
    docs = [s for s in DS if s["snapshot_date"] == asof]
    routine = [d for d in DV if d["is_routine"] == "1"]
    issues = [m for m in MV if m["movement_type"] == "ISSUE"]
    cycle = [s for s in SC if s["count_type"] == "CYCLE"]
    stock = [s for s in SS if s["snapshot_date"] == asof]
    lines = [m for m in MM if m["is_cancelled_order"] == "0" and m["was_short"] != "" and m["required_by_date"] <= asof]
    orders_due = [o for o in MO if o["is_cancelled"] == "0" and o["planned_end_date"] <= asof]
    active = lambda reason: len({h["mo_id"] for h in H if h["hold_reason"] == reason and h["start_date"] <= asof  # noqa: E731
                                 and (h["end_date"] == "" or h["end_date"] > asof)})
    total = sum(i["is_cancelled"] == "0" for i in I)
    return {
        "QUA-01": total,
        "QUA-02": sum(i["is_cancelled"] == "0" and i["detected_date"] <= asof
                      and (i["closed_date"] == "" or i["closed_date"] > asof) for i in I),
        "QUA-03": pct(total, len(completed)),
        "QUA-04": pct(sum(c["completed_by_due"] == "1" for c in due), len(due)),
        "QUA-05": round(sum(int(i["resolution_days"]) for i in closed) / len(closed), 1),
        "QUA-06": sum(s["snapshot_date"] == asof and s["action_type"] == "CORRECTIVE" and s["is_overdue"] == "1" for s in CS),
        "DOC-01": pct(sum(s["is_compliant"] == "1" for s in docs), len(docs)),
        "DOC-02": pct(sum(d["is_error"] == "1" for d in routine), len(routine)),
        "DOC-03": sum(s["is_expired"] == "1" for s in docs),
        "DOC-04": pct(sum(m["is_traceable"] == "1" for m in issues), len(issues)),
        "INV-01": pct(sum(s["has_difference"] == "0" for s in cycle), len(cycle)),
        "INV-02": pct(sum(s["is_below_min"] == "0" for s in stock), len(stock)),
        "INV-03": pct(sum(m["was_short"] == "1" for m in lines), len(lines)),
        "INV-04": sum(p["snapshot_date"] == asof for p in POS),
        "MNT-01": pct(sum(o["completed_by_planned"] == "1" for o in orders_due), len(orders_due)),
        "MNT-02": round(sum(int(o["delay_days"]) for o in completed) / len(completed), 1),
        "MNT-03": active("MATERIAL"),
        "MNT-04": active("DOCUMENTATION"),
        "LRN-01": pct(sum(x["incorporated_date"] != "" and x["incorporated_date"] <= asof for x in LL),
                      sum(x["approved_date"] != "" and x["approved_date"] <= asof for x in LL)),
    }


def test_star_schema_reproduces_every_kpi(project):
    expected = {r["kpi_id"]: float(r["sql_value"]) for r in _load(project, "Dim_KPI")}
    calculated = _kpis_from_csv(project)
    assert set(calculated) == set(expected)
    assert {k: (v, expected[k]) for k, v in calculated.items() if abs(v - expected[k]) > 1e-9} == {}


def test_monthly_kpi_table_matches_the_sql_queries(project):
    monthly = _load(project, "Fact_KPI_Monthly")
    assert len(monthly) == 19 * 24
    by_kpi = {k.kpi_id: {r["period"]: r["value"] for r in k.months} for k in project["kpis"]["kpis"]}
    for row in monthly:
        value = by_kpi[row["kpi_id"]][row["period"]]
        assert (row["value"] == "" and value is None) or float(row["value"]) == value


# -----------------------------------------------------------------------------
# 3. The Power BI project
# -----------------------------------------------------------------------------
def test_generated_project_passes_the_validator(project):
    result = validate_project(project["pbip"], project["data"])
    assert result["problems"] == []
    stats = result["stats"]
    assert stats["pages"] == 8 and stats["measures"] == len(builder.MEASURES)
    assert stats["schema_checked"] > 100                      # validated against the official schemas


def test_saved_project_in_the_repository_passes_the_validator():
    """The .pbip stored in the repository was last saved by Power BI Desktop
    (which adds lineage tags, a culture file and a diagram layout). It must
    still pass every check against the exported CSV files."""
    from config import settings
    if not (settings.POWERBI_DIR / "AQMI.pbip").exists():
        pytest.skip("no Power BI project in the repository")
    result = validate_project(settings.POWERBI_DIR, settings.POWERBI_DATA_DIR)
    assert result["problems"] == []
    assert result["stats"]["pages"] == 8


def test_saved_project_keeps_the_power_bi_desktop_conventions():
    """Files edited outside Desktop (Phase 9) must look exactly as Desktop writes them:
    CRLF line endings everywhere, JSON without a final line break, TMDL ending in a blank line."""
    from config import settings
    if not (settings.POWERBI_DIR / "AQMI.pbip").exists():
        pytest.skip("no Power BI project in the repository")
    problems = []
    for path in sorted(settings.POWERBI_DIR.rglob("*")):
        if not path.is_file() or path.name in (".gitignore", ".gitkeep"):
            continue
        data = path.read_bytes()
        if data.count(b"\n") != data.count(b"\r\n"):
            problems.append(f"{path.name}: line endings are not all CRLF")
        if path.suffix == ".tmdl" and not data.endswith(b"\r\n\r\n"):
            problems.append(f"{path.name}: TMDL must end with a blank line")
        if path.suffix != ".tmdl" and data.endswith(b"\n"):
            problems.append(f"{path.name}: JSON must not end with a line break")
    assert problems == []


def test_date_and_aircraft_axes_hide_the_blank_member():
    """Charts by month or by aircraft must not show a "(Blank)" category (Phase 8 fix)."""
    from config import settings
    pages = settings.POWERBI_DIR / "AQMI.Report" / "definition" / "pages"
    if not pages.exists():
        pytest.skip("no Power BI project in the repository")
    checked = 0
    for path in sorted(pages.glob("*/visuals/*/visual.json")):
        container = json.loads(path.read_text(encoding="utf-8"))
        category = container["visual"].get("query", {}).get("queryState", {}).get("Category")
        if not category:
            continue
        column = category["projections"][0]["field"].get("Column", {})
        target = (column.get("Expression", {}).get("SourceRef", {}).get("Entity"), column.get("Property"))
        if target in {("Dim_Date", "Month Label"), ("Dim_Aircraft", "Registration")}:
            filters = container.get("filterConfig", {}).get("filters", [])
            assert any(f["field"]["Column"]["Property"] == target[1] and "Not" in json.dumps(f["filter"])
                       for f in filters), path.parent.name
            checked += 1
    assert checked == 8


def test_every_kpi_has_a_dax_measure():
    switch = next(m for m in builder.MEASURES if m[1] == "KPI Value (Power BI)")[4]
    kpi_ids = re.findall(r'"([A-Z]{3}-\d{2})"', switch)
    assert len(kpi_ids) == 19 == len(set(kpi_ids))


def test_the_eight_requested_pages_exist(project):
    pages = json.loads((project["pbip"] / "AQMI.Report/definition/pages/pages.json").read_text(encoding="utf-8"))
    names = [json.loads((project["pbip"] / f"AQMI.Report/definition/pages/{p}/page.json").read_text(encoding="utf-8"))
             ["displayName"] for p in pages["pageOrder"]]
    assert names == ["Executive Overview", "Quality Performance", "Corrective Actions", "Document Control",
                     "Materials & Inventory", "Maintenance Production", "Aircraft Overview", "Audit & Traceability"]


def test_build_never_overwrites_an_existing_project(project):
    with pytest.raises(FileExistsError):
        builder.build(project["pbip"], schema_path=project["data"] / "_schema.json")


def test_build_is_deterministic(project, tmp_path):
    builder.build(tmp_path, schema_path=project["data"] / "_schema.json", data_folder=str(project["data"]) + "/")
    for path in sorted(project["pbip"].rglob("*")):
        if path.is_file():
            twin = tmp_path / path.relative_to(project["pbip"])
            assert twin.read_bytes() == path.read_bytes(), path.name


# -----------------------------------------------------------------------------
# 4. Negative tests: the validator must catch defects
# -----------------------------------------------------------------------------
def _broken_copy(project, tmp_path, relative, old, new):
    copy = tmp_path / "pbip"
    shutil.copytree(project["pbip"], copy)
    target = copy / relative
    content = target.read_text(encoding="utf-8")
    assert old in content
    target.write_text(content.replace(old, new, 1), encoding="utf-8")
    return validate_project(copy, project["data"])["problems"]


def test_unpublished_schema_version_is_checked_against_the_newest_one(project, tmp_path):
    """Power BI Desktop can save a schema version that Microsoft has not published yet
    (Phase 9: visualContainer 2.14.0). Those files must still be checked, not skipped."""
    copy = tmp_path / "pbip"
    shutil.copytree(project["pbip"], copy)
    target = copy / "AQMI.Report/definition/pages/p03capa/visuals/lessons/visual.json"
    content = target.read_text(encoding="utf-8").replace("visualContainer/2.1.0/", "visualContainer/2.99.0/")
    target.write_text(content, encoding="utf-8")
    result = validate_project(copy, project["data"])
    assert result["problems"] == []
    assert any("2.99.0" in f for f in result["stats"]["schema_fallbacks"])
    target.write_text(content.replace('"position": {', '"position": {"colour": 1,', 1), encoding="utf-8")
    assert any("SCHEMA" in p for p in validate_project(copy, project["data"])["problems"])


@pytest.mark.parametrize("relative, old, new, expected", [
    ("AQMI.SemanticModel/definition/tables/_Measures.tmdl", "Fact_Incidents[Is Cancelled]",
     "Fact_Incidents[Is Canceled]", "unknown column"),
    ("AQMI.SemanticModel/definition/tables/_Measures.tmdl", "[Completed Orders] )", "[Completed Order] )",
     "unknown measure"),
    ("AQMI.Report/definition/pages/p02quality/visuals/pareto/visual.json", '"Total Quality Incidents"',
     '"Total Quality Incident"', "unknown measure"),
    ("AQMI.Report/definition/pages/p01executive/visuals/cards/visual.json", '"position": {', '"position": {"colour": 1,',
     "SCHEMA"),
    ("AQMI.SemanticModel/definition/relationships.tmdl", "\tisActive: false\n\tfromColumn: Fact_Incidents.'Closed Date'",
     "\tfromColumn: Fact_Incidents.'Closed Date'", "active relationships"),
    ("AQMI.Report/definition/pages/p03capa/visuals/nav01/visual.json", "'p01executive'", "'p99nowhere'",
     "navigation to unknown page"),
    ("AQMI.SemanticModel/definition/tables/Dim_Aircraft.tmdl", "sourceColumn: fleet_number", "sourceColumn: fleet_no",
     "differs"),
    ("AQMI.Report/definition/pages/pages.json", '"activePageName"', '"activePageName" "', "JSON"),
    ("AQMI.SemanticModel/definition/tables/Dim_Aircraft.tmdl", "\tcolumn Registration",
     "\tRegistration column typed by hand\n\tcolumn Registration", "unexpected line"),
])
def test_validator_catches_defects(project, tmp_path, relative, old, new, expected):
    problems = _broken_copy(project, tmp_path, relative, old, new)
    assert any(expected in p for p in problems), problems
