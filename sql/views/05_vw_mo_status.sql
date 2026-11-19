-- =============================================================================
-- AQMI — vw_mo_status
-- One row per maintenance order with its delay and its hold time by reason.
-- Delay = calendar days between the planned and the actual end (0 if it
-- finished on time). Active holds are counted up to the cut-off date.
-- =============================================================================
CREATE VIEW vw_mo_status AS
WITH holds AS (
    SELECT h.mo_id,
           SUM(CASE WHEN h.hold_reason = 'MATERIAL'
                    THEN julianday(COALESCE(h.end_date, p.as_of_date)) - julianday(h.start_date) ELSE 0 END) AS material_hold_days,
           SUM(CASE WHEN h.hold_reason = 'DOCUMENTATION'
                    THEN julianday(COALESCE(h.end_date, p.as_of_date)) - julianday(h.start_date) ELSE 0 END) AS documentation_hold_days,
           MAX(h.hold_reason = 'MATERIAL'      AND h.end_date IS NULL) AS is_blocked_by_material,
           MAX(h.hold_reason = 'DOCUMENTATION' AND h.end_date IS NULL) AS is_blocked_by_documentation,
           MAX(h.hold_reason = 'MATERIAL')      AS had_material_hold,
           MAX(h.hold_reason = 'DOCUMENTATION') AS had_documentation_hold
    FROM Maintenance_Order_Holds h CROSS JOIN vw_parameters p
    GROUP BY h.mo_id
)
SELECT
    o.mo_id, o.mo_number, o.aircraft_id, a.registration, a.customer_id, o.maintenance_type, o.priority,
    o.responsible_department_id, o.planner_id, o.status,
    o.opened_date, o.planned_end_date, o.actual_end_date, o.closed_date,
    CASE WHEN o.status IN ('OPEN', 'IN_PROGRESS', 'ON_HOLD') THEN 1 ELSE 0 END           AS is_open,
    CASE WHEN o.actual_end_date IS NOT NULL
         THEN CAST(MAX(0, julianday(o.actual_end_date) - julianday(o.planned_end_date)) AS INTEGER) END AS delay_days,
    CASE WHEN o.actual_end_date IS NOT NULL
         THEN (o.actual_end_date <= o.planned_end_date) END                             AS completed_on_time,
    CASE WHEN o.actual_end_date IS NOT NULL
         THEN CAST(julianday(o.actual_end_date) - julianday(o.opened_date) AS INTEGER) END AS turnaround_days,
    CAST(COALESCE(h.material_hold_days, 0) AS INTEGER)      AS material_hold_days,
    CAST(COALESCE(h.documentation_hold_days, 0) AS INTEGER) AS documentation_hold_days,
    COALESCE(h.is_blocked_by_material, 0)                   AS is_blocked_by_material,
    COALESCE(h.is_blocked_by_documentation, 0)              AS is_blocked_by_documentation,
    COALESCE(h.had_material_hold, 0)                        AS had_material_hold,
    COALESCE(h.had_documentation_hold, 0)                   AS had_documentation_hold
FROM Maintenance_Orders o
JOIN Aircraft a USING (aircraft_id)
LEFT JOIN holds h USING (mo_id);
