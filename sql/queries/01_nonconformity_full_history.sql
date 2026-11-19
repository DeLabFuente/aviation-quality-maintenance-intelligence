-- =============================================================================
-- AQMI — Query 01: full history of a non-conformity (module F, traceability)
-- Question: "What happened with this non-conformity, who did it and when?"
-- Rebuilds the complete timeline from the audit log: creation, every status
-- change, root-cause analysis, actions, progress and effectiveness checks.
--
-- How to use it: change the number in the first lines (params). By default it
-- shows the non-conformity that led to the redesign of the closure form.
-- =============================================================================
WITH params AS (
    SELECT COALESCE(
        NULL,   -- <- write a number here, e.g. 'NC-2025-0023', to see another one
        (SELECT i.incident_number FROM Quality_Incidents i JOIN CAPA_Actions a USING (incident_id)
         WHERE a.title LIKE 'Redesign the work order closure record%')) AS incident_number
),
nc AS (SELECT i.* FROM Quality_Incidents i JOIN params p ON p.incident_number = i.incident_number),
actions AS (SELECT a.* FROM CAPA_Actions a JOIN nc USING (incident_id)),
timeline AS (
    SELECT a.event_datetime AS moment, 'Non-conformity' AS item, nc.incident_number AS reference,
           CASE a.action WHEN 'INSERT' THEN 'Created' ELSE a.field_name || ': ' || COALESCE(a.old_value, '—') || ' → ' || COALESCE(a.new_value, '—') END AS event,
           a.changed_by
    FROM Audit_Log a JOIN nc ON a.table_name = 'Quality_Incidents' AND a.record_id = nc.incident_id
    UNION ALL
    SELECT r.created_at, 'Root-cause analysis', r.method,
           COALESCE(r.ishikawa_category || ' — ', '') || r.root_cause_statement, r.analyzed_by
    FROM Root_Cause_Analyses r JOIN nc USING (incident_id)
    UNION ALL
    SELECT a.event_datetime, 'Action', x.action_number,
           CASE a.action WHEN 'INSERT' THEN 'Created: ' || x.title ELSE a.field_name || ': ' || COALESCE(a.old_value, '—') || ' → ' || COALESCE(a.new_value, '—') END,
           a.changed_by
    FROM Audit_Log a JOIN actions x ON a.table_name = 'CAPA_Actions' AND a.record_id = x.action_id
    UNION ALL
    SELECT u.created_at, 'Progress', x.action_number, u.progress_pct || ' % — ' || u.comment, u.created_by
    FROM CAPA_Progress_Updates u JOIN actions x USING (action_id)
)
SELECT t.moment, t.item, t.reference, t.event, e.first_name || ' ' || e.last_name AS who
FROM timeline t LEFT JOIN Employees e ON e.employee_id = t.changed_by
ORDER BY t.moment, t.item;
