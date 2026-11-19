-- rule: D07
-- title: An aircraft record is linked to an aircraft
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT document_code AS record_ref, 'AIRCRAFT_RECORD without aircraft' AS detail
FROM Documents WHERE document_type = 'AIRCRAFT_RECORD' AND aircraft_id IS NULL;
