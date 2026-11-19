-- rule: C04
-- title: A CLOSED action records the result, date and verifier of the effectiveness check
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT action_number AS record_ref, 'Closed without complete effectiveness verification' AS detail
FROM CAPA_Actions
WHERE status = 'CLOSED' AND (effectiveness_result IS NULL OR effectiveness_check_date IS NULL OR verified_by IS NULL);
