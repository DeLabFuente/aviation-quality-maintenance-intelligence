-- =============================================================================
-- AQMI — vw_parameters
-- One row with the cut-off date and the start of the period, read from
-- System_Parameters. Every other view measures "open", "overdue" or "expired"
-- against this date, never against the computer clock.
-- =============================================================================
CREATE VIEW vw_parameters AS
SELECT
    MAX(CASE WHEN parameter_key = 'AS_OF_DATE'   THEN parameter_value END) AS as_of_date,
    MAX(CASE WHEN parameter_key = 'PERIOD_START' THEN parameter_value END) AS period_start
FROM System_Parameters;
