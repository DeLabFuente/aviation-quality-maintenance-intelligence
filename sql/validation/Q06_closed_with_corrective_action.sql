-- rule: Q06
-- title: A CLOSED non-conformity (except observations) has at least one corrective action
-- severity: WARNING
-- type: P
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT i.incident_number AS record_ref, i.severity || ' closed without corrective action' AS detail
FROM Quality_Incidents i
WHERE i.status = 'CLOSED' AND i.severity <> 'OBSERVATION'
  AND NOT EXISTS (SELECT 1 FROM CAPA_Actions a WHERE a.incident_id = i.incident_id AND a.action_type = 'CORRECTIVE');
