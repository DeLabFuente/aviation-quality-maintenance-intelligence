-- rule: G10
-- title: Operational records identify who created them
-- severity: CRITICAL
-- type: E
-- enforced_by: NOT NULL + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT document_code AS record_ref, 'Documents: created_by is empty' AS detail FROM Documents WHERE created_by IS NULL
UNION ALL
SELECT 'Document_Revisions #' || revision_id AS record_ref, 'Document_Revisions: created_by is empty' AS detail FROM Document_Revisions WHERE created_by IS NULL
UNION ALL
SELECT mo_number AS record_ref, 'Maintenance_Orders: created_by is empty' AS detail FROM Maintenance_Orders WHERE created_by IS NULL
UNION ALL
SELECT 'Maintenance_Order_Materials #' || mo_material_id AS record_ref, 'Maintenance_Order_Materials: created_by is empty' AS detail FROM Maintenance_Order_Materials WHERE created_by IS NULL
UNION ALL
SELECT 'Maintenance_Order_Documents #' || mo_document_id AS record_ref, 'Maintenance_Order_Documents: created_by is empty' AS detail FROM Maintenance_Order_Documents WHERE created_by IS NULL
UNION ALL
SELECT 'Maintenance_Order_Holds #' || hold_id AS record_ref, 'Maintenance_Order_Holds: created_by is empty' AS detail FROM Maintenance_Order_Holds WHERE created_by IS NULL
UNION ALL
SELECT po_number AS record_ref, 'Purchase_Orders: created_by is empty' AS detail FROM Purchase_Orders WHERE created_by IS NULL
UNION ALL
SELECT 'Purchase_Order_Lines #' || po_line_id AS record_ref, 'Purchase_Order_Lines: created_by is empty' AS detail FROM Purchase_Order_Lines WHERE created_by IS NULL
UNION ALL
SELECT incident_number AS record_ref, 'Quality_Incidents: created_by is empty' AS detail FROM Quality_Incidents WHERE created_by IS NULL
UNION ALL
SELECT verification_number AS record_ref, 'Document_Verifications: created_by is empty' AS detail FROM Document_Verifications WHERE created_by IS NULL
UNION ALL
SELECT 'Root_Cause_Analyses #' || rca_id AS record_ref, 'Root_Cause_Analyses: created_by is empty' AS detail FROM Root_Cause_Analyses WHERE created_by IS NULL
UNION ALL
SELECT action_number AS record_ref, 'CAPA_Actions: created_by is empty' AS detail FROM CAPA_Actions WHERE created_by IS NULL
UNION ALL
SELECT 'CAPA_Progress_Updates #' || update_id AS record_ref, 'CAPA_Progress_Updates: created_by is empty' AS detail FROM CAPA_Progress_Updates WHERE created_by IS NULL
UNION ALL
SELECT count_number AS record_ref, 'Stock_Counts: created_by is empty' AS detail FROM Stock_Counts WHERE created_by IS NULL
UNION ALL
SELECT movement_number AS record_ref, 'Inventory_Movements: created_by is empty' AS detail FROM Inventory_Movements WHERE created_by IS NULL;
