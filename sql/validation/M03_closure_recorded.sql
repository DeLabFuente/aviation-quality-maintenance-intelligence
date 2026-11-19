-- rule: M03
-- title: CLOSED if and only if closure date and person are recorded; closure >= actual end
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT mo_number AS record_ref, 'Status ' || status || ', closed ' || COALESCE(closed_date, 'empty') AS detail
FROM Maintenance_Orders
WHERE (status = 'CLOSED') <> (closed_date IS NOT NULL)
   OR (status = 'CLOSED') <> (closed_by IS NOT NULL)
   OR closed_date < actual_end_date;
