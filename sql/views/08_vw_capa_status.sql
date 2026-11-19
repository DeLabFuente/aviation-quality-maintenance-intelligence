-- =============================================================================
-- AQMI — vw_capa_status
-- One row per corrective / preventive action: overdue status, rescheduling,
-- time to complete and latest reported progress.
-- =============================================================================
CREATE VIEW vw_capa_status AS
SELECT
    a.action_id, a.action_number, a.action_type, a.origin, a.incident_id, a.parent_action_id,
    a.title, a.responsible_id, a.department_id, a.status,
    a.created_date, a.original_due_date, a.due_date, a.completed_date,
    a.effectiveness_check_date, a.effectiveness_result, a.verified_by, a.closed_date,
    CASE WHEN a.status IN ('OPEN', 'IN_PROGRESS') THEN 1 ELSE 0 END                 AS is_open,
    CASE WHEN a.status IN ('OPEN', 'IN_PROGRESS') AND a.due_date < p.as_of_date THEN 1 ELSE 0 END AS is_overdue,
    CASE WHEN a.status IN ('OPEN', 'IN_PROGRESS') AND a.due_date < p.as_of_date
         THEN CAST(julianday(p.as_of_date) - julianday(a.due_date) AS INTEGER) ELSE 0 END AS days_overdue,
    (a.due_date <> a.original_due_date)                                            AS was_rescheduled,
    CASE WHEN a.completed_date IS NOT NULL THEN (a.completed_date <= a.due_date) END AS completed_on_time,
    CASE WHEN a.completed_date IS NOT NULL
         THEN CAST(julianday(a.completed_date) - julianday(a.created_date) AS INTEGER) END AS days_to_complete,
    COALESCE((SELECT u.progress_pct FROM CAPA_Progress_Updates u WHERE u.action_id = a.action_id
              ORDER BY u.update_date DESC, u.update_id DESC LIMIT 1), 0)             AS latest_progress_pct
FROM CAPA_Actions a
CROSS JOIN vw_parameters p;
