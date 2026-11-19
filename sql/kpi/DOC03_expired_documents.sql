-- kpi: DOC-03
-- name: Expired Documents
-- name_es: Documentos caducados
-- area: Document control
-- type: SNAPSHOT
-- unit: count
-- direction: LOWER_IS_BETTER
-- target: 0  (fictitious internal target of AEROQ MRO)
-- warning: 5  (fictitious internal warning level)
-- frequency: Monthly
-- tables: Documents, Document_Revisions, Audit_Log
-- question: How many controlled documents were past their review date?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- SNAPSHOT: state at the end of end_date of each period (TOTAL = at the cut-off date).
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
-- A controlled document is measured through the revision in force at each date.
-- Its review due date can be extended by a periodic review, so the review date in
-- force at each date is rebuilt from the audit log.
WITH review_changes AS (
    SELECT audit_id, record_id AS revision_id, date(event_datetime) AS change_date, old_value, new_value
    FROM Audit_Log
    WHERE table_name = 'Document_Revisions' AND field_name = 'review_due_date' AND action = 'UPDATE'
),
in_force AS (
    SELECT p.period, p.end_date, r.revision_id,
           COALESCE(
               (SELECT h.new_value FROM review_changes h
                 WHERE h.revision_id = r.revision_id AND h.change_date <= p.end_date
                 ORDER BY h.audit_id DESC LIMIT 1),
               (SELECT h.old_value FROM review_changes h
                 WHERE h.revision_id = r.revision_id AND h.change_date > p.end_date
                 ORDER BY h.audit_id LIMIT 1),
               r.review_due_date) AS review_due_then
    FROM vw_kpi_periods p
    JOIN Document_Revisions r
      ON r.lifecycle_status <> 'DRAFT'
     AND r.effective_date <= p.end_date
     AND (r.superseded_date IS NULL OR r.superseded_date > p.end_date)
    JOIN Documents d ON d.document_id = r.document_id AND d.is_controlled = 1
)
SELECT p.period,
       COUNT(f.revision_id) AS numerator,
       NULL                 AS denominator,
       COUNT(f.revision_id) AS value
FROM vw_kpi_periods p
LEFT JOIN in_force f ON f.period = p.period AND f.review_due_then < f.end_date
GROUP BY p.period
ORDER BY p.period;
