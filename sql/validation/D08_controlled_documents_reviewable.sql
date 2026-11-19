-- rule: D08
-- title: A controlled document has a review interval and its current revision a review date
-- severity: CRITICAL
-- type: P
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT d.document_code AS record_ref,
       CASE WHEN d.review_interval_months IS NULL THEN 'Controlled document without review interval'
            ELSE 'Current revision without review date' END AS detail
FROM Documents d
LEFT JOIN Document_Revisions r ON r.document_id = d.document_id AND r.lifecycle_status = 'CURRENT'
WHERE d.is_controlled = 1 AND (d.review_interval_months IS NULL OR r.review_due_date IS NULL);
