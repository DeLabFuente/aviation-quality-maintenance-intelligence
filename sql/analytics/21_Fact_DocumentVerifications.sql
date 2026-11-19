-- AQMI analytical model — Fact_DocumentVerifications: one row per verification of a document or record
SELECT v.verification_id, v.verification_number, v.verification_date, r.document_id, r.revision_code,
       v.verification_type, v.result, (v.result <> 'CONFORM') AS is_error,
       (v.verification_type <> 'INTERNAL_AUDIT') AS is_routine, v.verified_by, o.mo_number,
       (v.incident_id IS NOT NULL) AS raised_incident
FROM Document_Verifications v
JOIN Document_Revisions r USING (revision_id)
LEFT JOIN Maintenance_Orders o ON o.mo_id = v.mo_id
ORDER BY v.verification_id;
