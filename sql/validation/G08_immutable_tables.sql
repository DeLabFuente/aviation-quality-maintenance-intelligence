-- rule: G08
-- title: Movements, progress updates and the audit log cannot be modified
-- severity: CRITICAL
-- type: P
-- enforced_by: TRIGGER (presence checked)
-- returns: one row per record that breaks the rule (record_ref, detail)
WITH required(name) AS (VALUES ('Inventory_Movements'), ('CAPA_Progress_Updates'), ('Audit_Log'))
SELECT r.name AS record_ref, 'Missing trigger trg_' || lower(r.name) || '_no_update' AS detail
FROM required r
WHERE NOT EXISTS (SELECT 1 FROM sqlite_master m
                  WHERE m.type = 'trigger' AND m.name = 'trg_' || lower(r.name) || '_no_update');
