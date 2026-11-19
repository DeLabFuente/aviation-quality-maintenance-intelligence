-- rule: I11
-- title: The 'system' quantity of a count equals the stock calculated at that moment
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
WITH calc AS (
    SELECT s.count_id, s.count_number, s.system_qty,
           (SELECT COALESCE(SUM(CASE WHEN v.to_bucket = 'AVAILABLE' THEN v.quantity ELSE 0 END)
                          - SUM(CASE WHEN v.from_bucket = 'AVAILABLE' THEN v.quantity ELSE 0 END), 0)
            FROM Inventory_Movements v
            WHERE v.material_id = s.material_id AND v.movement_datetime < s.count_datetime) AS calculated_qty
    FROM Stock_Counts s WHERE s.count_type <> 'OPENING'
)
SELECT count_number AS record_ref, 'System quantity ' || system_qty || ', calculated ' || ROUND(calculated_qty, 3) AS detail
FROM calc WHERE ABS(system_qty - calculated_qty) > 0.000001;
