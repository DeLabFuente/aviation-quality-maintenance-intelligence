-- =============================================================================
-- AQMI — vw_revision_status and vw_document_status
-- Validity is CALCULATED from the dates and the cut-off date, so a document
-- can never be "expired" and "valid" at the same time.
--   VALID           current revision, review date not reached
--   REVIEW_OVERDUE  current revision whose review date has passed (expired)
--   NOT_CONTROLLED  current revision of a document without periodic review
--   OBSOLETE        superseded or withdrawn revision
--   DRAFT           revision in preparation
-- =============================================================================
CREATE VIEW vw_revision_status AS
SELECT
    r.revision_id, r.document_id, d.document_code, d.document_type, d.owner_department_id,
    r.revision_code, r.revision_seq, r.issue_date, r.effective_date, r.review_due_date, r.superseded_date,
    r.lifecycle_status, r.prepared_by, r.approved_by,
    CASE WHEN r.lifecycle_status IN ('SUPERSEDED', 'WITHDRAWN') THEN 'OBSOLETE'
         WHEN r.lifecycle_status = 'DRAFT'                       THEN 'DRAFT'
         WHEN d.is_controlled = 0                                THEN 'NOT_CONTROLLED'
         WHEN r.review_due_date < p.as_of_date                   THEN 'REVIEW_OVERDUE'
         ELSE 'VALID' END                                        AS validity_status,
    CASE WHEN r.lifecycle_status = 'CURRENT' AND d.is_controlled = 1 AND r.review_due_date < p.as_of_date
         THEN CAST(julianday(p.as_of_date) - julianday(r.review_due_date) AS INTEGER) ELSE 0 END AS days_overdue
FROM Document_Revisions r
JOIN Documents d USING (document_id)
CROSS JOIN vw_parameters p;

CREATE VIEW vw_document_status AS
SELECT
    d.document_id, d.document_code, d.title, d.document_type, d.owner_department_id, d.aircraft_id,
    d.is_controlled, d.review_interval_months,
    rs.revision_id AS current_revision_id, rs.revision_code AS current_revision, rs.effective_date,
    rs.review_due_date, rs.validity_status, rs.days_overdue,
    (SELECT COUNT(*) FROM Document_Revisions x WHERE x.document_id = d.document_id)                AS n_revisions,
    EXISTS (SELECT 1 FROM Document_Revisions x WHERE x.document_id = d.document_id
                                               AND x.lifecycle_status = 'DRAFT')                   AS has_draft
FROM Documents d
JOIN vw_revision_status rs ON rs.document_id = d.document_id AND rs.lifecycle_status = 'CURRENT';
