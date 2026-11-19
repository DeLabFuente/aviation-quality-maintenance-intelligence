-- AQMI analytical model — Dim_Department
SELECT department_id, department_code, department_name,
       department_code || ' · ' || department_name AS department_label
FROM Departments ORDER BY department_id;
