-- rule: D12
-- title: Current revision with its review date passed (expired document)
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
WITH p AS (SELECT (SELECT parameter_value FROM System_Parameters WHERE parameter_key = 'AS_OF_DATE') AS as_of,
             (SELECT parameter_value FROM System_Parameters WHERE parameter_key = 'PERIOD_START') AS period_start)
SELECT d.document_code AS record_ref,
       r.revision_code || ' review due ' || r.review_due_date || ' (' ||
       CAST(julianday(p.as_of) - julianday(r.review_due_date) AS INTEGER) || ' days overdue)' AS detail
FROM Document_Revisions r JOIN Documents d USING (document_id) CROSS JOIN p
WHERE r.lifecycle_status = 'CURRENT' AND d.is_controlled = 1 AND r.review_due_date < p.as_of;
