-- AQMI analytical model — Fact_MaintenanceOrders: one row per work order
SELECT
    o.mo_id, o.mo_number, o.aircraft_id, o.maintenance_type, o.priority, o.responsible_department_id, o.status,
    CASE o.status WHEN 'OPEN' THEN 1 WHEN 'IN_PROGRESS' THEN 2 WHEN 'ON_HOLD' THEN 3 WHEN 'COMPLETED' THEN 4
                  WHEN 'CLOSED' THEN 5 ELSE 6 END AS status_order,
    o.opened_date, o.planned_end_date, o.actual_end_date, o.closed_date,
    (o.status = 'CANCELLED') AS is_cancelled, o.is_open, o.delay_days,
    (o.actual_end_date IS NOT NULL AND o.actual_end_date <= o.planned_end_date) AS completed_by_planned,
    o.turnaround_days, o.material_hold_days, o.documentation_hold_days,
    o.had_material_hold, o.had_documentation_hold,
    CASE WHEN o.had_material_hold = 1 THEN 'With material hold' ELSE 'No material hold' END AS material_hold_group,
    o.is_blocked_by_material, o.is_blocked_by_documentation,
    (SELECT COUNT(*) FROM Quality_Incidents i WHERE i.mo_id = o.mo_id AND i.status <> 'CANCELLED') AS n_incidents,
    m.work_description
FROM vw_mo_status o
JOIN Maintenance_Orders m USING (mo_id)
ORDER BY o.mo_id;
