"""
Phase 3 tests: the database is built correctly and really enforces its rules.

Run from the main project folder:
    pytest -v

Every test that expects a rejection checks that SQLite raises an error,
i.e. that the bad data CANNOT enter the database.
"""

import sqlite3

import pytest

from config import settings
from scripts.common import get_connection
from tests.conftest import TS, add_employee

EXPECTED_TABLES = {
    "System_Parameters", "Departments", "Employees", "Customers", "Aircraft", "Suppliers",
    "Materials", "Documents", "Document_Revisions", "Maintenance_Orders",
    "Maintenance_Order_Materials", "Maintenance_Order_Documents", "Purchase_Orders",
    "Purchase_Order_Lines", "Incident_Categories", "Quality_Incidents",
    "Maintenance_Order_Holds", "Document_Verifications", "Root_Cause_Analyses",
    "CAPA_Actions", "CAPA_Progress_Updates", "Stock_Counts", "Inventory_Movements", "Audit_Log",
    "Lessons_Learned",   # Phase 9
}


# -----------------------------------------------------------------------------
# 1. Structure
# -----------------------------------------------------------------------------
def test_all_25_tables_exist(db):
    rows = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    assert {r[0] for r in rows} == EXPECTED_TABLES


def test_every_table_is_strict(db):
    rows = db.execute("SELECT name, strict FROM pragma_table_list WHERE schema='main' AND type='table' "
                      "AND name NOT LIKE 'sqlite_%'").fetchall()
    not_strict = [name for name, strict in rows if strict != 1]
    assert not_strict == []


def test_integrity_and_foreign_key_checks_pass(db):
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []


def test_connection_has_foreign_keys_on(db):
    assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_trigger_file_is_generated(db):
    text = settings.GENERATED_TRIGGERS_FILE.read_text(encoding="utf-8")
    assert "GENERATED AUTOMATICALLY" in text
    assert "trg_quality_incidents_audit_update" in text


def test_every_audited_table_is_accepted_by_audit_log(db):
    """Audit_Log.table_name must accept every table that has audit triggers (rule A05)."""
    audited = [r[0] for r in db.execute(
        "SELECT DISTINCT tbl_name FROM sqlite_master WHERE type='trigger' AND name LIKE '%_audit_insert'")]
    assert len(audited) == 22
    for table in audited:   # inserting a fake event must not violate the CHECK
        db.execute("INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, source) "
                   "VALUES (?, ?, 0, 'INSERT', 'SYSTEM')", (TS, table))


# -----------------------------------------------------------------------------
# 2. Reference data
# -----------------------------------------------------------------------------
def test_reference_data_loaded(db):
    assert db.execute("SELECT COUNT(*) FROM Departments").fetchone()[0] == 6
    assert db.execute("SELECT COUNT(*) FROM Incident_Categories").fetchone()[0] == 8
    as_of = db.execute("SELECT parameter_value FROM System_Parameters "
                       "WHERE parameter_key='AS_OF_DATE'").fetchone()[0]
    assert as_of == settings.AS_OF_DATE


def test_reference_data_was_audited(db):
    count = db.execute("SELECT COUNT(*) FROM Audit_Log WHERE table_name='Departments' "
                       "AND action='INSERT'").fetchone()[0]
    assert count == 6


