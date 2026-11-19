"""
Phase 9 tests: the lessons-learned register (table Lessons_Learned, rules L01-L07,
KPI LRN-01).

Three groups of tests:
  1. The database itself rejects lessons that break the rules (CHECK constraints
     and triggers): the bad data cannot even be written.
  2. The generated lessons are coherent, tell the NC-2025-0021 story, and did
     NOT change a single record that existed before Phase 9.
  3. Negative tests: a defect injected into a copy of the database is caught by
     the corresponding validation rule.

Run from the main project folder:
    pytest -v tests/test_lessons_learned.py
"""

import hashlib
import shutil
import sqlite3

import pytest

from config import generator_parameters as P
from scripts.common import get_connection
from scripts.generate_data import generate
from scripts.run_kpis import run_kpis
from scripts.run_validations import run_validations
from tests.conftest import TS

# Fingerprint of the 24 tables of v1.0 (Phase 8) generated with seed 145. It covers every
# record created by the simulation, including its audit trail. The only rows left out are
# the new ones: the audit events of Lessons_Learned and the SCHEMA_VERSION parameter.
V1_FINGERPRINT = "e380cf4fe3f177b5dff0e55aeaab9f5b9b48bc1cc94221cdf3eda78755a53799"
V1_TABLES = [
    "System_Parameters", "Departments", "Employees", "Customers", "Aircraft", "Suppliers",
    "Materials", "Documents", "Document_Revisions", "Maintenance_Orders",
    "Maintenance_Order_Materials", "Maintenance_Order_Documents", "Maintenance_Order_Holds",
    "Purchase_Orders", "Purchase_Order_Lines", "Incident_Categories", "Quality_Incidents",
    "Document_Verifications", "Root_Cause_Analyses", "CAPA_Actions", "CAPA_Progress_Updates",
    "Stock_Counts", "Inventory_Movements", "Audit_Log",
]


# -----------------------------------------------------------------------------
# 1. The database enforces the rules
# -----------------------------------------------------------------------------
@pytest.fixture
def closed_action(db, base_data):
    """A closed, verified preventive action (no incident needed) and a document revision."""
    emp1, emp2 = base_data["emp1"], base_data["emp2"]
    dept = db.execute("SELECT department_id FROM Departments WHERE department_code = 'QUA'").fetchone()[0]
    action = db.execute(
        "INSERT INTO CAPA_Actions (action_number, action_type, origin, title, description, responsible_id, "
        "department_id, created_date, original_due_date, due_date, completed_date, status, "
        "effectiveness_check_date, effectiveness_result, verified_by, closed_date, created_at, created_by) "
        "VALUES ('PA-2025-0001', 'PREVENTIVE', 'TREND_ANALYSIS', 'Trend review', 'Test', ?, ?, '2025-01-10', "
        "'2025-02-10', '2025-02-10', '2025-02-01', 'CLOSED', '2025-03-01', 'EFFECTIVE', ?, '2025-03-01', ?, ?)",
        (emp1, dept, emp2, TS, emp1)).lastrowid
    revision = db.execute(
        "INSERT INTO Document_Revisions (document_id, revision_code, revision_seq, issue_date, effective_date, "
        "review_due_date, lifecycle_status, prepared_by, approved_by, change_summary, created_at, created_by) "
        "VALUES (?, 'R00', 0, '2025-04-01', '2025-04-05', '2027-04-05', 'CURRENT', ?, ?, 'Initial issue', ?, ?)",
        (base_data["document"], emp2, emp1, TS, emp2)).lastrowid
    db.commit()
    return {"action": action, "revision": revision, "dept": dept, **base_data}


def _lesson(db, data, **values):
    row = {"lesson_number": "LL-2025-0001", "action_id": data["action"], "title": "Test lesson",
           "lesson_text": "What was learned", "recommendation": "What to change", "department_id": data["dept"],
           "scope": "DEPARTMENT", "status": "PROPOSED", "proposed_date": "2025-03-05",
           "proposed_by": data["emp1"], "created_at": "2025-03-05 10:00:00", "created_by": data["emp1"]}
    row.update(values)
    columns = ", ".join(row)
    return db.execute(f"INSERT INTO Lessons_Learned ({columns}) VALUES ({', '.join('?' for _ in row)})",
                      tuple(row.values())).lastrowid


