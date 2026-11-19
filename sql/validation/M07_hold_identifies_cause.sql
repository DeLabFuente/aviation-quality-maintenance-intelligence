-- rule: M07
-- title: A material hold names the material; a documentation hold names the document
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT o.mo_number AS record_ref, h.hold_reason || ' hold without its material or document' AS detail
FROM Maintenance_Order_Holds h JOIN Maintenance_Orders o USING (mo_id)
WHERE (h.hold_reason = 'MATERIAL' AND h.material_id IS NULL)
   OR (h.hold_reason = 'DOCUMENTATION' AND h.document_id IS NULL);
