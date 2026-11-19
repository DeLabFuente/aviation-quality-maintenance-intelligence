"""
Phase 6 tests: the 18 indicators (KPIs) and the indicator rules K01, K02, K04, K05.

Three kinds of test:
  * the catalogue and the results have the expected structure;
  * several KPIs are recalculated in plain Python, independently of the SQL,
    and both results must be identical;
  * NEGATIVE tests: a wrong value or a tampered history is introduced on
    purpose and the K rules must catch it.

Run from the main project folder:
    pytest -v
"""

import shutil
import sqlite3
from copy import deepcopy
from datetime import date

import pytest

from scripts import run_kpis as rk
from scripts.common import get_connection
from scripts.generate_data import generate

REQUIRED = {  # the KPIs requested in the project brief
    "Total Quality Incidents", "Open Non-Conformities", "Non-Conformity Rate", "Corrective Action Closure Rate",
    "Average Resolution Time", "Overdue Corrective Actions", "Document Compliance Rate",
    "Documentation Error Rate", "Expired Documents", "Traceability Compliance", "Inventory Accuracy",
    "Stock Availability", "Material Shortage Rate", "Pending Purchase Orders",
    "Maintenance Order Completion Rate", "Average Maintenance Delay", "Work Orders Blocked by Material",
    "Work Orders Blocked by Documentation",
}


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    folder = tmp_path_factory.mktemp("kpis")
    db_path = folder / "aqmi.db"
    generate(db_path, export_dir=None)
    summary = rk.run_kpis(db_path, report_dir=folder / "reports")
    return {"db": db_path, "summary": summary, "folder": folder,
            "kpi": {k.kpi_id: k for k in summary["kpis"]}}


def _total(dataset, kpi_id):
    return dataset["kpi"][kpi_id].total


# -----------------------------------------------------------------------------
# 1. Catalogue and structure
# -----------------------------------------------------------------------------
def test_catalogue_has_the_18_requested_kpis():
    kpis = rk.load_kpis()
    assert len(kpis) == 18
    assert {k.name for k in kpis} == REQUIRED
    assert {a: sum(k.area == a for k in kpis) for a in rk.AREAS} == \
        {"Quality": 6, "Document control": 4, "Inventory": 4, "Maintenance": 4}


def test_targets_are_marked_as_fictitious():
    for k in rk.load_kpis():
        header = k.sql.split("-- question:")[0]
        if k.target is not None:
            assert "fictitious internal target of AEROQ MRO" in header, k.kpi_id
            assert k.warning is not None and k.direction != "NEUTRAL", k.kpi_id


def test_every_kpi_returns_24_months_and_a_total(dataset):
    for k in dataset["summary"]["kpis"]:
        assert k.error is None, (k.kpi_id, k.error)
        assert len(k.months) == 24 and k.total is not None, k.kpi_id


def test_k_rules_pass(dataset):
    assert {rule: findings for rule, findings in dataset["summary"]["checks"].items() if findings} == {}
    assert dataset["summary"]["gate_passed"] is True


def test_reports_are_written(dataset):
    report = (dataset["folder"] / "reports" / "kpi_report.md").read_text(encoding="utf-8")
    assert "fictitious internal targets" in report and "PASSED" in report
    lines = (dataset["folder"] / "reports" / "kpi_values.csv").read_text(encoding="utf-8-sig").splitlines()
    assert len(lines) == 1 + 18 * 25


# -----------------------------------------------------------------------------
# 2. Independent recalculation in Python
# -----------------------------------------------------------------------------
@pytest.fixture(scope="module")
def raw(dataset):
    conn = get_connection(dataset["db"])
    conn.row_factory = sqlite3.Row
    data = {t: [dict(r) for r in conn.execute(f"SELECT * FROM {t}")] for t in (
        "Quality_Incidents", "Document_Verifications", "Maintenance_Orders", "Inventory_Movements",
        "Materials", "CAPA_Actions", "Stock_Counts")}
    data["due_changes"] = [dict(r) for r in conn.execute(
        "SELECT * FROM Audit_Log WHERE table_name = 'CAPA_Actions' AND field_name = 'due_date' ORDER BY audit_id")]
    data["as_of"] = conn.execute("SELECT as_of_date FROM vw_parameters").fetchone()[0]
    conn.close()
    return data


