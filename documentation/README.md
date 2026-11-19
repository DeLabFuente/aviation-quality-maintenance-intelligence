# AQMI — Documentation

The technical documentation is written in Spanish, one document per phase of the project. The case study is in English.

| # | Document | Content |
|---|---|---|
| — | [Case study — NC-2025-0021](case_study_nonconformity.md) (English) | One non-conformity from detection to verified closure and its lesson learned, with its audit trail and the evidence that the action worked |
| 01 | [Fase 1 — Alcance y arquitectura](01_fase1_alcance_y_arquitectura.md) | Scope, architecture, modules, preliminary data model, KPI catalogue, visual identity, regulatory context, decisions |
| 02 | [Fase 2 — Diccionario de datos](02_diccionario_de_datos.md) | Every table and column: type, constraints, keys, cardinalities |
| 03 | [Fase 2 — Reglas de negocio](03_reglas_de_negocio.md) | Business rules and where each one is enforced (constraint, trigger or validation rule) |
| 04 | [Fase 3 — Entorno y base de datos](04_fase3_entorno_y_base_de_datos.md) | Step-by-step installation of Python, the virtual environment and the database |
| 05 | [Fase 4 — Datos sintéticos](05_fase4_datos_sinteticos.md) | The simulator, volumes, the four planted patterns and the nine planted discrepancies |
| 06 | [Fase 5 — Consultas y validaciones](06_fase5_consultas_y_validaciones.md) | The 82 validation rules of Phase 5 (89 after Phase 9), the quality gate and the eight business queries |
| 07 | [Fase 6 — Indicadores](07_fase6_indicadores.md) | Definition of the 18 KPIs (plus LRN-01, Phase 9), fictitious targets and the KPI checks |
| 08 | [Fase 7 — Power BI](08_fase7_power_bi.md) | Star schema, DAX measures, the eight pages, visual identity and how the project is checked |
| 09 | [Fase 8 — Documentación y GitHub](09_fase8_documentacion_y_github.md) | README, case study, pre-publication check, continuous integration and how the repository is published |
| 10 | [Fase 9 — Pruebas finales y revisión profesional](10_fase9_pruebas_y_revision.md) | Windows test, professional review, visual polish, K03 check in Power BI, new screenshots and PDF, release v1.0 |
| 09b | [Fase 9 — Lecciones aprendidas](09b_fase9_lecciones_aprendidas.md) | The lessons-learned register: design, rules L01–L07, data generation, KPI LRN-01, Power BI block, tests and the decisions taken |

Generated reports are in [`../reports`](../reports): validation report, KPI report and pre-publication check.
