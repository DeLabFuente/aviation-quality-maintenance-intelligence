-- kpi: INV-04
-- name: Pending Purchase Orders
-- name_es: Pedidos pendientes
-- area: Inventory
-- type: SNAPSHOT
-- unit: count
-- direction: NEUTRAL
-- target: none
-- warning: none
-- frequency: Monthly
-- tables: Purchase_Orders, Purchase_Order_Lines, Inventory_Movements
-- question: How many purchase orders were sent and not yet fully received?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- SNAPSHOT: state at the end of end_date of each period (TOTAL = at the cut-off date).
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
SELECT p.period,
       COUNT(po.po_id) AS numerator,
       NULL            AS denominator,
       COUNT(po.po_id) AS value
FROM vw_kpi_periods p
LEFT JOIN Purchase_Orders po
       ON po.order_date <= p.end_date
      AND (po.cancelled_date IS NULL OR po.cancelled_date > p.end_date)
      AND EXISTS (
          SELECT 1 FROM Purchase_Order_Lines l
          WHERE l.po_id = po.po_id
            AND l.qty_ordered > COALESCE((
                SELECT SUM(v.quantity) FROM Inventory_Movements v
                WHERE v.po_line_id = l.po_line_id AND v.movement_type = 'RECEIPT'
                  AND v.movement_datetime < date(p.end_date, '+1 day')), 0))
GROUP BY p.period
ORDER BY p.period;
