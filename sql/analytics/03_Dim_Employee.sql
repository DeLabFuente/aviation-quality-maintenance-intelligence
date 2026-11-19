-- AQMI analytical model — Dim_Employee (department kept as text: no snowflake, no ambiguous paths)
SELECT e.employee_id, e.employee_code, e.first_name || ' ' || e.last_name AS full_name,
       e.department_code, d.department_name, e.job_title, e.is_department_head, e.is_active
FROM vw_employee_status e JOIN Departments d USING (department_id)
ORDER BY e.employee_id;
