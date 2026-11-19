-- =============================================================================
-- AQMI — vw_incident_status
-- One row per non-conformity with its age, resolution time and target status.
-- The closure targets are FICTITIOUS internal targets of AEROQ MRO.
-- =============================================================================
CREATE VIEW vw_incident_status AS
SELECT
    i.incident_id, i.incident_number, i.category_id, c.category_code, c.category_name_en, c.category_name_es,
    i.severity, i.priority, i.detection_source, i.status, i.responsible_department_id, i.owner_id,
    i.aircraft_id, i.mo_id, i.revision_id, i.material_id, i.supplier_id, i.po_line_id,
    i.detected_date, i.target_closure_date, i.closed_date,
    CASE WHEN i.status IN ('CLOSED', 'CANCELLED') THEN 0 ELSE 1 END                  AS is_open,
    CAST(julianday(COALESCE(i.closed_date, p.as_of_date)) - julianday(i.detected_date) AS INTEGER) AS age_days,
    CASE WHEN i.status = 'CLOSED'
         THEN CAST(julianday(i.closed_date) - julianday(i.detected_date) AS INTEGER) END AS resolution_days,
    CASE WHEN i.status NOT IN ('CLOSED', 'CANCELLED') AND i.target_closure_date < p.as_of_date
         THEN 1 ELSE 0 END                                                           AS is_overdue,
    CASE WHEN i.status = 'CLOSED' THEN (i.closed_date <= i.target_closure_date) END  AS closed_on_time,
    EXISTS (SELECT 1 FROM Root_Cause_Analyses r WHERE r.incident_id = i.incident_id) AS has_rca,
    (SELECT COUNT(*) FROM CAPA_Actions a WHERE a.incident_id = i.incident_id)        AS n_actions,
    (SELECT COUNT(*) FROM CAPA_Actions a WHERE a.incident_id = i.incident_id
                                         AND a.status IN ('OPEN', 'IN_PROGRESS'))    AS n_open_actions
FROM Quality_Incidents i
JOIN Incident_Categories c USING (category_id)
CROSS JOIN vw_parameters p;
