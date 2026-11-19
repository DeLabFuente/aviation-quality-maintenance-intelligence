"""
Phase 5 tests: views, business queries and the 89 validation rules
(82 in Phase 5 + the 7 lessons-learned rules of Phase 9).

The most important tests here are the NEGATIVE ones: a defect is injected on
purpose into a copy of the database, and the corresponding rule must catch it
and close the quality gate. A control that never fails proves nothing.

Run from the main project folder:
    pytest -v
"""

import shutil
import sqlite3

import pytest

from config import settings
from scripts.common import get_connection
from scripts.generate_data import generate
from scripts.run_validations import PLANTED_RULE, load_rules, run_validations

WARNING_RULES = {"G05", "G11", "D12", "M08", "M09", "I09", "I16", "Q06", "Q08", "Q12", "Q13", "C08", "C10", "L07", "A01", "A02"}


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    """Generate the data set once, validate it and keep the database for the tests."""
    folder = tmp_path_factory.mktemp("validation")
    db_path = folder / "aqmi.db"
    planted = generate(db_path, export_dir=None)["planted"]
    summary = run_validations(db_path, report_dir=folder / "reports", planted=planted)
    return {"db": db_path, "planted": planted, "summary": summary, "folder": folder}


def _findings(summary, rule_id):
    return next(r for r in summary["rules"] if r.rule_id == rule_id).findings


def _copy(dataset, tmp_path):
    copy = tmp_path / "defective.db"
    shutil.copy(dataset["db"], copy)
    return copy


# -----------------------------------------------------------------------------
# 1. The rule catalogue
# -----------------------------------------------------------------------------
def test_catalogue_has_89_rules_with_valid_headers():
    rules = load_rules()
    assert len(rules) == 89
    assert len({r.rule_id for r in rules}) == 89


def test_severities_match_the_business_rules_document():
    for rule in load_rules():
        expected = "WARNING" if rule.rule_id in WARNING_RULES else "CRITICAL"
        assert rule.severity == expected, rule.rule_id


# -----------------------------------------------------------------------------
# 2. Results on the generated data
# -----------------------------------------------------------------------------
def test_every_rule_runs_without_error(dataset):
    assert [r.rule_id for r in dataset["summary"]["rules"] if r.error] == []


def test_no_critical_rule_fails(dataset):
    assert [r.rule_id for r in dataset["summary"]["rules"] if r.result == "FAIL"] == []


def test_quality_gate_passes(dataset):
    assert dataset["summary"]["gate_passed"] is True


def test_planted_discrepancies_are_detected_exactly(dataset):
    for row in dataset["summary"]["reconciliation"]:
        assert row["missed"] == [] and row["unexpected"] == [], row
    assert sum(r["detected"] for r in dataset["summary"]["reconciliation"]) == len(dataset["planted"])


def test_reports_are_written(dataset):
    report = (dataset["folder"] / "reports" / "validation_report.md").read_text(encoding="utf-8")
    assert "Quality gate" in report and "PASSED" in report
    assert (dataset["folder"] / "reports" / "validation_findings.csv").exists()


# -----------------------------------------------------------------------------
# 3. Negative tests: inject a defect, the rule must catch it
# -----------------------------------------------------------------------------
def _validate_copy(path):
    return run_validations(path, report_dir=None, planted=None)


def test_negative_stock_is_caught(dataset, tmp_path):                         # I03
    path = _copy(dataset, tmp_path)
    conn = get_connection(path)
    mo_id, material_id, actor = conn.execute(
        "SELECT mo_id, material_id, performed_by FROM Inventory_Movements WHERE movement_type = 'ISSUE' LIMIT 1").fetchone()
    conn.execute("""INSERT INTO Inventory_Movements (movement_number, movement_datetime, material_id, movement_type,
                    quantity, from_bucket, to_bucket, mo_id, lot_number, performed_by, created_at, created_by)
                    VALUES ('MV-2026-99999', '2026-10-30 10:00:00', ?, 'ISSUE', 999, 'RESERVED', NULL, ?, 'FAKE-LOT', ?,
                            '2026-10-30 10:00:00', ?)""", (material_id, mo_id, actor, actor))
    conn.commit()
    conn.close()
    summary = _validate_copy(path)
    assert _findings(summary, "I03")
    assert _findings(summary, "I07")                    # the fake lot was never received
    assert summary["gate_passed"] is False


def test_status_without_hold_is_caught(dataset, tmp_path):                    # M05
    path = _copy(dataset, tmp_path)
    conn = get_connection(path)
    mo_id, planner = conn.execute(
        "SELECT mo_id, planner_id FROM Maintenance_Orders WHERE status = 'IN_PROGRESS' LIMIT 1").fetchone()
    conn.execute("UPDATE Maintenance_Orders SET status = 'ON_HOLD', updated_at = '2026-10-31 18:00:00', updated_by = ? "
                 "WHERE mo_id = ?", (planner, mo_id))
    conn.commit()
    conn.close()
    summary = _validate_copy(path)
    assert len(_findings(summary, "M05")) == 1
    assert summary["gate_passed"] is False


