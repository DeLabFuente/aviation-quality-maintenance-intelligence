-- rule: I15
-- title: No material is issued after its shelf-life expiry date
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT movement_number AS record_ref, 'Issued ' || substr(movement_datetime, 1, 10) || ', expired ' || shelf_life_expiry_date AS detail
FROM Inventory_Movements
WHERE movement_type = 'ISSUE' AND shelf_life_expiry_date IS NOT NULL
  AND shelf_life_expiry_date < substr(movement_datetime, 1, 10);
