-- rule: L02
-- title: The person who approves or rejects a lesson is not the person who proposed it
-- severity: CRITICAL
-- type: P
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT lesson_number AS record_ref, 'Approved by the person who proposed it' AS detail
FROM Lessons_Learned WHERE approved_by = proposed_by
UNION ALL
SELECT lesson_number, 'Rejected by the person who proposed it'
FROM Lessons_Learned WHERE rejected_by = proposed_by;
