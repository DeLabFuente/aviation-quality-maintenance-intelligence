-- rule: C08
-- title: An action closed as NOT_EFFECTIVE has a follow-up action
-- severity: WARNING
-- type: P
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT a.action_number AS record_ref, 'Not effective, no follow-up action' AS detail
FROM CAPA_Actions a
WHERE a.effectiveness_result = 'NOT_EFFECTIVE'
  AND NOT EXISTS (SELECT 1 FROM CAPA_Actions b WHERE b.parent_action_id = a.action_id);
