-- rule: M13
-- title: An order is not closed while a CRITICAL non-conformity linked to it is open
-- severity: CRITICAL
-- type: P
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT o.mo_number AS record_ref,
       'Closed ' || o.closed_date || ' with ' || i.incident_number || ' open until ' || COALESCE(i.closed_date, 'today') AS detail
FROM Maintenance_Orders o JOIN Quality_Incidents i ON i.mo_id = o.mo_id
WHERE o.status = 'CLOSED' AND i.severity = 'CRITICAL' AND i.status <> 'CANCELLED'
  AND i.detected_date <= o.closed_date
  AND (i.closed_date IS NULL OR i.closed_date > o.closed_date);
