-- rule: D03
-- title: A revision is SUPERSEDED if and only if it has a superseded date
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT d.document_code || ' ' || r.revision_code AS record_ref, 'Status ' || r.lifecycle_status || ' with superseded date ' || COALESCE(r.superseded_date, 'empty') AS detail
FROM Document_Revisions r JOIN Documents d USING (document_id)
WHERE (r.lifecycle_status = 'SUPERSEDED') <> (r.superseded_date IS NOT NULL);
