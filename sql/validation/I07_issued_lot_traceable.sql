-- rule: I07
-- title: Every lot issued to an order was previously received (or counted at go-live)
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT i.movement_number AS record_ref, 'Lot ' || i.lot_number || ' of ' || m.part_number || ' has no prior receipt' AS detail
FROM Inventory_Movements i JOIN Materials m USING (material_id)
WHERE i.movement_type = 'ISSUE'
  AND NOT EXISTS (
      SELECT 1 FROM Inventory_Movements r
      WHERE r.material_id = i.material_id AND r.lot_number = i.lot_number
        AND r.movement_datetime <= i.movement_datetime
        AND (r.movement_type = 'RECEIPT'
             OR (r.movement_type = 'ADJUSTMENT_IN'
                 AND r.stock_count_id IN (SELECT count_id FROM Stock_Counts WHERE count_type = 'OPENING'))));