def test_total_incidents_recalculated(dataset, raw):
    expected = sum(1 for i in raw["Quality_Incidents"] if i["status"] != "CANCELLED")
    assert _total(dataset, "QUA-01")["value"] == expected


def test_documentation_error_rate_recalculated(dataset, raw):
    checks = [v for v in raw["Document_Verifications"] if v["verification_type"] != "INTERNAL_AUDIT"]
    errors = sum(v["result"] != "CONFORM" for v in checks)
    assert _total(dataset, "DOC-02")["value"] == round(100 * errors / len(checks), 1)


def test_inventory_accuracy_recalculated(dataset, raw):
    cycle = [s for s in raw["Stock_Counts"] if s["count_type"] == "CYCLE"]
    matches = sum(s["counted_qty"] == s["system_qty"] for s in cycle)
    assert _total(dataset, "INV-01")["value"] == round(100 * matches / len(cycle), 1)


def test_average_delay_recalculated(dataset, raw):
    done = [o for o in raw["Maintenance_Orders"] if o["actual_end_date"] and o["status"] != "CANCELLED"]
    delays = [max(0, (date.fromisoformat(o["actual_end_date"]) - date.fromisoformat(o["planned_end_date"])).days)
              for o in done]
    assert _total(dataset, "MNT-02")["value"] == round(sum(delays) / len(delays), 1)


def test_stock_availability_recalculated(dataset, raw):
    available = {}
    for v in raw["Inventory_Movements"]:
        if v["to_bucket"] == "AVAILABLE":
            available[v["material_id"]] = available.get(v["material_id"], 0) + v["quantity"]
        if v["from_bucket"] == "AVAILABLE":
            available[v["material_id"]] = available.get(v["material_id"], 0) - v["quantity"]
    active = [m for m in raw["Materials"] if m["is_active"]]
    ok = sum(round(available.get(m["material_id"], 0), 3) >= m["min_stock_qty"] for m in active)
    assert (_total(dataset, "INV-02")["numerator"], _total(dataset, "INV-02")["denominator"]) == (ok, len(active))


@pytest.mark.parametrize("period, day", [("2025-04", "2025-04-30"), ("2025-10", "2025-10-31"), ("2026-06", "2026-06-30")])
def test_overdue_actions_in_the_past_recalculated(dataset, raw, period, day):
    """Replays the audit log in Python to find the due date in force on a past date."""
    def due_then(action):
        changes = [h for h in raw["due_changes"] if h["record_id"] == action["action_id"]]
        before = [h for h in changes if h["event_datetime"][:10] <= day]
        after = [h for h in changes if h["event_datetime"][:10] > day]
        return before[-1]["new_value"] if before else after[0]["old_value"] if after else action["due_date"]

    expected = sum(1 for a in raw["CAPA_Actions"]
                   if a["action_type"] == "CORRECTIVE" and a["status"] != "CANCELLED" and a["created_date"] <= day
                   and (a["completed_date"] is None or a["completed_date"] > day) and due_then(a) < day)
    row = next(r for r in dataset["kpi"]["QUA-06"].rows if r["period"] == period)
    assert row["value"] == expected


# -----------------------------------------------------------------------------
# 3. The data stories are visible in the indicators
# -----------------------------------------------------------------------------
def test_counting_procedure_improves_inventory_accuracy(dataset):
    year1, year2 = rk.years(dataset["kpi"]["INV-01"])
    assert year2 > year1 + 5


def test_fewer_non_conformities_per_order_in_year_two(dataset):
    year1, year2 = rk.years(dataset["kpi"]["QUA-03"])
    assert year2 < year1


