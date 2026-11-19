-- rule: M01
-- title: Planned end is not earlier than the opening date
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT mo_number AS record_ref, 'Opened ' || opened_date || ', planned end ' || planned_end_date AS detail
FROM Maintenance_Orders WHERE planned_end_date < opened_date;
