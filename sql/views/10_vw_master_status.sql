-- =============================================================================
-- AQMI — vw_employee_status and vw_aircraft_status
-- Status at the cut-off date, calculated from the dates (never stored).
-- =============================================================================
CREATE VIEW vw_employee_status AS
SELECT
    e.employee_id, e.employee_code, e.first_name, e.last_name, e.department_id, d.department_code,
    e.job_title, e.is_department_head, e.hire_date, e.termination_date,
    CASE WHEN e.hire_date <= p.as_of_date
          AND (e.termination_date IS NULL OR e.termination_date >= p.as_of_date) THEN 1 ELSE 0 END AS is_active
FROM Employees e
JOIN Departments d USING (department_id)
CROSS JOIN vw_parameters p;

CREATE VIEW vw_aircraft_status AS
SELECT
    a.aircraft_id, a.registration, a.fleet_number, a.aircraft_category, a.aircraft_model,
    a.customer_id, c.customer_name, a.contract_start_date, a.contract_end_date,
    (SELECT COUNT(*) FROM Maintenance_Orders o WHERE o.aircraft_id = a.aircraft_id
        AND o.status IN ('OPEN', 'IN_PROGRESS', 'ON_HOLD'))                      AS open_orders,
    CASE WHEN a.contract_end_date IS NOT NULL AND a.contract_end_date < p.as_of_date THEN 'OUT_OF_CONTRACT'
         WHEN EXISTS (SELECT 1 FROM Maintenance_Orders o WHERE o.aircraft_id = a.aircraft_id
                        AND o.status IN ('OPEN', 'IN_PROGRESS', 'ON_HOLD'))   THEN 'IN_MAINTENANCE'
         ELSE 'IN_SERVICE' END                                                     AS operational_status
FROM Aircraft a
JOIN Customers c USING (customer_id)
CROSS JOIN vw_parameters p;
