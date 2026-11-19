-- rule: Q11
-- title: With Ishikawa, the 6M category is filled in
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT i.incident_number AS record_ref, 'Method ' || r.method || ' without Ishikawa category' AS detail
FROM Root_Cause_Analyses r JOIN Quality_Incidents i USING (incident_id)
WHERE r.method <> 'FIVE_WHYS' AND r.ishikawa_category IS NULL;
