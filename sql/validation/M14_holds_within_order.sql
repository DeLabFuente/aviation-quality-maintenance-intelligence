-- rule: M14
-- title: Holds are within the dates of their order
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT o.mo_number AS record_ref,
       h.hold_reason || ' hold ' || h.start_date || ' to ' || COALESCE(h.end_date, 'open') ||
       '; order ' || o.opened_date || ' to ' || COALESCE(o.actual_end_date, 'open') AS detail
FROM Maintenance_Order_Holds h JOIN Maintenance_Orders o USING (mo_id)
WHERE h.start_date < o.opened_date
   OR (o.actual_end_date IS NOT NULL AND COALESCE(h.end_date, '9999-12-31') > o.actual_end_date);
