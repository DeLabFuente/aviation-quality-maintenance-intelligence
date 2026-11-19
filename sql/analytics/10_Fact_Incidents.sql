-- AQMI analytical model — Fact_Incidents: one row per non-conformity
SELECT
    i.incident_id, i.incident_number, q.title, i.category_id, i.severity,
    CASE i.severity WHEN 'CRITICAL' THEN 1 WHEN 'MAJOR' THEN 2 WHEN 'MINOR' THEN 3 ELSE 4 END AS severity_order,
    i.priority, i.detection_source, i.status,
    CASE i.status WHEN 'OPEN' THEN 1 WHEN 'UNDER_INVESTIGATION' THEN 2 WHEN 'ACTION_PLAN' THEN 3
                  WHEN 'IMPLEMENTATION' THEN 4 WHEN 'EFFECTIVENESS_CHECK' THEN 5 WHEN 'CLOSED' THEN 6 ELSE 7 END AS status_order,
    i.responsible_department_id, i.owner_id, i.aircraft_id, o.mo_number, i.supplier_id, i.material_id,
    i.detected_date, i.target_closure_date, i.closed_date,
    (i.status = 'CANCELLED') AS is_cancelled, i.is_open, i.age_days,
    CASE WHEN i.status = 'CLOSED' THEN i.resolution_days END AS resolution_days,
    i.is_overdue, i.closed_on_time, i.has_rca,
    (SELECT r.method FROM Root_Cause_Analyses r WHERE r.incident_id = i.incident_id ORDER BY r.rca_id DESC LIMIT 1) AS rca_method,
    COALESCE((SELECT r.ishikawa_category FROM Root_Cause_Analyses r
              WHERE r.incident_id = i.incident_id AND r.ishikawa_category IS NOT NULL
              ORDER BY r.rca_id DESC LIMIT 1), 'NOT ANALYSED') AS root_cause_6m,
    i.n_actions, i.n_open_actions
FROM vw_incident_status i
JOIN Quality_Incidents q USING (incident_id)
LEFT JOIN Maintenance_Orders o ON o.mo_id = i.mo_id
ORDER BY i.incident_id;
