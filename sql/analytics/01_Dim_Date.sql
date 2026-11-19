-- AQMI analytical model (Phase 7) — Dim_Date: one row per day of the simulated period.
WITH RECURSIVE days(d) AS (
    SELECT period_start FROM vw_parameters
    UNION ALL
    SELECT date(days.d, '+1 day') FROM days CROSS JOIN vw_parameters p WHERE days.d < p.as_of_date
),
base AS (
    SELECT d, CAST(strftime('%Y', d) AS INTEGER) AS y, CAST(strftime('%m', d) AS INTEGER) AS m FROM days
)
SELECT
    b.d                                                                      AS date,
    b.y                                                                      AS year,
    'Q' || ((b.m + 2) / 3)                                                   AS quarter,
    b.y || ' Q' || ((b.m + 2) / 3)                                           AS year_quarter,
    b.y * 10 + (b.m + 2) / 3                                                 AS year_quarter_num,
    b.m                                                                      AS month_number,
    substr('JanFebMarAprMayJunJulAugSepOctNovDec', 3 * b.m - 2, 3)           AS month_name,
    substr('JanFebMarAprMayJunJulAugSepOctNovDec', 3 * b.m - 2, 3) || ' ' || b.y AS month_label,
    strftime('%Y-%m', b.d)                                                   AS year_month,
    b.y * 100 + b.m                                                          AS year_month_num,
    date(b.d, 'start of month')                                              AS month_start,
    date(b.d, 'start of month', '+1 month', '-1 day')                        AS month_end,
    CASE WHEN b.d < date(p.period_start, '+12 months') THEN 'Year 1' ELSE 'Year 2' END AS period_year,
    CASE WHEN b.d < date(p.period_start, '+12 months')
         THEN 'Year 1 · Nov 2024 – Oct 2025' ELSE 'Year 2 · Nov 2025 – Oct 2026' END AS period_year_label,
    (b.d = date(b.d, 'start of month', '+1 month', '-1 day'))                AS is_month_end
FROM base b CROSS JOIN vw_parameters p
ORDER BY b.d;
