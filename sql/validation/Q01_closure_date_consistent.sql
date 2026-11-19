-- rule: Q01
-- title: CLOSED or CANCELLED if and only if there is a closure date, not before detection
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT incident_number AS record_ref, 'Status ' || status || ', detected ' || detected_date || ', closed ' || COALESCE(closed_date, 'empty') AS detail
FROM Quality_Incidents
WHERE (status IN ('CLOSED', 'CANCELLED')) <> (closed_date IS NOT NULL) OR closed_date < detected_date;
