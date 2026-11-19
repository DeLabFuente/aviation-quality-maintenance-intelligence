-- kpi: QUA-03
-- name: Non-Conformity Rate
-- name_es: Tasa de no conformidades
-- area: Quality
-- type: FLOW
-- unit: per 100 orders
-- direction: LOWER_IS_BETTER
-- target: none
-- warning: none
-- frequency: Monthly
-- tables: Quality_Incidents, Maintenance_Orders
-- question: How many non-conformities are detected for every 100 work orders completed?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- FLOW: counts the events between start_date and end_date of each period.
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
WITH incidents AS (
    SELECT p.period, COUNT(i.incident_id) AS n
    FROM vw_kpi_periods p
    LEFT JOIN Quality_Incidents i
           ON i.detected_date BETWEEN p.start_date AND p.end_date AND i.status <> 'CANCELLED'
    GROUP BY p.period
),
completed_orders AS (
    SELECT p.period, COUNT(o.mo_id) AS n
    FROM vw_kpi_periods p
    LEFT JOIN Maintenance_Orders o
           ON o.actual_end_date BETWEEN p.start_date AND p.end_date AND o.status <> 'CANCELLED'
    GROUP BY p.period
)
SELECT i.period,
       i.n AS numerator,
       o.n AS denominator,
       ROUND(100.0 * i.n / NULLIF(o.n, 0), 1) AS value
FROM incidents i
JOIN completed_orders o USING (period)
ORDER BY i.period;
