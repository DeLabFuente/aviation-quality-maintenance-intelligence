-- rule: G01
-- title: Every foreign key points to an existing record
-- severity: CRITICAL
-- type: E
-- enforced_by: FK + PRAGMA foreign_keys + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT "table" || ' #' || rowid AS record_ref,
       'Reference to ' || parent || ' not found' AS detail
FROM pragma_foreign_key_check;
