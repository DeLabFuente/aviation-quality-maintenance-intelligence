-- =============================================================================
-- AQMI — Aviation Quality & Maintenance Intelligence
-- File:    sql/schema/01_tables.sql
-- Purpose: Creates the 25 tables of the operational database (SQLite).
-- Source:  documentation/02_diccionario_de_datos.md (Phase 2 data dictionary)
--
-- Notes
--  * Every table is STRICT: SQLite rejects values of the wrong type.
--  * Dates are TEXT 'YYYY-MM-DD'; date-times are TEXT 'YYYY-MM-DD HH:MM:SS'.
--    The CHECK "date(x) IS x" rejects any badly written date.
--  * Rule codes in comments (G03, M02...) refer to
--    documentation/03_reglas_de_negocio.md.
--  * AEROQ MRO is a fictitious company. All data is synthetic.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. SYSTEM PARAMETERS
-- -----------------------------------------------------------------------------
CREATE TABLE System_Parameters (
    parameter_key        TEXT    NOT NULL PRIMARY KEY,
    parameter_value      TEXT    NOT NULL,
    description          TEXT    NOT NULL
) STRICT;


-- -----------------------------------------------------------------------------
-- 2. MASTER DATA
-- -----------------------------------------------------------------------------
CREATE TABLE Departments (
    department_id        INTEGER PRIMARY KEY,
    department_code      TEXT    NOT NULL UNIQUE
                         CHECK (department_code GLOB '[A-Z][A-Z][A-Z]'),
    department_name      TEXT    NOT NULL UNIQUE,
    is_active            INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at           TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
                         CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id)
) STRICT;

CREATE TABLE Employees (
    employee_id          INTEGER PRIMARY KEY,
    employee_code        TEXT    NOT NULL UNIQUE
                         CHECK (employee_code GLOB 'EMP-[0-9][0-9][0-9]'),
    first_name           TEXT    NOT NULL,
    last_name            TEXT    NOT NULL,
    department_id        INTEGER NOT NULL REFERENCES Departments (department_id),
    job_title            TEXT    NOT NULL,
    is_department_head   INTEGER NOT NULL DEFAULT 0 CHECK (is_department_head IN (0, 1)),
    email                TEXT    NOT NULL UNIQUE
                         CHECK (email LIKE '%_@aeroq-mro.example'),
    hire_date            TEXT    NOT NULL CHECK (date(hire_date) IS hire_date),
    termination_date     TEXT    CHECK (termination_date IS NULL
                                        OR (date(termination_date) IS termination_date
                                            AND termination_date >= hire_date)),
    created_at           TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
                         CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id)
) STRICT;

CREATE TABLE Customers (
    customer_id          INTEGER PRIMARY KEY,
    customer_code        TEXT    NOT NULL UNIQUE
                         CHECK (customer_code GLOB 'CUS-[0-9][0-9]'),
    customer_name        TEXT    NOT NULL UNIQUE,
    operation_type       TEXT    NOT NULL
                         CHECK (operation_type IN ('HEMS', 'AERIAL_WORK',
                                                   'PASSENGER_TRANSPORT', 'PRIVATE')),
    country_code         TEXT    NOT NULL CHECK (country_code GLOB '[A-Z][A-Z]'),
    created_at           TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
                         CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id)
) STRICT;

CREATE TABLE Aircraft (
    aircraft_id          INTEGER PRIMARY KEY,
    registration         TEXT    NOT NULL UNIQUE
                         CHECK (registration GLOB 'EC-Q[0-9][0-9]'),   -- impossible real-world format
    fleet_number         TEXT    NOT NULL UNIQUE
                         CHECK (fleet_number GLOB 'AQ-H[0-9][0-9]'),
    aircraft_category    TEXT    NOT NULL
                         CHECK (aircraft_category IN ('LIGHT_SINGLE', 'LIGHT_TWIN', 'MEDIUM_TWIN')),
    aircraft_model       TEXT    NOT NULL,                              -- fictitious designation
    serial_number        TEXT    NOT NULL UNIQUE,
    customer_id          INTEGER NOT NULL REFERENCES Customers (customer_id),
    year_of_manufacture  INTEGER NOT NULL CHECK (year_of_manufacture BETWEEN 1990 AND 2026),
    contract_start_date  TEXT    NOT NULL CHECK (date(contract_start_date) IS contract_start_date),
    contract_end_date    TEXT    CHECK (contract_end_date IS NULL
                                        OR (date(contract_end_date) IS contract_end_date
                                            AND contract_end_date >= contract_start_date)),
    created_at           TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
                         CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id)
) STRICT;

