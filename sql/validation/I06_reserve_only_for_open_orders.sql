-- rule: I06
-- title: Material is only reserved or issued for lines of the order while it is open
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT v.movement_number AS record_ref,
       v.movement_type || ' for ' || o.mo_number ||
       CASE WHEN l.mo_material_id IS NULL THEN ': material not required by the order'
            WHEN o.status = 'CANCELLED' AND v.movement_type = 'ISSUE' THEN ': order cancelled'
            ELSE ': after the order ended on ' || o.actual_end_date END AS detail
FROM Inventory_Movements v
JOIN Maintenance_Orders o USING (mo_id)
LEFT JOIN Maintenance_Order_Materials l ON l.mo_id = v.mo_id AND l.material_id = v.material_id
WHERE v.movement_type IN ('RESERVE', 'ISSUE')
  AND (l.mo_material_id IS NULL
       OR (o.status = 'CANCELLED' AND v.movement_type = 'ISSUE')
       OR (o.actual_end_date IS NOT NULL AND substr(v.movement_datetime, 1, 10) > o.actual_end_date));
