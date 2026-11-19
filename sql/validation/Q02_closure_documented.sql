-- rule: Q02
-- title: A CLOSED non-conformity records who closed it and the measures adopted
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT incident_number AS record_ref, 'Closed without ' ||
       CASE WHEN closed_by IS NULL THEN 'closing person' ELSE 'summary of measures' END AS detail
FROM Quality_Incidents WHERE status = 'CLOSED' AND (closed_by IS NULL OR closure_summary IS NULL);
