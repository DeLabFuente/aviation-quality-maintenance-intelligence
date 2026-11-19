# AQMI — Data Validation Report

> Generated automatically by `scripts/run_validations.py`. AEROQ MRO is fictitious and all data is synthetic.

| Item | Value |
|---|---|
| Database | `aqmi.db` |
| Data cut-off date | 2026-10-31 |
| Validation run | 2026-11-19 22:20 |
| Rules executed | 89 |
| **Quality gate** | **✅ PASSED** |
| Critical failures | 0 |
| Rules that could not run | 0 |
| Rules with warnings | 9 |
| Records flagged | 36 |
| Data Quality Score (rules passed / rules executed) | 89.9 % |

The quality gate passes when no CRITICAL rule fails, every rule runs, and the planted
discrepancies are detected exactly. WARNING findings do not block the gate: they are
the discrepancies a quality office must review.

## Results by group

| Group | Rules | Passed | Warnings | Critical failures |
|---|---|---|---|---|
| G — General | 11 | 11 | 0 | 0 |
| D — Document control | 12 | 11 | 1 | 0 |
| M — Maintenance orders | 14 | 12 | 2 | 0 |
| I — Materials & inventory | 16 | 14 | 2 | 0 |
| Q — Non-conformities | 13 | 11 | 2 | 0 |
| C — CAPA | 11 | 10 | 1 | 0 |
| L — Lessons learned | 7 | 6 | 1 | 0 |
| A — Audit & traceability | 5 | 5 | 0 | 0 |

## Planted discrepancies

The generator planted these discrepancies on purpose. The controls must find all of them, and nothing else.

| Kind | Rule | Planted | Detected | Missed | Unexpected | Result |
|---|---|---|---|---|---|---|
| OBSOLETE_REVISION_LINK | M09 | 3 | 3 | — | — | ✅ |
| RECEIPT_WITHOUT_CERTIFICATE | I09 | 2 | 2 | — | — | ✅ |
| FALSE_MATERIAL_HOLD | M08 | 2 | 2 | — | — | ✅ |
| INCIDENT_WITHOUT_LINKS | Q08 | 2 | 2 | — | — | ✅ |

## Findings

### C10 — Open action past its due date (overdue action)

Severity **WARNING** · Result **WARNING** · 2 record(s)

| Record | Detail |
|---|---|
| CA-2026-0028 | CORRECTIVE, due 2026-09-29 (32 days late), status IN_PROGRESS |
| CA-2026-0038 | CORRECTIVE, due 2026-09-21 (40 days late), status IN_PROGRESS |

### D12 — Current revision with its review date passed (expired document)

Severity **WARNING** · Result **WARNING** · 12 record(s)

| Record | Detail |
|---|---|
| PRO-LOG-002 | R00 review due 2026-04-05 (209 days overdue) |
| PRO-MNT-006 | R01 review due 2025-10-17 (379 days overdue) |
| WIN-MNT-017 | R01 review due 2026-10-12 (19 days overdue) |
| FRM-QUA-007 | R01 review due 2026-10-15 (16 days overdue) |
| FRM-MNT-008 | R01 review due 2025-07-12 (476 days overdue) |
| TDR-DOC-009 | R03 review due 2026-02-21 (252 days overdue) |
| TDR-DOC-021 | R01 review due 2025-02-06 (632 days overdue) |
| TDR-DOC-043 | R01 review due 2026-03-05 (240 days overdue) |
| TDR-DOC-047 | R01 review due 2026-10-24 (7 days overdue) |
| TDR-DOC-050 | R00 review due 2026-09-22 (39 days overdue) |
| TDR-DOC-053 | R02 review due 2026-10-20 (11 days overdue) |
| TDR-DOC-054 | R00 review due 2025-05-23 (526 days overdue) |

### I09 — Receipts of materials that require a certificate carry its reference

Severity **WARNING** · Result **WARNING** · 2 record(s)

| Record | Detail |
|---|---|
| MV-2025-00523 | Receipt of AQ-1142-06 (lot L2505-00206) without certificate reference |
| MV-2025-00870 | Receipt of AQ-3412-06 (lot L2507-00248) without certificate reference |

