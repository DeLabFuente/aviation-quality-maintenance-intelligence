"""
Phase 4 tests: the synthetic data is complete, reproducible and coherent.

The full catalogue of 86 business rules is implemented in Phase 5. These tests
check the properties that the generator itself must guarantee.

Run from the main project folder:
    pytest -v
"""

import hashlib

import pytest

from config import generator_parameters as P
from scripts.common import get_connection
from scripts.generate_data import TABLES, generate

# Expected volumes (ranges, because they come from a simulation). See documentation/05.
EXPECTED_RANGES = {
    "Employees": (44, 48), "Aircraft": (12, 12), "Suppliers": (40, 40), "Materials": (100, 100),
    "Documents": (250, 250), "Maintenance_Orders": (450, 550), "Quality_Incidents": (120, 190),
    "Purchase_Orders": (100, 220), "Purchase_Order_Lines": (250, 450), "CAPA_Actions": (120, 220),
    "Inventory_Movements": (3000, 4500), "Stock_Counts": (450, 560), "Document_Verifications": (650, 1000),
}


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    """Generate the full data set once for all the tests of this file."""
    db_path = tmp_path_factory.mktemp("gen") / "aqmi_test.db"
    result = generate(db_path, export_dir=None)
    conn = get_connection(db_path)
    yield conn, result
    conn.close()


def _scalar(conn, sql: str):
    return conn.execute(sql).fetchone()[0]


def _fingerprint(db_path) -> str:
    conn = get_connection(db_path)
    digest = hashlib.sha256()
    for table in TABLES:
        for row in conn.execute(f"SELECT * FROM {table} ORDER BY 1"):
            digest.update(repr(row).encode())
    conn.close()
    return digest.hexdigest()


# -----------------------------------------------------------------------------
# Volumes and reproducibility
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("table", sorted(EXPECTED_RANGES))
def test_volume_in_expected_range(generated, table):
    _, result = generated
    low, high = EXPECTED_RANGES[table]
    assert low <= result["counts"][table] <= high


def test_same_seed_gives_identical_data(tmp_path):
    generate(tmp_path / "a.db", export_dir=None)
    generate(tmp_path / "b.db", export_dir=None)
    assert _fingerprint(tmp_path / "a.db") == _fingerprint(tmp_path / "b.db")


def test_different_seed_gives_different_data(tmp_path):
    generate(tmp_path / "a.db", seed=145, export_dir=None)
    generate(tmp_path / "b.db", seed=999, export_dir=None)
    assert _fingerprint(tmp_path / "a.db") != _fingerprint(tmp_path / "b.db")


# -----------------------------------------------------------------------------
# Coherence that the simulation guarantees
# -----------------------------------------------------------------------------
def test_integrity_and_foreign_keys(generated):
    conn, _ = generated
    assert _scalar(conn, "PRAGMA integrity_check") == "ok"
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_no_event_after_cut_off_date(generated):
    conn, _ = generated
    assert _scalar(conn, "SELECT COUNT(*) FROM Audit_Log WHERE event_datetime > '2026-10-31 23:59:59'") == 0


def test_stock_never_negative(generated):                                     # rule I03
    conn, _ = generated
    sql = """
    WITH mv AS (
        SELECT material_id, movement_datetime t, movement_id, from_bucket b, -quantity q
          FROM Inventory_Movements WHERE from_bucket IS NOT NULL
        UNION ALL
        SELECT material_id, movement_datetime, movement_id, to_bucket, quantity
          FROM Inventory_Movements WHERE to_bucket IS NOT NULL),
    running AS (
        SELECT SUM(q) OVER (PARTITION BY material_id, b ORDER BY t, movement_id) balance FROM mv)
    SELECT COUNT(*) FROM running WHERE balance < -1e-9"""
    assert _scalar(conn, sql) == 0


def test_count_system_quantity_matches_movements(generated):                  # rule I11
    conn, _ = generated
    sql = """
    SELECT COUNT(*) FROM Stock_Counts s WHERE count_type <> 'OPENING' AND ABS(s.system_qty - COALESCE((
        SELECT SUM(CASE WHEN to_bucket = 'AVAILABLE' THEN quantity ELSE 0 END)
             - SUM(CASE WHEN from_bucket = 'AVAILABLE' THEN quantity ELSE 0 END)
          FROM Inventory_Movements v
         WHERE v.material_id = s.material_id AND v.movement_datetime < s.count_datetime), 0)) > 1e-9"""
    assert _scalar(conn, sql) == 0


def test_completed_orders_received_all_their_material(generated):             # rule M11
    conn, _ = generated
    sql = """
    SELECT COUNT(*) FROM Maintenance_Order_Materials l JOIN Maintenance_Orders m USING (mo_id)
     WHERE m.status IN ('COMPLETED', 'CLOSED') AND COALESCE((
           SELECT SUM(CASE movement_type WHEN 'ISSUE' THEN quantity ELSE -quantity END)
             FROM Inventory_Movements v
            WHERE v.mo_id = l.mo_id AND v.material_id = l.material_id
              AND movement_type IN ('ISSUE', 'RETURN')), 0) < l.qty_required"""
    assert _scalar(conn, sql) == 0