CREATE TABLE Suppliers (
    supplier_id          INTEGER PRIMARY KEY,
    supplier_code        TEXT    NOT NULL UNIQUE
                         CHECK (supplier_code GLOB 'SUP-[0-9][0-9][0-9]'),
    supplier_name        TEXT    NOT NULL UNIQUE,
    country_code         TEXT    NOT NULL CHECK (country_code GLOB '[A-Z][A-Z]'),
    supplier_type        TEXT    NOT NULL
                         CHECK (supplier_type IN ('MANUFACTURER', 'DISTRIBUTOR',
                                                  'REPAIR_STATION', 'SERVICE_PROVIDER')),
    approval_status      TEXT    NOT NULL                               -- internal list, not an official approval
                         CHECK (approval_status IN ('APPROVED', 'CONDITIONAL',
                                                    'SUSPENDED', 'INACTIVE')),
    approval_date        TEXT    NOT NULL CHECK (date(approval_date) IS approval_date),
    suspended_date       TEXT    CHECK (suspended_date IS NULL
                                        OR (date(suspended_date) IS suspended_date
                                            AND suspended_date >= approval_date)),
    next_evaluation_date TEXT    NOT NULL CHECK (date(next_evaluation_date) IS next_evaluation_date
                                                 AND next_evaluation_date >= approval_date),
    contact_email        TEXT    CHECK (contact_email IS NULL OR contact_email LIKE '%_@%_.example'),
    created_at           TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
                         CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id),
    CHECK ((approval_status = 'SUSPENDED') = (suspended_date IS NOT NULL))
) STRICT;

CREATE TABLE Materials (
    material_id                  INTEGER PRIMARY KEY,
    part_number                  TEXT    NOT NULL UNIQUE
                                 CHECK (part_number GLOB 'AQ-[0-9][0-9][0-9][0-9]-[0-9][0-9]'),
    description                  TEXT    NOT NULL CHECK (length(description) <= 120),
    material_class               TEXT    NOT NULL
                                 CHECK (material_class IN ('CONSUMABLE', 'STANDARD_PART',
                                                           'COMPONENT', 'RAW_MATERIAL')),
    unit_of_measure              TEXT    NOT NULL
                                 CHECK (unit_of_measure IN ('EA', 'L', 'KG', 'M', 'KIT')),
    preferred_supplier_id        INTEGER NOT NULL REFERENCES Suppliers (supplier_id),
    standard_lead_time_days      INTEGER NOT NULL CHECK (standard_lead_time_days > 0),
    min_stock_qty                REAL    NOT NULL CHECK (min_stock_qty >= 0),
    reorder_qty                  REAL    NOT NULL CHECK (reorder_qty > 0),
    unit_cost                    REAL    NOT NULL CHECK (unit_cost >= 0),
    is_serialized                INTEGER NOT NULL CHECK (is_serialized IN (0, 1)),
    is_shelf_life_controlled     INTEGER NOT NULL CHECK (is_shelf_life_controlled IN (0, 1)),
    requires_release_certificate INTEGER NOT NULL CHECK (requires_release_certificate IN (0, 1)),
    is_active                    INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at                   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
                                 CHECK (datetime(created_at) IS created_at),
    created_by                   INTEGER REFERENCES Employees (employee_id),
    updated_at                   TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by                   INTEGER REFERENCES Employees (employee_id)
) STRICT;


-- -----------------------------------------------------------------------------
-- 3. MODULE C — DOCUMENT CONTROL (documents and revisions)
-- -----------------------------------------------------------------------------
CREATE TABLE Documents (
    document_id            INTEGER PRIMARY KEY,
    document_code          TEXT    NOT NULL UNIQUE
                           CHECK (document_code GLOB '[A-Z][A-Z][A-Z]-[A-Z][A-Z][A-Z]-[0-9][0-9][0-9]'),
    title                  TEXT    NOT NULL CHECK (length(title) <= 150),
    document_type          TEXT    NOT NULL
                           CHECK (document_type IN ('PROCEDURE', 'WORK_INSTRUCTION', 'FORM',
                                                    'TECHNICAL_DATA_REF', 'AIRCRAFT_RECORD')),
    owner_department_id    INTEGER NOT NULL REFERENCES Departments (department_id),
    aircraft_id            INTEGER REFERENCES Aircraft (aircraft_id),
    is_controlled          INTEGER NOT NULL CHECK (is_controlled IN (0, 1)),
    review_interval_months INTEGER CHECK (review_interval_months IS NULL OR review_interval_months > 0),
    created_at             TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by             INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at             TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by             INTEGER REFERENCES Employees (employee_id),
    CHECK (document_type <> 'AIRCRAFT_RECORD' OR aircraft_id IS NOT NULL),          -- D07
    CHECK (is_controlled = 0 OR review_interval_months IS NOT NULL)                 -- D08
) STRICT;

