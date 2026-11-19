-- rule: I02
-- title: Each movement type carries its mandatory references
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT movement_number AS record_ref, movement_type || ' without its mandatory reference' AS detail
FROM Inventory_Movements
WHERE (movement_type IN ('RESERVE', 'UNRESERVE', 'ISSUE', 'RETURN') AND mo_id IS NULL)
   OR (movement_type = 'RECEIPT' AND po_line_id IS NULL)
   OR (movement_type IN ('RECEIPT', 'ISSUE', 'RETURN') AND lot_number IS NULL)
   OR (movement_type IN ('NONCONFORM', 'SCRAP') AND incident_id IS NULL)
   OR (movement_type IN ('ADJUSTMENT_IN', 'ADJUSTMENT_OUT') AND stock_count_id IS NULL)
   OR (movement_type IN ('BLOCK', 'UNBLOCK', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT') AND reason IS NULL);
