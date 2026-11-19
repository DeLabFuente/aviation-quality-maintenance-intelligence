-- =============================================================================
-- AQMI — Aviation Quality & Maintenance Intelligence
-- File:    sql/schema/02_indexes.sql
-- Purpose: Indexes. SQLite does NOT index foreign keys automatically, so every
--          foreign key gets its own index (unless it already leads a UNIQUE
--          constraint). Also: two partial unique indexes that enforce business
--          rules, and indexes on the dates used for time analysis.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. Partial unique indexes (business rules)
-- -----------------------------------------------------------------------------

-- D01: a document has at most one CURRENT revision
CREATE UNIQUE INDEX ux_document_revisions_one_current
    ON Document_Revisions (document_id)
    WHERE lifecycle_status = 'CURRENT';

-- M06: at most one active hold per reason on each maintenance order
CREATE UNIQUE INDEX ux_mo_holds_one_active_per_reason
    ON Maintenance_Order_Holds (mo_id, hold_reason)
    WHERE end_date IS NULL;


-- -----------------------------------------------------------------------------
-- 2. Foreign-key indexes
-- -----------------------------------------------------------------------------

-- Master data
CREATE INDEX ix_employees_department            ON Employees (department_id);
CREATE INDEX ix_aircraft_customer               ON Aircraft (customer_id);
CREATE INDEX ix_materials_preferred_supplier    ON Materials (preferred_supplier_id);

-- Documents
CREATE INDEX ix_documents_owner_department      ON Documents (owner_department_id);
CREATE INDEX ix_documents_aircraft              ON Documents (aircraft_id);
CREATE INDEX ix_doc_revisions_prepared_by       ON Document_Revisions (prepared_by);
CREATE INDEX ix_doc_revisions_approved_by       ON Document_Revisions (approved_by);

-- Maintenance orders
CREATE INDEX ix_mo_aircraft                     ON Maintenance_Orders (aircraft_id);
CREATE INDEX ix_mo_responsible_department       ON Maintenance_Orders (responsible_department_id);
CREATE INDEX ix_mo_planner                      ON Maintenance_Orders (planner_id);
CREATE INDEX ix_mo_closed_by                    ON Maintenance_Orders (closed_by);
CREATE INDEX ix_mo_materials_material           ON Maintenance_Order_Materials (material_id);
CREATE INDEX ix_mo_documents_revision           ON Maintenance_Order_Documents (revision_id);
CREATE INDEX ix_mo_holds_mo                     ON Maintenance_Order_Holds (mo_id);
CREATE INDEX ix_mo_holds_material               ON Maintenance_Order_Holds (material_id);
CREATE INDEX ix_mo_holds_document               ON Maintenance_Order_Holds (document_id);
CREATE INDEX ix_mo_holds_incident               ON Maintenance_Order_Holds (incident_id);
CREATE INDEX ix_mo_holds_raised_by              ON Maintenance_Order_Holds (raised_by);

-- Purchasing
CREATE INDEX ix_po_supplier                     ON Purchase_Orders (supplier_id);
CREATE INDEX ix_po_buyer                        ON Purchase_Orders (buyer_id);
CREATE INDEX ix_po_lines_material               ON Purchase_Order_Lines (material_id);
CREATE INDEX ix_po_lines_mo                     ON Purchase_Order_Lines (mo_id);

-- Quality incidents
CREATE INDEX ix_categories_default_department   ON Incident_Categories (default_department_id);
CREATE INDEX ix_incidents_category              ON Quality_Incidents (category_id);
CREATE INDEX ix_incidents_detected_by           ON Quality_Incidents (detected_by);
CREATE INDEX ix_incidents_responsible_dept      ON Quality_Incidents (responsible_department_id);
CREATE INDEX ix_incidents_owner                 ON Quality_Incidents (owner_id);
CREATE INDEX ix_incidents_aircraft              ON Quality_Incidents (aircraft_id);
CREATE INDEX ix_incidents_mo                    ON Quality_Incidents (mo_id);
CREATE INDEX ix_incidents_revision              ON Quality_Incidents (revision_id);
CREATE INDEX ix_incidents_material              ON Quality_Incidents (material_id);
CREATE INDEX ix_incidents_supplier              ON Quality_Incidents (supplier_id);
CREATE INDEX ix_incidents_po_line               ON Quality_Incidents (po_line_id);
CREATE INDEX ix_incidents_closed_by             ON Quality_Incidents (closed_by);