def test_valid_lesson_life_cycle_is_accepted_and_audited(db, closed_action):
    lesson = _lesson(db, closed_action)
    db.execute("UPDATE Lessons_Learned SET status = 'APPROVED', approved_date = '2025-03-10', approved_by = ?, "
               "updated_at = '2025-03-10 11:00:00', updated_by = ? WHERE lesson_id = ?",
               (closed_action["emp2"], closed_action["emp2"], lesson))
    db.execute("UPDATE Lessons_Learned SET status = 'INCORPORATED', incorporated_date = '2025-04-07', "
               "incorporated_revision_id = ?, updated_at = '2025-04-07 09:00:00', updated_by = ? WHERE lesson_id = ?",
               (closed_action["revision"], closed_action["emp2"], lesson))
    statuses = [r[0] for r in db.execute(
        "SELECT new_value FROM Audit_Log WHERE table_name = 'Lessons_Learned' AND field_name = 'status' "
        "ORDER BY audit_id")]
    assert statuses == ["APPROVED", "INCORPORATED"]
    assert db.execute("SELECT COUNT(*) FROM Audit_Log WHERE table_name = 'Lessons_Learned' "
                      "AND action = 'INSERT'").fetchone()[0] == 1


def test_lesson_cannot_be_approved_by_its_proposer(db, closed_action):       # L02
    with pytest.raises(sqlite3.IntegrityError):
        _lesson(db, closed_action, status="APPROVED", approved_date="2025-03-10", approved_by=closed_action["emp1"])


def test_rejection_needs_a_reason(db, closed_action):                        # L03
    with pytest.raises(sqlite3.IntegrityError):
        _lesson(db, closed_action, status="REJECTED", rejected_date="2025-03-10", rejected_by=closed_action["emp2"])
    _lesson(db, closed_action, status="REJECTED", rejected_date="2025-03-10", rejected_by=closed_action["emp2"],
            rejection_reason="Already covered by the procedure")


def test_incorporated_lesson_needs_a_revision(db, closed_action):            # L03
    with pytest.raises(sqlite3.IntegrityError):
        _lesson(db, closed_action, status="INCORPORATED", approved_date="2025-03-10",
                approved_by=closed_action["emp2"], incorporated_date="2025-04-07")


def test_approved_lesson_cannot_point_to_a_revision(db, closed_action):      # L03
    with pytest.raises(sqlite3.IntegrityError):
        _lesson(db, closed_action, status="APPROVED", approved_date="2025-03-10", approved_by=closed_action["emp2"],
                incorporated_date="2025-04-07", incorporated_revision_id=closed_action["revision"])


def test_incorporation_cannot_precede_the_approval(db, closed_action):       # L04
    with pytest.raises(sqlite3.IntegrityError):
        _lesson(db, closed_action, status="INCORPORATED", approved_date="2025-04-10",
                approved_by=closed_action["emp2"], incorporated_date="2025-04-07",
                incorporated_revision_id=closed_action["revision"])


def test_lesson_requires_an_action(db, closed_action):
    with pytest.raises(sqlite3.IntegrityError):
        _lesson(db, closed_action, action_id=None)
    with pytest.raises(sqlite3.IntegrityError):
        _lesson(db, closed_action, action_id=9999)


@pytest.mark.parametrize("number", ["LL-25-0001", "LL-2025-001", "LE-2025-0001"])
def test_lesson_number_format(db, closed_action, number):                    # G02
    with pytest.raises(sqlite3.IntegrityError):
        _lesson(db, closed_action, lesson_number=number)


def test_lesson_cannot_be_deleted(db, closed_action):                        # G09
    lesson = _lesson(db, closed_action)
    with pytest.raises(sqlite3.IntegrityError, match="G09"):
        db.execute("DELETE FROM Lessons_Learned WHERE lesson_id = ?", (lesson,))


# -----------------------------------------------------------------------------
# 2. The generated lessons
# -----------------------------------------------------------------------------
@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    folder = tmp_path_factory.mktemp("lessons")
    db_path = folder / "aqmi.db"
    planted = generate(db_path, export_dir=None)["planted"]
    summary = run_validations(db_path, report_dir=None, planted=planted)
    conn = get_connection(db_path)
    yield {"db": db_path, "conn": conn, "planted": planted, "summary": summary}
    conn.close()


