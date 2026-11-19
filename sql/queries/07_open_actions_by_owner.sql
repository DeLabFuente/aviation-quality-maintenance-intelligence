-- =============================================================================
-- AQMI — Query 07: open corrective and preventive actions by person responsible
-- Question: "Who has actions pending, how advanced are they, and which are late?"
-- =============================================================================
SELECT
    e.first_name || ' ' || e.last_name AS responsible, dep.department_code AS department,
    c.action_number, c.action_type, c.title, c.status, c.due_date,
    c.days_overdue, c.latest_progress_pct, c.was_rescheduled,
    i.incident_number
FROM vw_capa_status c
JOIN Employees e ON e.employee_id = c.responsible_id
JOIN Departments dep ON dep.department_id = c.department_id
LEFT JOIN Quality_Incidents i ON i.incident_id = c.incident_id
WHERE c.is_open = 1
ORDER BY c.days_overdue DESC, c.due_date;
