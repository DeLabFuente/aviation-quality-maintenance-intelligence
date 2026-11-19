-- =============================================================================
-- AQMI — vw_stock_count_result
-- One row per stock count with the difference found. Opening counts (system
-- go-live balance) are flagged so that they can be excluded from Inventory Accuracy.
-- =============================================================================
CREATE VIEW vw_stock_count_result AS
SELECT
    s.count_id, s.count_number, s.material_id, m.part_number, m.material_class,
    s.count_datetime, substr(s.count_datetime, 1, 10) AS count_date, s.count_type,
    s.system_qty, s.counted_qty,
    ROUND(s.counted_qty - s.system_qty, 3)                     AS difference_qty,
    (s.counted_qty <> s.system_qty)                            AS has_difference,
    ROUND(ABS(s.counted_qty - s.system_qty) * m.unit_cost, 2)  AS difference_value,
    (s.count_type = 'OPENING')                                 AS is_opening_count,
    s.counted_by
FROM Stock_Counts s
JOIN Materials m USING (material_id);
