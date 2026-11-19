-- rule: C09
-- title: The current due date is not earlier than the original one
-- severity: CRITICAL
-- type: P
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT action_number AS record_ref, 'Original due ' || original_due_date || ', current due ' || due_date AS detail
FROM CAPA_Actions WHERE due_date < original_due_date;
