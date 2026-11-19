-- =============================================================================
-- AQMI — vw_lesson_status (Phase 9)
-- One row per lesson learned, with the action and non-conformity it comes from,
-- the document revision that incorporates it and how long each step took.
-- The non-conformity is reached through the action: it is not stored twice.
-- =============================================================================
CREATE VIEW vw_lesson_status AS
SELECT
    l.lesson_id, l.lesson_number, l.action_id, a.action_number, a.action_type, a.effectiveness_result,
    a.incident_id, i.incident_number, l.title, l.lesson_text, l.recommendation,
    l.department_id, l.scope, l.status,
    l.proposed_date, l.proposed_by, l.approved_date, l.approved_by,
    l.rejected_date, l.rejected_by, l.rejection_reason,
    l.incorporated_date, l.incorporated_revision_id, r.document_id AS incorporated_document_id,
    d.document_code || ' ' || r.revision_code                                       AS incorporated_in,
    CASE WHEN l.status IN ('APPROVED', 'INCORPORATED') THEN 1 ELSE 0 END             AS is_approved,
    CASE WHEN l.status = 'INCORPORATED' THEN 1 ELSE 0 END                           AS is_incorporated,
    CASE WHEN l.status = 'APPROVED' THEN 1 ELSE 0 END                               AS is_pending_incorporation,
    CASE WHEN l.status = 'APPROVED'
         THEN CAST(julianday(p.as_of_date) - julianday(l.approved_date) AS INTEGER) END  AS days_pending,
    CAST(julianday(COALESCE(l.approved_date, l.rejected_date)) - julianday(l.proposed_date) AS INTEGER)
                                                                                     AS days_to_decision,
    CAST(julianday(l.incorporated_date) - julianday(l.approved_date) AS INTEGER)    AS days_to_incorporate
FROM Lessons_Learned l
JOIN CAPA_Actions a ON a.action_id = l.action_id
LEFT JOIN Quality_Incidents i ON i.incident_id = a.incident_id
LEFT JOIN Document_Revisions r ON r.revision_id = l.incorporated_revision_id
LEFT JOIN Documents d ON d.document_id = r.document_id
CROSS JOIN vw_parameters p;
