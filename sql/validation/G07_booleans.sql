-- rule: G07
-- title: Boolean fields only contain 0 or 1
-- severity: CRITICAL
-- type: E
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT department_code AS record_ref, 'Departments.is_active = ' || is_active || ' (only 0 or 1 allowed)' AS detail FROM Departments WHERE is_active NOT IN (0, 1)
UNION ALL
SELECT employee_code AS record_ref, 'Employees.is_department_head = ' || is_department_head || ' (only 0 or 1 allowed)' AS detail FROM Employees WHERE is_department_head NOT IN (0, 1)
UNION ALL
SELECT part_number AS record_ref, 'Materials.is_serialized = ' || is_serialized || ' (only 0 or 1 allowed)' AS detail FROM Materials WHERE is_serialized NOT IN (0, 1)
UNION ALL
SELECT part_number AS record_ref, 'Materials.is_shelf_life_controlled = ' || is_shelf_life_controlled || ' (only 0 or 1 allowed)' AS detail FROM Materials WHERE is_shelf_life_controlled NOT IN (0, 1)
UNION ALL
SELECT part_number AS record_ref, 'Materials.requires_release_certificate = ' || requires_release_certificate || ' (only 0 or 1 allowed)' AS detail FROM Materials WHERE requires_release_certificate NOT IN (0, 1)
UNION ALL
SELECT part_number AS record_ref, 'Materials.is_active = ' || is_active || ' (only 0 or 1 allowed)' AS detail FROM Materials WHERE is_active NOT IN (0, 1)
UNION ALL
SELECT document_code AS record_ref, 'Documents.is_controlled = ' || is_controlled || ' (only 0 or 1 allowed)' AS detail FROM Documents WHERE is_controlled NOT IN (0, 1)
UNION ALL
SELECT category_code AS record_ref, 'Incident_Categories.is_active = ' || is_active || ' (only 0 or 1 allowed)' AS detail FROM Incident_Categories WHERE is_active NOT IN (0, 1);
