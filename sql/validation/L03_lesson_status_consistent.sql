-- rule: L03
-- title: The status of a lesson matches the decision recorded (rejection always has a reason)
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT lesson_number AS record_ref,
       'Status ' || status || ' does not match the decision recorded' AS detail
FROM Lessons_Learned
WHERE (status IN ('APPROVED', 'INCORPORATED')) <> (approved_by IS NOT NULL AND approved_date IS NOT NULL)
   OR (status = 'REJECTED') <> (rejected_by IS NOT NULL AND rejected_date IS NOT NULL)
   OR (status = 'REJECTED') <> (rejection_reason IS NOT NULL AND trim(rejection_reason) <> '')
   OR (status = 'INCORPORATED') <> (incorporated_revision_id IS NOT NULL AND incorporated_date IS NOT NULL);
