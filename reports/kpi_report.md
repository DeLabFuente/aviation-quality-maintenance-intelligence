# AQMI — KPI Report

> Generated automatically by `scripts/run_kpis.py`. AEROQ MRO is fictitious and all data is synthetic.
> **Targets are fictitious internal targets of AEROQ MRO. They are not regulatory thresholds.**

| Item | Value |
|---|---|
| Period | 2024-11 to 2026-10 (24 months) |
| Cut-off date | 2026-10-31 |
| Report run | 2026-11-19 22:16 |
| Indicators | 19 |
| **KPI checks (K rules)** | **✅ PASSED** |

**How to read the values.** *Flow* indicators (things that happen) are given for the whole 24-month
period. *Snapshot* indicators (states such as open, overdue or blocked) are given at the cut-off date.
Year 1 = first 12 months, year 2 = last 12 months.

Traffic light: 🟢 target met · 🟡 between target and warning level · 🔴 beyond the warning level · — no target.

## Quality

| KPI | Indicator | Type | Value | Target (fictitious) | Status | Year 1 | Year 2 | Trend |
|---|---|---|---|---|---|---|---|---|
| QUA-01 | Total Quality Incidents | Flow | **141** | — | — | 86 | 55 | ↓ |
| QUA-02 | Open Non-Conformities | Snapshot | **13** | — | — | 11 | 13 | ↑ worse |
| QUA-03 | Non-Conformity Rate | Flow | **29.8** | — | — | 36.8 | 23.0 | ↓ better |
| QUA-04 | Corrective Action Closure Rate | Flow | **69.1 %** | ≥ 85.0 % | 🔴 | 🔴 73.1 % | 🔴 63.9 % | ↓ worse |
| QUA-05 | Average Resolution Time | Flow | **82.0 days** | ≤ 75.0 days | 🟡 | 🟡 75.3 days | 🔴 91.4 days | ↑ worse |
| QUA-06 | Overdue Corrective Actions | Snapshot | **2** | ≤ 0 | 🟡 | 🟡 1 | 🟡 2 | ↑ worse |

## Document control

| KPI | Indicator | Type | Value | Target (fictitious) | Status | Year 1 | Year 2 | Trend |
|---|---|---|---|---|---|---|---|---|
| DOC-01 | Document Compliance Rate | Snapshot | **94.4 %** | ≥ 95.0 % | 🟡 | 🟢 96.7 % | 🟡 94.4 % | ↓ worse |
| DOC-02 | Documentation Error Rate | Flow | **8.3 %** | ≤ 5.0 % | 🔴 | 🔴 8.7 % | 🟡 8.0 % | ↓ better |
| DOC-03 | Expired Documents | Snapshot | **12** | ≤ 0 | 🔴 | 🔴 7 | 🔴 12 | ↑ worse |
| DOC-04 | Traceability Compliance | Flow | **99.2 %** | ≥ 100.0 % | 🟡 | 🟡 99.1 % | 🟡 99.3 % | ↑ better |

## Inventory

| KPI | Indicator | Type | Value | Target (fictitious) | Status | Year 1 | Year 2 | Trend |
|---|---|---|---|---|---|---|---|---|
| INV-01 | Inventory Accuracy | Flow | **89.9 %** | ≥ 95.0 % | 🔴 | 🔴 85.6 % | 🟡 94.2 % | ↑ better |
| INV-02 | Stock Availability | Snapshot | **93.0 %** | ≥ 95.0 % | 🟡 | 🟡 93.0 % | 🟡 93.0 % | = |
| INV-03 | Material Shortage Rate | Flow | **6.6 %** | ≤ 5.0 % | 🟡 | 🟡 6.2 % | 🟡 7.0 % | ↑ worse |
| INV-04 | Pending Purchase Orders | Snapshot | **9** | — | — | 3 | 9 | ↑ |

## Maintenance

| KPI | Indicator | Type | Value | Target (fictitious) | Status | Year 1 | Year 2 | Trend |
|---|---|---|---|---|---|---|---|---|
| MNT-01 | Maintenance Order Completion Rate | Flow | **60.8 %** | ≥ 85.0 % | 🔴 | 🔴 65.5 % | 🔴 56.2 % | ↓ worse |
| MNT-02 | Average Maintenance Delay | Flow | **2.3 days** | ≤ 2.0 days | 🟡 | 🟡 2.2 days | 🟡 2.3 days | ↑ worse |
| MNT-03 | Work Orders Blocked by Material | Snapshot | **4** | — | — | 1 | 4 | ↑ worse |
| MNT-04 | Work Orders Blocked by Documentation | Snapshot | **0** | — | — | 0 | 0 | = |

