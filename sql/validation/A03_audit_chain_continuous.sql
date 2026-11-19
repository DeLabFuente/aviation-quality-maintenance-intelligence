-- rule: A03
-- title: The chain of changes of a field is continuous and ends in the current value
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
WITH ev AS (
    SELECT audit_id, table_name, record_id, field_name, old_value, new_value, event_datetime,
           LAG(new_value) OVER (PARTITION BY table_name, record_id, field_name ORDER BY event_datetime, audit_id) AS previous_new,
           ROW_NUMBER() OVER (PARTITION BY table_name, record_id, field_name ORDER BY event_datetime DESC, audit_id DESC) AS rn_last
    FROM Audit_Log WHERE action = 'UPDATE'
)
SELECT table_name || ' #' || record_id AS record_ref,
       field_name || ': change on ' || event_datetime || ' starts from ' || COALESCE(old_value, 'empty') ||
       ' but the previous change left ' || COALESCE(previous_new, 'empty') AS detail
FROM ev WHERE previous_new IS NOT NULL AND old_value IS NOT previous_new
UNION ALL
SELECT x.mo_number, 'Last recorded status ' || e.new_value || ' differs from current status ' || x.status
FROM ev e JOIN Maintenance_Orders x ON x.mo_id = e.record_id
WHERE e.table_name = 'Maintenance_Orders' AND e.field_name = 'status' AND e.rn_last = 1 AND e.new_value IS NOT x.status
UNION ALL
SELECT x.incident_number, 'Last recorded status ' || e.new_value || ' differs from current status ' || x.status
FROM ev e JOIN Quality_Incidents x ON x.incident_id = e.record_id
WHERE e.table_name = 'Quality_Incidents' AND e.field_name = 'status' AND e.rn_last = 1 AND e.new_value IS NOT x.status
UNION ALL
SELECT x.action_number, 'Last recorded status ' || e.new_value || ' differs from current status ' || x.status
FROM ev e JOIN CAPA_Actions x ON x.action_id = e.record_id
WHERE e.table_name = 'CAPA_Actions' AND e.field_name = 'status' AND e.rn_last = 1 AND e.new_value IS NOT x.status;
