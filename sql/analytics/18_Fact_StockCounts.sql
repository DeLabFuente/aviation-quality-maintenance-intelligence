-- AQMI analytical model — Fact_StockCounts: one row per stock count (opening and cycle counts)
SELECT count_id, count_number, count_date, material_id, count_type, system_qty, counted_qty, difference_qty,
       has_difference, difference_value
FROM vw_stock_count_result
ORDER BY count_id;
