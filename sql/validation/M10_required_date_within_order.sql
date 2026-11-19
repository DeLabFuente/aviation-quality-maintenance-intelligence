-- rule: M10
-- title: The required date of a material is within the order dates
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT o.mo_number AS record_ref, 'Material required on ' || l.required_by_date || ', order ' ||
       o.opened_date || ' to ' || o.planned_end_date AS detail
FROM Maintenance_Order_Materials l JOIN Maintenance_Orders o USING (mo_id)
WHERE l.required_by_date < o.opened_date OR l.required_by_date > o.planned_end_date;
