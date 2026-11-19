-- AQMI analytical model — Dim_IncidentCategory
SELECT category_id, category_code, category_name_en AS category_name, category_name_es,
       category_code || ' · ' || category_name_en AS category_label
FROM Incident_Categories ORDER BY category_code;
