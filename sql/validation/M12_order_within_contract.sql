-- rule: M12
-- title: Order dates are within the maintenance contract of the aircraft
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT o.mo_number AS record_ref,
       a.registration || ' contract ' || a.contract_start_date || ' to ' || COALESCE(a.contract_end_date, 'open') ||
       '; order ' || o.opened_date || ' to ' || COALESCE(o.actual_end_date, 'open') AS detail
FROM Maintenance_Orders o JOIN Aircraft a USING (aircraft_id)
WHERE o.opened_date < a.contract_start_date
   OR (a.contract_end_date IS NOT NULL
       AND (o.opened_date > a.contract_end_date OR o.actual_end_date > a.contract_end_date));