def test_receipts_without_certificate_break_traceability(dataset):
    """The 2 planted receipts without certificate are the only cause of incomplete traceability."""
    conn = get_connection(dataset["db"])
    lots = [r[0] for r in conn.execute("SELECT lot_number FROM Inventory_Movements "
                                       "WHERE movement_type = 'RECEIPT' AND certificate_ref IS NULL")]
    issued = conn.execute(f"SELECT COUNT(*) FROM Inventory_Movements WHERE movement_type = 'ISSUE' "
                          f"AND lot_number IN ({','.join('?' * len(lots))})", lots).fetchone()[0]
    conn.close()
    total = _total(dataset, "DOC-04")
    assert len(lots) == 2 and issued > 0
    assert total["denominator"] - total["numerator"] == issued


# -----------------------------------------------------------------------------
# 4. Negative tests: the K rules must catch wrong values
# -----------------------------------------------------------------------------
def _copy_kpi(dataset, kpi_id):
    return deepcopy(dataset["kpi"][kpi_id])


def test_k01_catches_percentage_above_100(dataset):
    k = _copy_kpi(dataset, "DOC-01")
    k.rows[3]["value"] = 120.0
    assert rk.check_k01([k]) and rk.check_k01([dataset["kpi"]["DOC-01"]]) == []


def test_k02_catches_zero_shown_instead_of_no_data(dataset):
    k = _copy_kpi(dataset, "MNT-01")
    k.rows[0].update(numerator=0, denominator=0, value=0.0)
    assert rk.check_k02([k])


def test_k04_catches_parts_not_adding_up(dataset):
    k = _copy_kpi(dataset, "QUA-01")
    k.rows[5]["numerator"] += 1
    conn = get_connection(dataset["db"])
    findings = rk.check_k04([k], conn)
    conn.close()
    assert findings and rk.check_k04([dataset["kpi"]["QUA-01"]], get_connection(dataset["db"])) == []


def test_k05_catches_a_tampered_audit_trail(dataset, tmp_path):
    """If the history of a due date is altered, the past no longer matches the present."""
    path = tmp_path / "tampered.db"
    shutil.copy(dataset["db"], path)
    conn = sqlite3.connect(path)
    for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type = 'trigger' AND tbl_name = 'Audit_Log'").fetchall():
        conn.execute(f"DROP TRIGGER {name}")          # the audit log is protected; remove the protection on the copy
    audit_id = conn.execute("""SELECT MAX(h.audit_id) FROM Audit_Log h
                               JOIN vw_capa_status c ON c.action_id = h.record_id
                               WHERE h.table_name = 'CAPA_Actions' AND h.field_name = 'due_date'
                                 AND c.is_overdue = 1""").fetchone()[0]
    assert audit_id is not None
    conn.execute("UPDATE Audit_Log SET new_value = '2099-12-31' WHERE audit_id = ?", (audit_id,))
    conn.commit()
    conn.close()
    summary = rk.run_kpis(path, report_dir=None)
    assert [f[0] for f in summary["checks"]["K05"]] == ["QUA-06"]
    assert summary["gate_passed"] is False


def test_a_kpi_that_cannot_run_closes_the_gate(dataset, monkeypatch):
    kpis = rk.load_kpis()
    kpis[0].sql = "SELECT * FROM table_that_does_not_exist"
    monkeypatch.setattr(rk, "load_kpis", lambda: kpis)
    summary = rk.run_kpis(dataset["db"], report_dir=None)
    assert summary["n_errors"] == 1 and summary["gate_passed"] is False


@pytest.mark.parametrize("direction, value, expected", [
    ("HIGHER_IS_BETTER", 95.0, "GREEN"), ("HIGHER_IS_BETTER", 94.9, "AMBER"),
    ("HIGHER_IS_BETTER", 90.0, "AMBER"), ("HIGHER_IS_BETTER", 89.9, "RED"),
    ("LOWER_IS_BETTER", 5.0, "GREEN"), ("LOWER_IS_BETTER", 8.0, "AMBER"), ("LOWER_IS_BETTER", 8.1, "RED"),
    ("HIGHER_IS_BETTER", None, "NO_DATA"),
])
def test_traffic_light(dataset, direction, value, expected):
    k = _copy_kpi(dataset, "DOC-01")
    k.direction = direction
    k.target, k.warning = (95, 90) if direction == "HIGHER_IS_BETTER" else (5, 8)
    assert rk.status(k, value) == expected
