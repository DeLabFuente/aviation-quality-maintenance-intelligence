-- rule: G09
-- title: No business record can be physically deleted
-- severity: CRITICAL
-- type: P
-- enforced_by: TRIGGER (presence checked)
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT t.name AS record_ref, 'Missing trigger trg_' || lower(t.name) || '_no_delete' AS detail
FROM sqlite_master t
WHERE t.type = 'table' AND t.name NOT LIKE 'sqlite_%'
  AND NOT EXISTS (SELECT 1 FROM sqlite_master m
                  WHERE m.type = 'trigger' AND m.name = 'trg_' || lower(t.name) || '_no_delete');
