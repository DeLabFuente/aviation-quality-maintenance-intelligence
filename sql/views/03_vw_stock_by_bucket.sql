-- =============================================================================
-- AQMI — vw_stock_by_bucket
-- Stock of every material by state, calculated from ALL the movements (the
-- stock is never stored, so it can never disagree with its movements).
-- =============================================================================
CREATE VIEW vw_stock_by_bucket AS
WITH flows AS (
    SELECT material_id, to_bucket AS bucket, quantity AS qty
    FROM Inventory_Movements WHERE to_bucket IS NOT NULL
    UNION ALL
    SELECT material_id, from_bucket, -quantity
    FROM Inventory_Movements WHERE from_bucket IS NOT NULL
),
balances AS (
    SELECT material_id,
           ROUND(SUM(CASE WHEN bucket = 'QUARANTINE'     THEN qty ELSE 0 END), 3) AS quarantine_qty,
           ROUND(SUM(CASE WHEN bucket = 'AVAILABLE'      THEN qty ELSE 0 END), 3) AS available_qty,
           ROUND(SUM(CASE WHEN bucket = 'RESERVED'       THEN qty ELSE 0 END), 3) AS reserved_qty,
           ROUND(SUM(CASE WHEN bucket = 'BLOCKED'        THEN qty ELSE 0 END), 3) AS blocked_qty,
           ROUND(SUM(CASE WHEN bucket = 'NON_CONFORMING' THEN qty ELSE 0 END), 3) AS non_conforming_qty
    FROM flows GROUP BY material_id
),
on_order AS (
    SELECT material_id, SUM(qty_pending) AS on_order_qty
    FROM vw_po_line_status GROUP BY material_id
)
SELECT
    m.material_id, m.part_number, m.description, m.material_class, m.unit_of_measure,
    m.preferred_supplier_id, m.min_stock_qty, m.reorder_qty, m.unit_cost,
    COALESCE(b.quarantine_qty, 0)     AS quarantine_qty,
    COALESCE(b.available_qty, 0)      AS available_qty,
    COALESCE(b.reserved_qty, 0)       AS reserved_qty,
    COALESCE(b.blocked_qty, 0)        AS blocked_qty,
    COALESCE(b.non_conforming_qty, 0) AS non_conforming_qty,
    ROUND(COALESCE(b.quarantine_qty, 0) + COALESCE(b.available_qty, 0) + COALESCE(b.reserved_qty, 0)
          + COALESCE(b.blocked_qty, 0) + COALESCE(b.non_conforming_qty, 0), 3) AS on_hand_qty,
    COALESCE(o.on_order_qty, 0)       AS on_order_qty,
    ROUND((COALESCE(b.available_qty, 0) + COALESCE(b.reserved_qty, 0)) * m.unit_cost, 2) AS usable_stock_value,
    CASE WHEN COALESCE(b.available_qty, 0) < m.min_stock_qty THEN 1 ELSE 0 END          AS is_below_min
FROM Materials m
LEFT JOIN balances b USING (material_id)
LEFT JOIN on_order o USING (material_id);
