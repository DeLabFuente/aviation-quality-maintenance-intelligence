-- =============================================================================
-- AQMI — vw_mo_material_status
-- One row per material line of a maintenance order: quantities reserved and
-- issued (from the movements) and whether the material was SHORT, i.e. it
-- could not be reserved on the date it was required (KPI "Material Shortage Rate").
-- =============================================================================
CREATE VIEW vw_mo_material_status AS
WITH mv AS (
    SELECT mo_id, material_id,
           SUM(CASE movement_type WHEN 'RESERVE' THEN quantity
                                  WHEN 'UNRESERVE' THEN -quantity
                                  WHEN 'ISSUE' THEN -quantity ELSE 0 END)          AS reserved_now_qty,
           SUM(CASE movement_type WHEN 'ISSUE' THEN quantity
                                  WHEN 'RETURN' THEN -quantity ELSE 0 END)          AS net_issued_qty,
           MIN(CASE WHEN movement_type = 'RESERVE' THEN substr(movement_datetime, 1, 10) END) AS first_reserved_date,
           MAX(CASE WHEN movement_type = 'ISSUE'   THEN substr(movement_datetime, 1, 10) END) AS last_issued_date
    FROM Inventory_Movements
    WHERE mo_id IS NOT NULL
    GROUP BY mo_id, material_id
)
SELECT
    l.mo_material_id, l.mo_id, o.mo_number, o.aircraft_id, o.status AS mo_status, l.material_id,
    l.qty_required, l.required_by_date,
    ROUND(COALESCE(mv.reserved_now_qty, 0), 3)                                  AS reserved_qty,
    ROUND(COALESCE(mv.net_issued_qty, 0), 3)                                    AS issued_qty,
    ROUND(MAX(0, l.qty_required - COALESCE(mv.net_issued_qty, 0)), 3)          AS pending_qty,
    mv.first_reserved_date, mv.last_issued_date,
    CASE WHEN o.status = 'CANCELLED' THEN NULL
         WHEN mv.first_reserved_date IS NULL THEN (l.required_by_date < p.as_of_date)
         ELSE (mv.first_reserved_date > l.required_by_date) END              AS was_short
FROM Maintenance_Order_Materials l
JOIN Maintenance_Orders o USING (mo_id)
CROSS JOIN vw_parameters p
LEFT JOIN mv ON mv.mo_id = l.mo_id AND mv.material_id = l.material_id;
