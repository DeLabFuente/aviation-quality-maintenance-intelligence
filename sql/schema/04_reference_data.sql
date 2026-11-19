-- =============================================================================
-- AQMI — Aviation Quality & Maintenance Intelligence
-- File:    sql/schema/04_reference_data.sql
-- Purpose: Fixed reference catalogues defined in Phase 2:
--            * the 6 departments of AEROQ MRO
--            * the 8 non-conformity categories
--          Operational data (employees, aircraft, orders...) is NOT loaded here:
--          it is generated in Phase 4.
-- =============================================================================

INSERT INTO Departments (department_code, department_name, created_at) VALUES
    ('QUA', 'Quality',                         '2024-11-01 08:00:00'),
    ('MNT', 'Maintenance',                     '2024-11-01 08:00:00'),
    ('PRD', 'Production Planning & Control',   '2024-11-01 08:00:00'),
    ('DOC', 'Document Control',                '2024-11-01 08:00:00'),
    ('LOG', 'Logistics & Materials',           '2024-11-01 08:00:00'),
    ('DIR', 'Management',                      '2024-11-01 08:00:00');

INSERT INTO Incident_Categories
    (category_code, category_name_es, category_name_en, description, default_department_id)
VALUES
    ('DOC', 'Documentación incorrecta', 'Incorrect documentation',
     'A document is wrong, incomplete, obsolete or not approved.',
     (SELECT department_id FROM Departments WHERE department_code = 'DOC')),

    ('REC', 'Error de registro', 'Recording error',
     'Information recorded in the system does not match its source document.',
     (SELECT department_id FROM Departments WHERE department_code = 'PRD')),

    ('INV', 'Discrepancia de inventario', 'Inventory discrepancy',
     'Physical stock differs from the stock recorded in the system.',
     (SELECT department_id FROM Departments WHERE department_code = 'LOG')),

    ('MNC', 'Material no conforme', 'Non-conforming material',
     'Material received or held in stock does not meet its requirements.',
     (SELECT department_id FROM Departments WHERE department_code = 'LOG')),

    ('PRC', 'Incumplimiento de procedimiento', 'Procedure non-compliance',
     'An internal procedure was not followed.',
     (SELECT department_id FROM Departments WHERE department_code = 'QUA')),

    ('TRC', 'Error de trazabilidad', 'Traceability error',
     'A record cannot be traced to its origin (lot, certificate, revision or order).',
     (SELECT department_id FROM Departments WHERE department_code = 'QUA')),

    ('MNT', 'Incidencia de mantenimiento', 'Maintenance issue',
     'Administrative issue arising during a maintenance order (no technical assessment).',
     (SELECT department_id FROM Departments WHERE department_code = 'MNT')),

    ('SUP', 'Problema de suministro', 'Supply problem',
     'Late, incomplete or incorrect delivery from a supplier.',
     (SELECT department_id FROM Departments WHERE department_code = 'LOG'));
