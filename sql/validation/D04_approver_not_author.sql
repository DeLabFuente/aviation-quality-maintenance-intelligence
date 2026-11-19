-- rule: D04
-- title: The approver of a revision is not its author
-- severity: CRITICAL
-- type: P
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT d.document_code || ' ' || r.revision_code AS record_ref, 'Prepared and approved by the same person' AS detail
FROM Document_Revisions r JOIN Documents d USING (document_id)
WHERE r.approved_by = r.prepared_by;
