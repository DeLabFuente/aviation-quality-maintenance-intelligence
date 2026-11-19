-- =============================================================================
-- AQMI — vw_po_status
-- One row per purchase order with its status calculated from its lines.
-- is_pending = 1 for orders sent and not completely received (KPI "Pending
-- Purchase Orders").
-- =============================================================================
CREATE VIEW vw_po_status AS
SELECT
    p.po_id, p.po_number, p.supplier_id, s.supplier_code, s.supplier_name,
    p.order_date, p.urgency, p.buyer_id, p.cancelled_date,
    COUNT(*)                                       AS n_lines,
    ROUND(SUM(l.line_value), 2)                    AS order_value,
    SUM(l.line_status = 'RECEIVED')                AS n_lines_received,
    MAX(l.last_receipt_date)                       AS last_receipt_date,
    CASE WHEN p.cancelled_date IS NOT NULL                 THEN 'CANCELLED'
         WHEN SUM(l.line_status = 'RECEIVED') = COUNT(*)   THEN 'RECEIVED'
         WHEN SUM(l.qty_received) > 0                      THEN 'PARTIALLY_RECEIVED'
         ELSE 'SENT' END                           AS po_status,
    CASE WHEN p.cancelled_date IS NULL
          AND SUM(l.line_status = 'RECEIVED') < COUNT(*) THEN 1 ELSE 0 END AS is_pending
FROM Purchase_Orders p
JOIN Suppliers s          ON s.supplier_id = p.supplier_id
JOIN vw_po_line_status l  ON l.po_id = p.po_id
GROUP BY p.po_id;
