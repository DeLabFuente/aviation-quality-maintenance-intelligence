-- rule: G05
-- title: No operational event is earlier than the start of the period
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
WITH p AS (SELECT (SELECT parameter_value FROM System_Parameters WHERE parameter_key = 'AS_OF_DATE') AS as_of,
             (SELECT parameter_value FROM System_Parameters WHERE parameter_key = 'PERIOD_START') AS period_start)
SELECT x.mo_number AS record_ref, 'Maintenance_Orders.opened_date = ' || x.opened_date || ' is before the start of the period' AS detail
FROM Maintenance_Orders x CROSS JOIN p WHERE substr(x.opened_date, 1, 10) < p.period_start
UNION ALL
SELECT x.incident_number AS record_ref, 'Quality_Incidents.detected_date = ' || x.detected_date || ' is before the start of the period' AS detail
FROM Quality_Incidents x CROSS JOIN p WHERE substr(x.detected_date, 1, 10) < p.period_start
UNION ALL
SELECT x.po_number AS record_ref, 'Purchase_Orders.order_date = ' || x.order_date || ' is before the start of the period' AS detail
FROM Purchase_Orders x CROSS JOIN p WHERE substr(x.order_date, 1, 10) < p.period_start
UNION ALL
SELECT x.verification_number AS record_ref, 'Document_Verifications.verification_date = ' || x.verification_date || ' is before the start of the period' AS detail
FROM Document_Verifications x CROSS JOIN p WHERE substr(x.verification_date, 1, 10) < p.period_start
UNION ALL
SELECT x.movement_number AS record_ref, 'Inventory_Movements.movement_datetime = ' || x.movement_datetime || ' is before the start of the period' AS detail
FROM Inventory_Movements x CROSS JOIN p WHERE substr(x.movement_datetime, 1, 10) < p.period_start
UNION ALL
SELECT x.action_number AS record_ref, 'CAPA_Actions.created_date = ' || x.created_date || ' is before the start of the period' AS detail
FROM CAPA_Actions x CROSS JOIN p WHERE substr(x.created_date, 1, 10) < p.period_start;
