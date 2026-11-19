-- =============================================================================
-- AQMI — Query 08: recurring problems (Pareto of non-conformities)
-- Question: "Which categories concentrate most of the non-conformities, and
-- which root cause (Ishikawa 6M) dominates in each one?"
-- =============================================================================
WITH by_category AS (
    SELECT category_code, category_name_en, COUNT(*) AS incidents,
           SUM(severity IN ('CRITICAL', 'MAJOR')) AS critical_or_major,
           ROUND(AVG(resolution_days), 1) AS avg_resolution_days
    FROM vw_incident_status WHERE status <> 'CANCELLED'
    GROUP BY category_code
),
causes AS (
    SELECT c.category_code, r.ishikawa_category, COUNT(*) AS n,
           ROW_NUMBER() OVER (PARTITION BY c.category_code ORDER BY COUNT(*) DESC) AS rn
    FROM Root_Cause_Analyses r
    JOIN Quality_Incidents i USING (incident_id)
    JOIN Incident_Categories c USING (category_id)
    WHERE r.ishikawa_category IS NOT NULL
    GROUP BY c.category_code, r.ishikawa_category
)
SELECT
    b.category_code, b.category_name_en, b.incidents, b.critical_or_major, b.avg_resolution_days,
    ROUND(100.0 * b.incidents / SUM(b.incidents) OVER (), 1) AS pct,
    ROUND(100.0 * SUM(b.incidents) OVER (ORDER BY b.incidents DESC, b.category_code
                                         ROWS UNBOUNDED PRECEDING) / SUM(b.incidents) OVER (), 1) AS cumulative_pct,
    c.ishikawa_category AS main_root_cause
FROM by_category b
LEFT JOIN causes c ON c.category_code = b.category_code AND c.rn = 1
ORDER BY b.incidents DESC, b.category_code;