CREATE TABLE Document_Revisions (
    revision_id          INTEGER PRIMARY KEY,
    document_id          INTEGER NOT NULL REFERENCES Documents (document_id),
    revision_code        TEXT    NOT NULL CHECK (revision_code GLOB 'R[0-9][0-9]'),
    revision_seq         INTEGER NOT NULL CHECK (revision_seq >= 0),
    issue_date           TEXT    NOT NULL CHECK (date(issue_date) IS issue_date),
    effective_date       TEXT    NOT NULL CHECK (date(effective_date) IS effective_date),
    review_due_date      TEXT    CHECK (review_due_date IS NULL OR date(review_due_date) IS review_due_date),
    superseded_date      TEXT    CHECK (superseded_date IS NULL OR date(superseded_date) IS superseded_date),
    lifecycle_status     TEXT    NOT NULL
                         CHECK (lifecycle_status IN ('DRAFT', 'CURRENT', 'SUPERSEDED', 'WITHDRAWN')),
    prepared_by          INTEGER NOT NULL REFERENCES Employees (employee_id),
    approved_by          INTEGER REFERENCES Employees (employee_id),
    change_summary       TEXT    NOT NULL,
    created_at           TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id),
    UNIQUE (document_id, revision_code),
    UNIQUE (document_id, revision_seq),
    CHECK (effective_date >= issue_date),                                            -- D02
    CHECK (review_due_date IS NULL OR review_due_date >= effective_date),            -- D02
    CHECK (superseded_date IS NULL OR superseded_date >= effective_date),            -- D02
    CHECK ((lifecycle_status = 'SUPERSEDED') = (superseded_date IS NOT NULL)),       -- D03
    CHECK (lifecycle_status = 'DRAFT' OR approved_by IS NOT NULL),                   -- D05
    CHECK (approved_by IS NULL OR approved_by <> prepared_by)                        -- D04
) STRICT;


-- -----------------------------------------------------------------------------
-- 4. MODULE E — MAINTENANCE ORDERS
-- -----------------------------------------------------------------------------
CREATE TABLE Maintenance_Orders (
    mo_id                     INTEGER PRIMARY KEY,
    mo_number                 TEXT    NOT NULL UNIQUE
                              CHECK (mo_number GLOB 'WO-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
    aircraft_id               INTEGER NOT NULL REFERENCES Aircraft (aircraft_id),
    maintenance_type          TEXT    NOT NULL
                              CHECK (maintenance_type IN ('SCHEDULED', 'UNSCHEDULED', 'MODIFICATION')),
    work_description          TEXT    NOT NULL CHECK (length(work_description) <= 200),
    priority                  TEXT    NOT NULL CHECK (priority IN ('ROUTINE', 'URGENT', 'AOG')),
    responsible_department_id INTEGER NOT NULL REFERENCES Departments (department_id),
    planner_id                INTEGER NOT NULL REFERENCES Employees (employee_id),
    opened_date               TEXT    NOT NULL CHECK (date(opened_date) IS opened_date),
    planned_end_date          TEXT    NOT NULL CHECK (date(planned_end_date) IS planned_end_date),
    actual_end_date           TEXT    CHECK (actual_end_date IS NULL OR date(actual_end_date) IS actual_end_date),
    status                    TEXT    NOT NULL
                              CHECK (status IN ('OPEN', 'IN_PROGRESS', 'ON_HOLD',
                                                'COMPLETED', 'CLOSED', 'CANCELLED')),
    closed_date               TEXT    CHECK (closed_date IS NULL OR date(closed_date) IS closed_date),
    closed_by                 INTEGER REFERENCES Employees (employee_id),
    cancellation_reason       TEXT,
    created_at                TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by                INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at                TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by                INTEGER REFERENCES Employees (employee_id),
    CHECK (planned_end_date >= opened_date),                                         -- M01
    CHECK (actual_end_date IS NULL OR actual_end_date >= opened_date),
    CHECK ((status IN ('COMPLETED', 'CLOSED')) = (actual_end_date IS NOT NULL)),     -- M02
    CHECK ((status = 'CLOSED') = (closed_date IS NOT NULL)),                         -- M03
    CHECK ((status = 'CLOSED') = (closed_by IS NOT NULL)),                           -- M03
    CHECK (closed_date IS NULL OR closed_date >= actual_end_date),                   -- M03
    CHECK ((status = 'CANCELLED') = (cancellation_reason IS NOT NULL))               -- M04
) STRICT;

CREATE TABLE Maintenance_Order_Materials (
    mo_material_id       INTEGER PRIMARY KEY,
    mo_id                INTEGER NOT NULL REFERENCES Maintenance_Orders (mo_id),
    material_id          INTEGER NOT NULL REFERENCES Materials (material_id),
    qty_required         REAL    NOT NULL CHECK (qty_required > 0),
    required_by_date     TEXT    NOT NULL CHECK (date(required_by_date) IS required_by_date),
    created_at           TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id),
    UNIQUE (mo_id, material_id)
) STRICT;

CREATE TABLE Maintenance_Order_Documents (
    mo_document_id       INTEGER PRIMARY KEY,
    mo_id                INTEGER NOT NULL REFERENCES Maintenance_Orders (mo_id),
    revision_id          INTEGER NOT NULL REFERENCES Document_Revisions (revision_id),
    usage_role           TEXT    NOT NULL
                         CHECK (usage_role IN ('WORK_INSTRUCTION', 'TECHNICAL_DATA', 'FORM', 'RECORD')),
    linked_date          TEXT    NOT NULL CHECK (date(linked_date) IS linked_date),
    created_at           TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id),
    UNIQUE (mo_id, revision_id)
) STRICT;


