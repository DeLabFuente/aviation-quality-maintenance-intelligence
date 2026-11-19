-- =============================================================================
-- AQMI — View vw_kpi_periods (Phase 6)
-- The reporting calendar of the indicators: one row per month of the simulated
-- period, plus one TOTAL row for the whole period.
--   * FLOW indicators (things that happen: incidents detected, counts made…)
--     count the events between start_date and end_date.
--   * SNAPSHOT indicators (states: open, overdue, blocked…) are measured at the
--     end of end_date. For TOTAL, that is the cut-off date.
-- =============================================================================
CREATE VIEW vw_kpi_periods AS
WITH RECURSIVE months(month_start) AS (
    SELECT date(period_start, 'start of month') FROM vw_parameters
    UNION ALL
    SELECT date(m.month_start, '+1 month')
    FROM months m CROSS JOIN vw_parameters p
    WHERE date(m.month_start, '+1 month') <= p.as_of_date
)
SELECT strftime('%Y-%m', m.month_start)                          AS period,
       MAX(m.month_start, p.period_start)                         AS start_date,
       MIN(date(m.month_start, '+1 month', '-1 day'), p.as_of_date) AS end_date,
       0                                                          AS is_total
FROM months m CROSS JOIN vw_parameters p
UNION ALL
SELECT 'TOTAL', period_start, as_of_date, 1 FROM vw_parameters;
