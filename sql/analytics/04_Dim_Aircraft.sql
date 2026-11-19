-- AQMI analytical model — Dim_Aircraft (customer and current operational status included)
SELECT a.aircraft_id, a.registration, a.fleet_number, a.aircraft_category, a.aircraft_model,
       a.customer_name, c.operation_type, a.contract_start_date, a.contract_end_date,
       a.operational_status, a.open_orders AS open_orders_now
FROM vw_aircraft_status a JOIN Customers c USING (customer_id)
ORDER BY a.registration;
