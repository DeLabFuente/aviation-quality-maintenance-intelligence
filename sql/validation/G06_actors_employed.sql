-- rule: G06
-- title: Every person acting on a record was employed on that date
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT 'Audit_Log #' || x.audit_id AS record_ref, 'Audit_Log.changed_by: ' || e.employee_code || ' was not employed on ' || substr(x.event_datetime, 1, 10) AS detail
FROM Audit_Log x JOIN Employees e ON e.employee_id = x.changed_by
WHERE substr(x.event_datetime, 1, 10) < e.hire_date OR (e.termination_date IS NOT NULL AND substr(x.event_datetime, 1, 10) > e.termination_date)
UNION ALL
SELECT x.movement_number AS record_ref, 'Inventory_Movements.performed_by: ' || e.employee_code || ' was not employed on ' || substr(x.movement_datetime, 1, 10) AS detail
FROM Inventory_Movements x JOIN Employees e ON e.employee_id = x.performed_by
WHERE substr(x.movement_datetime, 1, 10) < e.hire_date OR (e.termination_date IS NOT NULL AND substr(x.movement_datetime, 1, 10) > e.termination_date)
UNION ALL
SELECT x.verification_number AS record_ref, 'Document_Verifications.verified_by: ' || e.employee_code || ' was not employed on ' || x.verification_date AS detail
FROM Document_Verifications x JOIN Employees e ON e.employee_id = x.verified_by
WHERE x.verification_date < e.hire_date OR (e.termination_date IS NOT NULL AND x.verification_date > e.termination_date)
UNION ALL
SELECT x.count_number AS record_ref, 'Stock_Counts.counted_by: ' || e.employee_code || ' was not employed on ' || substr(x.count_datetime, 1, 10) AS detail
FROM Stock_Counts x JOIN Employees e ON e.employee_id = x.counted_by
WHERE substr(x.count_datetime, 1, 10) < e.hire_date OR (e.termination_date IS NOT NULL AND substr(x.count_datetime, 1, 10) > e.termination_date)
UNION ALL
SELECT 'Root_Cause_Analyses #' || x.rca_id AS record_ref, 'Root_Cause_Analyses.analyzed_by: ' || e.employee_code || ' was not employed on ' || x.analysis_date AS detail
FROM Root_Cause_Analyses x JOIN Employees e ON e.employee_id = x.analyzed_by
WHERE x.analysis_date < e.hire_date OR (e.termination_date IS NOT NULL AND x.analysis_date > e.termination_date)
UNION ALL
SELECT 'Maintenance_Order_Holds #' || x.hold_id AS record_ref, 'Maintenance_Order_Holds.raised_by: ' || e.employee_code || ' was not employed on ' || x.start_date AS detail
FROM Maintenance_Order_Holds x JOIN Employees e ON e.employee_id = x.raised_by
WHERE x.start_date < e.hire_date OR (e.termination_date IS NOT NULL AND x.start_date > e.termination_date)
UNION ALL
SELECT 'Document_Revisions #' || x.revision_id AS record_ref, 'Document_Revisions.prepared_by: ' || e.employee_code || ' was not employed on ' || x.issue_date AS detail
FROM Document_Revisions x JOIN Employees e ON e.employee_id = x.prepared_by
WHERE x.issue_date < e.hire_date OR (e.termination_date IS NOT NULL AND x.issue_date > e.termination_date)
UNION ALL
SELECT x.po_number AS record_ref, 'Purchase_Orders.buyer_id: ' || e.employee_code || ' was not employed on ' || x.order_date AS detail
FROM Purchase_Orders x JOIN Employees e ON e.employee_id = x.buyer_id
WHERE x.order_date < e.hire_date OR (e.termination_date IS NOT NULL AND x.order_date > e.termination_date)
UNION ALL
SELECT x.mo_number AS record_ref, 'Maintenance_Orders.planner_id: ' || e.employee_code || ' was not employed on ' || x.opened_date AS detail
FROM Maintenance_Orders x JOIN Employees e ON e.employee_id = x.planner_id
WHERE x.opened_date < e.hire_date OR (e.termination_date IS NOT NULL AND x.opened_date > e.termination_date)
UNION ALL
SELECT x.mo_number AS record_ref, 'Maintenance_Orders.closed_by: ' || e.employee_code || ' was not employed on ' || x.closed_date AS detail
FROM Maintenance_Orders x JOIN Employees e ON e.employee_id = x.closed_by
WHERE x.closed_date < e.hire_date OR (e.termination_date IS NOT NULL AND x.closed_date > e.termination_date)
UNION ALL
SELECT x.incident_number AS record_ref, 'Quality_Incidents.detected_by: ' || e.employee_code || ' was not employed on ' || x.detected_date AS detail
FROM Quality_Incidents x JOIN Employees e ON e.employee_id = x.detected_by
WHERE x.detected_date < e.hire_date OR (e.termination_date IS NOT NULL AND x.detected_date > e.termination_date)
UNION ALL
SELECT x.incident_number AS record_ref, 'Quality_Incidents.closed_by: ' || e.employee_code || ' was not employed on ' || x.closed_date AS detail
FROM Quality_Incidents x JOIN Employees e ON e.employee_id = x.closed_by
WHERE x.closed_date < e.hire_date OR (e.termination_date IS NOT NULL AND x.closed_date > e.termination_date)
UNION ALL
SELECT x.action_number AS record_ref, 'CAPA_Actions.verified_by: ' || e.employee_code || ' was not employed on ' || x.effectiveness_check_date AS detail
FROM CAPA_Actions x JOIN Employees e ON e.employee_id = x.verified_by
WHERE x.effectiveness_check_date < e.hire_date OR (e.termination_date IS NOT NULL AND x.effectiveness_check_date > e.termination_date)
UNION ALL
SELECT 'CAPA_Progress_Updates #' || x.update_id AS record_ref, 'CAPA_Progress_Updates.created_by: ' || e.employee_code || ' was not employed on ' || x.update_date AS detail
FROM CAPA_Progress_Updates x JOIN Employees e ON e.employee_id = x.created_by
WHERE x.update_date < e.hire_date OR (e.termination_date IS NOT NULL AND x.update_date > e.termination_date);
