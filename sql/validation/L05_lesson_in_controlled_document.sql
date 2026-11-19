-- rule: L05
-- title: A lesson is incorporated into a controlled procedure, work instruction or form
-- severity: CRITICAL
-- type: P
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT l.lesson_number AS record_ref,
       'Incorporated into ' || d.document_code || ' ' || r.revision_code || ' (' || d.document_type ||
       CASE WHEN d.is_controlled = 1 THEN ', controlled' ELSE ', not controlled' END || ')' AS detail
FROM Lessons_Learned l
JOIN Document_Revisions r ON r.revision_id = l.incorporated_revision_id
JOIN Documents d ON d.document_id = r.document_id
WHERE d.is_controlled <> 1
   OR d.document_type NOT IN ('PROCEDURE', 'WORK_INSTRUCTION', 'FORM');
