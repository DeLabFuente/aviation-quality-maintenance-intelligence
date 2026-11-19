-- rule: G04
-- title: No event is later than the cut-off date (AS_OF_DATE)
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
WITH p AS (SELECT (SELECT parameter_value FROM System_Parameters WHERE parameter_key = 'AS_OF_DATE') AS as_of,
             (SELECT parameter_value FROM System_Parameters WHERE parameter_key = 'PERIOD_START') AS period_start)
SELECT x.mo_number AS record_ref, 'Maintenance_Orders.opened_date = ' || x.opened_date || ' is after the cut-off date' AS detail
FROM Maintenance_Orders x CROSS JOIN p WHERE substr(x.opened_date, 1, 10) > p.as_of
UNION ALL
SELECT x.mo_number AS record_ref, 'Maintenance_Orders.actual_end_date = ' || x.actual_end_date || ' is after the cut-off date' AS detail
FROM Maintenance_Orders x CROSS JOIN p WHERE substr(x.actual_end_date, 1, 10) > p.as_of
UNION ALL
SELECT x.mo_number AS record_ref, 'Maintenance_Orders.closed_date = ' || x.closed_date || ' is after the cut-off date' AS detail
FROM Maintenance_Orders x CROSS JOIN p WHERE substr(x.closed_date, 1, 10) > p.as_of
UNION ALL
SELECT x.incident_number AS record_ref, 'Quality_Incidents.detected_date = ' || x.detected_date || ' is after the cut-off date' AS detail
FROM Quality_Incidents x CROSS JOIN p WHERE substr(x.detected_date, 1, 10) > p.as_of
UNION ALL
SELECT x.incident_number AS record_ref, 'Quality_Incidents.closed_date = ' || x.closed_date || ' is after the cut-off date' AS detail
FROM Quality_Incidents x CROSS JOIN p WHERE substr(x.closed_date, 1, 10) > p.as_of
UNION ALL
SELECT x.action_number AS record_ref, 'CAPA_Actions.created_date = ' || x.created_date || ' is after the cut-off date' AS detail
FROM CAPA_Actions x CROSS JOIN p WHERE substr(x.created_date, 1, 10) > p.as_of
UNION ALL
SELECT x.action_number AS record_ref, 'CAPA_Actions.completed_date = ' || x.completed_date || ' is after the cut-off date' AS detail
FROM CAPA_Actions x CROSS JOIN p WHERE substr(x.completed_date, 1, 10) > p.as_of
UNION ALL
SELECT x.action_number AS record_ref, 'CAPA_Actions.effectiveness_check_date = ' || x.effectiveness_check_date || ' is after the cut-off date' AS detail
FROM CAPA_Actions x CROSS JOIN p WHERE substr(x.effectiveness_check_date, 1, 10) > p.as_of
UNION ALL
SELECT x.action_number AS record_ref, 'CAPA_Actions.closed_date = ' || x.closed_date || ' is after the cut-off date' AS detail
FROM CAPA_Actions x CROSS JOIN p WHERE substr(x.closed_date, 1, 10) > p.as_of
UNION ALL
SELECT 'CAPA_Progress_Updates #' || x.update_id AS record_ref, 'CAPA_Progress_Updates.update_date = ' || x.update_date || ' is after the cut-off date' AS detail
FROM CAPA_Progress_Updates x CROSS JOIN p WHERE substr(x.update_date, 1, 10) > p.as_of
UNION ALL
SELECT x.verification_number AS record_ref, 'Document_Verifications.verification_date = ' || x.verification_date || ' is after the cut-off date' AS detail
FROM Document_Verifications x CROSS JOIN p WHERE substr(x.verification_date, 1, 10) > p.as_of
UNION ALL
SELECT 'Root_Cause_Analyses #' || x.rca_id AS record_ref, 'Root_Cause_Analyses.analysis_date = ' || x.analysis_date || ' is after the cut-off date' AS detail
FROM Root_Cause_Analyses x CROSS JOIN p WHERE substr(x.analysis_date, 1, 10) > p.as_of
UNION ALL
SELECT 'Maintenance_Order_Holds #' || x.hold_id AS record_ref, 'Maintenance_Order_Holds.start_date = ' || x.start_date || ' is after the cut-off date' AS detail
FROM Maintenance_Order_Holds x CROSS JOIN p WHERE substr(x.start_date, 1, 10) > p.as_of
UNION ALL
SELECT 'Maintenance_Order_Holds #' || x.hold_id AS record_ref, 'Maintenance_Order_Holds.end_date = ' || x.end_date || ' is after the cut-off date' AS detail
FROM Maintenance_Order_Holds x CROSS JOIN p WHERE substr(x.end_date, 1, 10) > p.as_of
UNION ALL
SELECT x.po_number AS record_ref, 'Purchase_Orders.order_date = ' || x.order_date || ' is after the cut-off date' AS detail
FROM Purchase_Orders x CROSS JOIN p WHERE substr(x.order_date, 1, 10) > p.as_of
UNION ALL
SELECT x.po_number AS record_ref, 'Purchase_Orders.cancelled_date = ' || x.cancelled_date || ' is after the cut-off date' AS detail
FROM Purchase_Orders x CROSS JOIN p WHERE substr(x.cancelled_date, 1, 10) > p.as_of
UNION ALL
SELECT x.movement_number AS record_ref, 'Inventory_Movements.movement_datetime = ' || x.movement_datetime || ' is after the cut-off date' AS detail
FROM Inventory_Movements x CROSS JOIN p WHERE substr(x.movement_datetime, 1, 10) > p.as_of
UNION ALL
SELECT x.count_number AS record_ref, 'Stock_Counts.count_datetime = ' || x.count_datetime || ' is after the cut-off date' AS detail
FROM Stock_Counts x CROSS JOIN p WHERE substr(x.count_datetime, 1, 10) > p.as_of
UNION ALL
SELECT 'Audit_Log #' || x.audit_id AS record_ref, 'Audit_Log.event_datetime = ' || x.event_datetime || ' is after the cut-off date' AS detail
FROM Audit_Log x CROSS JOIN p WHERE substr(x.event_datetime, 1, 10) > p.as_of
UNION ALL
SELECT 'Document_Revisions #' || x.revision_id AS record_ref, 'Document_Revisions.issue_date = ' || x.issue_date || ' is after the cut-off date' AS detail
FROM Document_Revisions x CROSS JOIN p WHERE substr(x.issue_date, 1, 10) > p.as_of
UNION ALL
SELECT 'Document_Revisions #' || x.revision_id AS record_ref, 'Document_Revisions.superseded_date = ' || x.superseded_date || ' is after the cut-off date' AS detail
FROM Document_Revisions x CROSS JOIN p WHERE substr(x.superseded_date, 1, 10) > p.as_of
UNION ALL
SELECT x.employee_code AS record_ref, 'Employees.hire_date = ' || x.hire_date || ' is after the cut-off date' AS detail
FROM Employees x CROSS JOIN p WHERE substr(x.hire_date, 1, 10) > p.as_of
UNION ALL
SELECT 'Document_Revisions #' || x.revision_id, 'Revision in force from ' || x.effective_date || ', after the cut-off date'
FROM Document_Revisions x CROSS JOIN p WHERE x.lifecycle_status IN ('CURRENT', 'SUPERSEDED') AND x.effective_date > p.as_of
UNION ALL
SELECT x.lesson_number AS record_ref, 'Lessons_Learned.proposed_date = ' || x.proposed_date || ' is after the cut-off date' AS detail
FROM Lessons_Learned x CROSS JOIN p WHERE substr(x.proposed_date, 1, 10) > p.as_of
UNION ALL
SELECT x.lesson_number AS record_ref, 'Lessons_Learned.approved_date = ' || x.approved_date || ' is after the cut-off date' AS detail
FROM Lessons_Learned x CROSS JOIN p WHERE substr(x.approved_date, 1, 10) > p.as_of
UNION ALL
SELECT x.lesson_number AS record_ref, 'Lessons_Learned.rejected_date = ' || x.rejected_date || ' is after the cut-off date' AS detail
FROM Lessons_Learned x CROSS JOIN p WHERE substr(x.rejected_date, 1, 10) > p.as_of
UNION ALL
SELECT x.lesson_number AS record_ref, 'Lessons_Learned.incorporated_date = ' || x.incorporated_date || ' is after the cut-off date' AS detail
FROM Lessons_Learned x CROSS JOIN p WHERE substr(x.incorporated_date, 1, 10) > p.as_of;
