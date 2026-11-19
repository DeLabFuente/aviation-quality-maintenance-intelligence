-- kpi: QUA-04
-- name: Corrective Action Closure Rate
-- name_es: Cierre de acciones correctivas en plazo
-- area: Quality
-- type: FLOW
-- unit: %
-- direction: HIGHER_IS_BETTER
-- target: 85  (fictitious internal target of AEROQ MRO)
-- warning: 75  (fictitious internal warning level)
-- frequency: Monthly
-- tables: CAPA_Actions
-- question: Of the corrective actions due in the period, what share was implemented by its due date?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- FLOW: counts the events between start_date and end_date of each period.
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
SELECT p.period,
       COALESCE(SUM(c.completed_date IS NOT NULL AND c.completed_date <= c.due_date), 0) AS numerator,
       COUNT(c.action_id)                                                                AS denominator,
       ROUND(100.0 * SUM(c.completed_date IS NOT NULL AND c.completed_date <= c.due_date)
             / NULLIF(COUNT(c.action_id), 0), 1)                                         AS value
FROM vw_kpi_periods p
LEFT JOIN CAPA_Actions c
       ON c.action_type = 'CORRECTIVE'
      AND c.status <> 'CANCELLED'
      AND c.due_date BETWEEN p.start_date AND p.end_date
GROUP BY p.period
ORDER BY p.period;
