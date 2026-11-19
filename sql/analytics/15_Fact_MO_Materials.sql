-- AQMI analytical model — Fact_MO_Materials: one row per material line of a work order
SELECT l.mo_material_id, l.mo_id, l.mo_number, l.aircraft_id, l.material_id, l.qty_required, l.required_by_date,
       l.first_reserved_date, l.last_issued_date, l.was_short, (l.mo_status = 'CANCELLED') AS is_cancelled_order
FROM vw_mo_material_status l
ORDER BY l.mo_material_id;
