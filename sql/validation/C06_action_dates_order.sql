-- rule: C06
-- title: Dates in order: creation <= completion <= effectiveness check <= closure
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT action_number AS record_ref,
       'Created ' || created_date || ', completed ' || COALESCE(completed_date, '-') || ', checked ' ||
       COALESCE(effectiveness_check_date, '-') || ', closed ' || COALESCE(closed_date, '-') AS detail
FROM CAPA_Actions
WHERE completed_date < created_date OR effectiveness_check_date < completed_date
   OR (effectiveness_check_date IS NOT NULL AND completed_date IS NULL)
   OR closed_date < effectiveness_check_date OR closed_date < created_date;
