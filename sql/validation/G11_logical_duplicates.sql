-- rule: G11
-- title: No logical duplicates (same content recorded twice)
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT group_concat(incident_number, ' / ') AS record_ref,
       'Possible duplicate non-conformity: same category, title, date and linked records' AS detail
FROM Quality_Incidents
GROUP BY category_id, title, detected_date, aircraft_id, mo_id, revision_id, material_id, supplier_id
HAVING COUNT(*) > 1
UNION ALL
SELECT group_concat(mo_number, ' / '), 'Possible duplicate order: same aircraft, type, description and opening date'
FROM Maintenance_Orders
GROUP BY aircraft_id, maintenance_type, work_description, opened_date
HAVING COUNT(*) > 1;