def test_closed_incident_with_open_action_is_caught(dataset, tmp_path):       # Q05
    path = _copy(dataset, tmp_path)
    conn = get_connection(path)
    incident_id, owner, dept = conn.execute(
        "SELECT incident_id, owner_id, responsible_department_id FROM Quality_Incidents "
        "WHERE status = 'CLOSED' AND severity <> 'OBSERVATION' LIMIT 1").fetchone()
    conn.execute("""INSERT INTO CAPA_Actions (action_number, action_type, origin, incident_id, title, description,
                    responsible_id, department_id, created_date, original_due_date, due_date, status,
                    created_at, created_by)
                    VALUES ('CA-2026-9999', 'CORRECTIVE', 'INCIDENT', ?, 'Injected action', 'Test', ?, ?,
                            '2026-10-30', '2026-11-30', '2026-11-30', 'OPEN', '2026-10-30 10:00:00', ?)""",
                 (incident_id, owner, dept, owner))
    conn.commit()
    conn.close()
    summary = _validate_copy(path)
    assert len(_findings(summary, "Q05")) == 1
    assert summary["gate_passed"] is False


def test_broken_foreign_key_is_caught(dataset, tmp_path):                     # G01
    path = _copy(dataset, tmp_path)
    conn = sqlite3.connect(path)                         # foreign keys OFF on purpose
    conn.execute("""INSERT INTO Employees (employee_code, first_name, last_name, department_id, job_title, email,
                    hire_date, created_at) VALUES ('EMP-999', 'Test', 'Orphan', 999, 'Clerk',
                    'emp-999@aeroq-mro.example', '2020-01-01', '2026-10-30 10:00:00')""")
    conn.commit()
    conn.close()
    summary = _validate_copy(path)
    assert _findings(summary, "G01")
    assert summary["gate_passed"] is False


def test_missed_planted_discrepancy_closes_the_gate(dataset):
    fake = dataset["planted"] + [{"kind": "INCIDENT_WITHOUT_LINKS", "table": "Quality_Incidents",
                                  "reference": "NC-2099-9999", "date": "", "description": "not in the data"}]
    summary = run_validations(dataset["db"], report_dir=None, planted=fake)
    assert summary["reconciliation_ok"] is False
    assert summary["gate_passed"] is False


# -----------------------------------------------------------------------------
# 4. Views agree with the rules and with the movements
# -----------------------------------------------------------------------------
def test_views_agree_with_warning_rules(dataset):
    conn = get_connection(dataset["db"])
    summary = dataset["summary"]
    overdue_docs = conn.execute("SELECT COUNT(*) FROM vw_document_status WHERE validity_status = 'REVIEW_OVERDUE'").fetchone()[0]
    overdue_actions = conn.execute("SELECT SUM(is_overdue) FROM vw_capa_status").fetchone()[0]
    overdue_incidents = conn.execute("SELECT SUM(is_overdue) FROM vw_incident_status").fetchone()[0]
    conn.close()
    assert overdue_docs == len(_findings(summary, "D12"))
    assert overdue_actions == len(_findings(summary, "C10"))
    assert overdue_incidents == len(_findings(summary, "Q12"))


def test_stock_view_matches_movements(dataset):
    conn = get_connection(dataset["db"])
    view_total = conn.execute("SELECT ROUND(SUM(on_hand_qty), 3) FROM vw_stock_by_bucket").fetchone()[0]
    movement_total = conn.execute("""SELECT ROUND(SUM(CASE WHEN to_bucket IS NOT NULL THEN quantity ELSE 0 END)
                                            - SUM(CASE WHEN from_bucket IS NOT NULL THEN quantity ELSE 0 END), 3)
                                     FROM Inventory_Movements""").fetchone()[0]
    conn.close()
    assert view_total == movement_total


def test_every_view_returns_rows(dataset):
    conn = get_connection(dataset["db"])
    views = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'view'")]
    empty = [v for v in views if conn.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0] == 0]
    conn.close()
    assert len(views) == 15 and empty == []


@pytest.mark.parametrize("query_file", sorted(p.name for p in settings.SQL_QUERIES_DIR.glob("*.sql")))
def test_business_query_runs_and_returns_rows(dataset, query_file):
    conn = get_connection(dataset["db"])
    rows = conn.execute((settings.SQL_QUERIES_DIR / query_file).read_text(encoding="utf-8")).fetchall()
    conn.close()
    assert rows


def test_planted_kinds_have_a_rule():
    assert set(PLANTED_RULE) == {"OBSOLETE_REVISION_LINK", "RECEIPT_WITHOUT_CERTIFICATE",
                                 "FALSE_MATERIAL_HOLD", "INCIDENT_WITHOUT_LINKS"}
