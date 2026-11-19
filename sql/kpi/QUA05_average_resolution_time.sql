-- kpi: QUA-05
-- name: Average Resolution Time
-- name_es: Tiempo medio de resolución
-- area: Quality
-- type: FLOW
-- unit: days
-- direction: LOWER_IS_BETTER
-- target: 75  (fictitious internal target of AEROQ MRO)
-- warning: 90  (fictitious internal warning level)
-- frequency: Monthly
-- tables: Quality_Incidents
-- question: How many days, on average, does it take to close a non-conformity?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- FLOW: counts the events between start_date and end_date of each period.
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
SELECT p.period,
       COALESCE(SUM(CAST(julianday(i.closed_date) - julianday(i.detected_date) AS INTEGER)), 0) AS numerator,
       COUNT(i.incident_id)                                                                   AS denominator,
       ROUND(1.0 * SUM(CAST(julianday(i.closed_date) - julianday(i.detected_date) AS INTEGER))
             / NULLIF(COUNT(i.incident_id), 0), 1)                                            AS value
FROM vw_kpi_periods p
LEFT JOIN Quality_Incidents i
       ON i.status = 'CLOSED'
      AND i.closed_date BETWEEN p.start_date AND p.end_date
GROUP BY p.period
ORDER BY p.period;
