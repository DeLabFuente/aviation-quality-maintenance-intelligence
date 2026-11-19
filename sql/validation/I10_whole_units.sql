-- rule: I10
-- title: Materials counted in units (EA, KIT) only have whole quantities
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT v.movement_number AS record_ref, m.part_number || ': ' || v.quantity || ' ' || m.unit_of_measure AS detail
FROM Inventory_Movements v JOIN Materials m USING (material_id)
WHERE m.unit_of_measure IN ('EA', 'KIT') AND v.quantity <> CAST(v.quantity AS INTEGER);
