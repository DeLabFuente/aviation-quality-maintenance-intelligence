-- rule: D11
-- title: A verification is not earlier than the issue of the revision verified
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT v.verification_number AS record_ref,
       'Verified on ' || v.verification_date || ', revision issued on ' || r.issue_date AS detail
FROM Document_Verifications v JOIN Document_Revisions r USING (revision_id)
WHERE v.verification_date < r.issue_date;
