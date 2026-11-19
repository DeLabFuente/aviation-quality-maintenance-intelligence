-- kpi: LRN-01
-- name: Lesson Incorporation Rate
-- name_es: Lecciones aprendidas incorporadas
-- area: Continuous improvement
-- type: SNAPSHOT
-- unit: %
-- direction: HIGHER_IS_BETTER
-- target: 80  (fictitious internal target of AEROQ MRO)
-- warning: 60  (fictitious internal warning level)
-- frequency: Monthly
-- tables: Lessons_Learned, Document_Revisions
-- question: Of the lessons learned approved so far, what share is already incorporated into a controlled document?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- SNAPSHOT: state at the end of end_date of each period (TOTAL = at the cut-off date).
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Lessons learned are a general quality-management practice, not a regulatory requirement.
-- Full definition: documentation/09b_fase9_lecciones_aprendidas.md
-- =============================================================================
-- An approved lesson is never rejected later, so the state at each date can be
-- rebuilt from the approval and incorporation dates (the audit log confirms them:
-- rule K05 compares the result at the cut-off date with the current status).
SELECT p.period,
       COALESCE(SUM(l.incorporated_date IS NOT NULL AND l.incorporated_date <= p.end_date), 0) AS numerator,
       COUNT(l.lesson_id)                                                                  AS denominator,
       ROUND(100.0 * SUM(l.incorporated_date IS NOT NULL AND l.incorporated_date <= p.end_date)
             / NULLIF(COUNT(l.lesson_id), 0), 1)                                           AS value
FROM vw_kpi_periods p
LEFT JOIN Lessons_Learned l
       ON l.approved_date IS NOT NULL
      AND l.approved_date <= p.end_date
GROUP BY p.period
ORDER BY p.period;
