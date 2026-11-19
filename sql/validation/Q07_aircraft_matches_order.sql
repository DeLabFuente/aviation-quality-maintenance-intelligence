-- rule: Q07
-- title: If a non-conformity names an order and an aircraft, the aircraft is the order's
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT i.incident_number AS record_ref, 'Aircraft ' || a.registration || ' but order ' || o.mo_number || ' is for ' || b.registration AS detail
FROM Quality_Incidents i
JOIN Maintenance_Orders o ON o.mo_id = i.mo_id
JOIN Aircraft a ON a.aircraft_id = i.aircraft_id
JOIN Aircraft b ON b.aircraft_id = o.aircraft_id
WHERE i.aircraft_id <> o.aircraft_id;
