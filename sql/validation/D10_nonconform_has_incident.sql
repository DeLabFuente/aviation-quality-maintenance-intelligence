-- rule: D10
-- title: A NON_CONFORM verification is linked to a non-conformity
-- severity: CRITICAL
-- type: P
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT verification_number AS record_ref, 'NON_CONFORM result without non-conformity' AS detail
FROM Document_Verifications WHERE result = 'NON_CONFORM' AND incident_id IS NULL;
