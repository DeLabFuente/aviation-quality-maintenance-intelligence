-- rule: D09
-- title: A verification that is not CONFORM describes the discrepancy
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT verification_number AS record_ref, 'Result ' || result || ' without description' AS detail
FROM Document_Verifications WHERE result <> 'CONFORM' AND discrepancy_description IS NULL;
