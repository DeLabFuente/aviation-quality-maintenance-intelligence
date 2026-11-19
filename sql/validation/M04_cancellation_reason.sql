-- rule: M04
-- title: CANCELLED if and only if there is a cancellation reason
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT mo_number AS record_ref, 'Status ' || status || ' and cancellation reason ' ||
       CASE WHEN cancellation_reason IS NULL THEN 'empty' ELSE 'present' END AS detail
FROM Maintenance_Orders WHERE (status = 'CANCELLED') <> (cancellation_reason IS NOT NULL);
