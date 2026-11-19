-- kpi: INV-02
-- name: Stock Availability
-- name_es: Disponibilidad de stock
-- area: Inventory
-- type: SNAPSHOT
-- unit: %
-- direction: HIGHER_IS_BETTER
-- target: 95  (fictitious internal target of AEROQ MRO)
-- warning: 90  (fictitious internal warning level)
-- frequency: Monthly
-- tables: Materials, Inventory_Movements
-- question: What share of active materials had available stock at or above their minimum?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- SNAPSHOT: state at the end of end_date of each period (TOTAL = at the cut-off date).
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
-- Available stock at each date = movements into AVAILABLE minus movements out of it, up to that date.
WITH stock_then AS (
    SELECT p.period, m.material_id, m.min_stock_qty,
           ROUND(COALESCE((
               SELECT SUM(CASE WHEN v.to_bucket = 'AVAILABLE' THEN v.quantity ELSE 0 END)
                    - SUM(CASE WHEN v.from_bucket = 'AVAILABLE' THEN v.quantity ELSE 0 END)
               FROM Inventory_Movements v
               WHERE v.material_id = m.material_id
                 AND v.movement_datetime < date(p.end_date, '+1 day')), 0), 3) AS available_qty
    FROM vw_kpi_periods p
    CROSS JOIN Materials m
    WHERE m.is_active = 1
)
SELECT period,
       SUM(available_qty >= min_stock_qty)                                       AS numerator,
       COUNT(*)                                                                  AS denominator,
       ROUND(100.0 * SUM(available_qty >= min_stock_qty) / NULLIF(COUNT(*), 0), 1) AS value
FROM stock_then
GROUP BY period
ORDER BY period;
