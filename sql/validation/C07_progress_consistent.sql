-- rule: C07
-- title: Progress never decreases and reaches 100 % before the action is completed
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
WITH ordered AS (
    SELECT action_id, update_date, progress_pct,
           LAG(progress_pct) OVER (PARTITION BY action_id ORDER BY update_date, update_id) AS previous_pct
    FROM CAPA_Progress_Updates
)
SELECT a.action_number AS record_ref, 'Progress went from ' || o.previous_pct || ' % to ' || o.progress_pct || ' % on ' || o.update_date AS detail
FROM ordered o JOIN CAPA_Actions a USING (action_id)
WHERE o.progress_pct < o.previous_pct
UNION ALL
SELECT a.action_number, 'Status ' || a.status || ' without a 100 % progress update'
FROM CAPA_Actions a
WHERE a.status IN ('COMPLETED', 'CLOSED')
  AND NOT EXISTS (SELECT 1 FROM CAPA_Progress_Updates u WHERE u.action_id = a.action_id AND u.progress_pct = 100);
