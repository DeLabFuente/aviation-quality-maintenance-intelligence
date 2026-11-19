-- kpi: QUA-06
-- name: Overdue Corrective Actions
-- name_es: Acciones correctivas vencidas
-- area: Quality
-- type: SNAPSHOT
-- unit: count
-- direction: LOWER_IS_BETTER
-- target: 0  (fictitious internal target of AEROQ MRO)
-- warning: 2  (fictitious internal warning level)
-- frequency: Monthly
-- tables: CAPA_Actions, Audit_Log
-- question: How many corrective actions were past their due date and not yet implemented?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- SNAPSHOT: state at the end of end_date of each period (TOTAL = at the cut-off date).
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
-- The due date can be extended. To measure the past correctly, the due date in
-- force at each date is rebuilt from the audit log (traceability in use).
WITH due_changes AS (
    SELECT audit_id, record_id AS action_id, date(event_datetime) AS change_date, old_value, new_value
    FROM Audit_Log
    WHERE table_name = 'CAPA_Actions' AND field_name = 'due_date' AND action = 'UPDATE'
),
open_actions AS (
    SELECT p.period, p.end_date, c.action_id,
           COALESCE(
               (SELECT h.new_value FROM due_changes h
                 WHERE h.action_id = c.action_id AND h.change_date <= p.end_date
                 ORDER BY h.audit_id DESC LIMIT 1),
               (SELECT h.old_value FROM due_changes h
                 WHERE h.action_id = c.action_id AND h.change_date > p.end_date
                 ORDER BY h.audit_id LIMIT 1),
               c.due_date) AS due_date_then
    FROM vw_kpi_periods p
    JOIN CAPA_Actions c
      ON c.action_type = 'CORRECTIVE'
     AND c.status <> 'CANCELLED'
     AND c.created_date <= p.end_date
     AND (c.completed_date IS NULL OR c.completed_date > p.end_date)
)
SELECT p.period,
       COUNT(o.action_id) AS numerator,
       NULL               AS denominator,
       COUNT(o.action_id) AS value
FROM vw_kpi_periods p
LEFT JOIN open_actions o
       ON o.period = p.period AND o.due_date_then < o.end_date
GROUP BY p.period
ORDER BY p.period;
