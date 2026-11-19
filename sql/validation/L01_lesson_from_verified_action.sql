-- rule: L01
-- title: A lesson is proposed only from a closed action whose effectiveness was verified
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
-- Both results count: an action verified as NOT_EFFECTIVE also leaves a lesson.
SELECT l.lesson_number AS record_ref,
       'Proposed on ' || l.proposed_date || ' from ' || a.action_number || ' (status ' || a.status ||
       ', effectiveness ' || COALESCE(a.effectiveness_result, 'not verified') ||
       ', closed ' || COALESCE(a.closed_date, 'not closed') || ')' AS detail
FROM Lessons_Learned l JOIN CAPA_Actions a USING (action_id)
WHERE a.status <> 'CLOSED'
   OR a.effectiveness_result IS NULL
   OR a.closed_date IS NULL
   OR l.proposed_date < a.closed_date;
