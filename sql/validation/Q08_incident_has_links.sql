-- rule: Q08
-- title: A non-conformity is linked to at least one record (aircraft, order, revision, material, supplier or PO line)
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT incident_number AS record_ref, 'No related aircraft, order, document, material, supplier or purchase line' AS detail
FROM Quality_Incidents
WHERE aircraft_id IS NULL AND mo_id IS NULL AND revision_id IS NULL
  AND material_id IS NULL AND supplier_id IS NULL AND po_line_id IS NULL;
