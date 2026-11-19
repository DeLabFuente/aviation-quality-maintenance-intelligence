-- rule: I16
-- title: Stock below minimum (available + in quarantine) with no pending purchase order
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
WITH available AS (
    SELECT material_id,
           SUM(CASE WHEN to_bucket IN ('AVAILABLE', 'QUARANTINE') THEN quantity ELSE 0 END)
         - SUM(CASE WHEN from_bucket IN ('AVAILABLE', 'QUARANTINE') THEN quantity ELSE 0 END) AS qty
    FROM Inventory_Movements GROUP BY material_id
),
pending AS (
    SELECT l.material_id, SUM(l.qty_ordered - COALESCE(r.received, 0)) AS qty
    FROM Purchase_Order_Lines l JOIN Purchase_Orders p USING (po_id)
    LEFT JOIN (SELECT po_line_id, SUM(quantity) AS received FROM Inventory_Movements
               WHERE movement_type = 'RECEIPT' GROUP BY po_line_id) r USING (po_line_id)
    WHERE p.cancelled_date IS NULL AND l.qty_ordered > COALESCE(r.received, 0)
    GROUP BY l.material_id
)
SELECT m.part_number AS record_ref,
       'Available and in quarantine ' || ROUND(COALESCE(a.qty, 0), 3) || ', below minimum ' || m.min_stock_qty || ', nothing on order' AS detail
FROM Materials m
LEFT JOIN available a USING (material_id)
LEFT JOIN pending o USING (material_id)
WHERE m.is_active = 1 AND m.min_stock_qty > 0
  AND COALESCE(a.qty, 0) < m.min_stock_qty AND COALESCE(o.qty, 0) = 0;
