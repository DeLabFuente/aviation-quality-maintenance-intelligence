-- rule: I14
-- title: A movement to NON_CONFORMING is linked to a 'non-conforming material' incident
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT v.movement_number AS record_ref, 'Linked to ' || i.incident_number || ' of category ' || c.category_code AS detail
FROM Inventory_Movements v
JOIN Quality_Incidents i USING (incident_id)
JOIN Incident_Categories c ON c.category_id = i.category_id
WHERE v.movement_type = 'NONCONFORM' AND c.category_code <> 'MNC';
