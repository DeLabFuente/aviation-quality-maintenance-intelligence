-- AQMI analytical model — Fact_CAPA_Snapshot: actions not yet implemented at each month end.
-- The due date in force at each month end is rebuilt from the audit log (same logic as KPI QUA-06).
WITH due_changes AS (
    SELECT audit_id, record_id AS action_id, date(event_datetime) AS change_date, old_value, new_value
    FROM Audit_Log WHERE table_name = 'CAPA_Actions' AND field_name = 'due_date' AND action = 'UPDATE'
),
open_actions AS (
    SELECT p.end_date AS snapshot_date, c.action_id, c.action_number, c.action_type, c.department_id, c.responsible_id,
           COALESCE(
               (SELECT h.new_value FROM due_changes h WHERE h.action_id = c.action_id AND h.change_date <= p.end_date
                ORDER BY h.audit_id DESC LIMIT 1),
               (SELECT h.old_value FROM due_changes h WHERE h.action_id = c.action_id AND h.change_date > p.end_date
                ORDER BY h.audit_id LIMIT 1),
               c.due_date) AS due_date_then
    FROM vw_kpi_periods p
    JOIN CAPA_Actions c ON c.status <> 'CANCELLED' AND c.created_date <= p.end_date
                       AND (c.completed_date IS NULL OR c.completed_date > p.end_date)
    WHERE p.is_total = 0
)
SELECT snapshot_date, action_id, action_number, action_type, department_id, responsible_id, due_date_then,
       (due_date_then < snapshot_date) AS is_overdue,
       CASE WHEN due_date_then < snapshot_date
            THEN CAST(julianday(snapshot_date) - julianday(due_date_then) AS INTEGER) ELSE 0 END AS days_overdue
FROM open_actions
ORDER BY snapshot_date, action_id;
