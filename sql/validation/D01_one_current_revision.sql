-- rule: D01
-- title: A document has at most one current revision
-- severity: CRITICAL
-- type: N
-- enforced_by: PARTIAL UNIQUE INDEX + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT d.document_code AS record_ref, COUNT(*) || ' revisions are CURRENT at the same time' AS detail
FROM Document_Revisions r JOIN Documents d USING (document_id)
WHERE r.lifecycle_status = 'CURRENT'
GROUP BY r.document_id HAVING COUNT(*) > 1;
