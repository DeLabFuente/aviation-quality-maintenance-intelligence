-- rule: L07
-- title: Approved lesson not incorporated into a document more than 90 days after its approval
-- severity: WARNING
-- type: P
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
-- 90 days is a fictitious internal policy of AEROQ MRO, not a regulatory requirement.
WITH p AS (SELECT (SELECT parameter_value FROM System_Parameters WHERE parameter_key = 'AS_OF_DATE') AS as_of)
SELECT l.lesson_number AS record_ref,
       'Approved on ' || l.approved_date || ', pending incorporation for ' ||
       CAST(julianday(p.as_of) - julianday(l.approved_date) AS INTEGER) || ' days' AS detail
FROM Lessons_Learned l CROSS JOIN p
WHERE l.status = 'APPROVED' AND julianday(p.as_of) - julianday(l.approved_date) > 90;