# -----------------------------------------------------------------------------
# 3. Data types, formats and foreign keys (rules G01, G02, G03)
# -----------------------------------------------------------------------------
def test_foreign_key_rejects_unknown_department(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO Employees (employee_code, first_name, last_name, department_id, "
                   "job_title, email, hire_date, created_at) VALUES ('EMP-099', 'A', 'B', 999, "
                   "'Clerk', 'emp-099@aeroq-mro.example', '2020-01-01', ?)", (TS,))


def test_invalid_date_is_rejected(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO Employees (employee_code, first_name, last_name, department_id, "
                   "job_title, email, hire_date, created_at) VALUES ('EMP-098', 'A', 'B', 1, "
                   "'Clerk', 'emp-098@aeroq-mro.example', '2025-02-30', ?)", (TS,))


def test_wrong_code_format_is_rejected(db):
    with pytest.raises(sqlite3.IntegrityError):
        add_employee(db, code="E-1")


def test_strict_table_rejects_text_in_integer_column(db, base_data):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO Customers (customer_code, customer_name, operation_type, "
                   "country_code, created_at) VALUES ('CUS-01', 'Test Customer', 'HEMS', 'ES', ?)", (TS,))
        db.execute("INSERT INTO Aircraft (registration, fleet_number, aircraft_category, "
                   "aircraft_model, serial_number, customer_id, year_of_manufacture, "
                   "contract_start_date, created_at) VALUES ('EC-Q01', 'AQ-H01', 'LIGHT_TWIN', "
                   "'LT-200', 'SN-1', 1, 'two thousand', '2024-01-01', ?)", (TS,))


def test_email_must_use_fictitious_domain(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO Employees (employee_code, first_name, last_name, department_id, "
                   "job_title, email, hire_date, created_at) VALUES ('EMP-097', 'A', 'B', 1, "
                   "'Clerk', 'someone@gmail.com', '2020-01-01', ?)", (TS,))


# -----------------------------------------------------------------------------
# 4. Business rules enforced by the database
# -----------------------------------------------------------------------------
def _add_revision(db, data, code="R00", seq=0, status="CURRENT"):
    return db.execute(
        "INSERT INTO Document_Revisions (document_id, revision_code, revision_seq, issue_date, "
        "effective_date, review_due_date, lifecycle_status, prepared_by, approved_by, change_summary, "
        "created_at, created_by) VALUES (?, ?, ?, '2025-01-10', '2025-01-15', '2027-01-15', ?, ?, ?, "
        "'Initial issue', ?, ?)",
        (data["document"], code, seq, status, data["emp1"], data["emp2"], TS, data["emp1"])).lastrowid


def test_only_one_current_revision_per_document(db, base_data):            # D01
    _add_revision(db, base_data, "R00", 0)
    with pytest.raises(sqlite3.IntegrityError):
        _add_revision(db, base_data, "R01", 1)


def test_revision_cannot_be_approved_by_its_author(db, base_data):         # D04
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO Document_Revisions (document_id, revision_code, revision_seq, "
                   "issue_date, effective_date, lifecycle_status, prepared_by, approved_by, "
                   "change_summary, created_at, created_by) VALUES (?, 'R00', 0, '2025-01-10', "
                   "'2025-01-15', 'CURRENT', ?, ?, 'x', ?, ?)",
                   (base_data["document"], base_data["emp1"], base_data["emp1"], TS, base_data["emp1"]))


def test_receipt_cannot_go_directly_to_available(db, base_data):           # I01
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO Inventory_Movements (movement_number, movement_datetime, material_id, "
                   "movement_type, quantity, from_bucket, to_bucket, lot_number, performed_by, "
                   "created_at, created_by) VALUES ('MV-2025-00001', ?, ?, 'RECEIPT', 10, NULL, "
                   "'AVAILABLE', 'LOT-1', ?, ?, ?)",
                   (TS, base_data["material"], base_data["emp1"], TS, base_data["emp1"]))


def test_capa_cannot_be_verified_by_its_owner(db, base_data):              # C05
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO CAPA_Actions (action_number, action_type, origin, title, description, "
                   "responsible_id, department_id, created_date, original_due_date, due_date, "
                   "completed_date, status, effectiveness_check_date, effectiveness_result, "
                   "verified_by, closed_date, created_at, created_by) VALUES ('PA-2025-0001', "
                   "'PREVENTIVE', 'TREND_ANALYSIS', 'Test', 'Test action', ?, 1, '2025-01-15', "
                   "'2025-02-15', '2025-02-15', '2025-02-01', 'CLOSED', '2025-03-01', 'EFFECTIVE', "
                   "?, '2025-03-01', ?, ?)",
                   (base_data["emp1"], base_data["emp1"], TS, base_data["emp1"]))


def test_corrective_action_requires_an_incident(db, base_data):            # C01
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO CAPA_Actions (action_number, action_type, origin, title, description, "
                   "responsible_id, department_id, created_date, original_due_date, due_date, status, "
                   "created_at, created_by) VALUES ('CA-2025-0001', 'CORRECTIVE', 'TREND_ANALYSIS', "
                   "'Test', 'Test', ?, 1, '2025-01-15', '2025-02-15', '2025-02-15', 'OPEN', ?, ?)",
                   (base_data["emp1"], TS, base_data["emp1"]))


# -----------------------------------------------------------------------------
# 5. Triggers: no deletes, immutable records, audited updates (G08, G09, A01, A02)
# -----------------------------------------------------------------------------
def test_physical_delete_is_blocked(db):
    with pytest.raises(sqlite3.IntegrityError, match="G09"):
        db.execute("DELETE FROM Departments WHERE department_code = 'DIR'")


def test_audit_log_cannot_be_modified(db):
    with pytest.raises(sqlite3.IntegrityError, match="G08"):
        db.execute("UPDATE Audit_Log SET changed_by = NULL")


def test_update_without_updated_at_is_blocked(db, base_data):
    with pytest.raises(sqlite3.IntegrityError, match="updated_at"):
        db.execute("UPDATE Suppliers SET approval_status = 'CONDITIONAL' WHERE supplier_id = ?",
                   (base_data["supplier"],))


def test_update_back_in_time_is_blocked(db, base_data):
    db.execute("UPDATE Suppliers SET approval_status = 'CONDITIONAL', updated_at = '2025-03-01 10:00:00', "
               "updated_by = ? WHERE supplier_id = ?", (base_data["emp1"], base_data["supplier"]))
    with pytest.raises(sqlite3.IntegrityError, match="chronological"):
        db.execute("UPDATE Suppliers SET approval_status = 'APPROVED', updated_at = '2025-02-01 10:00:00', "
                   "updated_by = ? WHERE supplier_id = ?", (base_data["emp1"], base_data["supplier"]))


def test_update_writes_one_audit_event_per_changed_field(db, base_data):
    db.execute("UPDATE Suppliers SET approval_status = 'CONDITIONAL', next_evaluation_date = '2025-06-01', "
               "updated_at = '2025-03-01 10:00:00', updated_by = ? WHERE supplier_id = ?",
               (base_data["emp2"], base_data["supplier"]))
    events = db.execute(
        "SELECT field_name, old_value, new_value, changed_by, event_datetime FROM Audit_Log "
        "WHERE table_name = 'Suppliers' AND action = 'UPDATE' ORDER BY field_name").fetchall()
    assert events == [
        ("approval_status", "APPROVED", "CONDITIONAL", base_data["emp2"], "2025-03-01 10:00:00"),
        ("next_evaluation_date", "2025-01-01", "2025-06-01", base_data["emp2"], "2025-03-01 10:00:00"),
    ]


def test_insert_is_audited_with_its_own_date_and_author(db, base_data):
    event = db.execute("SELECT event_datetime, changed_by FROM Audit_Log WHERE table_name = 'Documents' "
                       "AND action = 'INSERT' AND record_id = ?", (base_data["document"],)).fetchone()
    assert event == (TS, base_data["emp1"])


def test_main_database_can_be_opened():
    """Smoke test: the real database exists after running build_database.py."""
    if not settings.DATABASE_PATH.exists():
        pytest.skip("Run 'python scripts/build_database.py' first to create database/aqmi.db")
    conn = get_connection()
    try:
        assert conn.execute("SELECT COUNT(*) FROM Departments").fetchone()[0] == 6
    finally:
        conn.close()
