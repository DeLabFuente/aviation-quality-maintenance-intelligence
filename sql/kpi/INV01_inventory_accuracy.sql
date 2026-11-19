-- kpi: INV-01
-- name: Inventory Accuracy
-- name_es: Exactitud de inventario
-- area: Inventory
-- type: FLOW
-- unit: %
-- direction: HIGHER_IS_BETTER
-- target: 95  (fictitious internal target of AEROQ MRO)
-- warning: 90  (fictitious internal warning level)
-- frequency: Monthly
-- tables: Stock_Counts
-- question: Of the cycle counts made, what share matched the stock recorded in the system?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- FLOW: counts the events between start_date and end_date of each period.
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
-- Opening counts are excluded: they set the initial stock, there is nothing to compare.
SELECT p.period,
       COALESCE(SUM(s.counted_qty = s.system_qty), 0)                                  AS numerator,
       COUNT(s.count_id)                                                               AS denominator,
       ROUND(100.0 * SUM(s.counted_qty = s.system_qty) / NULLIF(COUNT(s.count_id), 0), 1) AS value
FROM vw_kpi_periods p
LEFT JOIN Stock_Counts s
       ON s.count_type = 'CYCLE'
      AND substr(s.count_datetime, 1, 10) BETWEEN p.start_date AND p.end_date
GROUP BY p.period
ORDER BY p.period;
