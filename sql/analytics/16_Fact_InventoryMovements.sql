-- AQMI analytical model — Fact_InventoryMovements: one row per stock movement
SELECT v.movement_id, v.movement_number, substr(v.movement_datetime, 1, 10) AS movement_date, v.movement_datetime,
       v.material_id, v.movement_type, v.quantity, COALESCE(v.from_bucket, 'OUTSIDE') AS from_bucket,
       COALESCE(v.to_bucket, 'OUTSIDE') AS to_bucket, o.mo_number, v.lot_number, v.certificate_ref,
       CASE WHEN v.movement_type = 'ISSUE'
            THEN (v.mo_id IS NOT NULL AND v.lot_number IS NOT NULL
                  AND (m.is_serialized = 0 OR v.serial_number IS NOT NULL)
                  AND (m.requires_release_certificate = 0 OR v.certificate_ref IS NOT NULL)) END AS is_traceable,
       ROUND(v.quantity * m.unit_cost, 2) AS movement_value
FROM Inventory_Movements v
JOIN Materials m USING (material_id)
LEFT JOIN Maintenance_Orders o ON o.mo_id = v.mo_id
ORDER BY v.movement_id;