-- -----------------------------------------------------------------------------
-- 5. MODULE D — PURCHASING (needed before incidents, which may cite a PO line)
-- -----------------------------------------------------------------------------
CREATE TABLE Purchase_Orders (
    po_id                INTEGER PRIMARY KEY,
    po_number            TEXT    NOT NULL UNIQUE
                         CHECK (po_number GLOB 'PO-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
    supplier_id          INTEGER NOT NULL REFERENCES Suppliers (supplier_id),
    order_date           TEXT    NOT NULL CHECK (date(order_date) IS order_date),
    urgency              TEXT    NOT NULL CHECK (urgency IN ('ROUTINE', 'URGENT', 'AOG')),
    buyer_id             INTEGER NOT NULL REFERENCES Employees (employee_id),
    cancelled_date       TEXT    CHECK (cancelled_date IS NULL
                                        OR (date(cancelled_date) IS cancelled_date
                                            AND cancelled_date >= order_date)),
    created_at           TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id)
) STRICT;

CREATE TABLE Purchase_Order_Lines (
    po_line_id           INTEGER PRIMARY KEY,
    po_id                INTEGER NOT NULL REFERENCES Purchase_Orders (po_id),
    line_number          INTEGER NOT NULL CHECK (line_number > 0),
    material_id          INTEGER NOT NULL REFERENCES Materials (material_id),
    qty_ordered          REAL    NOT NULL CHECK (qty_ordered > 0),
    unit_price           REAL    NOT NULL CHECK (unit_price >= 0),
    promised_date        TEXT    NOT NULL CHECK (date(promised_date) IS promised_date),
    mo_id                INTEGER REFERENCES Maintenance_Orders (mo_id),
    created_at           TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id),
    UNIQUE (po_id, line_number),
    UNIQUE (po_id, material_id)
) STRICT;


-- -----------------------------------------------------------------------------
-- 6. MODULE A — QUALITY MANAGEMENT
-- -----------------------------------------------------------------------------
CREATE TABLE Incident_Categories (
    category_id            INTEGER PRIMARY KEY,
    category_code          TEXT    NOT NULL UNIQUE CHECK (category_code GLOB '[A-Z][A-Z][A-Z]'),
    category_name_es       TEXT    NOT NULL UNIQUE,
    category_name_en       TEXT    NOT NULL UNIQUE,
    description            TEXT    NOT NULL,
    default_department_id  INTEGER NOT NULL REFERENCES Departments (department_id),
    is_active              INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
) STRICT;

CREATE TABLE Quality_Incidents (
    incident_id               INTEGER PRIMARY KEY,
    incident_number           TEXT    NOT NULL UNIQUE
                              CHECK (incident_number GLOB 'NC-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
    category_id               INTEGER NOT NULL REFERENCES Incident_Categories (category_id),
    severity                  TEXT    NOT NULL
                              CHECK (severity IN ('CRITICAL', 'MAJOR', 'MINOR', 'OBSERVATION')),
    priority                  TEXT    NOT NULL CHECK (priority IN ('P1', 'P2', 'P3')),
    detection_source          TEXT    NOT NULL
                              CHECK (detection_source IN ('DOCUMENT_VERIFICATION', 'STOCK_COUNT',
                                                          'RECEIVING_INSPECTION', 'PRODUCTION',
                                                          'INTERNAL_AUDIT', 'CUSTOMER', 'SUPPLIER')),
    title                     TEXT    NOT NULL CHECK (length(title) <= 120),
    description               TEXT    NOT NULL,
    detected_date             TEXT    NOT NULL CHECK (date(detected_date) IS detected_date),
    detected_by               INTEGER NOT NULL REFERENCES Employees (employee_id),
    responsible_department_id INTEGER NOT NULL REFERENCES Departments (department_id),
    owner_id                  INTEGER NOT NULL REFERENCES Employees (employee_id),
    aircraft_id               INTEGER REFERENCES Aircraft (aircraft_id),
    mo_id                     INTEGER REFERENCES Maintenance_Orders (mo_id),
    revision_id               INTEGER REFERENCES Document_Revisions (revision_id),
    material_id               INTEGER REFERENCES Materials (material_id),
    supplier_id               INTEGER REFERENCES Suppliers (supplier_id),
    po_line_id                INTEGER REFERENCES Purchase_Order_Lines (po_line_id),
    containment_action        TEXT,
    status                    TEXT    NOT NULL
                              CHECK (status IN ('OPEN', 'UNDER_INVESTIGATION', 'ACTION_PLAN',
                                                'IMPLEMENTATION', 'EFFECTIVENESS_CHECK',
                                                'CLOSED', 'CANCELLED')),
    target_closure_date       TEXT    NOT NULL CHECK (date(target_closure_date) IS target_closure_date),
    closed_date               TEXT    CHECK (closed_date IS NULL OR date(closed_date) IS closed_date),
    closed_by                 INTEGER REFERENCES Employees (employee_id),
    closure_summary           TEXT,
    created_at                TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by                INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at                TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by                INTEGER REFERENCES Employees (employee_id),
    CHECK (target_closure_date >= detected_date),
    CHECK (severity NOT IN ('CRITICAL', 'MAJOR') OR containment_action IS NOT NULL),   -- Q03
    CHECK ((status IN ('CLOSED', 'CANCELLED')) = (closed_date IS NOT NULL)),          -- Q01
    CHECK (closed_date IS NULL OR closed_date >= detected_date),                       -- Q01
    CHECK (status <> 'CLOSED' OR (closed_by IS NOT NULL AND closure_summary IS NOT NULL)) -- Q02
) STRICT;

CREATE TABLE Maintenance_Order_Holds (
    hold_id              INTEGER PRIMARY KEY,
    mo_id                INTEGER NOT NULL REFERENCES Maintenance_Orders (mo_id),
    hold_reason          TEXT    NOT NULL CHECK (hold_reason IN ('MATERIAL', 'DOCUMENTATION', 'OTHER')),
    material_id          INTEGER REFERENCES Materials (material_id),
    document_id          INTEGER REFERENCES Documents (document_id),
    incident_id          INTEGER REFERENCES Quality_Incidents (incident_id),
    start_date           TEXT    NOT NULL CHECK (date(start_date) IS start_date),
    end_date             TEXT    CHECK (end_date IS NULL
                                        OR (date(end_date) IS end_date AND end_date >= start_date)),
    comment              TEXT    NOT NULL,
    raised_by            INTEGER NOT NULL REFERENCES Employees (employee_id),
    created_at           TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id),
    CHECK (hold_reason <> 'MATERIAL' OR material_id IS NOT NULL),                    -- M07
    CHECK (hold_reason <> 'DOCUMENTATION' OR document_id IS NOT NULL)                -- M07
) STRICT;

