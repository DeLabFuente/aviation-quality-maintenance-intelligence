-- rule: I08
-- title: Serialized materials move one unit at a time with a serial number
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT v.movement_number AS record_ref,
       m.part_number || ': quantity ' || v.quantity || ', serial ' || COALESCE(v.serial_number, 'missing') AS detail
FROM Inventory_Movements v JOIN Materials m USING (material_id)
WHERE m.is_serialized = 1 AND (v.quantity <> 1 OR v.serial_number IS NULL);
