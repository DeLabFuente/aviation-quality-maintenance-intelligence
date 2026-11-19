-- rule: A05
-- title: Every audit event points to an existing record
-- severity: CRITICAL
-- type: E
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Aircraft #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Aircraft' AND NOT EXISTS (SELECT 1 FROM Aircraft x WHERE x.aircraft_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'CAPA_Actions #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'CAPA_Actions' AND NOT EXISTS (SELECT 1 FROM CAPA_Actions x WHERE x.action_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'CAPA_Progress_Updates #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'CAPA_Progress_Updates' AND NOT EXISTS (SELECT 1 FROM CAPA_Progress_Updates x WHERE x.update_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Customers #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Customers' AND NOT EXISTS (SELECT 1 FROM Customers x WHERE x.customer_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Departments #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Departments' AND NOT EXISTS (SELECT 1 FROM Departments x WHERE x.department_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Document_Revisions #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Document_Revisions' AND NOT EXISTS (SELECT 1 FROM Document_Revisions x WHERE x.revision_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Document_Verifications #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Document_Verifications' AND NOT EXISTS (SELECT 1 FROM Document_Verifications x WHERE x.verification_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Documents #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Documents' AND NOT EXISTS (SELECT 1 FROM Documents x WHERE x.document_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Employees #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Employees' AND NOT EXISTS (SELECT 1 FROM Employees x WHERE x.employee_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Inventory_Movements #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Inventory_Movements' AND NOT EXISTS (SELECT 1 FROM Inventory_Movements x WHERE x.movement_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Maintenance_Order_Documents #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Maintenance_Order_Documents' AND NOT EXISTS (SELECT 1 FROM Maintenance_Order_Documents x WHERE x.mo_document_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Maintenance_Order_Holds #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Maintenance_Order_Holds' AND NOT EXISTS (SELECT 1 FROM Maintenance_Order_Holds x WHERE x.hold_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Maintenance_Order_Materials #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Maintenance_Order_Materials' AND NOT EXISTS (SELECT 1 FROM Maintenance_Order_Materials x WHERE x.mo_material_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Maintenance_Orders #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Maintenance_Orders' AND NOT EXISTS (SELECT 1 FROM Maintenance_Orders x WHERE x.mo_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Materials #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Materials' AND NOT EXISTS (SELECT 1 FROM Materials x WHERE x.material_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Purchase_Order_Lines #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Purchase_Order_Lines' AND NOT EXISTS (SELECT 1 FROM Purchase_Order_Lines x WHERE x.po_line_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Purchase_Orders #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Purchase_Orders' AND NOT EXISTS (SELECT 1 FROM Purchase_Orders x WHERE x.po_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Quality_Incidents #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Quality_Incidents' AND NOT EXISTS (SELECT 1 FROM Quality_Incidents x WHERE x.incident_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Root_Cause_Analyses #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Root_Cause_Analyses' AND NOT EXISTS (SELECT 1 FROM Root_Cause_Analyses x WHERE x.rca_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Stock_Counts #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Stock_Counts' AND NOT EXISTS (SELECT 1 FROM Stock_Counts x WHERE x.count_id = a.record_id)
UNION ALL
SELECT 'Audit_Log #' || a.audit_id AS record_ref, 'Suppliers #' || a.record_id || ' does not exist' AS detail FROM Audit_Log a
WHERE a.table_name = 'Suppliers' AND NOT EXISTS (SELECT 1 FROM Suppliers x WHERE x.supplier_id = a.record_id);
