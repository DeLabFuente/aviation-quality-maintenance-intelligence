-- AQMI analytical model — Dim_Supplier (approval status at the cut-off date)
SELECT supplier_id, supplier_code, supplier_name, supplier_code || ' · ' || supplier_name AS supplier_label,
       country_code, supplier_type, approval_status
FROM Suppliers ORDER BY supplier_code;