## Continuous improvement

| KPI | Indicator | Type | Value | Target (fictitious) | Status | Year 1 | Year 2 | Trend |
|---|---|---|---|---|---|---|---|---|
| LRN-01 | Lesson Incorporation Rate | Snapshot | **76.9 %** | ≥ 80.0 % | 🟡 | 🔴 44.0 % | 🟡 76.9 % | ↑ better |

## KPI checks

| Rule | Check | Result | Findings |
|---|---|---|---|
| K01 | Every percentage is between 0 and 100; no value is negative | ✅ PASS | 0 |
| K02 | A zero denominator gives 'no data', never 0 % | ✅ PASS | 0 |
| K04 | The parts add up to the total | ✅ PASS | 0 |
| K05 | Each state-at-a-date KPI, rebuilt from history, equals the current state at the cut-off date | ✅ PASS | 0 |
| K03 | Power BI shows the same value as the SQL reference query | Phase 9 | — |

## Last 12 months

Monthly values. The full series (24 months) is in `kpi_values.csv`.

| KPI | 2025-11 | 2025-12 | 2026-01 | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 | 2026-10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DOC-01 | 97.2 | 96.3 | 95.8 | 95.8 | 94.9 | 95.8 | 93.5 | 93.9 | 94.9 | 95.3 | 95.3 | 94.4 |
| DOC-02 | 9.7 | 10.8 | 8.1 | 6.5 | 6.3 | 10.7 | 11.8 | 10.7 | 2.4 | 13.3 | 8 | 0 |
| DOC-03 | 6 | 8 | 9 | 9 | 11 | 9 | 14 | 13 | 11 | 10 | 10 | 12 |
| DOC-04 | 100 | 98.7 | 100 | 100 | 98.4 | 97.8 | 100 | 96 | 100 | 100 | 100 | 100 |
| INV-01 | 100 | 90 | 87.5 | 100 | 95 | 93.8 | 93.8 | 95 | 93.8 | 93.8 | 100 | 87.5 |
| INV-02 | 92 | 98 | 97 | 98 | 95 | 97 | 96 | 97 | 98 | 96 | 95 | 93 |
| INV-03 | 16.3 | 6.3 | 10.6 | 10.8 | 4.3 | 0 | 6.3 | 9.1 | 0 | 2.8 | 9.4 | 7.7 |
| INV-04 | 7 | 7 | 4 | 3 | 3 | 3 | 4 | 6 | 4 | 4 | 5 | 9 |
| MNT-01 | 59.1 | 68 | 47.6 | 76.5 | 55.6 | 71.4 | 56.5 | 55.6 | 34.6 | 57.1 | 41.2 | 59.3 |
| MNT-02 | 2.3 | 2.7 | 2.8 | 1.9 | 2.6 | 2.1 | 1.4 | 2.3 | 3.2 | 1.5 | 3.2 | 1.9 |
| MNT-03 | 3 | 1 | 0 | 1 | 0 | 0 | 2 | 3 | 0 | 1 | 0 | 4 |
| MNT-04 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| QUA-01 | 8 | 4 | 2 | 4 | 3 | 2 | 8 | 3 | 5 | 8 | 5 | 3 |
| QUA-02 | 17 | 17 | 14 | 13 | 12 | 9 | 12 | 11 | 13 | 17 | 15 | 13 |
| QUA-03 | 42.1 | 14.8 | 9.5 | 22.2 | 16.7 | 13.3 | 36.4 | 17.6 | 18.5 | 57.1 | 31.3 | 12 |
| QUA-04 | 66.7 | 75 | 28.6 | 50 | 40 | 83.3 | 66.7 | 80 | 100 | 62.5 | 40 | 80 |
| QUA-05 | 75 | 74.5 | 121 | 111.4 | 121 | 71.4 | 128.8 | 75.3 | 70 | 63.5 | 90.6 | 69.6 |
| QUA-06 | 1 | 2 | 3 | 1 | 1 | 0 | 0 | 1 | 0 | 2 | 3 | 2 |
| LRN-01 | 40.7 | 50 | 50 | 65.6 | 64.9 | 66.7 | 64.3 | 67.4 | 71.1 | 65.3 | 78 | 76.9 |