CREATE TABLE Document_Verifications (
    verification_id         INTEGER PRIMARY KEY,
    verification_number     TEXT    NOT NULL UNIQUE
                            CHECK (verification_number GLOB 'DV-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
    revision_id             INTEGER NOT NULL REFERENCES Document_Revisions (revision_id),
    mo_id                   INTEGER REFERENCES Maintenance_Orders (mo_id),
    verification_type       TEXT    NOT NULL
                            CHECK (verification_type IN ('PERIODIC_REVIEW', 'PRE_USE_CHECK',
                                                         'RECORD_VS_SOURCE', 'INTERNAL_AUDIT')),
    verification_date       TEXT    NOT NULL CHECK (date(verification_date) IS verification_date),
    verified_by             INTEGER NOT NULL REFERENCES Employees (employee_id),
    result                  TEXT    NOT NULL
                            CHECK (result IN ('CONFORM', 'MINOR_DISCREPANCY', 'NON_CONFORM')),
    discrepancy_description TEXT,
    incident_id             INTEGER REFERENCES Quality_Incidents (incident_id),
    created_at              TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by              INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at              TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by              INTEGER REFERENCES Employees (employee_id),
    CHECK (result = 'CONFORM' OR discrepancy_description IS NOT NULL)                 -- D09
) STRICT;

CREATE TABLE Root_Cause_Analyses (
    rca_id               INTEGER PRIMARY KEY,
    incident_id          INTEGER NOT NULL UNIQUE REFERENCES Quality_Incidents (incident_id),
    method               TEXT    NOT NULL
                         CHECK (method IN ('FIVE_WHYS', 'ISHIKAWA', 'FIVE_WHYS_AND_ISHIKAWA')),
    ishikawa_category    TEXT    CHECK (ishikawa_category IS NULL
                                        OR ishikawa_category IN ('MANPOWER', 'METHOD', 'MATERIAL',
                                                                 'MACHINE', 'MEASUREMENT', 'ENVIRONMENT')),
    why_1                TEXT,
    why_2                TEXT,
    why_3                TEXT,
    why_4                TEXT,
    why_5                TEXT,
    root_cause_statement TEXT    NOT NULL,
    analysis_date        TEXT    NOT NULL CHECK (date(analysis_date) IS analysis_date),
    analyzed_by          INTEGER NOT NULL REFERENCES Employees (employee_id),
    created_at           TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id),
    CHECK (method = 'FIVE_WHYS' OR ishikawa_category IS NOT NULL),                    -- Q11
    CHECK (method = 'ISHIKAWA' OR why_1 IS NOT NULL),                                 -- Q10
    CHECK (why_2 IS NULL OR why_1 IS NOT NULL),                                       -- Q10 (no gaps)
    CHECK (why_3 IS NULL OR why_2 IS NOT NULL),
    CHECK (why_4 IS NULL OR why_3 IS NOT NULL),
    CHECK (why_5 IS NULL OR why_4 IS NOT NULL)
) STRICT;


