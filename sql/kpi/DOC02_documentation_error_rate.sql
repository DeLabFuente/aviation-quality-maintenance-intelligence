-- kpi: DOC-02
-- name: Documentation Error Rate
-- name_es: Tasa de errores documentales
-- area: Document control
-- type: FLOW
-- unit: %
-- direction: LOWER_IS_BETTER
-- target: 5  (fictitious internal target of AEROQ MRO)
-- warning: 8  (fictitious internal warning level)
-- frequency: Monthly
-- tables: Document_Verifications
-- question: Of the routine document and record checks made, what share found a discrepancy?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- FLOW: counts the events between start_date and end_date of each period.
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
-- Internal audits are excluded: they are aimed where the risk is, and their
-- findings are already measured as non-conformities (Quality area).
SELECT p.period,
       COALESCE(SUM(v.result <> 'CONFORM'), 0)                                          AS numerator,
       COUNT(v.verification_id)                                                         AS denominator,
       ROUND(100.0 * SUM(v.result <> 'CONFORM') / NULLIF(COUNT(v.verification_id), 0), 1) AS value
FROM vw_kpi_periods p
LEFT JOIN Document_Verifications v
       ON v.verification_date BETWEEN p.start_date AND p.end_date
      AND v.verification_type <> 'INTERNAL_AUDIT'
GROUP BY p.period
ORDER BY p.period;
