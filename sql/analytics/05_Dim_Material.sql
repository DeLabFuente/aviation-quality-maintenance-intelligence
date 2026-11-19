-- AQMI analytical model — Dim_Material
SELECT m.material_id, m.part_number, m.description, m.part_number || ' · ' || m.description AS material_label,
       m.material_class, m.unit_of_measure, s.supplier_code AS preferred_supplier_code,
       m.standard_lead_time_days, m.min_stock_qty, m.reorder_qty, m.unit_cost,
       m.is_serialized, m.is_shelf_life_controlled, m.requires_release_certificate, m.is_active
FROM Materials m JOIN Suppliers s ON s.supplier_id = m.preferred_supplier_id
ORDER BY m.part_number;