### I16 — Stock below minimum (available + in quarantine) with no pending purchase order

Severity **WARNING** · Result **WARNING** · 1 record(s)

| Record | Detail |
|---|---|
| AQ-3342-06 | Available and in quarantine 2.0, below minimum 3.0, nothing on order |

### L07 — Approved lesson not incorporated into a document more than 90 days after its approval

Severity **WARNING** · Result **WARNING** · 10 record(s)

| Record | Detail |
|---|---|
| LL-2025-0001 | Approved on 2025-03-04, pending incorporation for 606 days |
| LL-2025-0004 | Approved on 2025-03-26, pending incorporation for 584 days |
| LL-2025-0005 | Approved on 2025-03-26, pending incorporation for 584 days |
| LL-2025-0006 | Approved on 2025-04-07, pending incorporation for 572 days |
| LL-2025-0007 | Approved on 2025-04-04, pending incorporation for 575 days |
| LL-2025-0011 | Approved on 2025-04-30, pending incorporation for 549 days |
| LL-2025-0014 | Approved on 2025-06-05, pending incorporation for 513 days |
| LL-2025-0032 | Approved on 2025-12-23, pending incorporation for 312 days |
| LL-2026-0013 | Approved on 2026-05-19, pending incorporation for 165 days |
| LL-2026-0018 | Approved on 2026-07-30, pending incorporation for 93 days |

### M08 — A material hold corresponds to a real shortage when it was recorded

Severity **WARNING** · Result **WARNING** · 2 record(s)

| Record | Detail |
|---|---|
| WO-2025-0049 | Hold on AQ-2319-09 started 2025-03-24 while 15.0 were available (required 6.0) |
| WO-2025-0061 | Hold on AQ-1107-02 started 2025-04-18 while 16.75 were available (required 1.0) |

### M09 — An order only uses revisions in force on the date they were linked

Severity **WARNING** · Result **WARNING** · 3 record(s)

| Record | Detail |
|---|---|
| WO-2025-0125 | WIN-MNT-018 R00 linked on 2025-07-24 (superseded on 2023-10-02) |
| WO-2025-0199 | WIN-MNT-059 R00 linked on 2025-10-24 (superseded on 2024-01-09) |
| WO-2025-0203 | WIN-MNT-038 R00 linked on 2025-10-28 (superseded on 2024-01-06) |

### Q08 — A non-conformity is linked to at least one record (aircraft, order, revision, material, supplier or PO line)

Severity **WARNING** · Result **WARNING** · 2 record(s)

| Record | Detail |
|---|---|
| NC-2025-0038 | No related aircraft, order, document, material, supplier or purchase line |
| NC-2025-0059 | No related aircraft, order, document, material, supplier or purchase line |

### Q12 — Open non-conformity past its target closure date

Severity **WARNING** · Result **WARNING** · 2 record(s)

| Record | Detail |
|---|---|
| NC-2026-0024 | MINOR, target 2026-10-06 (25 days late), status IMPLEMENTATION |
| NC-2026-0025 | MINOR, target 2026-10-11 (20 days late), status EFFECTIVENESS_CHECK |

## All rules

