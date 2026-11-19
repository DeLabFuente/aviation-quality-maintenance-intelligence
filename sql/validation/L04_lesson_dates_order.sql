-- rule: L04
-- title: Lesson dates are in order: proposal, then decision, then incorporation
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT lesson_number AS record_ref, 'Approved on ' || approved_date || ', before its proposal on ' || proposed_date AS detail
FROM Lessons_Learned WHERE approved_date < proposed_date
UNION ALL
SELECT lesson_number, 'Rejected on ' || rejected_date || ', before its proposal on ' || proposed_date
FROM Lessons_Learned WHERE rejected_date < proposed_date
UNION ALL
SELECT lesson_number, 'Incorporated on ' || incorporated_date || ', before its approval on ' || approved_date
FROM Lessons_Learned WHERE incorporated_date < approved_date;
