-- kpi: QUA-02
-- name: Open Non-Conformities
-- name_es: No conformidades abiertas
-- area: Quality
-- type: SNAPSHOT
-- unit: count
-- direction: LOWER_IS_BETTER
-- target: none
-- warning: none
-- frequency: Monthly
-- tables: Quality_Incidents
-- question: How many non-conformities were open at the end of the period?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- SNAPSHOT: state at the end of end_date of each period (TOTAL = at the cut-off date).
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
SELECT p.period,
       COUNT(i.incident_id) AS numerator,
       NULL                 AS denominator,
       COUNT(i.incident_id) AS value
FROM vw_kpi_periods p
LEFT JOIN Quality_Incidents i
       ON i.status <> 'CANCELLED'
      AND i.detected_date <= p.end_date
      AND (i.closed_date IS NULL OR i.closed_date > p.end_date)
GROUP BY p.period
ORDER BY p.period;
