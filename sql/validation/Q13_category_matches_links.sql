-- rule: Q13
-- title: The category is consistent with the linked records (SUP->supplier, INV->material, DOC/TRC->document or order)
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT i.incident_number AS record_ref, 'Category ' || c.category_code || ' without the expected linked record' AS detail
FROM Quality_Incidents i JOIN Incident_Categories c USING (category_id)
WHERE (c.category_code = 'SUP' AND i.supplier_id IS NULL AND i.po_line_id IS NULL)
   OR (c.category_code = 'INV' AND i.material_id IS NULL)
   OR (c.category_code IN ('DOC', 'TRC') AND i.revision_id IS NULL AND i.mo_id IS NULL);
