# Case study — NC-2025-0021: from detection to verified closure

> **Synthetic data.** AEROQ MRO is a fictitious company and every person, aircraft and record below is synthetic. This document is generated from the AQMI database by `scripts/build_case_study.py`; every date and figure can be checked with the queries indicated.

This case follows one non-conformity through the whole quality cycle: detection, investigation, root-cause analysis, corrective action, effectiveness verification and formal closure. It also checks, with data, whether the action worked.

## 1. The finding

| Field | Value |
|---|---|
| Non-conformity | **NC-2025-0021** — Date discrepancy between task record and system |
| Category / severity / priority | Recording error · Minor · P2 |
| Detected | 21 Mar 2025, during a document verification, by Andrés García Martínez |
| Related records | Aircraft EC-Q08 (AQ-H08) · maintenance order WO-2025-0037 (unscheduled) · document FRM-PRD-004 R00 (Form – Work order closure record) |
| Responsible department / owner | Production Planning & Control · Natalia Gutiérrez López |
| Target closure date | 19 Jun 2025 |

Date discrepancy between task record and system. Detected during a document verification.

## 2. Investigation and root cause

- **Method:** Ishikawa (cause-and-effect) diagram, by Natalia Gutiérrez López on 03 Apr 2025.
- **Cause category:** Method (the way the work is done, not the people or the material).
- **Root cause:** Records were transcribed at the end of the shift instead of at the time of the task.

## 3. Action plan

| Action | Type | What | Responsible | Due | Completed |
|---|---|---|---|---|---|
| CA-2025-0028 | Corrective | **Redesign the work order closure record FRM-PRD-004.** Redesign the form so that mandatory fields are evident; brief production staff. | Andrés García Martínez | 05 May 2025 | 28 Apr 2025 |

## 4. Effectiveness verification and closure

- CA-2025-0028 was verified on 20 May 2025 by Beatriz Garrido Ramos: **Effective** — No recurrence observed since implementation.
- The non-conformity was closed on 20 May 2025: Measures adopted: Redesign the work order closure record FRM-PRD-004.
- From detection to closure: **60 days**, before the target closure date (19 Jun 2025).

The action was closed only **after** an independent effectiveness check, and the non-conformity only after its action. The database enforces this order: its constraints reject closing an action without an effectiveness result, a check date and a verifier, and the verifier cannot be the person responsible for the action. Validation rules then check the dates of the whole cycle.

## 5. Did it work? What the data shows

Record-versus-source checks of work order closure records, by revision of form FRM-PRD-004:

| Form revision | In force from | Records checked | With discrepancies | Rate |
|---|---|---|---|---|
| R00 | 20 Mar 2024 | 115 | 19 | 16.5 % |
| R01 | 07 May 2025 | 353 | 18 | 5.1 % |

The discrepancy rate fell by about two thirds after the redesigned form came into force. In this synthetic dataset the pattern was introduced on purpose, so that the dashboards have a documented cause and effect to show (see section 4 of the [Phase 4 document](05_fase4_datos_sinteticos.md), in Spanish). In a real organisation the same comparison is the evidence that the action was effective.

## 6. Full audit trail

The creation and every field change of the non-conformity and of its action come from `Audit_Log`, which database triggers write on every insert and update, so no change can bypass the log. The root-cause analysis and the progress updates come from their own tables.

| When | Item | Reference | Event | Who |
|---|---|---|---|---|
| 2025-03-21 09:08 | Non-conformity | NC-2025-0021 | Created | Andrés García Martínez |
| 2025-03-25 10:11 | Non-conformity | NC-2025-0021 | status: OPEN → UNDER_INVESTIGATION | Natalia Gutiérrez López |
| 2025-04-03 10:23 | Action | CA-2025-0028 | Created: Redesign the work order closure record FRM-PRD-004 | Natalia Gutiérrez López |
| 2025-04-03 10:23 | Non-conformity | NC-2025-0021 | status: UNDER_INVESTIGATION → ACTION_PLAN | Natalia Gutiérrez López |
| 2025-04-03 10:23 | Root-cause analysis | ISHIKAWA | METHOD — Records were transcribed at the end of the shift instead of at the time of the task. | Natalia Gutiérrez López |
| 2025-04-03 15:44 | Non-conformity | NC-2025-0021 | status: ACTION_PLAN → IMPLEMENTATION | Natalia Gutiérrez López |
| 2025-04-11 12:15 | Action | CA-2025-0028 | status: OPEN → IN_PROGRESS | Andrés García Martínez |
| 2025-04-11 12:15 | Progress | CA-2025-0028 | 35 % — Implementation in progress (35 %) | Andrés García Martínez |
| 2025-04-21 09:23 | Progress | CA-2025-0028 | 65 % — Implementation in progress (65 %) | Andrés García Martínez |
| 2025-04-28 14:21 | Action | CA-2025-0028 | completed_date: — → 2025-04-28 | Andrés García Martínez |
| 2025-04-28 14:21 | Action | CA-2025-0028 | status: IN_PROGRESS → COMPLETED | Andrés García Martínez |
| 2025-04-28 14:21 | Non-conformity | NC-2025-0021 | status: IMPLEMENTATION → EFFECTIVENESS_CHECK | Natalia Gutiérrez López |
| 2025-04-28 14:21 | Progress | CA-2025-0028 | 100 % — Action implemented | Andrés García Martínez |
| 2025-05-20 12:05 | Action | CA-2025-0028 | status: COMPLETED → CLOSED | Beatriz Garrido Ramos |
| 2025-05-20 12:05 | Action | CA-2025-0028 | effectiveness_check_date: — → 2025-05-20 | Beatriz Garrido Ramos |
| 2025-05-20 12:05 | Action | CA-2025-0028 | effectiveness_result: — → EFFECTIVE | Beatriz Garrido Ramos |
| 2025-05-20 12:05 | Action | CA-2025-0028 | effectiveness_comment: — → No recurrence observed since implementation. | Beatriz Garrido Ramos |
| 2025-05-20 12:05 | Action | CA-2025-0028 | verified_by: — → 4 | Beatriz Garrido Ramos |
| 2025-05-20 12:05 | Action | CA-2025-0028 | closed_date: — → 2025-05-20 | Beatriz Garrido Ramos |
| 2025-05-20 12:05 | Non-conformity | NC-2025-0021 | status: EFFECTIVENESS_CHECK → CLOSED | Pablo López Garrido |
| 2025-05-20 12:05 | Non-conformity | NC-2025-0021 | closed_date: — → 2025-05-20 | Pablo López Garrido |
| 2025-05-20 12:05 | Non-conformity | NC-2025-0021 | closed_by: — → 5 | Pablo López Garrido |
| 2025-05-20 12:05 | Non-conformity | NC-2025-0021 | closure_summary: — → Measures adopted: Redesign the work order closure record FRM-PRD-004. | Pablo López Garrido |

## 7. How to reproduce it

- **SQL:** run [`sql/queries/01_nonconformity_full_history.sql`](../sql/queries/01_nonconformity_full_history.sql) on `database/aqmi.db` (for example in DB Browser for SQLite). Write another number in the first lines to follow any other non-conformity.
- **Power BI:** page *Audit & Traceability*: choose *Quality_Incidents* in the *Table* filter and NC-2025-0021 in the *Record* filter. The *Audit trail* table shows the history of the non-conformity record.
- **Regenerate this document:** `python scripts/build_case_study.py`.
