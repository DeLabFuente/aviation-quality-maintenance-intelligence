-- rule: I12
-- title: Every count difference has an adjustment of the same quantity and a comment
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT s.count_number AS record_ref,
       'Difference ' || ROUND(s.counted_qty - s.system_qty, 3) || ', adjusted ' || ROUND(COALESCE(a.adjusted, 0), 3) ||
       CASE WHEN s.comment IS NULL THEN ', no comment' ELSE '' END AS detail
FROM Stock_Counts s
LEFT JOIN (SELECT stock_count_id,
                  SUM(CASE movement_type WHEN 'ADJUSTMENT_IN' THEN quantity ELSE -quantity END) AS adjusted
           FROM Inventory_Movements WHERE stock_count_id IS NOT NULL GROUP BY stock_count_id) a
       ON a.stock_count_id = s.count_id
WHERE s.counted_qty <> s.system_qty
  AND (ABS((s.counted_qty - s.system_qty) - COALESCE(a.adjusted, 0)) > 0.000001 OR s.comment IS NULL);
