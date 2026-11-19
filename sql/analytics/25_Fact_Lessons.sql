-- AQMI analytical model — Fact_Lessons: one row per lesson learned (Phase 9)
SELECT
    s.lesson_id, s.lesson_number, s.action_number, s.action_type, s.effectiveness_result, s.incident_number,
    s.title, s.recommendation, s.department_id, s.scope, s.status,
    CASE s.status WHEN 'PROPOSED' THEN 1 WHEN 'APPROVED' THEN 2 WHEN 'INCORPORATED' THEN 3 ELSE 4 END AS status_order,
    s.proposed_date, s.approved_date, s.rejected_date, s.incorporated_date,
    COALESCE(s.incorporated_in, CASE s.status WHEN 'APPROVED' THEN 'Pending' ELSE '—' END) AS incorporated_in,
    e.first_name || ' ' || e.last_name AS proposed_by_name,
    s.is_approved, s.is_incorporated, s.is_pending_incorporation, s.days_pending,
    s.days_to_decision, s.days_to_incorporate
FROM vw_lesson_status s
JOIN Employees e ON e.employee_id = s.proposed_by
ORDER BY s.lesson_id;
