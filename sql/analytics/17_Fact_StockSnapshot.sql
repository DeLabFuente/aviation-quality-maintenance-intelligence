-- AQMI analytical model — Fact_StockSnapshot: stock of each active material at each month end, by state
WITH flows AS (
    SELECT material_id, movement_datetime, to_bucket AS bucket, quantity AS qty FROM Inventory_Movements WHERE to_bucket IS NOT NULL
    UNION ALL
    SELECT material_id, movement_datetime, from_bucket, -quantity FROM Inventory_Movements WHERE from_bucket IS NOT NULL
),
snap AS (
    SELECT p.end_date AS snapshot_date, m.material_id, m.min_stock_qty, m.unit_cost,
           ROUND(COALESCE(SUM(CASE WHEN f.bucket = 'AVAILABLE'      THEN f.qty END), 0), 3) AS available_qty,
           ROUND(COALESCE(SUM(CASE WHEN f.bucket = 'RESERVED'       THEN f.qty END), 0), 3) AS reserved_qty,
           ROUND(COALESCE(SUM(CASE WHEN f.bucket = 'QUARANTINE'     THEN f.qty END), 0), 3) AS quarantine_qty,
           ROUND(COALESCE(SUM(CASE WHEN f.bucket = 'BLOCKED'        THEN f.qty END), 0), 3) AS blocked_qty,
           ROUND(COALESCE(SUM(CASE WHEN f.bucket = 'NON_CONFORMING' THEN f.qty END), 0), 3) AS non_conforming_qty
    FROM vw_kpi_periods p
    CROSS JOIN Materials m
    LEFT JOIN flows f ON f.material_id = m.material_id AND f.movement_datetime < date(p.end_date, '+1 day')
    WHERE p.is_total = 0 AND m.is_active = 1
    GROUP BY p.end_date, m.material_id
)
SELECT snapshot_date, material_id, min_stock_qty, available_qty, reserved_qty, quarantine_qty, blocked_qty,
       non_conforming_qty, (available_qty < min_stock_qty) AS is_below_min,
       ROUND(available_qty * unit_cost, 2) AS available_value, ROUND(reserved_qty * unit_cost, 2) AS reserved_value,
       ROUND(quarantine_qty * unit_cost, 2) AS quarantine_value, ROUND(blocked_qty * unit_cost, 2) AS blocked_value,
       ROUND(non_conforming_qty * unit_cost, 2) AS non_conforming_value
FROM snap
ORDER BY snapshot_date, material_id;
