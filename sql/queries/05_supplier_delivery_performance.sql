-- =============================================================================
-- AQMI — Query 05: supplier delivery performance
-- Question: "Which suppliers deliver on time, and which ones cause problems?"
-- On time = full quantity received on or before the promised date.
-- =============================================================================
SELECT
    s.supplier_code, s.supplier_name, s.approval_status,
    COUNT(l.po_line_id)                                       AS lines_received,
    ROUND(100.0 * AVG(l.is_on_time), 1)                       AS on_time_pct,
    ROUND(AVG(l.days_late), 1)                                AS avg_days_late,
    MAX(l.days_late)                                          AS max_days_late,
    (SELECT COUNT(*) FROM Quality_Incidents i WHERE i.supplier_id = s.supplier_id) AS non_conformities
FROM Suppliers s
JOIN vw_po_line_status l ON l.supplier_id = s.supplier_id AND l.line_status = 'RECEIVED'
GROUP BY s.supplier_id
HAVING COUNT(l.po_line_id) >= 5
ORDER BY on_time_pct, lines_received DESC;
