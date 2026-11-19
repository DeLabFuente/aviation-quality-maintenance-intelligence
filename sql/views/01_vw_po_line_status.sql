-- =============================================================================
-- AQMI — vw_po_line_status
-- One row per purchase order line: quantity received, receipt dates, status
-- and delivery performance. Received quantities are calculated from the
-- RECEIPT movements (they are not stored in the line).
-- On time = the full quantity was received on or before the promised date.
-- =============================================================================
CREATE VIEW vw_po_line_status AS
WITH receipts AS (
    SELECT po_line_id,
           SUM(quantity)                         AS qty_received,
           MIN(substr(movement_datetime, 1, 10)) AS first_receipt_date,
           MAX(substr(movement_datetime, 1, 10)) AS last_receipt_date
    FROM Inventory_Movements
    WHERE movement_type = 'RECEIPT'
    GROUP BY po_line_id
)
SELECT
    l.po_line_id, l.po_id, p.po_number, p.supplier_id, s.supplier_code, l.material_id,
    p.order_date, p.urgency, l.promised_date, p.cancelled_date, l.mo_id,
    l.qty_ordered, l.unit_price, ROUND(l.qty_ordered * l.unit_price, 2)        AS line_value,
    COALESCE(r.qty_received, 0)                                               AS qty_received,
    CASE WHEN p.cancelled_date IS NOT NULL THEN 0
         ELSE MAX(0, l.qty_ordered - COALESCE(r.qty_received, 0)) END          AS qty_pending,
    r.first_receipt_date, r.last_receipt_date,
    CASE WHEN p.cancelled_date IS NOT NULL                    THEN 'CANCELLED'
         WHEN COALESCE(r.qty_received, 0) >= l.qty_ordered    THEN 'RECEIVED'
         WHEN COALESCE(r.qty_received, 0) > 0                 THEN 'PARTIALLY_RECEIVED'
         ELSE 'OPEN' END                                                      AS line_status,
    CASE WHEN COALESCE(r.qty_received, 0) >= l.qty_ordered
         THEN CAST(MAX(0, julianday(r.last_receipt_date) - julianday(l.promised_date)) AS INTEGER)
    END                                                                       AS days_late,
    CASE WHEN COALESCE(r.qty_received, 0) >= l.qty_ordered
         THEN (r.last_receipt_date <= l.promised_date)
    END                                                                       AS is_on_time
FROM Purchase_Order_Lines l
JOIN Purchase_Orders p USING (po_id)
JOIN Suppliers s       ON s.supplier_id = p.supplier_id
LEFT JOIN receipts r   USING (po_line_id);
