-- rule: D02
-- title: Revision dates are in order (issue <= effective <= review; effective <= superseded)
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT d.document_code || ' ' || r.revision_code AS record_ref,
       'issue ' || r.issue_date || ', effective ' || r.effective_date || ', review ' || COALESCE(r.review_due_date, '-')
       || ', superseded ' || COALESCE(r.superseded_date, '-') AS detail
FROM Document_Revisions r JOIN Documents d USING (document_id)
WHERE r.effective_date < r.issue_date
   OR r.review_due_date < r.effective_date
   OR r.superseded_date < r.effective_date;