def _scalar(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


def test_existing_data_did_not_change_since_v1(dataset):
    """The lessons are generated after the simulation with their own random generator:
    every record of v1.0 (and therefore every KPI, the case study and the screenshots) is unchanged."""
    conn, digest = dataset["conn"], hashlib.sha256()
    for table in V1_TABLES:
        where = {"Audit_Log": " WHERE table_name <> 'Lessons_Learned'",
                 "System_Parameters": " WHERE parameter_key <> 'SCHEMA_VERSION'"}.get(table, "")
        for row in conn.execute(f"SELECT * FROM {table}{where} ORDER BY 1"):
            digest.update(repr(row).encode())
    assert digest.hexdigest() == V1_FINGERPRINT


def test_lessons_are_audited_after_the_existing_events(dataset):
    conn = dataset["conn"]
    first_lesson_event = _scalar(conn, "SELECT MIN(audit_id) FROM Audit_Log WHERE table_name = 'Lessons_Learned'")
    last_other_event = _scalar(conn, "SELECT MAX(audit_id) FROM Audit_Log WHERE table_name <> 'Lessons_Learned'")
    assert first_lesson_event > last_other_event
    assert _scalar(conn, "SELECT COUNT(*) FROM Lessons_Learned") == _scalar(
        conn, "SELECT COUNT(*) FROM Audit_Log WHERE table_name = 'Lessons_Learned' AND action = 'INSERT'")


def test_volume_and_every_outcome_present(dataset):
    conn = dataset["conn"]
    assert 40 <= _scalar(conn, "SELECT COUNT(*) FROM Lessons_Learned") <= 90
    statuses = {r[0] for r in conn.execute("SELECT DISTINCT status FROM Lessons_Learned")}
    assert {"APPROVED", "INCORPORATED", "REJECTED"} <= statuses
    assert {r[0] for r in conn.execute("SELECT DISTINCT scope FROM Lessons_Learned")} == {"DEPARTMENT", "COMPANY"}


def test_some_approved_lessons_are_pending(dataset):
    assert _scalar(dataset["conn"], "SELECT COUNT(*) FROM Lessons_Learned WHERE status = 'APPROVED'") >= 3


def test_lessons_come_only_from_closed_and_verified_actions(dataset):       # L01
    assert _scalar(dataset["conn"], """
        SELECT COUNT(*) FROM Lessons_Learned l JOIN CAPA_Actions a USING (action_id)
         WHERE a.status <> 'CLOSED' OR a.effectiveness_result IS NULL OR l.proposed_date < a.closed_date""") == 0


def test_not_effective_actions_leave_a_lesson_that_is_kept(dataset):
    conn = dataset["conn"]
    missing = _scalar(conn, """
        SELECT COUNT(*) FROM CAPA_Actions a
         WHERE a.status = 'CLOSED' AND a.effectiveness_result = 'NOT_EFFECTIVE'
           AND a.closed_date <= date((SELECT as_of_date FROM vw_parameters), '-30 days')
           AND NOT EXISTS (SELECT 1 FROM Lessons_Learned l WHERE l.action_id = a.action_id)""")
    assert missing == 0
    assert _scalar(conn, """SELECT COUNT(*) FROM Lessons_Learned l JOIN CAPA_Actions a USING (action_id)
                             WHERE a.effectiveness_result = 'NOT_EFFECTIVE'""") > 0
    assert _scalar(conn, """SELECT COUNT(*) FROM Lessons_Learned l JOIN CAPA_Actions a USING (action_id)
                             WHERE a.effectiveness_result = 'NOT_EFFECTIVE' AND l.status = 'REJECTED'""") == 0


def test_story_nc_2025_0021_lesson_is_incorporated_in_the_redesigned_form(dataset):
    row = dataset["conn"].execute("""
        SELECT l.status, d.document_code, r.revision_code, l.proposed_by <> l.approved_by
          FROM Lessons_Learned l JOIN CAPA_Actions a USING (action_id)
          JOIN Quality_Incidents i ON i.incident_id = a.incident_id
          JOIN Document_Revisions r ON r.revision_id = l.incorporated_revision_id
          JOIN Documents d ON d.document_id = r.document_id
         WHERE i.incident_number = 'NC-2025-0021'""").fetchall()
    assert row == [("INCORPORATED", P.CLOSURE_FORM_DOC, "R01", 1)]


def test_lesson_numbers_follow_the_order_of_proposal(dataset):
    rows = dataset["conn"].execute(
        "SELECT lesson_number, created_at FROM Lessons_Learned ORDER BY lesson_number").fetchall()
    for year in {n[3:7] for n, _ in rows}:
        of_year = [(n, t) for n, t in rows if n[3:7] == year]
        assert [t for _, t in of_year] == sorted(t for _, t in of_year)
        assert int(of_year[-1][0][-4:]) == len(of_year)


def test_lesson_rules_pass_on_the_generated_data(dataset):
    results = {r.rule_id: r.result for r in dataset["summary"]["rules"] if r.rule_id.startswith("L")}
    assert results == {"L01": "PASS", "L02": "PASS", "L03": "PASS", "L04": "PASS", "L05": "PASS",
                       "L06": "PASS", "L07": "WARNING"}


def test_lrn01_matches_the_register(dataset):
    kpi = next(k for k in run_kpis(dataset["db"], report_dir=None)["kpis"] if k.kpi_id == "LRN-01")
    conn = dataset["conn"]
    incorporated = _scalar(conn, "SELECT COUNT(*) FROM Lessons_Learned WHERE status = 'INCORPORATED'")
    approved = _scalar(conn, "SELECT COUNT(*) FROM Lessons_Learned WHERE status IN ('APPROVED', 'INCORPORATED')")
    assert (kpi.total["numerator"], kpi.total["denominator"]) == (incorporated, approved)
    assert kpi.total["value"] == round(100 * incorporated / approved, 1)
    assert kpi.target == 80 and "fictitious internal target of AEROQ MRO" in kpi.sql


# -----------------------------------------------------------------------------
# 3. Negative tests: the validation rules catch injected defects
# -----------------------------------------------------------------------------
def _defective(dataset, tmp_path, sql, params=()):
    path = tmp_path / "defective.db"
    shutil.copy(dataset["db"], path)
    conn = get_connection(path)
    conn.execute(sql, params)
    conn.commit()
    conn.close()
    return run_validations(path, report_dir=None, planted=dataset["planted"])


def _findings(summary, rule_id):
    return next(r for r in summary["rules"] if r.rule_id == rule_id).findings


def test_lesson_from_an_open_action_is_caught(dataset, tmp_path):            # L01
    open_action = _scalar(dataset["conn"], "SELECT action_id FROM CAPA_Actions WHERE status = 'IN_PROGRESS' LIMIT 1")
    lesson = _scalar(dataset["conn"], "SELECT lesson_id FROM Lessons_Learned ORDER BY lesson_id DESC LIMIT 1")
    summary = _defective(dataset, tmp_path,
                         "UPDATE Lessons_Learned SET action_id = ?, updated_at = '2026-10-31 22:00:00', updated_by = 4 "
                         "WHERE lesson_id = ?", (open_action, lesson))
    assert len(_findings(summary, "L01")) == 1
    assert summary["gate_passed"] is False


def test_lesson_incorporated_into_a_record_is_caught(dataset, tmp_path):     # L05
    conn = dataset["conn"]
    lesson, approved = conn.execute("SELECT lesson_id, approved_date FROM Lessons_Learned "
                                    "WHERE status = 'INCORPORATED' ORDER BY lesson_id LIMIT 1").fetchone()
    record = _scalar(conn, """SELECT r.revision_id FROM Document_Revisions r JOIN Documents d USING (document_id)
                               WHERE d.document_type = 'AIRCRAFT_RECORD' LIMIT 1""")
    summary = _defective(dataset, tmp_path,
                         "UPDATE Lessons_Learned SET incorporated_revision_id = ?, "
                         "updated_at = '2026-10-31 22:00:00', updated_by = 11 WHERE lesson_id = ?", (record, lesson))
    assert len(_findings(summary, "L05")) == 1
    assert summary["gate_passed"] is False


def test_lesson_incorporated_into_an_older_revision_is_caught(dataset, tmp_path):   # L06
    conn = dataset["conn"]
    lesson, action_id = conn.execute(
        "SELECT lesson_id, action_id FROM Lessons_Learned WHERE status = 'INCORPORATED' "
        "AND lesson_id <> (SELECT l.lesson_id FROM Lessons_Learned l JOIN CAPA_Actions a USING (action_id) "
        "JOIN Quality_Incidents i ON i.incident_id = a.incident_id WHERE i.incident_number = 'NC-2025-0021') "
        "ORDER BY lesson_id DESC LIMIT 1").fetchone()
    old = _scalar(conn, """SELECT r.revision_id FROM Document_Revisions r JOIN Documents d USING (document_id)
                            WHERE d.is_controlled = 1 AND d.document_type = 'PROCEDURE'
                              AND r.lifecycle_status = 'CURRENT' AND r.effective_date < '2024-01-01' LIMIT 1""")
    summary = _defective(dataset, tmp_path,
                         "UPDATE Lessons_Learned SET incorporated_revision_id = ?, "
                         "updated_at = '2026-10-31 22:00:00', updated_by = 11 WHERE lesson_id = ?", (old, lesson))
    assert len(_findings(summary, "L06")) == 1
    assert summary["gate_passed"] is False


def test_lesson_proposed_after_the_proposer_left_is_caught(dataset, tmp_path):     # G06
    leaver = _scalar(dataset["conn"], "SELECT employee_id FROM Employees WHERE termination_date IS NOT NULL LIMIT 1")
    lesson = _scalar(dataset["conn"], "SELECT lesson_id FROM Lessons_Learned WHERE proposed_date > "
                                      "(SELECT MAX(termination_date) FROM Employees) "
                                      "AND status IN ('PROPOSED', 'APPROVED', 'INCORPORATED') "
                                      "AND approved_by <> ? LIMIT 1", (leaver,))
    summary = _defective(dataset, tmp_path,
                         "UPDATE Lessons_Learned SET proposed_by = ?, updated_at = '2026-10-31 22:00:00', "
                         "updated_by = 4 WHERE lesson_id = ?", (leaver, lesson))
    assert any("Lessons_Learned.proposed_by" in detail for _, detail in _findings(summary, "G06"))
    assert summary["gate_passed"] is False
