-- kpi: DOC-04
-- name: Traceability Compliance
-- name_es: Cumplimiento de trazabilidad
-- area: Document control
-- type: FLOW
-- unit: %
-- direction: HIGHER_IS_BETTER
-- target: 100  (fictitious internal target of AEROQ MRO)
-- warning: 99  (fictitious internal warning level)
-- frequency: Monthly
-- tables: Inventory_Movements, Materials
-- question: Of the material issued to work orders, what share carries complete traceability data?
-- returns: one row per month (YYYY-MM) and one TOTAL row: period, numerator, denominator, value
-- =============================================================================
-- FLOW: counts the events between start_date and end_date of each period.
-- Targets are fictitious internal targets of AEROQ MRO, not regulatory thresholds.
-- Full definition: documentation/07_fase6_indicadores.md
-- =============================================================================
-- Complete = work order + lot + serial number (serialized parts only)
--            + release certificate (materials that require one).
SELECT p.period,
       COALESCE(SUM(v.mo_id IS NOT NULL AND v.lot_number IS NOT NULL
                    AND (m.is_serialized = 0 OR v.serial_number IS NOT NULL)
                    AND (m.requires_release_certificate = 0 OR v.certificate_ref IS NOT NULL)), 0) AS numerator,
       COUNT(v.movement_id)                                                                       AS denominator,
       ROUND(100.0 * SUM(v.mo_id IS NOT NULL AND v.lot_number IS NOT NULL
                         AND (m.is_serialized = 0 OR v.serial_number IS NOT NULL)
                         AND (m.requires_release_certificate = 0 OR v.certificate_ref IS NOT NULL))
             / NULLIF(COUNT(v.movement_id), 0), 1)                                                AS value
FROM vw_kpi_periods p
LEFT JOIN Inventory_Movements v
       ON v.movement_type = 'ISSUE'
      AND substr(v.movement_datetime, 1, 10) BETWEEN p.start_date AND p.end_date
LEFT JOIN Materials m ON m.material_id = v.material_id
GROUP BY p.period
ORDER BY p.period;
