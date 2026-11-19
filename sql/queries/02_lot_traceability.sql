-- =============================================================================
-- AQMI — Query 02: traceability of a lot, from the supplier to the aircraft
-- Question: "Where did this lot come from, which certificate came with it, and
-- on which aircraft and work orders was it used?"
--
-- How to use it: write a lot number in params. By default it takes the first lot
-- of a component that was issued to a work order.
-- =============================================================================
WITH params AS (
    SELECT COALESCE(
        NULL,   -- <- write a lot number here, e.g. 'L2503-00142'
        (SELECT v.lot_number FROM Inventory_Movements v JOIN Materials m USING (material_id)
         WHERE v.movement_type = 'ISSUE' AND m.material_class = 'COMPONENT'
         ORDER BY v.movement_id LIMIT 1)) AS lot_number
)
SELECT
    v.movement_datetime, v.movement_type, v.movement_number, m.part_number, m.description,
    v.lot_number, v.serial_number, v.certificate_ref, v.quantity,
    COALESCE(v.from_bucket, '—') || ' → ' || COALESCE(v.to_bucket, '—') AS stock_state,
    s.supplier_code, po.po_number, o.mo_number, a.registration AS aircraft,
    e.first_name || ' ' || e.last_name AS performed_by
FROM Inventory_Movements v
JOIN params p ON p.lot_number = v.lot_number
JOIN Materials m ON m.material_id = v.material_id
LEFT JOIN Purchase_Order_Lines l ON l.po_line_id = v.po_line_id
LEFT JOIN Purchase_Orders po ON po.po_id = l.po_id
LEFT JOIN Suppliers s ON s.supplier_id = po.supplier_id
LEFT JOIN Maintenance_Orders o ON o.mo_id = v.mo_id
LEFT JOIN Aircraft a ON a.aircraft_id = o.aircraft_id
JOIN Employees e ON e.employee_id = v.performed_by
ORDER BY v.movement_datetime, v.movement_id;
