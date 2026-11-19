-- =============================================================================
-- AQMI — Query 04: materials below their minimum stock
-- Question: "What is running out, and is it already on order?"
-- =============================================================================
SELECT
    s.part_number, s.description, s.material_class, s.unit_of_measure,
    s.available_qty, s.reserved_qty, s.quarantine_qty, s.min_stock_qty, s.on_order_qty,
    sup.supplier_code AS preferred_supplier,
    (SELECT MIN(l.promised_date) FROM vw_po_line_status l
      WHERE l.material_id = s.material_id AND l.qty_pending > 0) AS next_promised_delivery,
    CASE WHEN s.on_order_qty > 0 THEN 'On order'
         WHEN s.available_qty + s.quarantine_qty >= s.min_stock_qty THEN 'In receiving inspection'
         ELSE 'ORDER NEEDED' END AS action
FROM vw_stock_by_bucket s
JOIN Suppliers sup ON sup.supplier_id = s.preferred_supplier_id
WHERE s.is_below_min = 1
ORDER BY action = 'ORDER NEEDED' DESC, s.available_qty - s.min_stock_qty;
