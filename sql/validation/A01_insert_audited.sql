-- rule: A01
-- title: Every operational record has its INSERT event in the audit log
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT x.registration AS record_ref, 'Aircraft: creation not recorded in Audit_Log' AS detail FROM Aircraft x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Aircraft' AND a.record_id = x.aircraft_id AND a.action = 'INSERT')
UNION ALL
SELECT x.action_number AS record_ref, 'CAPA_Actions: creation not recorded in Audit_Log' AS detail FROM CAPA_Actions x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'CAPA_Actions' AND a.record_id = x.action_id AND a.action = 'INSERT')
UNION ALL
SELECT 'CAPA_Progress_Updates #' || x.update_id AS record_ref, 'CAPA_Progress_Updates: creation not recorded in Audit_Log' AS detail FROM CAPA_Progress_Updates x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'CAPA_Progress_Updates' AND a.record_id = x.update_id AND a.action = 'INSERT')
UNION ALL
SELECT x.customer_code AS record_ref, 'Customers: creation not recorded in Audit_Log' AS detail FROM Customers x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Customers' AND a.record_id = x.customer_id AND a.action = 'INSERT')
UNION ALL
SELECT x.department_code AS record_ref, 'Departments: creation not recorded in Audit_Log' AS detail FROM Departments x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Departments' AND a.record_id = x.department_id AND a.action = 'INSERT')
UNION ALL
SELECT 'Document_Revisions #' || x.revision_id AS record_ref, 'Document_Revisions: creation not recorded in Audit_Log' AS detail FROM Document_Revisions x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Document_Revisions' AND a.record_id = x.revision_id AND a.action = 'INSERT')
UNION ALL
SELECT x.verification_number AS record_ref, 'Document_Verifications: creation not recorded in Audit_Log' AS detail FROM Document_Verifications x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Document_Verifications' AND a.record_id = x.verification_id AND a.action = 'INSERT')
UNION ALL
SELECT x.document_code AS record_ref, 'Documents: creation not recorded in Audit_Log' AS detail FROM Documents x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Documents' AND a.record_id = x.document_id AND a.action = 'INSERT')
UNION ALL
SELECT x.employee_code AS record_ref, 'Employees: creation not recorded in Audit_Log' AS detail FROM Employees x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Employees' AND a.record_id = x.employee_id AND a.action = 'INSERT')
UNION ALL
SELECT x.movement_number AS record_ref, 'Inventory_Movements: creation not recorded in Audit_Log' AS detail FROM Inventory_Movements x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Inventory_Movements' AND a.record_id = x.movement_id AND a.action = 'INSERT')
UNION ALL
SELECT 'Maintenance_Order_Documents #' || x.mo_document_id AS record_ref, 'Maintenance_Order_Documents: creation not recorded in Audit_Log' AS detail FROM Maintenance_Order_Documents x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Maintenance_Order_Documents' AND a.record_id = x.mo_document_id AND a.action = 'INSERT')
UNION ALL
SELECT 'Maintenance_Order_Holds #' || x.hold_id AS record_ref, 'Maintenance_Order_Holds: creation not recorded in Audit_Log' AS detail FROM Maintenance_Order_Holds x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Maintenance_Order_Holds' AND a.record_id = x.hold_id AND a.action = 'INSERT')
UNION ALL
SELECT 'Maintenance_Order_Materials #' || x.mo_material_id AS record_ref, 'Maintenance_Order_Materials: creation not recorded in Audit_Log' AS detail FROM Maintenance_Order_Materials x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Maintenance_Order_Materials' AND a.record_id = x.mo_material_id AND a.action = 'INSERT')
UNION ALL
SELECT x.mo_number AS record_ref, 'Maintenance_Orders: creation not recorded in Audit_Log' AS detail FROM Maintenance_Orders x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Maintenance_Orders' AND a.record_id = x.mo_id AND a.action = 'INSERT')
UNION ALL
SELECT x.part_number AS record_ref, 'Materials: creation not recorded in Audit_Log' AS detail FROM Materials x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Materials' AND a.record_id = x.material_id AND a.action = 'INSERT')
UNION ALL
SELECT 'Purchase_Order_Lines #' || x.po_line_id AS record_ref, 'Purchase_Order_Lines: creation not recorded in Audit_Log' AS detail FROM Purchase_Order_Lines x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Purchase_Order_Lines' AND a.record_id = x.po_line_id AND a.action = 'INSERT')
UNION ALL
SELECT x.po_number AS record_ref, 'Purchase_Orders: creation not recorded in Audit_Log' AS detail FROM Purchase_Orders x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Purchase_Orders' AND a.record_id = x.po_id AND a.action = 'INSERT')
UNION ALL
SELECT x.incident_number AS record_ref, 'Quality_Incidents: creation not recorded in Audit_Log' AS detail FROM Quality_Incidents x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Quality_Incidents' AND a.record_id = x.incident_id AND a.action = 'INSERT')
UNION ALL
SELECT 'Root_Cause_Analyses #' || x.rca_id AS record_ref, 'Root_Cause_Analyses: creation not recorded in Audit_Log' AS detail FROM Root_Cause_Analyses x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Root_Cause_Analyses' AND a.record_id = x.rca_id AND a.action = 'INSERT')
UNION ALL
SELECT x.count_number AS record_ref, 'Stock_Counts: creation not recorded in Audit_Log' AS detail FROM Stock_Counts x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Stock_Counts' AND a.record_id = x.count_id AND a.action = 'INSERT')
UNION ALL
SELECT x.supplier_code AS record_ref, 'Suppliers: creation not recorded in Audit_Log' AS detail FROM Suppliers x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Suppliers' AND a.record_id = x.supplier_id AND a.action = 'INSERT')
UNION ALL
SELECT x.lesson_number AS record_ref, 'Lessons_Learned: creation not recorded in Audit_Log' AS detail FROM Lessons_Learned x
WHERE NOT EXISTS (SELECT 1 FROM Audit_Log a WHERE a.table_name = 'Lessons_Learned' AND a.record_id = x.lesson_id AND a.action = 'INSERT');
