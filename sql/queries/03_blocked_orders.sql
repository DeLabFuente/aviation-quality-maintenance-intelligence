-- =============================================================================
-- AQMI — Query 03: work orders blocked today and why
-- Question: "Which orders are stopped, since when, and what are we waiting for?"
-- For material holds it shows the available stock and the next delivery promised.
-- =============================================================================
SELECT
    o.mo_number, a.registration AS aircraft, o.priority, h.hold_reason,
    h.start_date AS blocked_since,
    CAST(julianday(p.as_of_date) - julianday(h.start_date) AS INTEGER) AS days_blocked,
    COALESCE(m.part_number, d.document_code) AS waiting_for,
    h.comment,
    s.available_qty,
    (SELECT MIN(l.promised_date) FROM vw_po_line_status l
      WHERE l.material_id = h.material_id AND l.qty_pending > 0) AS next_promised_delivery
FROM Maintenance_Order_Holds h
JOIN Maintenance_Orders o USING (mo_id)
JOIN Aircraft a ON a.aircraft_id = o.aircraft_id
LEFT JOIN Materials m ON m.material_id = h.material_id
LEFT JOIN Documents d ON d.document_id = h.document_id
LEFT JOIN vw_stock_by_bucket s ON s.material_id = h.material_id
CROSS JOIN vw_parameters p
WHERE h.end_date IS NULL
ORDER BY days_blocked DESC;
