-- rule: I13
-- title: No purchase order to a supplier after its suspension
-- severity: CRITICAL
-- type: P
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT p.po_number AS record_ref, 'Ordered ' || p.order_date || ' from ' || s.supplier_code || ', suspended on ' || s.suspended_date AS detail
FROM Purchase_Orders p JOIN Suppliers s USING (supplier_id)
WHERE s.suspended_date IS NOT NULL AND p.order_date >= s.suspended_date;
