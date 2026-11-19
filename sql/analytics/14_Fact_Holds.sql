-- AQMI analytical model — Fact_Holds: one row per work-order hold (material or documentation)
SELECT h.hold_id, h.mo_id, o.mo_number, o.aircraft_id, h.hold_reason, h.material_id, d.document_code,
       h.start_date, h.end_date,
       CAST(julianday(COALESCE(h.end_date, p.as_of_date)) - julianday(h.start_date) AS INTEGER) AS hold_days,
       (h.end_date IS NULL) AS is_active, h.comment
FROM Maintenance_Order_Holds h
JOIN Maintenance_Orders o USING (mo_id)
LEFT JOIN Documents d ON d.document_id = h.document_id
CROSS JOIN vw_parameters p
ORDER BY h.hold_id;
