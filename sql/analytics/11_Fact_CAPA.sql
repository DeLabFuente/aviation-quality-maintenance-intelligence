-- AQMI analytical model — Fact_CAPA: one row per corrective or preventive action
SELECT
    c.action_id, c.action_number, c.action_type, c.origin, i.incident_number, c.title,
    c.responsible_id, c.department_id, c.status,
    CASE c.status WHEN 'OPEN' THEN 1 WHEN 'IN_PROGRESS' THEN 2 WHEN 'COMPLETED' THEN 3 WHEN 'CLOSED' THEN 4 ELSE 5 END AS status_order,
    c.created_date, c.original_due_date, c.due_date, c.completed_date, c.closed_date,
    COALESCE(c.effectiveness_result, 'NOT VERIFIED') AS effectiveness_result,
    (c.status = 'CANCELLED') AS is_cancelled, c.is_open, c.is_overdue, c.days_overdue, c.was_rescheduled,
    (c.completed_date IS NOT NULL AND c.completed_date <= c.due_date) AS completed_by_due,
    c.days_to_complete, c.latest_progress_pct
FROM vw_capa_status c
LEFT JOIN Quality_Incidents i ON i.incident_id = c.incident_id
ORDER BY c.action_id;
