-- rule: C05
-- title: The person verifying effectiveness is not the person responsible for the action
-- severity: CRITICAL
-- type: P
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT action_number AS record_ref, 'Verified by the person responsible for the action' AS detail
FROM CAPA_Actions WHERE verified_by = responsible_id;
