-- rule: Q05
-- title: A CLOSED non-conformity has all its corrective actions closed or cancelled
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT i.incident_number AS record_ref, 'Closed while ' || a.action_number || ' is ' || a.status AS detail
FROM Quality_Incidents i JOIN CAPA_Actions a ON a.incident_id = i.incident_id
WHERE i.status = 'CLOSED' AND a.action_type = 'CORRECTIVE' AND a.status NOT IN ('CLOSED', 'CANCELLED');
