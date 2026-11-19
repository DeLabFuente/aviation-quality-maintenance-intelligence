-- AQMI analytical model — Fact_PO_Snapshot: purchase orders pending (sent, not fully received) at each month end
SELECT p.end_date AS snapshot_date, po.po_id, po.po_number, po.supplier_id, po.urgency
FROM vw_kpi_periods p
JOIN Purchase_Orders po
  ON po.order_date <= p.end_date
 AND (po.cancelled_date IS NULL OR po.cancelled_date > p.end_date)
 AND EXISTS (
     SELECT 1 FROM Purchase_Order_Lines l
     WHERE l.po_id = po.po_id
       AND l.qty_ordered > COALESCE((SELECT SUM(v.quantity) FROM Inventory_Movements v
                                     WHERE v.po_line_id = l.po_line_id AND v.movement_type = 'RECEIPT'
                                       AND v.movement_datetime < date(p.end_date, '+1 day')), 0))
WHERE p.is_total = 0
ORDER BY p.end_date, po.po_id;
