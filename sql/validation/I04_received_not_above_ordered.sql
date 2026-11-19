-- rule: I04
-- title: The quantity received on a line does not exceed the quantity ordered
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT p.po_number || ' line ' || l.line_number AS record_ref,
       'Ordered ' || l.qty_ordered || ', received ' || SUM(v.quantity) AS detail
FROM Purchase_Order_Lines l
JOIN Purchase_Orders p USING (po_id)
JOIN Inventory_Movements v ON v.po_line_id = l.po_line_id AND v.movement_type = 'RECEIPT'
GROUP BY l.po_line_id HAVING SUM(v.quantity) > l.qty_ordered + 0.000001;
