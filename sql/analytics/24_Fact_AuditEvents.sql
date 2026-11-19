-- AQMI analytical model — Fact_AuditEvents: one row per recorded change (the audit trail)
SELECT a.audit_id, a.event_datetime, substr(a.event_datetime, 1, 10) AS event_date, a.table_name, a.record_id,
       CASE a.table_name
           WHEN 'Quality_Incidents'       THEN (SELECT incident_number FROM Quality_Incidents WHERE incident_id = a.record_id)
           WHEN 'CAPA_Actions'            THEN (SELECT action_number FROM CAPA_Actions WHERE action_id = a.record_id)
           WHEN 'Lessons_Learned'         THEN (SELECT lesson_number FROM Lessons_Learned WHERE lesson_id = a.record_id)
           WHEN 'Maintenance_Orders'      THEN (SELECT mo_number FROM Maintenance_Orders WHERE mo_id = a.record_id)
           WHEN 'Maintenance_Order_Holds' THEN (SELECT o.mo_number || ' hold' FROM Maintenance_Order_Holds h
                                                JOIN Maintenance_Orders o USING (mo_id) WHERE h.hold_id = a.record_id)
           WHEN 'Document_Revisions'      THEN (SELECT d.document_code || ' ' || r.revision_code FROM Document_Revisions r
                                                JOIN Documents d USING (document_id) WHERE r.revision_id = a.record_id)
           WHEN 'Documents'               THEN (SELECT document_code FROM Documents WHERE document_id = a.record_id)
           WHEN 'Document_Verifications'  THEN (SELECT verification_number FROM Document_Verifications WHERE verification_id = a.record_id)
           WHEN 'Purchase_Orders'         THEN (SELECT po_number FROM Purchase_Orders WHERE po_id = a.record_id)
           WHEN 'Inventory_Movements'     THEN (SELECT movement_number FROM Inventory_Movements WHERE movement_id = a.record_id)
           WHEN 'Stock_Counts'            THEN (SELECT count_number FROM Stock_Counts WHERE count_id = a.record_id)
           WHEN 'Materials'               THEN (SELECT part_number FROM Materials WHERE material_id = a.record_id)
           WHEN 'Suppliers'               THEN (SELECT supplier_code FROM Suppliers WHERE supplier_id = a.record_id)
           WHEN 'Employees'               THEN (SELECT employee_code FROM Employees WHERE employee_id = a.record_id)
           ELSE a.table_name || ' #' || a.record_id END AS record_ref,
       a.action, COALESCE(a.field_name, '(new record)') AS field_name, a.old_value, a.new_value,
       CASE WHEN a.action = 'INSERT' THEN 'Record created'
            ELSE a.field_name || ': ' || COALESCE(a.old_value, '—') || ' → ' || COALESCE(a.new_value, '—') END AS change_label,
       a.changed_by, a.source
FROM Audit_Log a
ORDER BY a.audit_id;
