-- rule: Q12
-- title: Open non-conformity past its target closure date
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
WITH p AS (SELECT (SELECT parameter_value FROM System_Parameters WHERE parameter_key = 'AS_OF_DATE') AS as_of,
             (SELECT parameter_value FROM System_Parameters WHERE parameter_key = 'PERIOD_START') AS period_start)
SELECT i.incident_number AS record_ref,
       i.severity || ', target ' || i.target_closure_date || ' (' ||
       CAST(julianday(p.as_of) - julianday(i.target_closure_date) AS INTEGER) || ' days late), status ' || i.status AS detail
FROM Quality_Incidents i CROSS JOIN p
WHERE i.status NOT IN ('CLOSED', 'CANCELLED') AND i.target_closure_date < p.as_of;