def test_on_hold_status_matches_active_holds(generated):                      # rule M05
    conn, _ = generated
    sql = """
    SELECT COUNT(*) FROM Maintenance_Orders m
     WHERE (m.status = 'ON_HOLD') <> EXISTS (
           SELECT 1 FROM Maintenance_Order_Holds h WHERE h.mo_id = m.mo_id AND h.end_date IS NULL)"""
    assert _scalar(conn, sql) == 0


def test_closed_incidents_have_closed_corrective_actions(generated):          # rule Q05
    conn, _ = generated
    sql = """
    SELECT COUNT(*) FROM Quality_Incidents i WHERE status = 'CLOSED' AND EXISTS (
           SELECT 1 FROM CAPA_Actions a WHERE a.incident_id = i.incident_id
              AND a.action_type = 'CORRECTIVE' AND a.status NOT IN ('CLOSED', 'CANCELLED'))"""
    assert _scalar(conn, sql) == 0


def test_audit_trail_is_a_continuous_chain(generated):                        # rule A03
    conn, _ = generated
    sql = """
    WITH ev AS (
        SELECT old_value, LAG(new_value) OVER (PARTITION BY table_name, record_id, field_name
                                               ORDER BY event_datetime, audit_id) previous
          FROM Audit_Log WHERE action = 'UPDATE')
    SELECT COUNT(*) FROM ev WHERE previous IS NOT NULL AND old_value IS NOT previous"""
    assert _scalar(conn, sql) == 0


def test_document_revisions_do_not_overlap(generated):                        # rule D06
    conn, _ = generated
    sql = """
    SELECT COUNT(*) FROM Document_Revisions a JOIN Document_Revisions b
        ON a.document_id = b.document_id AND b.revision_seq = a.revision_seq + 1
     WHERE b.lifecycle_status IN ('CURRENT', 'SUPERSEDED') AND a.superseded_date IS NOT b.effective_date"""
    assert _scalar(conn, sql) == 0


# -----------------------------------------------------------------------------
# Planted discrepancies and stories
# -----------------------------------------------------------------------------
def test_planted_discrepancies_match_configuration(generated):
    _, result = generated
    kinds = [p["kind"] for p in result["planted"]]
    assert kinds.count("OBSOLETE_REVISION_LINK") == P.PLANTED_OBSOLETE_REVISION_LINKS
    assert kinds.count("RECEIPT_WITHOUT_CERTIFICATE") == P.PLANTED_RECEIPTS_WITHOUT_CERTIFICATE
    assert kinds.count("FALSE_MATERIAL_HOLD") == P.PLANTED_FALSE_MATERIAL_HOLDS
    assert kinds.count("INCIDENT_WITHOUT_LINKS") == P.PLANTED_INCIDENTS_WITHOUT_LINKS


def test_story_late_supplier_improves_after_plan(generated):
    conn, _ = generated
    plan_closed = _scalar(conn, f"SELECT completed_date FROM CAPA_Actions WHERE title LIKE '%{P.LATE_SUPPLIER_CODE}%'")
    sql = f"""
    SELECT AVG(substr(v.movement_datetime, 1, 10) > l.promised_date) FROM Inventory_Movements v
      JOIN Purchase_Order_Lines l USING (po_line_id) JOIN Purchase_Orders p USING (po_id)
      JOIN Suppliers s USING (supplier_id)
     WHERE v.movement_type = 'RECEIPT' AND s.supplier_code = '{P.LATE_SUPPLIER_CODE}'
       AND p.order_date {{}} '{plan_closed}'"""
    assert _scalar(conn, sql.format("<")) > 2 * _scalar(conn, sql.format(">="))


def test_story_closure_form_redesign_reduces_errors(generated):
    conn, _ = generated
    rates = conn.execute(f"""
        SELECT r.revision_seq, AVG(v.result = 'NON_CONFORM') FROM Document_Verifications v
          JOIN Document_Revisions r USING (revision_id) JOIN Documents d USING (document_id)
         WHERE d.document_code = '{P.CLOSURE_FORM_DOC}' AND v.verification_type = 'RECORD_VS_SOURCE'
         GROUP BY 1 ORDER BY 1""").fetchall()
    assert rates[0][1] > 3 * rates[-1][1]


def test_story_high_unscheduled_aircraft(generated):
    conn, _ = generated
    top = _scalar(conn, """
        SELECT a.registration FROM Maintenance_Orders m JOIN Aircraft a USING (aircraft_id)
         GROUP BY 1 ORDER BY AVG(m.maintenance_type = 'UNSCHEDULED') DESC LIMIT 1""")
    assert top == P.HIGH_UNSCHEDULED_AIRCRAFT
