-- rule: G03
-- title: Dates and date-times have a valid ISO format
-- severity: CRITICAL
-- type: E
-- enforced_by: CHECK (date(x) IS x) + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT department_code AS record_ref, 'Departments.created_at is not a valid date-time: ' || created_at AS detail FROM Departments WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT department_code AS record_ref, 'Departments.updated_at is not a valid date-time: ' || updated_at AS detail FROM Departments WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT employee_code AS record_ref, 'Employees.hire_date is not a valid date: ' || hire_date AS detail FROM Employees WHERE hire_date IS NOT NULL AND date(hire_date) IS NOT hire_date
UNION ALL
SELECT employee_code AS record_ref, 'Employees.termination_date is not a valid date: ' || termination_date AS detail FROM Employees WHERE termination_date IS NOT NULL AND date(termination_date) IS NOT termination_date
UNION ALL
SELECT employee_code AS record_ref, 'Employees.created_at is not a valid date-time: ' || created_at AS detail FROM Employees WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT employee_code AS record_ref, 'Employees.updated_at is not a valid date-time: ' || updated_at AS detail FROM Employees WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT customer_code AS record_ref, 'Customers.created_at is not a valid date-time: ' || created_at AS detail FROM Customers WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT customer_code AS record_ref, 'Customers.updated_at is not a valid date-time: ' || updated_at AS detail FROM Customers WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT registration AS record_ref, 'Aircraft.contract_start_date is not a valid date: ' || contract_start_date AS detail FROM Aircraft WHERE contract_start_date IS NOT NULL AND date(contract_start_date) IS NOT contract_start_date
UNION ALL
SELECT registration AS record_ref, 'Aircraft.contract_end_date is not a valid date: ' || contract_end_date AS detail FROM Aircraft WHERE contract_end_date IS NOT NULL AND date(contract_end_date) IS NOT contract_end_date
UNION ALL
SELECT registration AS record_ref, 'Aircraft.created_at is not a valid date-time: ' || created_at AS detail FROM Aircraft WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT registration AS record_ref, 'Aircraft.updated_at is not a valid date-time: ' || updated_at AS detail FROM Aircraft WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT supplier_code AS record_ref, 'Suppliers.approval_date is not a valid date: ' || approval_date AS detail FROM Suppliers WHERE approval_date IS NOT NULL AND date(approval_date) IS NOT approval_date
UNION ALL
SELECT supplier_code AS record_ref, 'Suppliers.suspended_date is not a valid date: ' || suspended_date AS detail FROM Suppliers WHERE suspended_date IS NOT NULL AND date(suspended_date) IS NOT suspended_date
UNION ALL
SELECT supplier_code AS record_ref, 'Suppliers.next_evaluation_date is not a valid date: ' || next_evaluation_date AS detail FROM Suppliers WHERE next_evaluation_date IS NOT NULL AND date(next_evaluation_date) IS NOT next_evaluation_date
UNION ALL
SELECT supplier_code AS record_ref, 'Suppliers.created_at is not a valid date-time: ' || created_at AS detail FROM Suppliers WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT supplier_code AS record_ref, 'Suppliers.updated_at is not a valid date-time: ' || updated_at AS detail FROM Suppliers WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT part_number AS record_ref, 'Materials.created_at is not a valid date-time: ' || created_at AS detail FROM Materials WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT part_number AS record_ref, 'Materials.updated_at is not a valid date-time: ' || updated_at AS detail FROM Materials WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT document_code AS record_ref, 'Documents.created_at is not a valid date-time: ' || created_at AS detail FROM Documents WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT document_code AS record_ref, 'Documents.updated_at is not a valid date-time: ' || updated_at AS detail FROM Documents WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT 'Document_Revisions #' || revision_id AS record_ref, 'Document_Revisions.issue_date is not a valid date: ' || issue_date AS detail FROM Document_Revisions WHERE issue_date IS NOT NULL AND date(issue_date) IS NOT issue_date
UNION ALL
SELECT 'Document_Revisions #' || revision_id AS record_ref, 'Document_Revisions.effective_date is not a valid date: ' || effective_date AS detail FROM Document_Revisions WHERE effective_date IS NOT NULL AND date(effective_date) IS NOT effective_date
UNION ALL
SELECT 'Document_Revisions #' || revision_id AS record_ref, 'Document_Revisions.review_due_date is not a valid date: ' || review_due_date AS detail FROM Document_Revisions WHERE review_due_date IS NOT NULL AND date(review_due_date) IS NOT review_due_date
UNION ALL
SELECT 'Document_Revisions #' || revision_id AS record_ref, 'Document_Revisions.superseded_date is not a valid date: ' || superseded_date AS detail FROM Document_Revisions WHERE superseded_date IS NOT NULL AND date(superseded_date) IS NOT superseded_date
UNION ALL
SELECT 'Document_Revisions #' || revision_id AS record_ref, 'Document_Revisions.created_at is not a valid date-time: ' || created_at AS detail FROM Document_Revisions WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT 'Document_Revisions #' || revision_id AS record_ref, 'Document_Revisions.updated_at is not a valid date-time: ' || updated_at AS detail FROM Document_Revisions WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT mo_number AS record_ref, 'Maintenance_Orders.opened_date is not a valid date: ' || opened_date AS detail FROM Maintenance_Orders WHERE opened_date IS NOT NULL AND date(opened_date) IS NOT opened_date
UNION ALL
SELECT mo_number AS record_ref, 'Maintenance_Orders.planned_end_date is not a valid date: ' || planned_end_date AS detail FROM Maintenance_Orders WHERE planned_end_date IS NOT NULL AND date(planned_end_date) IS NOT planned_end_date
UNION ALL
SELECT mo_number AS record_ref, 'Maintenance_Orders.actual_end_date is not a valid date: ' || actual_end_date AS detail FROM Maintenance_Orders WHERE actual_end_date IS NOT NULL AND date(actual_end_date) IS NOT actual_end_date
UNION ALL
SELECT mo_number AS record_ref, 'Maintenance_Orders.closed_date is not a valid date: ' || closed_date AS detail FROM Maintenance_Orders WHERE closed_date IS NOT NULL AND date(closed_date) IS NOT closed_date
UNION ALL
SELECT mo_number AS record_ref, 'Maintenance_Orders.created_at is not a valid date-time: ' || created_at AS detail FROM Maintenance_Orders WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT mo_number AS record_ref, 'Maintenance_Orders.updated_at is not a valid date-time: ' || updated_at AS detail FROM Maintenance_Orders WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT 'Maintenance_Order_Materials #' || mo_material_id AS record_ref, 'Maintenance_Order_Materials.required_by_date is not a valid date: ' || required_by_date AS detail FROM Maintenance_Order_Materials WHERE required_by_date IS NOT NULL AND date(required_by_date) IS NOT required_by_date
UNION ALL
SELECT 'Maintenance_Order_Materials #' || mo_material_id AS record_ref, 'Maintenance_Order_Materials.created_at is not a valid date-time: ' || created_at AS detail FROM Maintenance_Order_Materials WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT 'Maintenance_Order_Materials #' || mo_material_id AS record_ref, 'Maintenance_Order_Materials.updated_at is not a valid date-time: ' || updated_at AS detail FROM Maintenance_Order_Materials WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT 'Maintenance_Order_Documents #' || mo_document_id AS record_ref, 'Maintenance_Order_Documents.linked_date is not a valid date: ' || linked_date AS detail FROM Maintenance_Order_Documents WHERE linked_date IS NOT NULL AND date(linked_date) IS NOT linked_date
UNION ALL
SELECT 'Maintenance_Order_Documents #' || mo_document_id AS record_ref, 'Maintenance_Order_Documents.created_at is not a valid date-time: ' || created_at AS detail FROM Maintenance_Order_Documents WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT 'Maintenance_Order_Documents #' || mo_document_id AS record_ref, 'Maintenance_Order_Documents.updated_at is not a valid date-time: ' || updated_at AS detail FROM Maintenance_Order_Documents WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT po_number AS record_ref, 'Purchase_Orders.order_date is not a valid date: ' || order_date AS detail FROM Purchase_Orders WHERE order_date IS NOT NULL AND date(order_date) IS NOT order_date
UNION ALL
SELECT po_number AS record_ref, 'Purchase_Orders.cancelled_date is not a valid date: ' || cancelled_date AS detail FROM Purchase_Orders WHERE cancelled_date IS NOT NULL AND date(cancelled_date) IS NOT cancelled_date
UNION ALL
SELECT po_number AS record_ref, 'Purchase_Orders.created_at is not a valid date-time: ' || created_at AS detail FROM Purchase_Orders WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT po_number AS record_ref, 'Purchase_Orders.updated_at is not a valid date-time: ' || updated_at AS detail FROM Purchase_Orders WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT 'Purchase_Order_Lines #' || po_line_id AS record_ref, 'Purchase_Order_Lines.promised_date is not a valid date: ' || promised_date AS detail FROM Purchase_Order_Lines WHERE promised_date IS NOT NULL AND date(promised_date) IS NOT promised_date
UNION ALL
SELECT 'Purchase_Order_Lines #' || po_line_id AS record_ref, 'Purchase_Order_Lines.created_at is not a valid date-time: ' || created_at AS detail FROM Purchase_Order_Lines WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT 'Purchase_Order_Lines #' || po_line_id AS record_ref, 'Purchase_Order_Lines.updated_at is not a valid date-time: ' || updated_at AS detail FROM Purchase_Order_Lines WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT incident_number AS record_ref, 'Quality_Incidents.detected_date is not a valid date: ' || detected_date AS detail FROM Quality_Incidents WHERE detected_date IS NOT NULL AND date(detected_date) IS NOT detected_date
UNION ALL
SELECT incident_number AS record_ref, 'Quality_Incidents.target_closure_date is not a valid date: ' || target_closure_date AS detail FROM Quality_Incidents WHERE target_closure_date IS NOT NULL AND date(target_closure_date) IS NOT target_closure_date
UNION ALL
SELECT incident_number AS record_ref, 'Quality_Incidents.closed_date is not a valid date: ' || closed_date AS detail FROM Quality_Incidents WHERE closed_date IS NOT NULL AND date(closed_date) IS NOT closed_date
UNION ALL
SELECT incident_number AS record_ref, 'Quality_Incidents.created_at is not a valid date-time: ' || created_at AS detail FROM Quality_Incidents WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT incident_number AS record_ref, 'Quality_Incidents.updated_at is not a valid date-time: ' || updated_at AS detail FROM Quality_Incidents WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT 'Maintenance_Order_Holds #' || hold_id AS record_ref, 'Maintenance_Order_Holds.start_date is not a valid date: ' || start_date AS detail FROM Maintenance_Order_Holds WHERE start_date IS NOT NULL AND date(start_date) IS NOT start_date
UNION ALL
SELECT 'Maintenance_Order_Holds #' || hold_id AS record_ref, 'Maintenance_Order_Holds.end_date is not a valid date: ' || end_date AS detail FROM Maintenance_Order_Holds WHERE end_date IS NOT NULL AND date(end_date) IS NOT end_date
UNION ALL
SELECT 'Maintenance_Order_Holds #' || hold_id AS record_ref, 'Maintenance_Order_Holds.created_at is not a valid date-time: ' || created_at AS detail FROM Maintenance_Order_Holds WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT 'Maintenance_Order_Holds #' || hold_id AS record_ref, 'Maintenance_Order_Holds.updated_at is not a valid date-time: ' || updated_at AS detail FROM Maintenance_Order_Holds WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT verification_number AS record_ref, 'Document_Verifications.verification_date is not a valid date: ' || verification_date AS detail FROM Document_Verifications WHERE verification_date IS NOT NULL AND date(verification_date) IS NOT verification_date
UNION ALL
SELECT verification_number AS record_ref, 'Document_Verifications.created_at is not a valid date-time: ' || created_at AS detail FROM Document_Verifications WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT verification_number AS record_ref, 'Document_Verifications.updated_at is not a valid date-time: ' || updated_at AS detail FROM Document_Verifications WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT 'Root_Cause_Analyses #' || rca_id AS record_ref, 'Root_Cause_Analyses.analysis_date is not a valid date: ' || analysis_date AS detail FROM Root_Cause_Analyses WHERE analysis_date IS NOT NULL AND date(analysis_date) IS NOT analysis_date
UNION ALL
SELECT 'Root_Cause_Analyses #' || rca_id AS record_ref, 'Root_Cause_Analyses.created_at is not a valid date-time: ' || created_at AS detail FROM Root_Cause_Analyses WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT 'Root_Cause_Analyses #' || rca_id AS record_ref, 'Root_Cause_Analyses.updated_at is not a valid date-time: ' || updated_at AS detail FROM Root_Cause_Analyses WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT action_number AS record_ref, 'CAPA_Actions.created_date is not a valid date: ' || created_date AS detail FROM CAPA_Actions WHERE created_date IS NOT NULL AND date(created_date) IS NOT created_date
UNION ALL
SELECT action_number AS record_ref, 'CAPA_Actions.original_due_date is not a valid date: ' || original_due_date AS detail FROM CAPA_Actions WHERE original_due_date IS NOT NULL AND date(original_due_date) IS NOT original_due_date
UNION ALL
SELECT action_number AS record_ref, 'CAPA_Actions.due_date is not a valid date: ' || due_date AS detail FROM CAPA_Actions WHERE due_date IS NOT NULL AND date(due_date) IS NOT due_date
UNION ALL
SELECT action_number AS record_ref, 'CAPA_Actions.completed_date is not a valid date: ' || completed_date AS detail FROM CAPA_Actions WHERE completed_date IS NOT NULL AND date(completed_date) IS NOT completed_date
UNION ALL
SELECT action_number AS record_ref, 'CAPA_Actions.effectiveness_check_date is not a valid date: ' || effectiveness_check_date AS detail FROM CAPA_Actions WHERE effectiveness_check_date IS NOT NULL AND date(effectiveness_check_date) IS NOT effectiveness_check_date
UNION ALL
SELECT action_number AS record_ref, 'CAPA_Actions.closed_date is not a valid date: ' || closed_date AS detail FROM CAPA_Actions WHERE closed_date IS NOT NULL AND date(closed_date) IS NOT closed_date
UNION ALL
SELECT action_number AS record_ref, 'CAPA_Actions.created_at is not a valid date-time: ' || created_at AS detail FROM CAPA_Actions WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT action_number AS record_ref, 'CAPA_Actions.updated_at is not a valid date-time: ' || updated_at AS detail FROM CAPA_Actions WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT 'CAPA_Progress_Updates #' || update_id AS record_ref, 'CAPA_Progress_Updates.update_date is not a valid date: ' || update_date AS detail FROM CAPA_Progress_Updates WHERE update_date IS NOT NULL AND date(update_date) IS NOT update_date
UNION ALL
SELECT 'CAPA_Progress_Updates #' || update_id AS record_ref, 'CAPA_Progress_Updates.created_at is not a valid date-time: ' || created_at AS detail FROM CAPA_Progress_Updates WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT count_number AS record_ref, 'Stock_Counts.count_datetime is not a valid date-time: ' || count_datetime AS detail FROM Stock_Counts WHERE count_datetime IS NOT NULL AND datetime(count_datetime) IS NOT count_datetime
UNION ALL
SELECT count_number AS record_ref, 'Stock_Counts.created_at is not a valid date-time: ' || created_at AS detail FROM Stock_Counts WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT count_number AS record_ref, 'Stock_Counts.updated_at is not a valid date-time: ' || updated_at AS detail FROM Stock_Counts WHERE updated_at IS NOT NULL AND datetime(updated_at) IS NOT updated_at
UNION ALL
SELECT movement_number AS record_ref, 'Inventory_Movements.movement_datetime is not a valid date-time: ' || movement_datetime AS detail FROM Inventory_Movements WHERE movement_datetime IS NOT NULL AND datetime(movement_datetime) IS NOT movement_datetime
UNION ALL
SELECT movement_number AS record_ref, 'Inventory_Movements.shelf_life_expiry_date is not a valid date: ' || shelf_life_expiry_date AS detail FROM Inventory_Movements WHERE shelf_life_expiry_date IS NOT NULL AND date(shelf_life_expiry_date) IS NOT shelf_life_expiry_date
UNION ALL
SELECT movement_number AS record_ref, 'Inventory_Movements.created_at is not a valid date-time: ' || created_at AS detail FROM Inventory_Movements WHERE created_at IS NOT NULL AND datetime(created_at) IS NOT created_at
UNION ALL
SELECT 'Audit_Log #' || audit_id AS record_ref, 'Audit_Log.event_datetime is not a valid date-time: ' || event_datetime AS detail FROM Audit_Log WHERE event_datetime IS NOT NULL AND datetime(event_datetime) IS NOT event_datetime;
