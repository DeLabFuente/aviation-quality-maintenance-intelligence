-- rule: M02
-- title: COMPLETED or CLOSED if and only if there is an actual end date
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT mo_number AS record_ref, 'Status ' || status || ', actual end ' || COALESCE(actual_end_date, 'empty') AS detail
FROM Maintenance_Orders WHERE (status IN ('COMPLETED', 'CLOSED')) <> (actual_end_date IS NOT NULL);
