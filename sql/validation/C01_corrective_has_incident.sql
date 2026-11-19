-- rule: C01
-- title: A corrective action has a non-conformity; origin INCIDENT if and only if it has one
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT action_number AS record_ref, action_type || ' with origin ' || origin || ' and ' ||
       CASE WHEN incident_id IS NULL THEN 'no' ELSE 'a' END || ' non-conformity' AS detail
FROM CAPA_Actions
WHERE (action_type = 'CORRECTIVE' AND incident_id IS NULL) OR ((origin = 'INCIDENT') <> (incident_id IS NOT NULL));