| Rule | Title | Severity | Result | Records |
|---|---|---|---|---|
| A01 | Every operational record has its INSERT event in the audit log | WARNING | PASS | 0 |
| A02 | Every status change of orders, non-conformities, actions and lessons is in the audit log | WARNING | PASS | 0 |
| A03 | The chain of changes of a field is continuous and ends in the current value | CRITICAL | PASS | 0 |
| A04 | There is no DELETE event in the audit log | CRITICAL | PASS | 0 |
| A05 | Every audit event points to an existing record | CRITICAL | PASS | 0 |
| C01 | A corrective action has a non-conformity; origin INCIDENT if and only if it has one | CRITICAL | PASS | 0 |
| C02 | The number prefix (CA/PA) matches the action type | CRITICAL | PASS | 0 |
| C03 | Due dates are not before creation; the action is not created before the non-conformity | CRITICAL | PASS | 0 |
| C04 | A CLOSED action records the result, date and verifier of the effectiveness check | CRITICAL | PASS | 0 |
| C05 | The person verifying effectiveness is not the person responsible for the action | CRITICAL | PASS | 0 |
| C06 | Dates in order: creation <= completion <= effectiveness check <= closure | CRITICAL | PASS | 0 |
| C07 | Progress never decreases and reaches 100 % before the action is completed | CRITICAL | PASS | 0 |
| C08 | An action closed as NOT_EFFECTIVE has a follow-up action | WARNING | PASS | 0 |
| C09 | The current due date is not earlier than the original one | CRITICAL | PASS | 0 |
| C10 | Open action past its due date (overdue action) | WARNING | WARNING | 2 |
| C11 | Progress updates are between the creation and the closure of the action | CRITICAL | PASS | 0 |
| D01 | A document has at most one current revision | CRITICAL | PASS | 0 |
| D02 | Revision dates are in order (issue <= effective <= review; effective <= superseded) | CRITICAL | PASS | 0 |
| D03 | A revision is SUPERSEDED if and only if it has a superseded date | CRITICAL | PASS | 0 |
| D04 | The approver of a revision is not its author | CRITICAL | PASS | 0 |
| D05 | Every revision that is not a draft has an approver | CRITICAL | PASS | 0 |
| D06 | Revisions do not overlap: each one starts the day the previous one is superseded | CRITICAL | PASS | 0 |
| D07 | An aircraft record is linked to an aircraft | CRITICAL | PASS | 0 |
| D08 | A controlled document has a review interval and its current revision a review date | CRITICAL | PASS | 0 |
| D09 | A verification that is not CONFORM describes the discrepancy | CRITICAL | PASS | 0 |
| D10 | A NON_CONFORM verification is linked to a non-conformity | CRITICAL | PASS | 0 |
| D11 | A verification is not earlier than the issue of the revision verified | CRITICAL | PASS | 0 |
| D12 | Current revision with its review date passed (expired document) | WARNING | WARNING | 12 |
| G01 | Every foreign key points to an existing record | CRITICAL | PASS | 0 |
| G02 | Business codes are unique and follow their format | CRITICAL | PASS | 0 |
| G03 | Dates and date-times have a valid ISO format | CRITICAL | PASS | 0 |
| G04 | No event is later than the cut-off date (AS_OF_DATE) | CRITICAL | PASS | 0 |
| G05 | No operational event is earlier than the start of the period | WARNING | PASS | 0 |
| G06 | Every person acting on a record was employed on that date | CRITICAL | PASS | 0 |
| G07 | Boolean fields only contain 0 or 1 | CRITICAL | PASS | 0 |
| G08 | Movements, progress updates and the audit log cannot be modified | CRITICAL | PASS | 0 |
| G09 | No business record can be physically deleted | CRITICAL | PASS | 0 |
| G10 | Operational records identify who created them | CRITICAL | PASS | 0 |
| G11 | No logical duplicates (same content recorded twice) | WARNING | PASS | 0 |
| I01 | Each movement type moves stock between its own pair of states | CRITICAL | PASS | 0 |
| I02 | Each movement type carries its mandatory references | CRITICAL | PASS | 0 |
| I03 | No stock state is ever negative (running balance) | CRITICAL | PASS | 0 |
| I04 | The quantity received on a line does not exceed the quantity ordered | CRITICAL | PASS | 0 |
| I05 | No receipt or promised date earlier than the order date | CRITICAL | PASS | 0 |
| I06 | Material is only reserved or issued for lines of the order while it is open | CRITICAL | PASS | 0 |
| I07 | Every lot issued to an order was previously received (or counted at go-live) | CRITICAL | PASS | 0 |
| I08 | Serialized materials move one unit at a time with a serial number | CRITICAL | PASS | 0 |
| I09 | Receipts of materials that require a certificate carry its reference | WARNING | WARNING | 2 |
| I10 | Materials counted in units (EA, KIT) only have whole quantities | CRITICAL | PASS | 0 |
| I11 | The 'system' quantity of a count equals the stock calculated at that moment | CRITICAL | PASS | 0 |
| I12 | Every count difference has an adjustment of the same quantity and a comment | CRITICAL | PASS | 0 |
| I13 | No purchase order to a supplier after its suspension | CRITICAL | PASS | 0 |
| I14 | A movement to NON_CONFORMING is linked to a 'non-conforming material' incident | CRITICAL | PASS | 0 |
| I15 | No material is issued after its shelf-life expiry date | CRITICAL | PASS | 0 |
| I16 | Stock below minimum (available + in quarantine) with no pending purchase order | WARNING | WARNING | 1 |
| L01 | A lesson is proposed only from a closed action whose effectiveness was verified | CRITICAL | PASS | 0 |
| L02 | The person who approves or rejects a lesson is not the person who proposed it | CRITICAL | PASS | 0 |
| L03 | The status of a lesson matches the decision recorded (rejection always has a reason) | CRITICAL | PASS | 0 |
| L04 | Lesson dates are in order: proposal, then decision, then incorporation | CRITICAL | PASS | 0 |
| L05 | A lesson is incorporated into a controlled procedure, work instruction or form | CRITICAL | PASS | 0 |
| L06 | The incorporated revision was in force on the incorporation date and came into force after the approval | CRITICAL | PASS | 0 |
| L07 | Approved lesson not incorporated into a document more than 90 days after its approval | WARNING | WARNING | 10 |
| M01 | Planned end is not earlier than the opening date | CRITICAL | PASS | 0 |
| M02 | COMPLETED or CLOSED if and only if there is an actual end date | CRITICAL | PASS | 0 |
| M03 | CLOSED if and only if closure date and person are recorded; closure >= actual end | CRITICAL | PASS | 0 |
| M04 | CANCELLED if and only if there is a cancellation reason | CRITICAL | PASS | 0 |
| M05 | ON_HOLD if and only if the order has an active hold | CRITICAL | PASS | 0 |
| M06 | At most one active hold per reason on each order | CRITICAL | PASS | 0 |
| M07 | A material hold names the material; a documentation hold names the document | CRITICAL | PASS | 0 |
| M08 | A material hold corresponds to a real shortage when it was recorded | WARNING | WARNING | 2 |
| M09 | An order only uses revisions in force on the date they were linked | WARNING | WARNING | 3 |
| M10 | The required date of a material is within the order dates | CRITICAL | PASS | 0 |
| M11 | A COMPLETED or CLOSED order received all its material, net of returns | CRITICAL | PASS | 0 |
| M12 | Order dates are within the maintenance contract of the aircraft | CRITICAL | PASS | 0 |
| M13 | An order is not closed while a CRITICAL non-conformity linked to it is open | CRITICAL | PASS | 0 |
| M14 | Holds are within the dates of their order | CRITICAL | PASS | 0 |
| Q01 | CLOSED or CANCELLED if and only if there is a closure date, not before detection | CRITICAL | PASS | 0 |
| Q02 | A CLOSED non-conformity records who closed it and the measures adopted | CRITICAL | PASS | 0 |
| Q03 | CRITICAL and MAJOR non-conformities have a containment action | CRITICAL | PASS | 0 |
| Q04 | CRITICAL and MAJOR non-conformities have a root-cause analysis once investigated | CRITICAL | PASS | 0 |
| Q05 | A CLOSED non-conformity has all its corrective actions closed or cancelled | CRITICAL | PASS | 0 |
| Q06 | A CLOSED non-conformity (except observations) has at least one corrective action | WARNING | PASS | 0 |
| Q07 | If a non-conformity names an order and an aircraft, the aircraft is the order's | CRITICAL | PASS | 0 |
| Q08 | A non-conformity is linked to at least one record (aircraft, order, revision, material, supplier or PO line) | WARNING | WARNING | 2 |
| Q09 | The root-cause analysis is after detection and before closure | CRITICAL | PASS | 0 |
| Q10 | With 5 Whys, why_1 is filled in and the chain has no gaps | CRITICAL | PASS | 0 |
| Q11 | With Ishikawa, the 6M category is filled in | CRITICAL | PASS | 0 |
| Q12 | Open non-conformity past its target closure date | WARNING | WARNING | 2 |
| Q13 | The category is consistent with the linked records (SUP->supplier, INV->material, DOC/TRC->document or order) | WARNING | PASS | 0 |
