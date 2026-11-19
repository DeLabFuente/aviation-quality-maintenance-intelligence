-- kpi: MNT-02
-- name: Average Maintenance Delay
-- name_es: Retraso medio de las órdenes
-- area: Maintenance
-- type: FLOW
-- unit: days
-- direction: LOWER_IS_BETTER
-- target: 2  (fictitious internal target of AEROQ MRO)
-- warning: 4  (fictitious internal warning level)
-- frequency: Monthly
-- tables: Maintenance_Orders
-- question: How many days late, on average, are work orders completed? (orders on time count as 0)
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- FLOW: counts the events between start_date and end_date of each period.
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
SELECT p.period,
       COALESCE(SUM(CAST(MAX(0, julianday(o.actual_end_date) - julianday(o.planned_end_date)) AS INTEGER)), 0) AS numerator,
       COUNT(o.mo_id)                                                                                        AS denominator,
       ROUND(1.0 * SUM(CAST(MAX(0, julianday(o.actual_end_date) - julianday(o.planned_end_date)) AS INTEGER))
             / NULLIF(COUNT(o.mo_id), 0), 1)                                                                 AS value
FROM vw_kpi_periods p
LEFT JOIN Maintenance_Orders o
       ON o.status <> 'CANCELLED'
      AND o.actual_end_date BETWEEN p.start_date AND p.end_date
GROUP BY p.period
ORDER BY p.period;
