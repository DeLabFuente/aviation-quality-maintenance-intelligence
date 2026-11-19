-- rule: Q10
-- title: With 5 Whys, why_1 is filled in and the chain has no gaps
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT i.incident_number AS record_ref, 'Method ' || r.method || ': incomplete chain of whys' AS detail
FROM Root_Cause_Analyses r JOIN Quality_Incidents i USING (incident_id)
WHERE (r.method <> 'ISHIKAWA' AND r.why_1 IS NULL)
   OR (r.why_2 IS NOT NULL AND r.why_1 IS NULL) OR (r.why_3 IS NOT NULL AND r.why_2 IS NULL)
   OR (r.why_4 IS NOT NULL AND r.why_3 IS NULL) OR (r.why_5 IS NOT NULL AND r.why_4 IS NULL);
