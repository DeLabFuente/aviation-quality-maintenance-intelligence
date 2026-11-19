-- rule: D05
-- title: Every revision that is not a draft has an approver
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT d.document_code || ' ' || r.revision_code AS record_ref, 'Status ' || r.lifecycle_status || ' without approver' AS detail
FROM Document_Revisions r JOIN Documents d USING (document_id)
WHERE r.lifecycle_status <> 'DRAFT' AND r.approved_by IS NULL;
