-- rule: C02
-- title: The number prefix (CA/PA) matches the action type
-- severity: CRITICAL
-- type: E
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT action_number AS record_ref, 'Type ' || action_type AS detail
FROM CAPA_Actions
WHERE NOT ((action_type = 'CORRECTIVE' AND action_number GLOB 'CA-*') OR (action_type = 'PREVENTIVE' AND action_number GLOB 'PA-*'));