-- Document verifications and root-cause analyses
CREATE INDEX ix_verifications_revision          ON Document_Verifications (revision_id);
CREATE INDEX ix_verifications_mo                ON Document_Verifications (mo_id);
CREATE INDEX ix_verifications_verified_by       ON Document_Verifications (verified_by);
CREATE INDEX ix_verifications_incident          ON Document_Verifications (incident_id);
CREATE INDEX ix_rca_analyzed_by                 ON Root_Cause_Analyses (analyzed_by);

-- CAPA
CREATE INDEX ix_capa_incident                   ON CAPA_Actions (incident_id);
CREATE INDEX ix_capa_parent                     ON CAPA_Actions (parent_action_id);
CREATE INDEX ix_capa_responsible                ON CAPA_Actions (responsible_id);
CREATE INDEX ix_capa_department                 ON CAPA_Actions (department_id);
CREATE INDEX ix_capa_verified_by                ON CAPA_Actions (verified_by);
CREATE INDEX ix_capa_updates_action             ON CAPA_Progress_Updates (action_id);

-- Lessons learned (Phase 9)
CREATE INDEX ix_lessons_action                  ON Lessons_Learned (action_id);
CREATE INDEX ix_lessons_department              ON Lessons_Learned (department_id);
CREATE INDEX ix_lessons_proposed_by             ON Lessons_Learned (proposed_by);
CREATE INDEX ix_lessons_approved_by             ON Lessons_Learned (approved_by);
CREATE INDEX ix_lessons_rejected_by             ON Lessons_Learned (rejected_by);
CREATE INDEX ix_lessons_revision                ON Lessons_Learned (incorporated_revision_id);

-- Stock counts and inventory movements
CREATE INDEX ix_stock_counts_material           ON Stock_Counts (material_id, count_datetime);
CREATE INDEX ix_stock_counts_counted_by         ON Stock_Counts (counted_by);
CREATE INDEX ix_movements_material_datetime     ON Inventory_Movements (material_id, movement_datetime);
CREATE INDEX ix_movements_mo_material           ON Inventory_Movements (mo_id, material_id);
CREATE INDEX ix_movements_po_line               ON Inventory_Movements (po_line_id);
CREATE INDEX ix_movements_incident              ON Inventory_Movements (incident_id);
CREATE INDEX ix_movements_stock_count           ON Inventory_Movements (stock_count_id);
CREATE INDEX ix_movements_performed_by          ON Inventory_Movements (performed_by);

-- Audit log
CREATE INDEX ix_audit_record                    ON Audit_Log (table_name, record_id, event_datetime);
CREATE INDEX ix_audit_changed_by                ON Audit_Log (changed_by);


-- -----------------------------------------------------------------------------
-- 3. Date indexes for time analysis
-- -----------------------------------------------------------------------------
CREATE INDEX ix_incidents_detected_date         ON Quality_Incidents (detected_date);
CREATE INDEX ix_mo_opened_date                  ON Maintenance_Orders (opened_date);
CREATE INDEX ix_capa_due_date                   ON CAPA_Actions (due_date);
CREATE INDEX ix_verifications_date              ON Document_Verifications (verification_date);
CREATE INDEX ix_audit_event_datetime            ON Audit_Log (event_datetime);

-- Note: the audit columns created_by / updated_by are not indexed. They are
-- rarely used to filter, and indexing them would slow down every insert.
