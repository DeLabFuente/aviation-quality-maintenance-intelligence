-- kpi: INV-03
-- name: Material Shortage Rate
-- name_es: Tasa de faltas de material
-- area: Inventory
-- type: FLOW
-- unit: %
-- direction: LOWER_IS_BETTER
-- target: 5  (fictitious internal target of AEROQ MRO)
-- warning: 8  (fictitious internal warning level)
-- frequency: Monthly
-- tables: Maintenance_Order_Materials, Inventory_Movements
-- question: Of the material lines required in the period, what share was not available on the required date?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- FLOW: counts the events between start_date and end_date of each period.
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
-- Short = reserved after the required date, or still not reserved at the cut-off
-- date when the required date has passed (definition in vw_mo_material_status).
SELECT p.period,
       COALESCE(SUM(l.was_short), 0)                                         AS numerator,
       COUNT(l.mo_material_id)                                               AS denominator,
       ROUND(100.0 * SUM(l.was_short) / NULLIF(COUNT(l.mo_material_id), 0), 1) AS value
FROM vw_kpi_periods p
LEFT JOIN vw_mo_material_status l
       ON l.was_short IS NOT NULL                    -- cancelled orders are excluded
      AND l.required_by_date BETWEEN p.start_date AND p.end_date
GROUP BY p.period
ORDER BY p.period;
