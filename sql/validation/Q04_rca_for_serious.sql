-- rule: Q04
-- title: CRITICAL and MAJOR non-conformities have a root-cause analysis once investigated
-- severity: CRITICAL
-- type: P
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT i.incident_number AS record_ref, i.severity || ' in status ' || i.status || ' without root-cause analysis' AS detail
FROM Quality_Incidents i
WHERE i.severity IN ('CRITICAL', 'MAJOR')
  AND i.status NOT IN ('OPEN', 'UNDER_INVESTIGATION', 'CANCELLED')
  AND NOT EXISTS (SELECT 1 FROM Root_Cause_Analyses r WHERE r.incident_id = i.incident_id);
