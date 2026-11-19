"""
Shared test fixtures.

Each test gets its own brand-new database in a temporary folder, so the tests
never touch database/aqmi.db and never depend on each other.
"""

import sqlite3

import pytest

from scripts.build_database import build_database
from scripts.common import get_connection

TS = "2025-01-15 09:00:00"   # a valid timestamp inside the simulated period


@pytest.fixture
def db(tmp_path) -> sqlite3.Connection:
    """A freshly built, empty AQMI database (reference data only)."""
    db_path = tmp_path / "test_aqmi.db"
    build_database(db_path)
    conn = get_connection(db_path)
    yield conn
    conn.close()


def dept_id(conn: sqlite3.Connection, code: str) -> int:
    return conn.execute("SELECT department_id FROM Departments WHERE department_code = ?", (code,)).fetchone()[0]


def add_employee(conn: sqlite3.Connection, code: str = "EMP-001", dept: str = "QUA") -> int:
    cur = conn.execute(
        "INSERT INTO Employees (employee_code, first_name, last_name, department_id, job_title, "
        "email, hire_date, created_at) VALUES (?, 'Test', 'Person', ?, 'Quality Inspector', ?, "
        "'2020-01-01', ?)",
        (code, dept_id(conn, dept), f"{code.lower()}@aeroq-mro.example", TS),
    )
    return cur.lastrowid


@pytest.fixture
def base_data(db):
    """Minimal master data: two employees, a supplier, a material, a document."""
    emp1 = add_employee(db, "EMP-001", "QUA")
    emp2 = add_employee(db, "EMP-002", "DOC")
    supplier = db.execute(
        "INSERT INTO Suppliers (supplier_code, supplier_name, country_code, supplier_type, "
        "approval_status, approval_date, next_evaluation_date, created_at) "
        "VALUES ('SUP-001', 'Test Supplier', 'ES', 'DISTRIBUTOR', 'APPROVED', '2024-01-01', "
        "'2025-01-01', ?)", (TS,)).lastrowid
    material = db.execute(
        "INSERT INTO Materials (part_number, description, material_class, unit_of_measure, "
        "preferred_supplier_id, standard_lead_time_days, min_stock_qty, reorder_qty, unit_cost, "
        "is_serialized, is_shelf_life_controlled, requires_release_certificate, created_at) "
        "VALUES ('AQ-0001-01', 'Test filter', 'CONSUMABLE', 'EA', ?, 10, 5, 20, 12.5, 0, 0, 1, ?)",
        (supplier, TS)).lastrowid
    document = db.execute(
        "INSERT INTO Documents (document_code, title, document_type, owner_department_id, "
        "is_controlled, review_interval_months, created_at, created_by) "
        "VALUES ('PRO-QUA-001', 'Control of non-conformities', 'PROCEDURE', ?, 1, 24, ?, ?)",
        (dept_id(db, "QUA"), TS, emp1)).lastrowid
    db.commit()
    return {"emp1": emp1, "emp2": emp2, "supplier": supplier, "material": material, "document": document}
