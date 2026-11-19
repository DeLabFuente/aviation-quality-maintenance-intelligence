-- =============================================================================
-- AQMI — Aviation Quality & Maintenance Intelligence
-- File:    sql/schema/03_triggers.sql
-- GENERATED AUTOMATICALLY by scripts/trigger_builder.py — DO NOT EDIT BY HAND.
-- It is rebuilt every time scripts/build_database.py runs.
-- =============================================================================


-- ----------------------------------------------------------------------------
-- System_Parameters
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_system_parameters_no_delete
BEFORE DELETE ON System_Parameters
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on System_Parameters. Cancel or deactivate the record instead.');
END;


-- ----------------------------------------------------------------------------
-- Departments
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_departments_no_delete
BEFORE DELETE ON Departments
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Departments. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_departments_audit_insert
AFTER INSERT ON Departments
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Departments', NEW.department_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_departments_update_guard
BEFORE UPDATE ON Departments
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.department_id IS NOT OLD.department_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Departments must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_departments_audit_update
AFTER UPDATE ON Departments
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Departments', NEW.department_id, 'UPDATE', 'department_code',
           CAST(OLD.department_code AS TEXT), CAST(NEW.department_code AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.department_code IS NOT NEW.department_code;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Departments', NEW.department_id, 'UPDATE', 'department_name',
           CAST(OLD.department_name AS TEXT), CAST(NEW.department_name AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.department_name IS NOT NEW.department_name;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Departments', NEW.department_id, 'UPDATE', 'is_active',
           CAST(OLD.is_active AS TEXT), CAST(NEW.is_active AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.is_active IS NOT NEW.is_active;
END;


-- ----------------------------------------------------------------------------
-- Employees
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_employees_no_delete
BEFORE DELETE ON Employees
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Employees. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_employees_audit_insert
AFTER INSERT ON Employees
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Employees', NEW.employee_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_employees_update_guard
BEFORE UPDATE ON Employees
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.employee_id IS NOT OLD.employee_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Employees must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_employees_audit_update
AFTER UPDATE ON Employees
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Employees', NEW.employee_id, 'UPDATE', 'employee_code',
           CAST(OLD.employee_code AS TEXT), CAST(NEW.employee_code AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.employee_code IS NOT NEW.employee_code;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Employees', NEW.employee_id, 'UPDATE', 'first_name',
           CAST(OLD.first_name AS TEXT), CAST(NEW.first_name AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.first_name IS NOT NEW.first_name;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Employees', NEW.employee_id, 'UPDATE', 'last_name',
           CAST(OLD.last_name AS TEXT), CAST(NEW.last_name AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.last_name IS NOT NEW.last_name;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Employees', NEW.employee_id, 'UPDATE', 'department_id',
           CAST(OLD.department_id AS TEXT), CAST(NEW.department_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.department_id IS NOT NEW.department_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Employees', NEW.employee_id, 'UPDATE', 'job_title',
           CAST(OLD.job_title AS TEXT), CAST(NEW.job_title AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.job_title IS NOT NEW.job_title;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Employees', NEW.employee_id, 'UPDATE', 'is_department_head',
           CAST(OLD.is_department_head AS TEXT), CAST(NEW.is_department_head AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.is_department_head IS NOT NEW.is_department_head;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Employees', NEW.employee_id, 'UPDATE', 'email',
           CAST(OLD.email AS TEXT), CAST(NEW.email AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.email IS NOT NEW.email;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Employees', NEW.employee_id, 'UPDATE', 'hire_date',
           CAST(OLD.hire_date AS TEXT), CAST(NEW.hire_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.hire_date IS NOT NEW.hire_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Employees', NEW.employee_id, 'UPDATE', 'termination_date',
           CAST(OLD.termination_date AS TEXT), CAST(NEW.termination_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.termination_date IS NOT NEW.termination_date;
END;


-- ----------------------------------------------------------------------------
-- Customers
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_customers_no_delete
BEFORE DELETE ON Customers
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Customers. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_customers_audit_insert
AFTER INSERT ON Customers
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Customers', NEW.customer_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_customers_update_guard
BEFORE UPDATE ON Customers
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.customer_id IS NOT OLD.customer_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Customers must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_customers_audit_update
AFTER UPDATE ON Customers
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Customers', NEW.customer_id, 'UPDATE', 'customer_code',
           CAST(OLD.customer_code AS TEXT), CAST(NEW.customer_code AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.customer_code IS NOT NEW.customer_code;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Customers', NEW.customer_id, 'UPDATE', 'customer_name',
           CAST(OLD.customer_name AS TEXT), CAST(NEW.customer_name AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.customer_name IS NOT NEW.customer_name;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Customers', NEW.customer_id, 'UPDATE', 'operation_type',
           CAST(OLD.operation_type AS TEXT), CAST(NEW.operation_type AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.operation_type IS NOT NEW.operation_type;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Customers', NEW.customer_id, 'UPDATE', 'country_code',
           CAST(OLD.country_code AS TEXT), CAST(NEW.country_code AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.country_code IS NOT NEW.country_code;
END;


-- ----------------------------------------------------------------------------
-- Aircraft
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_aircraft_no_delete
BEFORE DELETE ON Aircraft
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Aircraft. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_aircraft_audit_insert
AFTER INSERT ON Aircraft
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Aircraft', NEW.aircraft_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_aircraft_update_guard
BEFORE UPDATE ON Aircraft
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.aircraft_id IS NOT OLD.aircraft_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Aircraft must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_aircraft_audit_update
AFTER UPDATE ON Aircraft
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Aircraft', NEW.aircraft_id, 'UPDATE', 'registration',
           CAST(OLD.registration AS TEXT), CAST(NEW.registration AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.registration IS NOT NEW.registration;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Aircraft', NEW.aircraft_id, 'UPDATE', 'fleet_number',
           CAST(OLD.fleet_number AS TEXT), CAST(NEW.fleet_number AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.fleet_number IS NOT NEW.fleet_number;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Aircraft', NEW.aircraft_id, 'UPDATE', 'aircraft_category',
           CAST(OLD.aircraft_category AS TEXT), CAST(NEW.aircraft_category AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.aircraft_category IS NOT NEW.aircraft_category;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Aircraft', NEW.aircraft_id, 'UPDATE', 'aircraft_model',
           CAST(OLD.aircraft_model AS TEXT), CAST(NEW.aircraft_model AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.aircraft_model IS NOT NEW.aircraft_model;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Aircraft', NEW.aircraft_id, 'UPDATE', 'serial_number',
           CAST(OLD.serial_number AS TEXT), CAST(NEW.serial_number AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.serial_number IS NOT NEW.serial_number;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Aircraft', NEW.aircraft_id, 'UPDATE', 'customer_id',
           CAST(OLD.customer_id AS TEXT), CAST(NEW.customer_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.customer_id IS NOT NEW.customer_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Aircraft', NEW.aircraft_id, 'UPDATE', 'year_of_manufacture',
           CAST(OLD.year_of_manufacture AS TEXT), CAST(NEW.year_of_manufacture AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.year_of_manufacture IS NOT NEW.year_of_manufacture;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Aircraft', NEW.aircraft_id, 'UPDATE', 'contract_start_date',
           CAST(OLD.contract_start_date AS TEXT), CAST(NEW.contract_start_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.contract_start_date IS NOT NEW.contract_start_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Aircraft', NEW.aircraft_id, 'UPDATE', 'contract_end_date',
           CAST(OLD.contract_end_date AS TEXT), CAST(NEW.contract_end_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.contract_end_date IS NOT NEW.contract_end_date;
END;


-- ----------------------------------------------------------------------------
-- Suppliers
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_suppliers_no_delete
BEFORE DELETE ON Suppliers
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Suppliers. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_suppliers_audit_insert
AFTER INSERT ON Suppliers
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Suppliers', NEW.supplier_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_suppliers_update_guard
BEFORE UPDATE ON Suppliers
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.supplier_id IS NOT OLD.supplier_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Suppliers must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_suppliers_audit_update
AFTER UPDATE ON Suppliers
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Suppliers', NEW.supplier_id, 'UPDATE', 'supplier_code',
           CAST(OLD.supplier_code AS TEXT), CAST(NEW.supplier_code AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.supplier_code IS NOT NEW.supplier_code;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Suppliers', NEW.supplier_id, 'UPDATE', 'supplier_name',
           CAST(OLD.supplier_name AS TEXT), CAST(NEW.supplier_name AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.supplier_name IS NOT NEW.supplier_name;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Suppliers', NEW.supplier_id, 'UPDATE', 'country_code',
           CAST(OLD.country_code AS TEXT), CAST(NEW.country_code AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.country_code IS NOT NEW.country_code;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Suppliers', NEW.supplier_id, 'UPDATE', 'supplier_type',
           CAST(OLD.supplier_type AS TEXT), CAST(NEW.supplier_type AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.supplier_type IS NOT NEW.supplier_type;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Suppliers', NEW.supplier_id, 'UPDATE', 'approval_status',
           CAST(OLD.approval_status AS TEXT), CAST(NEW.approval_status AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.approval_status IS NOT NEW.approval_status;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Suppliers', NEW.supplier_id, 'UPDATE', 'approval_date',
           CAST(OLD.approval_date AS TEXT), CAST(NEW.approval_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.approval_date IS NOT NEW.approval_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Suppliers', NEW.supplier_id, 'UPDATE', 'suspended_date',
           CAST(OLD.suspended_date AS TEXT), CAST(NEW.suspended_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.suspended_date IS NOT NEW.suspended_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Suppliers', NEW.supplier_id, 'UPDATE', 'next_evaluation_date',
           CAST(OLD.next_evaluation_date AS TEXT), CAST(NEW.next_evaluation_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.next_evaluation_date IS NOT NEW.next_evaluation_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Suppliers', NEW.supplier_id, 'UPDATE', 'contact_email',
           CAST(OLD.contact_email AS TEXT), CAST(NEW.contact_email AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.contact_email IS NOT NEW.contact_email;
END;


-- ----------------------------------------------------------------------------
-- Materials
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_materials_no_delete
BEFORE DELETE ON Materials
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Materials. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_materials_audit_insert
AFTER INSERT ON Materials
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Materials', NEW.material_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_materials_update_guard
BEFORE UPDATE ON Materials
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.material_id IS NOT OLD.material_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Materials must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_materials_audit_update
AFTER UPDATE ON Materials
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'part_number',
           CAST(OLD.part_number AS TEXT), CAST(NEW.part_number AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.part_number IS NOT NEW.part_number;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'description',
           CAST(OLD.description AS TEXT), CAST(NEW.description AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.description IS NOT NEW.description;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'material_class',
           CAST(OLD.material_class AS TEXT), CAST(NEW.material_class AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.material_class IS NOT NEW.material_class;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'unit_of_measure',
           CAST(OLD.unit_of_measure AS TEXT), CAST(NEW.unit_of_measure AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.unit_of_measure IS NOT NEW.unit_of_measure;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'preferred_supplier_id',
           CAST(OLD.preferred_supplier_id AS TEXT), CAST(NEW.preferred_supplier_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.preferred_supplier_id IS NOT NEW.preferred_supplier_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'standard_lead_time_days',
           CAST(OLD.standard_lead_time_days AS TEXT), CAST(NEW.standard_lead_time_days AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.standard_lead_time_days IS NOT NEW.standard_lead_time_days;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'min_stock_qty',
           CAST(OLD.min_stock_qty AS TEXT), CAST(NEW.min_stock_qty AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.min_stock_qty IS NOT NEW.min_stock_qty;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'reorder_qty',
           CAST(OLD.reorder_qty AS TEXT), CAST(NEW.reorder_qty AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.reorder_qty IS NOT NEW.reorder_qty;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'unit_cost',
           CAST(OLD.unit_cost AS TEXT), CAST(NEW.unit_cost AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.unit_cost IS NOT NEW.unit_cost;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'is_serialized',
           CAST(OLD.is_serialized AS TEXT), CAST(NEW.is_serialized AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.is_serialized IS NOT NEW.is_serialized;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'is_shelf_life_controlled',
           CAST(OLD.is_shelf_life_controlled AS TEXT), CAST(NEW.is_shelf_life_controlled AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.is_shelf_life_controlled IS NOT NEW.is_shelf_life_controlled;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'requires_release_certificate',
           CAST(OLD.requires_release_certificate AS TEXT), CAST(NEW.requires_release_certificate AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.requires_release_certificate IS NOT NEW.requires_release_certificate;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Materials', NEW.material_id, 'UPDATE', 'is_active',
           CAST(OLD.is_active AS TEXT), CAST(NEW.is_active AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.is_active IS NOT NEW.is_active;
END;


-- ----------------------------------------------------------------------------
-- Documents
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_documents_no_delete
BEFORE DELETE ON Documents
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Documents. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_documents_audit_insert
AFTER INSERT ON Documents
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Documents', NEW.document_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_documents_update_guard
BEFORE UPDATE ON Documents
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.document_id IS NOT OLD.document_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Documents must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_documents_audit_update
AFTER UPDATE ON Documents
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Documents', NEW.document_id, 'UPDATE', 'document_code',
           CAST(OLD.document_code AS TEXT), CAST(NEW.document_code AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.document_code IS NOT NEW.document_code;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Documents', NEW.document_id, 'UPDATE', 'title',
           CAST(OLD.title AS TEXT), CAST(NEW.title AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.title IS NOT NEW.title;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Documents', NEW.document_id, 'UPDATE', 'document_type',
           CAST(OLD.document_type AS TEXT), CAST(NEW.document_type AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.document_type IS NOT NEW.document_type;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Documents', NEW.document_id, 'UPDATE', 'owner_department_id',
           CAST(OLD.owner_department_id AS TEXT), CAST(NEW.owner_department_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.owner_department_id IS NOT NEW.owner_department_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Documents', NEW.document_id, 'UPDATE', 'aircraft_id',
           CAST(OLD.aircraft_id AS TEXT), CAST(NEW.aircraft_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.aircraft_id IS NOT NEW.aircraft_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Documents', NEW.document_id, 'UPDATE', 'is_controlled',
           CAST(OLD.is_controlled AS TEXT), CAST(NEW.is_controlled AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.is_controlled IS NOT NEW.is_controlled;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Documents', NEW.document_id, 'UPDATE', 'review_interval_months',
           CAST(OLD.review_interval_months AS TEXT), CAST(NEW.review_interval_months AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.review_interval_months IS NOT NEW.review_interval_months;
END;


-- ----------------------------------------------------------------------------
-- Document_Revisions
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_document_revisions_no_delete
BEFORE DELETE ON Document_Revisions
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Document_Revisions. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_document_revisions_audit_insert
AFTER INSERT ON Document_Revisions
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Document_Revisions', NEW.revision_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_document_revisions_update_guard
BEFORE UPDATE ON Document_Revisions
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.revision_id IS NOT OLD.revision_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Document_Revisions must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_document_revisions_audit_update
AFTER UPDATE ON Document_Revisions
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Revisions', NEW.revision_id, 'UPDATE', 'document_id',
           CAST(OLD.document_id AS TEXT), CAST(NEW.document_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.document_id IS NOT NEW.document_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Revisions', NEW.revision_id, 'UPDATE', 'revision_code',
           CAST(OLD.revision_code AS TEXT), CAST(NEW.revision_code AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.revision_code IS NOT NEW.revision_code;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Revisions', NEW.revision_id, 'UPDATE', 'revision_seq',
           CAST(OLD.revision_seq AS TEXT), CAST(NEW.revision_seq AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.revision_seq IS NOT NEW.revision_seq;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Revisions', NEW.revision_id, 'UPDATE', 'issue_date',
           CAST(OLD.issue_date AS TEXT), CAST(NEW.issue_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.issue_date IS NOT NEW.issue_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Revisions', NEW.revision_id, 'UPDATE', 'effective_date',
           CAST(OLD.effective_date AS TEXT), CAST(NEW.effective_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.effective_date IS NOT NEW.effective_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Revisions', NEW.revision_id, 'UPDATE', 'review_due_date',
           CAST(OLD.review_due_date AS TEXT), CAST(NEW.review_due_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.review_due_date IS NOT NEW.review_due_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Revisions', NEW.revision_id, 'UPDATE', 'superseded_date',
           CAST(OLD.superseded_date AS TEXT), CAST(NEW.superseded_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.superseded_date IS NOT NEW.superseded_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Revisions', NEW.revision_id, 'UPDATE', 'lifecycle_status',
           CAST(OLD.lifecycle_status AS TEXT), CAST(NEW.lifecycle_status AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.lifecycle_status IS NOT NEW.lifecycle_status;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Revisions', NEW.revision_id, 'UPDATE', 'prepared_by',
           CAST(OLD.prepared_by AS TEXT), CAST(NEW.prepared_by AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.prepared_by IS NOT NEW.prepared_by;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Revisions', NEW.revision_id, 'UPDATE', 'approved_by',
           CAST(OLD.approved_by AS TEXT), CAST(NEW.approved_by AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.approved_by IS NOT NEW.approved_by;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Revisions', NEW.revision_id, 'UPDATE', 'change_summary',
           CAST(OLD.change_summary AS TEXT), CAST(NEW.change_summary AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.change_summary IS NOT NEW.change_summary;
END;


-- ----------------------------------------------------------------------------
-- Maintenance_Orders
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_maintenance_orders_no_delete
BEFORE DELETE ON Maintenance_Orders
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Maintenance_Orders. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_maintenance_orders_audit_insert
AFTER INSERT ON Maintenance_Orders
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Maintenance_Orders', NEW.mo_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_maintenance_orders_update_guard
BEFORE UPDATE ON Maintenance_Orders
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.mo_id IS NOT OLD.mo_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Maintenance_Orders must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_maintenance_orders_audit_update
AFTER UPDATE ON Maintenance_Orders
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'mo_number',
           CAST(OLD.mo_number AS TEXT), CAST(NEW.mo_number AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.mo_number IS NOT NEW.mo_number;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'aircraft_id',
           CAST(OLD.aircraft_id AS TEXT), CAST(NEW.aircraft_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.aircraft_id IS NOT NEW.aircraft_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'maintenance_type',
           CAST(OLD.maintenance_type AS TEXT), CAST(NEW.maintenance_type AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.maintenance_type IS NOT NEW.maintenance_type;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'work_description',
           CAST(OLD.work_description AS TEXT), CAST(NEW.work_description AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.work_description IS NOT NEW.work_description;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'priority',
           CAST(OLD.priority AS TEXT), CAST(NEW.priority AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.priority IS NOT NEW.priority;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'responsible_department_id',
           CAST(OLD.responsible_department_id AS TEXT), CAST(NEW.responsible_department_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.responsible_department_id IS NOT NEW.responsible_department_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'planner_id',
           CAST(OLD.planner_id AS TEXT), CAST(NEW.planner_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.planner_id IS NOT NEW.planner_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'opened_date',
           CAST(OLD.opened_date AS TEXT), CAST(NEW.opened_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.opened_date IS NOT NEW.opened_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'planned_end_date',
           CAST(OLD.planned_end_date AS TEXT), CAST(NEW.planned_end_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.planned_end_date IS NOT NEW.planned_end_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'actual_end_date',
           CAST(OLD.actual_end_date AS TEXT), CAST(NEW.actual_end_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.actual_end_date IS NOT NEW.actual_end_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'status',
           CAST(OLD.status AS TEXT), CAST(NEW.status AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.status IS NOT NEW.status;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'closed_date',
           CAST(OLD.closed_date AS TEXT), CAST(NEW.closed_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.closed_date IS NOT NEW.closed_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'closed_by',
           CAST(OLD.closed_by AS TEXT), CAST(NEW.closed_by AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.closed_by IS NOT NEW.closed_by;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Orders', NEW.mo_id, 'UPDATE', 'cancellation_reason',
           CAST(OLD.cancellation_reason AS TEXT), CAST(NEW.cancellation_reason AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.cancellation_reason IS NOT NEW.cancellation_reason;
END;


-- ----------------------------------------------------------------------------
-- Maintenance_Order_Materials
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_maintenance_order_materials_no_delete
BEFORE DELETE ON Maintenance_Order_Materials
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Maintenance_Order_Materials. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_maintenance_order_materials_audit_insert
AFTER INSERT ON Maintenance_Order_Materials
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Maintenance_Order_Materials', NEW.mo_material_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_maintenance_order_materials_update_guard
BEFORE UPDATE ON Maintenance_Order_Materials
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.mo_material_id IS NOT OLD.mo_material_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Maintenance_Order_Materials must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_maintenance_order_materials_audit_update
AFTER UPDATE ON Maintenance_Order_Materials
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Materials', NEW.mo_material_id, 'UPDATE', 'mo_id',
           CAST(OLD.mo_id AS TEXT), CAST(NEW.mo_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.mo_id IS NOT NEW.mo_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Materials', NEW.mo_material_id, 'UPDATE', 'material_id',
           CAST(OLD.material_id AS TEXT), CAST(NEW.material_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.material_id IS NOT NEW.material_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Materials', NEW.mo_material_id, 'UPDATE', 'qty_required',
           CAST(OLD.qty_required AS TEXT), CAST(NEW.qty_required AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.qty_required IS NOT NEW.qty_required;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Materials', NEW.mo_material_id, 'UPDATE', 'required_by_date',
           CAST(OLD.required_by_date AS TEXT), CAST(NEW.required_by_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.required_by_date IS NOT NEW.required_by_date;
END;


-- ----------------------------------------------------------------------------
-- Maintenance_Order_Documents
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_maintenance_order_documents_no_delete
BEFORE DELETE ON Maintenance_Order_Documents
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Maintenance_Order_Documents. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_maintenance_order_documents_audit_insert
AFTER INSERT ON Maintenance_Order_Documents
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Maintenance_Order_Documents', NEW.mo_document_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_maintenance_order_documents_update_guard
BEFORE UPDATE ON Maintenance_Order_Documents
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.mo_document_id IS NOT OLD.mo_document_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Maintenance_Order_Documents must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_maintenance_order_documents_audit_update
AFTER UPDATE ON Maintenance_Order_Documents
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Documents', NEW.mo_document_id, 'UPDATE', 'mo_id',
           CAST(OLD.mo_id AS TEXT), CAST(NEW.mo_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.mo_id IS NOT NEW.mo_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Documents', NEW.mo_document_id, 'UPDATE', 'revision_id',
           CAST(OLD.revision_id AS TEXT), CAST(NEW.revision_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.revision_id IS NOT NEW.revision_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Documents', NEW.mo_document_id, 'UPDATE', 'usage_role',
           CAST(OLD.usage_role AS TEXT), CAST(NEW.usage_role AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.usage_role IS NOT NEW.usage_role;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Documents', NEW.mo_document_id, 'UPDATE', 'linked_date',
           CAST(OLD.linked_date AS TEXT), CAST(NEW.linked_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.linked_date IS NOT NEW.linked_date;
END;


-- ----------------------------------------------------------------------------
-- Purchase_Orders
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_purchase_orders_no_delete
BEFORE DELETE ON Purchase_Orders
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Purchase_Orders. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_purchase_orders_audit_insert
AFTER INSERT ON Purchase_Orders
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Purchase_Orders', NEW.po_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_purchase_orders_update_guard
BEFORE UPDATE ON Purchase_Orders
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.po_id IS NOT OLD.po_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Purchase_Orders must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_purchase_orders_audit_update
AFTER UPDATE ON Purchase_Orders
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Orders', NEW.po_id, 'UPDATE', 'po_number',
           CAST(OLD.po_number AS TEXT), CAST(NEW.po_number AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.po_number IS NOT NEW.po_number;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Orders', NEW.po_id, 'UPDATE', 'supplier_id',
           CAST(OLD.supplier_id AS TEXT), CAST(NEW.supplier_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.supplier_id IS NOT NEW.supplier_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Orders', NEW.po_id, 'UPDATE', 'order_date',
           CAST(OLD.order_date AS TEXT), CAST(NEW.order_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.order_date IS NOT NEW.order_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Orders', NEW.po_id, 'UPDATE', 'urgency',
           CAST(OLD.urgency AS TEXT), CAST(NEW.urgency AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.urgency IS NOT NEW.urgency;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Orders', NEW.po_id, 'UPDATE', 'buyer_id',
           CAST(OLD.buyer_id AS TEXT), CAST(NEW.buyer_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.buyer_id IS NOT NEW.buyer_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Orders', NEW.po_id, 'UPDATE', 'cancelled_date',
           CAST(OLD.cancelled_date AS TEXT), CAST(NEW.cancelled_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.cancelled_date IS NOT NEW.cancelled_date;
END;


-- ----------------------------------------------------------------------------
-- Purchase_Order_Lines
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_purchase_order_lines_no_delete
BEFORE DELETE ON Purchase_Order_Lines
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Purchase_Order_Lines. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_purchase_order_lines_audit_insert
AFTER INSERT ON Purchase_Order_Lines
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Purchase_Order_Lines', NEW.po_line_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_purchase_order_lines_update_guard
BEFORE UPDATE ON Purchase_Order_Lines
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.po_line_id IS NOT OLD.po_line_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Purchase_Order_Lines must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_purchase_order_lines_audit_update
AFTER UPDATE ON Purchase_Order_Lines
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Order_Lines', NEW.po_line_id, 'UPDATE', 'po_id',
           CAST(OLD.po_id AS TEXT), CAST(NEW.po_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.po_id IS NOT NEW.po_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Order_Lines', NEW.po_line_id, 'UPDATE', 'line_number',
           CAST(OLD.line_number AS TEXT), CAST(NEW.line_number AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.line_number IS NOT NEW.line_number;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Order_Lines', NEW.po_line_id, 'UPDATE', 'material_id',
           CAST(OLD.material_id AS TEXT), CAST(NEW.material_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.material_id IS NOT NEW.material_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Order_Lines', NEW.po_line_id, 'UPDATE', 'qty_ordered',
           CAST(OLD.qty_ordered AS TEXT), CAST(NEW.qty_ordered AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.qty_ordered IS NOT NEW.qty_ordered;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Order_Lines', NEW.po_line_id, 'UPDATE', 'unit_price',
           CAST(OLD.unit_price AS TEXT), CAST(NEW.unit_price AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.unit_price IS NOT NEW.unit_price;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Order_Lines', NEW.po_line_id, 'UPDATE', 'promised_date',
           CAST(OLD.promised_date AS TEXT), CAST(NEW.promised_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.promised_date IS NOT NEW.promised_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Purchase_Order_Lines', NEW.po_line_id, 'UPDATE', 'mo_id',
           CAST(OLD.mo_id AS TEXT), CAST(NEW.mo_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.mo_id IS NOT NEW.mo_id;
END;


-- ----------------------------------------------------------------------------
-- Incident_Categories
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_incident_categories_no_delete
BEFORE DELETE ON Incident_Categories
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Incident_Categories. Cancel or deactivate the record instead.');
END;


-- ----------------------------------------------------------------------------
-- Quality_Incidents
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_quality_incidents_no_delete
BEFORE DELETE ON Quality_Incidents
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Quality_Incidents. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_quality_incidents_audit_insert
AFTER INSERT ON Quality_Incidents
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Quality_Incidents', NEW.incident_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_quality_incidents_update_guard
BEFORE UPDATE ON Quality_Incidents
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.incident_id IS NOT OLD.incident_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Quality_Incidents must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_quality_incidents_audit_update
AFTER UPDATE ON Quality_Incidents
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'incident_number',
           CAST(OLD.incident_number AS TEXT), CAST(NEW.incident_number AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.incident_number IS NOT NEW.incident_number;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'category_id',
           CAST(OLD.category_id AS TEXT), CAST(NEW.category_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.category_id IS NOT NEW.category_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'severity',
           CAST(OLD.severity AS TEXT), CAST(NEW.severity AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.severity IS NOT NEW.severity;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'priority',
           CAST(OLD.priority AS TEXT), CAST(NEW.priority AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.priority IS NOT NEW.priority;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'detection_source',
           CAST(OLD.detection_source AS TEXT), CAST(NEW.detection_source AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.detection_source IS NOT NEW.detection_source;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'title',
           CAST(OLD.title AS TEXT), CAST(NEW.title AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.title IS NOT NEW.title;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'description',
           CAST(OLD.description AS TEXT), CAST(NEW.description AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.description IS NOT NEW.description;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'detected_date',
           CAST(OLD.detected_date AS TEXT), CAST(NEW.detected_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.detected_date IS NOT NEW.detected_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'detected_by',
           CAST(OLD.detected_by AS TEXT), CAST(NEW.detected_by AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.detected_by IS NOT NEW.detected_by;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'responsible_department_id',
           CAST(OLD.responsible_department_id AS TEXT), CAST(NEW.responsible_department_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.responsible_department_id IS NOT NEW.responsible_department_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'owner_id',
           CAST(OLD.owner_id AS TEXT), CAST(NEW.owner_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.owner_id IS NOT NEW.owner_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'aircraft_id',
           CAST(OLD.aircraft_id AS TEXT), CAST(NEW.aircraft_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.aircraft_id IS NOT NEW.aircraft_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'mo_id',
           CAST(OLD.mo_id AS TEXT), CAST(NEW.mo_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.mo_id IS NOT NEW.mo_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'revision_id',
           CAST(OLD.revision_id AS TEXT), CAST(NEW.revision_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.revision_id IS NOT NEW.revision_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'material_id',
           CAST(OLD.material_id AS TEXT), CAST(NEW.material_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.material_id IS NOT NEW.material_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'supplier_id',
           CAST(OLD.supplier_id AS TEXT), CAST(NEW.supplier_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.supplier_id IS NOT NEW.supplier_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'po_line_id',
           CAST(OLD.po_line_id AS TEXT), CAST(NEW.po_line_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.po_line_id IS NOT NEW.po_line_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'containment_action',
           CAST(OLD.containment_action AS TEXT), CAST(NEW.containment_action AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.containment_action IS NOT NEW.containment_action;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'status',
           CAST(OLD.status AS TEXT), CAST(NEW.status AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.status IS NOT NEW.status;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'target_closure_date',
           CAST(OLD.target_closure_date AS TEXT), CAST(NEW.target_closure_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.target_closure_date IS NOT NEW.target_closure_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'closed_date',
           CAST(OLD.closed_date AS TEXT), CAST(NEW.closed_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.closed_date IS NOT NEW.closed_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'closed_by',
           CAST(OLD.closed_by AS TEXT), CAST(NEW.closed_by AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.closed_by IS NOT NEW.closed_by;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Quality_Incidents', NEW.incident_id, 'UPDATE', 'closure_summary',
           CAST(OLD.closure_summary AS TEXT), CAST(NEW.closure_summary AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.closure_summary IS NOT NEW.closure_summary;
END;


-- ----------------------------------------------------------------------------
-- Maintenance_Order_Holds
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_maintenance_order_holds_no_delete
BEFORE DELETE ON Maintenance_Order_Holds
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Maintenance_Order_Holds. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_maintenance_order_holds_audit_insert
AFTER INSERT ON Maintenance_Order_Holds
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Maintenance_Order_Holds', NEW.hold_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_maintenance_order_holds_update_guard
BEFORE UPDATE ON Maintenance_Order_Holds
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.hold_id IS NOT OLD.hold_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Maintenance_Order_Holds must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_maintenance_order_holds_audit_update
AFTER UPDATE ON Maintenance_Order_Holds
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Holds', NEW.hold_id, 'UPDATE', 'mo_id',
           CAST(OLD.mo_id AS TEXT), CAST(NEW.mo_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.mo_id IS NOT NEW.mo_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Holds', NEW.hold_id, 'UPDATE', 'hold_reason',
           CAST(OLD.hold_reason AS TEXT), CAST(NEW.hold_reason AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.hold_reason IS NOT NEW.hold_reason;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Holds', NEW.hold_id, 'UPDATE', 'material_id',
           CAST(OLD.material_id AS TEXT), CAST(NEW.material_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.material_id IS NOT NEW.material_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Holds', NEW.hold_id, 'UPDATE', 'document_id',
           CAST(OLD.document_id AS TEXT), CAST(NEW.document_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.document_id IS NOT NEW.document_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Holds', NEW.hold_id, 'UPDATE', 'incident_id',
           CAST(OLD.incident_id AS TEXT), CAST(NEW.incident_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.incident_id IS NOT NEW.incident_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Holds', NEW.hold_id, 'UPDATE', 'start_date',
           CAST(OLD.start_date AS TEXT), CAST(NEW.start_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.start_date IS NOT NEW.start_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Holds', NEW.hold_id, 'UPDATE', 'end_date',
           CAST(OLD.end_date AS TEXT), CAST(NEW.end_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.end_date IS NOT NEW.end_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Holds', NEW.hold_id, 'UPDATE', 'comment',
           CAST(OLD.comment AS TEXT), CAST(NEW.comment AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.comment IS NOT NEW.comment;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Maintenance_Order_Holds', NEW.hold_id, 'UPDATE', 'raised_by',
           CAST(OLD.raised_by AS TEXT), CAST(NEW.raised_by AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.raised_by IS NOT NEW.raised_by;
END;


-- ----------------------------------------------------------------------------
-- Document_Verifications
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_document_verifications_no_delete
BEFORE DELETE ON Document_Verifications
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Document_Verifications. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_document_verifications_audit_insert
AFTER INSERT ON Document_Verifications
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Document_Verifications', NEW.verification_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_document_verifications_update_guard
BEFORE UPDATE ON Document_Verifications
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.verification_id IS NOT OLD.verification_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Document_Verifications must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_document_verifications_audit_update
AFTER UPDATE ON Document_Verifications
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Verifications', NEW.verification_id, 'UPDATE', 'verification_number',
           CAST(OLD.verification_number AS TEXT), CAST(NEW.verification_number AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.verification_number IS NOT NEW.verification_number;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Verifications', NEW.verification_id, 'UPDATE', 'revision_id',
           CAST(OLD.revision_id AS TEXT), CAST(NEW.revision_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.revision_id IS NOT NEW.revision_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Verifications', NEW.verification_id, 'UPDATE', 'mo_id',
           CAST(OLD.mo_id AS TEXT), CAST(NEW.mo_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.mo_id IS NOT NEW.mo_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Verifications', NEW.verification_id, 'UPDATE', 'verification_type',
           CAST(OLD.verification_type AS TEXT), CAST(NEW.verification_type AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.verification_type IS NOT NEW.verification_type;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Verifications', NEW.verification_id, 'UPDATE', 'verification_date',
           CAST(OLD.verification_date AS TEXT), CAST(NEW.verification_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.verification_date IS NOT NEW.verification_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Verifications', NEW.verification_id, 'UPDATE', 'verified_by',
           CAST(OLD.verified_by AS TEXT), CAST(NEW.verified_by AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.verified_by IS NOT NEW.verified_by;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Verifications', NEW.verification_id, 'UPDATE', 'result',
           CAST(OLD.result AS TEXT), CAST(NEW.result AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.result IS NOT NEW.result;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Verifications', NEW.verification_id, 'UPDATE', 'discrepancy_description',
           CAST(OLD.discrepancy_description AS TEXT), CAST(NEW.discrepancy_description AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.discrepancy_description IS NOT NEW.discrepancy_description;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Document_Verifications', NEW.verification_id, 'UPDATE', 'incident_id',
           CAST(OLD.incident_id AS TEXT), CAST(NEW.incident_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.incident_id IS NOT NEW.incident_id;
END;


-- ----------------------------------------------------------------------------
-- Root_Cause_Analyses
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_root_cause_analyses_no_delete
BEFORE DELETE ON Root_Cause_Analyses
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Root_Cause_Analyses. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_root_cause_analyses_audit_insert
AFTER INSERT ON Root_Cause_Analyses
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Root_Cause_Analyses', NEW.rca_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_root_cause_analyses_update_guard
BEFORE UPDATE ON Root_Cause_Analyses
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.rca_id IS NOT OLD.rca_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Root_Cause_Analyses must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_root_cause_analyses_audit_update
AFTER UPDATE ON Root_Cause_Analyses
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Root_Cause_Analyses', NEW.rca_id, 'UPDATE', 'incident_id',
           CAST(OLD.incident_id AS TEXT), CAST(NEW.incident_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.incident_id IS NOT NEW.incident_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Root_Cause_Analyses', NEW.rca_id, 'UPDATE', 'method',
           CAST(OLD.method AS TEXT), CAST(NEW.method AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.method IS NOT NEW.method;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Root_Cause_Analyses', NEW.rca_id, 'UPDATE', 'ishikawa_category',
           CAST(OLD.ishikawa_category AS TEXT), CAST(NEW.ishikawa_category AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.ishikawa_category IS NOT NEW.ishikawa_category;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Root_Cause_Analyses', NEW.rca_id, 'UPDATE', 'why_1',
           CAST(OLD.why_1 AS TEXT), CAST(NEW.why_1 AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.why_1 IS NOT NEW.why_1;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Root_Cause_Analyses', NEW.rca_id, 'UPDATE', 'why_2',
           CAST(OLD.why_2 AS TEXT), CAST(NEW.why_2 AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.why_2 IS NOT NEW.why_2;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Root_Cause_Analyses', NEW.rca_id, 'UPDATE', 'why_3',
           CAST(OLD.why_3 AS TEXT), CAST(NEW.why_3 AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.why_3 IS NOT NEW.why_3;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Root_Cause_Analyses', NEW.rca_id, 'UPDATE', 'why_4',
           CAST(OLD.why_4 AS TEXT), CAST(NEW.why_4 AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.why_4 IS NOT NEW.why_4;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Root_Cause_Analyses', NEW.rca_id, 'UPDATE', 'why_5',
           CAST(OLD.why_5 AS TEXT), CAST(NEW.why_5 AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.why_5 IS NOT NEW.why_5;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Root_Cause_Analyses', NEW.rca_id, 'UPDATE', 'root_cause_statement',
           CAST(OLD.root_cause_statement AS TEXT), CAST(NEW.root_cause_statement AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.root_cause_statement IS NOT NEW.root_cause_statement;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Root_Cause_Analyses', NEW.rca_id, 'UPDATE', 'analysis_date',
           CAST(OLD.analysis_date AS TEXT), CAST(NEW.analysis_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.analysis_date IS NOT NEW.analysis_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Root_Cause_Analyses', NEW.rca_id, 'UPDATE', 'analyzed_by',
           CAST(OLD.analyzed_by AS TEXT), CAST(NEW.analyzed_by AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.analyzed_by IS NOT NEW.analyzed_by;
END;


-- ----------------------------------------------------------------------------
-- CAPA_Actions
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_capa_actions_no_delete
BEFORE DELETE ON CAPA_Actions
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on CAPA_Actions. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_capa_actions_audit_insert
AFTER INSERT ON CAPA_Actions
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'CAPA_Actions', NEW.action_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_capa_actions_update_guard
BEFORE UPDATE ON CAPA_Actions
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.action_id IS NOT OLD.action_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of CAPA_Actions must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_capa_actions_audit_update
AFTER UPDATE ON CAPA_Actions
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'action_number',
           CAST(OLD.action_number AS TEXT), CAST(NEW.action_number AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.action_number IS NOT NEW.action_number;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'action_type',
           CAST(OLD.action_type AS TEXT), CAST(NEW.action_type AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.action_type IS NOT NEW.action_type;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'origin',
           CAST(OLD.origin AS TEXT), CAST(NEW.origin AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.origin IS NOT NEW.origin;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'incident_id',
           CAST(OLD.incident_id AS TEXT), CAST(NEW.incident_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.incident_id IS NOT NEW.incident_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'parent_action_id',
           CAST(OLD.parent_action_id AS TEXT), CAST(NEW.parent_action_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.parent_action_id IS NOT NEW.parent_action_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'title',
           CAST(OLD.title AS TEXT), CAST(NEW.title AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.title IS NOT NEW.title;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'description',
           CAST(OLD.description AS TEXT), CAST(NEW.description AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.description IS NOT NEW.description;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'responsible_id',
           CAST(OLD.responsible_id AS TEXT), CAST(NEW.responsible_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.responsible_id IS NOT NEW.responsible_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'department_id',
           CAST(OLD.department_id AS TEXT), CAST(NEW.department_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.department_id IS NOT NEW.department_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'created_date',
           CAST(OLD.created_date AS TEXT), CAST(NEW.created_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.created_date IS NOT NEW.created_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'original_due_date',
           CAST(OLD.original_due_date AS TEXT), CAST(NEW.original_due_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.original_due_date IS NOT NEW.original_due_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'due_date',
           CAST(OLD.due_date AS TEXT), CAST(NEW.due_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.due_date IS NOT NEW.due_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'completed_date',
           CAST(OLD.completed_date AS TEXT), CAST(NEW.completed_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.completed_date IS NOT NEW.completed_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'status',
           CAST(OLD.status AS TEXT), CAST(NEW.status AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.status IS NOT NEW.status;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'effectiveness_check_date',
           CAST(OLD.effectiveness_check_date AS TEXT), CAST(NEW.effectiveness_check_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.effectiveness_check_date IS NOT NEW.effectiveness_check_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'effectiveness_result',
           CAST(OLD.effectiveness_result AS TEXT), CAST(NEW.effectiveness_result AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.effectiveness_result IS NOT NEW.effectiveness_result;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'effectiveness_comment',
           CAST(OLD.effectiveness_comment AS TEXT), CAST(NEW.effectiveness_comment AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.effectiveness_comment IS NOT NEW.effectiveness_comment;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'verified_by',
           CAST(OLD.verified_by AS TEXT), CAST(NEW.verified_by AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.verified_by IS NOT NEW.verified_by;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'closed_date',
           CAST(OLD.closed_date AS TEXT), CAST(NEW.closed_date AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.closed_date IS NOT NEW.closed_date;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'CAPA_Actions', NEW.action_id, 'UPDATE', 'cancellation_reason',
           CAST(OLD.cancellation_reason AS TEXT), CAST(NEW.cancellation_reason AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.cancellation_reason IS NOT NEW.cancellation_reason;
END;


-- ----------------------------------------------------------------------------
-- CAPA_Progress_Updates
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_capa_progress_updates_no_delete
BEFORE DELETE ON CAPA_Progress_Updates
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on CAPA_Progress_Updates. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_capa_progress_updates_no_update
BEFORE UPDATE ON CAPA_Progress_Updates
BEGIN
    SELECT RAISE(ABORT, 'AQMI G08: CAPA_Progress_Updates records cannot be modified. Record a correcting entry instead.');
END;

CREATE TRIGGER trg_capa_progress_updates_audit_insert
AFTER INSERT ON CAPA_Progress_Updates
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'CAPA_Progress_Updates', NEW.update_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;


-- ----------------------------------------------------------------------------
-- Stock_Counts
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_stock_counts_no_delete
BEFORE DELETE ON Stock_Counts
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Stock_Counts. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_stock_counts_audit_insert
AFTER INSERT ON Stock_Counts
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Stock_Counts', NEW.count_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;

CREATE TRIGGER trg_stock_counts_update_guard
BEFORE UPDATE ON Stock_Counts
WHEN NEW.updated_at IS NULL
  OR NEW.updated_by IS NULL
  OR NEW.updated_at < NEW.created_at
  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)
  OR NEW.created_at IS NOT OLD.created_at
  OR NEW.created_by IS NOT OLD.created_by
  OR NEW.count_id IS NOT OLD.count_id
BEGIN
    SELECT RAISE(ABORT, 'AQMI: every update of Stock_Counts must set updated_at and updated_by in chronological order, and must not change the id or the creation data.');
END;

CREATE TRIGGER trg_stock_counts_audit_update
AFTER UPDATE ON Stock_Counts
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Stock_Counts', NEW.count_id, 'UPDATE', 'count_number',
           CAST(OLD.count_number AS TEXT), CAST(NEW.count_number AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.count_number IS NOT NEW.count_number;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Stock_Counts', NEW.count_id, 'UPDATE', 'material_id',
           CAST(OLD.material_id AS TEXT), CAST(NEW.material_id AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.material_id IS NOT NEW.material_id;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Stock_Counts', NEW.count_id, 'UPDATE', 'count_datetime',
           CAST(OLD.count_datetime AS TEXT), CAST(NEW.count_datetime AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.count_datetime IS NOT NEW.count_datetime;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Stock_Counts', NEW.count_id, 'UPDATE', 'count_type',
           CAST(OLD.count_type AS TEXT), CAST(NEW.count_type AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.count_type IS NOT NEW.count_type;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Stock_Counts', NEW.count_id, 'UPDATE', 'system_qty',
           CAST(OLD.system_qty AS TEXT), CAST(NEW.system_qty AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.system_qty IS NOT NEW.system_qty;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Stock_Counts', NEW.count_id, 'UPDATE', 'counted_qty',
           CAST(OLD.counted_qty AS TEXT), CAST(NEW.counted_qty AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.counted_qty IS NOT NEW.counted_qty;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Stock_Counts', NEW.count_id, 'UPDATE', 'counted_by',
           CAST(OLD.counted_by AS TEXT), CAST(NEW.counted_by AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.counted_by IS NOT NEW.counted_by;
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,
                           field_name, old_value, new_value, changed_by, source)
    SELECT NEW.updated_at, 'Stock_Counts', NEW.count_id, 'UPDATE', 'comment',
           CAST(OLD.comment AS TEXT), CAST(NEW.comment AS TEXT), NEW.updated_by, 'TRIGGER'
    WHERE OLD.comment IS NOT NEW.comment;
END;


-- ----------------------------------------------------------------------------
-- Inventory_Movements
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_inventory_movements_no_delete
BEFORE DELETE ON Inventory_Movements
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Inventory_Movements. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_inventory_movements_no_update
BEFORE UPDATE ON Inventory_Movements
BEGIN
    SELECT RAISE(ABORT, 'AQMI G08: Inventory_Movements records cannot be modified. Record a correcting entry instead.');
END;

CREATE TRIGGER trg_inventory_movements_audit_insert
AFTER INSERT ON Inventory_Movements
BEGIN
    INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)
    VALUES (NEW.created_at, 'Inventory_Movements', NEW.movement_id, 'INSERT', NEW.created_by, 'TRIGGER');
END;


-- ----------------------------------------------------------------------------
-- Audit_Log
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_audit_log_no_delete
BEFORE DELETE ON Audit_Log
BEGIN
    SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on Audit_Log. Cancel or deactivate the record instead.');
END;

CREATE TRIGGER trg_audit_log_no_update
BEFORE UPDATE ON Audit_Log
BEGIN
    SELECT RAISE(ABORT, 'AQMI G08: Audit_Log records cannot be modified. Record a correcting entry instead.');
END;
