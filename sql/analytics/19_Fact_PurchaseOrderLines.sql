-- AQMI analytical model — Fact_PurchaseOrderLines: one row per purchase order line
SELECT po_line_id, po_number, supplier_id, material_id, order_date, urgency, promised_date,
       (cancelled_date IS NOT NULL) AS is_cancelled, qty_ordered, qty_received, qty_pending, line_value,
       first_receipt_date, last_receipt_date, line_status, (line_status = 'RECEIVED') AS is_received,
       days_late, is_on_time
FROM vw_po_line_status
ORDER BY po_line_id;
