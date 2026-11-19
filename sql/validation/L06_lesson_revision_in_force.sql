-- rule: L06
-- title: The incorporated revision was in force on the incorporation date and came into force after the approval
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
-- Exception (decision approved in Phase 9): when the revision is the
-- output of the action itself (it came into force between the creation and the
-- closure of the action), the lesson is already incorporated when it is approved.
-- Example: NC-2025-0021, whose corrective action was the redesign of FRM-PRD-004 (R01).
SELECT l.lesson_number AS record_ref,
       d.document_code || ' ' || r.revision_code || ' was not in force on ' || l.incorporated_date ||
       ' (status ' || r.lifecycle_status || ', in force ' || r.effective_date || ' to ' ||
       COALESCE(r.superseded_date, 'today') || ')' AS detail
FROM Lessons_Learned l
JOIN Document_Revisions r ON r.revision_id = l.incorporated_revision_id
JOIN Documents d ON d.document_id = r.document_id
WHERE r.lifecycle_status NOT IN ('CURRENT', 'SUPERSEDED')
   OR r.effective_date > l.incorporated_date
   OR (r.superseded_date IS NOT NULL AND r.superseded_date <= l.incorporated_date)
UNION ALL
SELECT l.lesson_number,
       d.document_code || ' ' || r.revision_code || ' came into force on ' || r.effective_date ||
       ', not after the approval of the lesson on ' || l.approved_date
FROM Lessons_Learned l
JOIN Document_Revisions r ON r.revision_id = l.incorporated_revision_id
JOIN Documents d ON d.document_id = r.document_id
JOIN CAPA_Actions a ON a.action_id = l.action_id
WHERE r.effective_date <= l.approved_date
  AND NOT (r.effective_date BETWEEN a.created_date AND a.closed_date);   -- approved exception