-- -----------------------------------------------------------------------------
-- 7. MODULE B — CORRECTIVE AND PREVENTIVE ACTIONS (CAPA)
-- -----------------------------------------------------------------------------
CREATE TABLE CAPA_Actions (
    action_id                INTEGER PRIMARY KEY,
    action_number            TEXT    NOT NULL UNIQUE
                             CHECK (action_number GLOB '[CP]A-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
    action_type              TEXT    NOT NULL CHECK (action_type IN ('CORRECTIVE', 'PREVENTIVE')),
    origin                   TEXT    NOT NULL
                             CHECK (origin IN ('INCIDENT', 'TREND_ANALYSIS', 'INTERNAL_AUDIT')),
    incident_id              INTEGER REFERENCES Quality_Incidents (incident_id),
    parent_action_id         INTEGER REFERENCES CAPA_Actions (action_id),
    title                    TEXT    NOT NULL CHECK (length(title) <= 120),
    description              TEXT    NOT NULL,
    responsible_id           INTEGER NOT NULL REFERENCES Employees (employee_id),
    department_id            INTEGER NOT NULL REFERENCES Departments (department_id),
    created_date             TEXT    NOT NULL CHECK (date(created_date) IS created_date),
    original_due_date        TEXT    NOT NULL CHECK (date(original_due_date) IS original_due_date),
    due_date                 TEXT    NOT NULL CHECK (date(due_date) IS due_date),
    completed_date           TEXT    CHECK (completed_date IS NULL OR date(completed_date) IS completed_date),
    status                   TEXT    NOT NULL
                             CHECK (status IN ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CLOSED', 'CANCELLED')),
    effectiveness_check_date TEXT    CHECK (effectiveness_check_date IS NULL
                                            OR date(effectiveness_check_date) IS effectiveness_check_date),
    effectiveness_result     TEXT    CHECK (effectiveness_result IS NULL
                                            OR effectiveness_result IN ('EFFECTIVE', 'NOT_EFFECTIVE')),
    effectiveness_comment    TEXT,
    verified_by              INTEGER REFERENCES Employees (employee_id),
    closed_date              TEXT    CHECK (closed_date IS NULL OR date(closed_date) IS closed_date),
    cancellation_reason      TEXT,
    created_at               TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by               INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at               TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by               INTEGER REFERENCES Employees (employee_id),
    CHECK ((action_type = 'CORRECTIVE' AND action_number GLOB 'CA-*')
        OR (action_type = 'PREVENTIVE' AND action_number GLOB 'PA-*')),              -- C02
    CHECK (action_type <> 'CORRECTIVE' OR incident_id IS NOT NULL),                   -- C01
    CHECK ((origin = 'INCIDENT') = (incident_id IS NOT NULL)),                        -- C01
    CHECK (original_due_date >= created_date),                                        -- C03
    CHECK (due_date >= original_due_date),                                            -- C09
    CHECK (completed_date IS NULL OR completed_date >= created_date),                 -- C06
    CHECK (status NOT IN ('COMPLETED', 'CLOSED') OR completed_date IS NOT NULL),
    CHECK (effectiveness_check_date IS NULL
           OR (completed_date IS NOT NULL AND effectiveness_check_date >= completed_date)), -- C06
    CHECK (status <> 'CLOSED'
           OR (effectiveness_result IS NOT NULL
               AND effectiveness_check_date IS NOT NULL
               AND verified_by IS NOT NULL)),                                         -- C04
    CHECK (verified_by IS NULL OR verified_by <> responsible_id),                     -- C05
    CHECK ((status IN ('CLOSED', 'CANCELLED')) = (closed_date IS NOT NULL)),
    CHECK (closed_date IS NULL OR closed_date >= created_date),
    CHECK (closed_date IS NULL OR effectiveness_check_date IS NULL
           OR closed_date >= effectiveness_check_date),                               -- C06
    CHECK ((status = 'CANCELLED') = (cancellation_reason IS NOT NULL))
) STRICT;

CREATE TABLE CAPA_Progress_Updates (
    update_id            INTEGER PRIMARY KEY,
    action_id            INTEGER NOT NULL REFERENCES CAPA_Actions (action_id),
    update_date          TEXT    NOT NULL CHECK (date(update_date) IS update_date),
    progress_pct         INTEGER NOT NULL CHECK (progress_pct BETWEEN 0 AND 100),
    comment              TEXT    NOT NULL,
    created_at           TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER NOT NULL REFERENCES Employees (employee_id)   -- who reported the progress
) STRICT;

-- Lessons learned (added in Phase 9). A lesson is what the organisation learned
-- from a closed and verified action, and the change it recommends. The
-- non-conformity is reached through the action (it is not stored twice).
-- General quality-management practice; not presented as a regulatory requirement.
-- Life cycle: PROPOSED -> APPROVED -> INCORPORATED, or PROPOSED -> REJECTED.
CREATE TABLE Lessons_Learned (
    lesson_id                INTEGER PRIMARY KEY,
    lesson_number            TEXT    NOT NULL UNIQUE
                             CHECK (lesson_number GLOB 'LL-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
    action_id                INTEGER NOT NULL REFERENCES CAPA_Actions (action_id),
    title                    TEXT    NOT NULL CHECK (length(title) <= 120),
    lesson_text              TEXT    NOT NULL,        -- what was learned
    recommendation           TEXT    NOT NULL,        -- what should change
    department_id            INTEGER NOT NULL REFERENCES Departments (department_id),  -- owner of the lesson
    scope                    TEXT    NOT NULL CHECK (scope IN ('DEPARTMENT', 'COMPANY')),
    status                   TEXT    NOT NULL
                             CHECK (status IN ('PROPOSED', 'APPROVED', 'INCORPORATED', 'REJECTED')),
    proposed_date            TEXT    NOT NULL CHECK (date(proposed_date) IS proposed_date),
    proposed_by              INTEGER NOT NULL REFERENCES Employees (employee_id),
    approved_date            TEXT    CHECK (approved_date IS NULL OR date(approved_date) IS approved_date),
    approved_by              INTEGER REFERENCES Employees (employee_id),
    rejected_date            TEXT    CHECK (rejected_date IS NULL OR date(rejected_date) IS rejected_date),
    rejected_by              INTEGER REFERENCES Employees (employee_id),
    rejection_reason         TEXT,
    incorporated_date        TEXT    CHECK (incorporated_date IS NULL
                                            OR date(incorporated_date) IS incorporated_date),
    incorporated_revision_id INTEGER REFERENCES Document_Revisions (revision_id),
    created_at               TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by               INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at               TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by               INTEGER REFERENCES Employees (employee_id),
    -- L03: the status matches the decision recorded
    CHECK ((status IN ('APPROVED', 'INCORPORATED')) = (approved_by IS NOT NULL)),
    CHECK ((approved_by IS NULL) = (approved_date IS NULL)),
    CHECK ((status = 'REJECTED') = (rejected_by IS NOT NULL)),
    CHECK ((rejected_by IS NULL) = (rejected_date IS NULL)),
    CHECK ((status = 'REJECTED') = (rejection_reason IS NOT NULL)),                 -- reason is mandatory
    CHECK ((status = 'INCORPORATED') = (incorporated_revision_id IS NOT NULL)),
    CHECK ((incorporated_revision_id IS NULL) = (incorporated_date IS NULL)),
    -- L02: the decision is taken by someone other than the proposer
    CHECK (approved_by IS NULL OR approved_by <> proposed_by),
    CHECK (rejected_by IS NULL OR rejected_by <> proposed_by),
    -- L04: proposal <= decision <= incorporation
    CHECK (approved_date IS NULL OR approved_date >= proposed_date),
    CHECK (rejected_date IS NULL OR rejected_date >= proposed_date),
    CHECK (incorporated_date IS NULL OR incorporated_date >= approved_date)
) STRICT;


-- -----------------------------------------------------------------------------
-- 8. MODULE D — STOCK COUNTS AND INVENTORY MOVEMENTS
-- -----------------------------------------------------------------------------
CREATE TABLE Stock_Counts (
    count_id             INTEGER PRIMARY KEY,
    count_number         TEXT    NOT NULL UNIQUE
                         CHECK (count_number GLOB 'SC-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
    material_id          INTEGER NOT NULL REFERENCES Materials (material_id),
    count_datetime       TEXT    NOT NULL CHECK (datetime(count_datetime) IS count_datetime),
    count_type           TEXT    NOT NULL CHECK (count_type IN ('OPENING', 'CYCLE', 'ANNUAL', 'AD_HOC')),  -- OPENING = go-live balance
    system_qty           REAL    NOT NULL CHECK (system_qty >= 0),
    counted_qty          REAL    NOT NULL CHECK (counted_qty >= 0),
    counted_by           INTEGER NOT NULL REFERENCES Employees (employee_id),
    comment              TEXT,
    created_at           TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by           INTEGER NOT NULL REFERENCES Employees (employee_id),
    updated_at           TEXT    CHECK (updated_at IS NULL OR datetime(updated_at) IS updated_at),
    updated_by           INTEGER REFERENCES Employees (employee_id),
    CHECK (counted_qty = system_qty OR comment IS NOT NULL)
) STRICT;

CREATE TABLE Inventory_Movements (
    movement_id            INTEGER PRIMARY KEY,
    movement_number        TEXT    NOT NULL UNIQUE
                           CHECK (movement_number GLOB 'MV-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9]'),
    movement_datetime      TEXT    NOT NULL CHECK (datetime(movement_datetime) IS movement_datetime),
    material_id            INTEGER NOT NULL REFERENCES Materials (material_id),
    movement_type          TEXT    NOT NULL
                           CHECK (movement_type IN ('RECEIPT', 'INSPECTION_RELEASE', 'RESERVE',
                                                    'UNRESERVE', 'ISSUE', 'RETURN', 'BLOCK',
                                                    'UNBLOCK', 'NONCONFORM', 'SCRAP',
                                                    'ADJUSTMENT_IN', 'ADJUSTMENT_OUT')),
    quantity               REAL    NOT NULL CHECK (quantity > 0),
    from_bucket            TEXT    CHECK (from_bucket IS NULL
                                          OR from_bucket IN ('QUARANTINE', 'AVAILABLE', 'RESERVED',
                                                             'BLOCKED', 'NON_CONFORMING')),
    to_bucket              TEXT    CHECK (to_bucket IS NULL
                                          OR to_bucket IN ('QUARANTINE', 'AVAILABLE', 'RESERVED',
                                                           'BLOCKED', 'NON_CONFORMING')),
    mo_id                  INTEGER REFERENCES Maintenance_Orders (mo_id),
    po_line_id             INTEGER REFERENCES Purchase_Order_Lines (po_line_id),
    incident_id            INTEGER REFERENCES Quality_Incidents (incident_id),
    stock_count_id         INTEGER REFERENCES Stock_Counts (count_id),
    lot_number             TEXT,
    serial_number          TEXT,
    certificate_ref        TEXT,
    shelf_life_expiry_date TEXT    CHECK (shelf_life_expiry_date IS NULL
                                          OR date(shelf_life_expiry_date) IS shelf_life_expiry_date),
    reason                 TEXT,
    performed_by           INTEGER NOT NULL REFERENCES Employees (employee_id),
    created_at             TEXT    NOT NULL CHECK (datetime(created_at) IS created_at),
    created_by             INTEGER NOT NULL REFERENCES Employees (employee_id),
    -- I01: each movement type moves stock between its own pair of buckets
    CHECK (
           (movement_type = 'RECEIPT'            AND from_bucket IS NULL           AND to_bucket = 'QUARANTINE')
        OR (movement_type = 'INSPECTION_RELEASE' AND from_bucket = 'QUARANTINE'    AND to_bucket = 'AVAILABLE')
        OR (movement_type = 'RESERVE'            AND from_bucket = 'AVAILABLE'     AND to_bucket = 'RESERVED')
        OR (movement_type = 'UNRESERVE'          AND from_bucket = 'RESERVED'      AND to_bucket = 'AVAILABLE')
        OR (movement_type = 'ISSUE'              AND from_bucket = 'RESERVED'      AND to_bucket IS NULL)
        OR (movement_type = 'RETURN'             AND from_bucket IS NULL           AND to_bucket = 'QUARANTINE')
        OR (movement_type = 'BLOCK'              AND from_bucket = 'AVAILABLE'     AND to_bucket = 'BLOCKED')
        OR (movement_type = 'UNBLOCK'            AND from_bucket = 'BLOCKED'       AND to_bucket = 'AVAILABLE')
        OR (movement_type = 'NONCONFORM'         AND from_bucket IN ('QUARANTINE', 'AVAILABLE', 'BLOCKED')
                                                 AND to_bucket = 'NON_CONFORMING')
        OR (movement_type = 'SCRAP'              AND from_bucket = 'NON_CONFORMING' AND to_bucket IS NULL)
        OR (movement_type = 'ADJUSTMENT_IN'      AND from_bucket IS NULL           AND to_bucket = 'AVAILABLE')
        OR (movement_type = 'ADJUSTMENT_OUT'     AND from_bucket = 'AVAILABLE'     AND to_bucket IS NULL)
    ),
    -- I02: mandatory references for each movement type
    CHECK (movement_type NOT IN ('RESERVE', 'UNRESERVE', 'ISSUE', 'RETURN') OR mo_id IS NOT NULL),
    CHECK (movement_type <> 'RECEIPT' OR po_line_id IS NOT NULL),
    CHECK (movement_type NOT IN ('RECEIPT', 'ISSUE', 'RETURN') OR lot_number IS NOT NULL),
    CHECK (movement_type NOT IN ('NONCONFORM', 'SCRAP') OR incident_id IS NOT NULL),
    CHECK (movement_type NOT IN ('ADJUSTMENT_IN', 'ADJUSTMENT_OUT') OR stock_count_id IS NOT NULL),
    CHECK (movement_type NOT IN ('BLOCK', 'UNBLOCK', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT') OR reason IS NOT NULL)
) STRICT;


-- -----------------------------------------------------------------------------
-- 9. MODULE F — AUDIT LOG (written by triggers; never updated or deleted)
-- -----------------------------------------------------------------------------
CREATE TABLE Audit_Log (
    audit_id             INTEGER PRIMARY KEY,
    event_datetime       TEXT    NOT NULL CHECK (datetime(event_datetime) IS event_datetime),
    table_name           TEXT    NOT NULL
                         CHECK (table_name IN ('Departments', 'Employees', 'Customers', 'Aircraft',
                                               'Suppliers', 'Materials', 'Documents',
                                               'Document_Revisions', 'Maintenance_Orders',
                                               'Maintenance_Order_Materials',
                                               'Maintenance_Order_Documents', 'Purchase_Orders',
                                               'Purchase_Order_Lines', 'Quality_Incidents',
                                               'Maintenance_Order_Holds', 'Document_Verifications',
                                               'Root_Cause_Analyses', 'CAPA_Actions',
                                               'CAPA_Progress_Updates', 'Lessons_Learned',
                                               'Stock_Counts', 'Inventory_Movements')),
    record_id            INTEGER NOT NULL,
    action               TEXT    NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    field_name           TEXT,
    old_value            TEXT,
    new_value            TEXT,
    changed_by           INTEGER REFERENCES Employees (employee_id),
    source               TEXT    NOT NULL DEFAULT 'TRIGGER' CHECK (source IN ('TRIGGER', 'SYSTEM')),
    CHECK (action <> 'UPDATE' OR field_name IS NOT NULL)
) STRICT;
