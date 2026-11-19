-- rule: A04
-- title: There is no DELETE event in the audit log
-- severity: CRITICAL
-- type: P
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT table_name || ' #' || record_id AS record_ref, 'DELETE recorded on ' || event_datetime AS detail
FROM Audit_Log WHERE action = 'DELETE';
