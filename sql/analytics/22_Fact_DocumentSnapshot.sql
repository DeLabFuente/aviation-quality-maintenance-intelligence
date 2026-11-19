-- AQMI analytical model — Fact_DocumentSnapshot: controlled documents in force at each month end.
-- The review date in force is rebuilt from the audit log (same logic as KPIs DOC-01 and DOC-03).
WITH review_changes AS (
    SELECT audit_id, record_id AS revision_id, date(event_datetime) AS change_date, old_value, new_value
    FROM Audit_Log WHERE table_name = 'Document_Revisions' AND field_name = 'review_due_date' AND action = 'UPDATE'
),
in_force AS (
    SELECT p.end_date AS snapshot_date, d.document_id, d.owner_department_id, r.revision_id, r.revision_code,
           COALESCE(
               (SELECT h.new_value FROM review_changes h WHERE h.revision_id = r.revision_id AND h.change_date <= p.end_date
                ORDER BY h.audit_id DESC LIMIT 1),
               (SELECT h.old_value FROM review_changes h WHERE h.revision_id = r.revision_id AND h.change_date > p.end_date
                ORDER BY h.audit_id LIMIT 1),
               r.review_due_date) AS review_due_then
    FROM vw_kpi_periods p
    JOIN Document_Revisions r ON r.lifecycle_status <> 'DRAFT' AND r.effective_date <= p.end_date
                             AND (r.superseded_date IS NULL OR r.superseded_date > p.end_date)
    JOIN Documents d ON d.document_id = r.document_id AND d.is_controlled = 1
    WHERE p.is_total = 0
)
SELECT snapshot_date, document_id, owner_department_id, revision_id, revision_code, review_due_then,
       (review_due_then >= snapshot_date) AS is_compliant, (review_due_then < snapshot_date) AS is_expired,
       CASE WHEN review_due_then < snapshot_date
            THEN CAST(julianday(snapshot_date) - julianday(review_due_then) AS INTEGER) ELSE 0 END AS days_overdue
FROM in_force
ORDER BY snapshot_date, document_id;
