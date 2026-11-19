-- rule: Q09
-- title: The root-cause analysis is after detection and before closure
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT i.incident_number AS record_ref,
       'Analysis ' || r.analysis_date || ', detected ' || i.detected_date || ', closed ' || COALESCE(i.closed_date, '-') AS detail
FROM Root_Cause_Analyses r JOIN Quality_Incidents i USING (incident_id)
WHERE r.analysis_date < i.detected_date OR r.analysis_date > i.closed_date;
