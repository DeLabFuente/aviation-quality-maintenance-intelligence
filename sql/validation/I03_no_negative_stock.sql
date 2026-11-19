-- rule: I03
-- title: No stock state is ever negative (running balance)
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
WITH flows AS (
    SELECT movement_id, movement_number, material_id, movement_datetime, from_bucket AS bucket, -quantity AS qty
    FROM Inventory_Movements WHERE from_bucket IS NOT NULL
    UNION ALL
    SELECT movement_id, movement_number, material_id, movement_datetime, to_bucket, quantity
    FROM Inventory_Movements WHERE to_bucket IS NOT NULL
),
running AS (
    SELECT movement_number, material_id, bucket,
           SUM(qty) OVER (PARTITION BY material_id, bucket ORDER BY movement_datetime, movement_id) AS balance
    FROM flows
)
SELECT r.movement_number AS record_ref,
       m.part_number || ' ' || r.bucket || ' balance becomes ' || ROUND(r.balance, 3) AS detail
FROM running r JOIN Materials m USING (material_id)
WHERE r.balance < -0.000001;
