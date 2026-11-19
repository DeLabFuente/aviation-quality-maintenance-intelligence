-- kpi: QUA-01
-- name: Total Quality Incidents
-- name_es: Total de no conformidades
-- area: Quality
-- type: FLOW
-- unit: count
-- direction: NEUTRAL
-- target: none
-- warning: none
-- frequency: Monthly
-- tables: Quality_Incidents
-- question: How many non-conformities were detected in the period?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- FLOW: counts the events between start_date and end_date of each period.
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
SELECT p.period,
       COUNT(i.incident_id) AS numerator,
       NULL                 AS denominator,
       COUNT(i.incident_id) AS value
FROM vw_kpi_periods p
LEFT JOIN Quality_Incidents i
       ON i.detected_date BETWEEN p.start_date AND p.end_date
      AND i.status <> 'CANCELLED'                    -- cancelled = registered in error
GROUP BY p.period
ORDER BY p.period;
