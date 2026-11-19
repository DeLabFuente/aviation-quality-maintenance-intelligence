-- rule: G02
-- title: Business codes are unique and follow their format
-- severity: CRITICAL
-- type: E
-- enforced_by: UQ + CHECK (GLOB) + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT employee_code AS record_ref, 'Employees.employee_code does not follow the format EMP-[0-9][0-9][0-9]' AS detail FROM Employees WHERE employee_code NOT GLOB 'EMP-[0-9][0-9][0-9]'
UNION ALL
SELECT employee_code, 'Employees.employee_code is duplicated (' || COUNT(*) || ' records)' FROM Employees GROUP BY employee_code HAVING COUNT(*) > 1
UNION ALL
SELECT customer_code AS record_ref, 'Customers.customer_code does not follow the format CUS-[0-9][0-9]' AS detail FROM Customers WHERE customer_code NOT GLOB 'CUS-[0-9][0-9]'
UNION ALL
SELECT customer_code, 'Customers.customer_code is duplicated (' || COUNT(*) || ' records)' FROM Customers GROUP BY customer_code HAVING COUNT(*) > 1
UNION ALL
SELECT registration AS record_ref, 'Aircraft.registration does not follow the format EC-Q[0-9][0-9]' AS detail FROM Aircraft WHERE registration NOT GLOB 'EC-Q[0-9][0-9]'
UNION ALL
SELECT registration, 'Aircraft.registration is duplicated (' || COUNT(*) || ' records)' FROM Aircraft GROUP BY registration HAVING COUNT(*) > 1
UNION ALL
SELECT supplier_code AS record_ref, 'Suppliers.supplier_code does not follow the format SUP-[0-9][0-9][0-9]' AS detail FROM Suppliers WHERE supplier_code NOT GLOB 'SUP-[0-9][0-9][0-9]'
UNION ALL
SELECT supplier_code, 'Suppliers.supplier_code is duplicated (' || COUNT(*) || ' records)' FROM Suppliers GROUP BY supplier_code HAVING COUNT(*) > 1
UNION ALL
SELECT part_number AS record_ref, 'Materials.part_number does not follow the format AQ-[0-9][0-9][0-9][0-9]-[0-9][0-9]' AS detail FROM Materials WHERE part_number NOT GLOB 'AQ-[0-9][0-9][0-9][0-9]-[0-9][0-9]'
UNION ALL
SELECT part_number, 'Materials.part_number is duplicated (' || COUNT(*) || ' records)' FROM Materials GROUP BY part_number HAVING COUNT(*) > 1
UNION ALL
SELECT document_code AS record_ref, 'Documents.document_code does not follow the format [A-Z][A-Z][A-Z]-[A-Z][A-Z][A-Z]-[0-9][0-9][0-9]' AS detail FROM Documents WHERE document_code NOT GLOB '[A-Z][A-Z][A-Z]-[A-Z][A-Z][A-Z]-[0-9][0-9][0-9]'
UNION ALL
SELECT document_code, 'Documents.document_code is duplicated (' || COUNT(*) || ' records)' FROM Documents GROUP BY document_code HAVING COUNT(*) > 1
UNION ALL
SELECT mo_number AS record_ref, 'Maintenance_Orders.mo_number does not follow the format WO-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]' AS detail FROM Maintenance_Orders WHERE mo_number NOT GLOB 'WO-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'
UNION ALL
SELECT mo_number, 'Maintenance_Orders.mo_number is duplicated (' || COUNT(*) || ' records)' FROM Maintenance_Orders GROUP BY mo_number HAVING COUNT(*) > 1
UNION ALL
SELECT incident_number AS record_ref, 'Quality_Incidents.incident_number does not follow the format NC-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]' AS detail FROM Quality_Incidents WHERE incident_number NOT GLOB 'NC-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'
UNION ALL
SELECT incident_number, 'Quality_Incidents.incident_number is duplicated (' || COUNT(*) || ' records)' FROM Quality_Incidents GROUP BY incident_number HAVING COUNT(*) > 1
UNION ALL
SELECT action_number AS record_ref, 'CAPA_Actions.action_number does not follow the format [CP]A-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]' AS detail FROM CAPA_Actions WHERE action_number NOT GLOB '[CP]A-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'
UNION ALL
SELECT action_number, 'CAPA_Actions.action_number is duplicated (' || COUNT(*) || ' records)' FROM CAPA_Actions GROUP BY action_number HAVING COUNT(*) > 1
UNION ALL
SELECT po_number AS record_ref, 'Purchase_Orders.po_number does not follow the format PO-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]' AS detail FROM Purchase_Orders WHERE po_number NOT GLOB 'PO-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'
UNION ALL
SELECT po_number, 'Purchase_Orders.po_number is duplicated (' || COUNT(*) || ' records)' FROM Purchase_Orders GROUP BY po_number HAVING COUNT(*) > 1
UNION ALL
SELECT verification_number AS record_ref, 'Document_Verifications.verification_number does not follow the format DV-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]' AS detail FROM Document_Verifications WHERE verification_number NOT GLOB 'DV-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'
UNION ALL
SELECT verification_number, 'Document_Verifications.verification_number is duplicated (' || COUNT(*) || ' records)' FROM Document_Verifications GROUP BY verification_number HAVING COUNT(*) > 1
UNION ALL
SELECT count_number AS record_ref, 'Stock_Counts.count_number does not follow the format SC-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]' AS detail FROM Stock_Counts WHERE count_number NOT GLOB 'SC-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'
UNION ALL
SELECT count_number, 'Stock_Counts.count_number is duplicated (' || COUNT(*) || ' records)' FROM Stock_Counts GROUP BY count_number HAVING COUNT(*) > 1
UNION ALL
SELECT movement_number AS record_ref, 'Inventory_Movements.movement_number does not follow the format MV-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9]' AS detail FROM Inventory_Movements WHERE movement_number NOT GLOB 'MV-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9]'
UNION ALL
SELECT movement_number, 'Inventory_Movements.movement_number is duplicated (' || COUNT(*) || ' records)' FROM Inventory_Movements GROUP BY movement_number HAVING COUNT(*) > 1
UNION ALL
SELECT lesson_number AS record_ref, 'Lessons_Learned.lesson_number does not follow the format LL-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]' AS detail FROM Lessons_Learned WHERE lesson_number NOT GLOB 'LL-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'
UNION ALL
SELECT lesson_number, 'Lessons_Learned.lesson_number is duplicated (' || COUNT(*) || ' records)' FROM Lessons_Learned GROUP BY lesson_number HAVING COUNT(*) > 1;
