-- rule: C10
-- title: Open action past its due date (overdue action)
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
WITH p AS (SELECT (SELECT parameter_value FROM System_Parameters WHERE parameter_key = 'AS_OF_DATE') AS as_of,
             (SELECT parameter_value FROM System_Parameters WHERE parameter_key = 'PERIOD_START') AS period_start)
SELECT a.action_number AS record_ref,
       a.action_type || ', due ' || a.due_date || ' (' || CAST(julianday(p.as_of) - julianday(a.due_date) AS INTEGER) ||
       ' days late), status ' || a.status AS detail
FROM CAPA_Actions a CROSS JOIN p
WHERE a.status IN ('OPEN', 'IN_PROGRESS') AND a.due_date < p.as_of;
