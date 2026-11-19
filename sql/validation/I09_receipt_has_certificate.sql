-- rule: I09
-- title: Receipts of materials that require a certificate carry its reference
-- severity: WARNING
-- type: P
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT v.movement_number AS record_ref, 'Receipt of ' || m.part_number || ' (lot ' || v.lot_number || ') without certificate reference' AS detail
FROM Inventory_Movements v JOIN Materials m USING (material_id)
WHERE v.movement_type = 'RECEIPT' AND m.requires_release_certificate = 1 AND v.certificate_ref IS NULL;
