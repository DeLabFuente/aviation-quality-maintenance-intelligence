-- rule: D06
-- title: Revisions do not overlap: each one starts the day the previous one is superseded
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT d.document_code || ' ' || a.revision_code || ' -> ' || b.revision_code AS record_ref,
       'Superseded on ' || COALESCE(a.superseded_date, 'never') || ' but next revision effective on ' || b.effective_date AS detail
FROM Document_Revisions a
JOIN Document_Revisions b ON b.document_id = a.document_id AND b.revision_seq = a.revision_seq + 1
JOIN Documents d ON d.document_id = a.document_id
WHERE b.lifecycle_status IN ('CURRENT', 'SUPERSEDED') AND a.superseded_date IS NOT b.effective_date;
