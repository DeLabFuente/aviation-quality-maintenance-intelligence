-- rule: C11
-- title: Progress updates are between the creation and the closure of the action
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT a.action_number AS record_ref,
       'Update on ' || u.update_date || ', action created ' || a.created_date || ', closed ' || COALESCE(a.closed_date, '-') AS detail
FROM CAPA_Progress_Updates u JOIN CAPA_Actions a USING (action_id)
WHERE u.update_date < a.created_date OR u.update_date > a.closed_date;
