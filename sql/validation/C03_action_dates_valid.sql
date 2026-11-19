-- rule: C03
-- title: Due dates are not before creation; the action is not created before the non-conformity
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT a.action_number AS record_ref,
       'Created ' || a.created_date || ', due ' || a.original_due_date || ' / ' || a.due_date ||
       COALESCE(', non-conformity detected ' || i.detected_date, '') AS detail
FROM CAPA_Actions a LEFT JOIN Quality_Incidents i USING (incident_id)
WHERE a.original_due_date < a.created_date OR a.due_date < a.created_date OR a.created_date < i.detected_date;
