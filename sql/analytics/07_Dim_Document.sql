-- AQMI analytical model — Dim_Document (current revision and validity at the cut-off date)
SELECT d.document_id, d.document_code, d.title, d.document_type, dep.department_code AS owner_department_code,
       a.registration AS aircraft_registration, d.is_controlled, d.review_interval_months,
       d.current_revision, d.effective_date, d.review_due_date, d.validity_status, d.days_overdue, d.n_revisions
FROM vw_document_status d
JOIN Departments dep ON dep.department_id = d.owner_department_id
LEFT JOIN Aircraft a ON a.aircraft_id = d.aircraft_id
ORDER BY d.document_code;
