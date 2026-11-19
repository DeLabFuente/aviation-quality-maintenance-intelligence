-- rule: I05
-- title: No receipt or promised date earlier than the order date
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT v.movement_number AS record_ref, 'Received ' || substr(v.movement_datetime, 1, 10) || ', ordered ' || p.order_date AS detail
FROM Inventory_Movements v
JOIN Purchase_Order_Lines l USING (po_line_id)
JOIN Purchase_Orders p ON p.po_id = l.po_id
WHERE v.movement_type = 'RECEIPT' AND substr(v.movement_datetime, 1, 10) < p.order_date
UNION ALL
SELECT p.po_number || ' line ' || l.line_number, 'Promised ' || l.promised_date || ', ordered ' || p.order_date
FROM Purchase_Order_Lines l JOIN Purchase_Orders p USING (po_id)
WHERE l.promised_date < p.order_date;
