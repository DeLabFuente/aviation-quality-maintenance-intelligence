-- rule: Q03
-- title: CRITICAL and MAJOR non-conformities have a containment action
-- severity: CRITICAL
-- type: P
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT incident_number AS record_ref, severity || ' without containment action' AS detail
FROM Quality_Incidents WHERE severity IN ('CRITICAL', 'MAJOR') AND containment_action IS NULL;
