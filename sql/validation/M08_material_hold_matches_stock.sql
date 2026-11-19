-- rule: M08
-- title: A material hold corresponds to a real shortage when it was recorded
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
WITH holds AS (
    SELECT h.hold_id, h.mo_id, h.material_id, h.start_date, l.qty_required,
           (SELECT COALESCE(SUM(CASE WHEN v.to_bucket = 'AVAILABLE' THEN v.quantity ELSE 0 END)
                          - SUM(CASE WHEN v.from_bucket = 'AVAILABLE' THEN v.quantity ELSE 0 END), 0)
            FROM Inventory_Movements v
            WHERE v.material_id = h.material_id AND v.movement_datetime < h.created_at) AS available_qty
    FROM Maintenance_Order_Holds h
    JOIN Maintenance_Order_Materials l ON l.mo_id = h.mo_id AND l.material_id = h.material_id
    WHERE h.hold_reason = 'MATERIAL'
)
SELECT o.mo_number AS record_ref,
       'Hold on ' || m.part_number || ' started ' || x.start_date || ' while ' || x.available_qty ||
       ' were available (required ' || x.qty_required || ')' AS detail
FROM holds x
JOIN Maintenance_Orders o ON o.mo_id = x.mo_id
JOIN Materials m ON m.material_id = x.material_id
WHERE x.available_qty >= x.qty_required;
