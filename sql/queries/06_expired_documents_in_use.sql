-- =============================================================================
-- AQMI — Query 06: expired documents and the work orders that used them
-- Question: "Which documents are overdue for review, and have they been used
-- on work orders after their review date?"
-- =============================================================================
SELECT
    d.document_code, d.title, d.current_revision, d.review_due_date, d.days_overdue,
    dep.department_code AS owner,
    COUNT(l.mo_id) AS orders_after_due_date,
    group_concat(o.mo_number, ', ') AS orders
FROM vw_document_status d
JOIN Departments dep ON dep.department_id = d.owner_department_id
LEFT JOIN Maintenance_Order_Documents l
       ON l.revision_id = d.current_revision_id AND l.linked_date > d.review_due_date
LEFT JOIN Maintenance_Orders o ON o.mo_id = l.mo_id
WHERE d.validity_status = 'REVIEW_OVERDUE'
GROUP BY d.document_id
ORDER BY d.days_overdue DESC;
