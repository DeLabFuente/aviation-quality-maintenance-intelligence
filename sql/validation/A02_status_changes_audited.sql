-- rule: A02
-- title: Every status change of orders, non-conformities, actions and lessons is in the audit log
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT x.mo_number AS record_ref, 'Status ' || x.status || ' but no status change recorded' AS detail FROM Maintenance_Orders x
WHERE x.status <> 'OPEN' AND NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Maintenance_Orders' AND a.record_id = x.mo_id AND a.action = 'UPDATE' AND a.field_name = 'status')
UNION ALL
SELECT x.incident_number AS record_ref, 'Status ' || x.status || ' but no status change recorded' AS detail FROM Quality_Incidents x
WHERE x.status <> 'OPEN' AND NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Quality_Incidents' AND a.record_id = x.incident_id AND a.action = 'UPDATE' AND a.field_name = 'status')
UNION ALL
SELECT x.action_number AS record_ref, 'Status ' || x.status || ' but no status change recorded' AS detail FROM CAPA_Actions x
WHERE x.status <> 'OPEN' AND NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'CAPA_Actions' AND a.record_id = x.action_id AND a.action = 'UPDATE' AND a.field_name = 'status')
UNION ALL
SELECT x.lesson_number AS record_ref, 'Status ' || x.status || ' but no status change recorded' AS detail FROM Lessons_Learned x
WHERE x.status <> 'PROPOSED' AND NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Lessons_Learned' AND a.record_id = x.lesson_id AND a.action = 'UPDATE' AND a.field_name = 'status');
