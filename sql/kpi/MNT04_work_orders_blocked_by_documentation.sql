-- kpi: MNT-04
-- name: Work Orders Blocked by Documentation
-- name_es: Órdenes bloqueadas por documentación
-- area: Maintenance
-- type: SNAPSHOT
-- unit: count
-- direction: LOWER_IS_BETTER
-- target: none
-- warning: none
-- frequency: Monthly
-- tables: Maintenance_Order_Holds
-- question: How many work orders were stopped by a documentation hold at the end of the period?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- SNAPSHOT: state at the end of end_date of each period (TOTAL = at the cut-off date).
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
SELECT p.period,
       COUNT(DISTINCT h.mo_id) AS numerator,
       NULL                    AS denominator,
       COUNT(DISTINCT h.mo_id) AS value
FROM vw_kpi_periods p
LEFT JOIN Maintenance_Order_Holds h
       ON h.hold_reason = 'DOCUMENTATION'
      AND h.start_date <= p.end_date
      AND (h.end_date IS NULL OR h.end_date > p.end_date)
GROUP BY p.period
ORDER BY p.period;
