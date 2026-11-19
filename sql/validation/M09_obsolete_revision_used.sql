-- rule: M09
-- title: An order only uses revisions in force on the date they were linked
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT o.mo_number AS record_ref,
       d.document_code || ' ' || r.revision_code || ' linked on ' || l.linked_date ||
       CASE WHEN r.effective_date > l.linked_date THEN ' (not yet in force)'
            ELSE ' (superseded on ' || r.superseded_date || ')' END AS detail
FROM Maintenance_Order_Documents l
JOIN Maintenance_Orders o USING (mo_id)
JOIN Document_Revisions r USING (revision_id)
JOIN Documents d ON d.document_id = r.document_id
WHERE r.effective_date > l.linked_date OR r.superseded_date < l.linked_date;
