"""
AQMI — Phase 7: generate the Power BI project (.pbip) from code.

A .pbip project is Power BI saved as text files instead of a single binary .pbix:
    powerbi/AQMI.pbip                 the file you double-click to open in Power BI Desktop
    powerbi/AQMI.SemanticModel/       the data model, written in TMDL (tables, relationships, DAX measures)
    powerbi/AQMI.Report/              the report, written in PBIR (one JSON file per page and per visual)

This script creates the FIRST VERSION of that project from the analytical model
exported by scripts/export_powerbi.py (data/processed/_schema.json). After that, the
project is opened and polished in Power BI Desktop, which saves its changes in the
same files.

Because Desktop edits these files, the script never overwrites an existing project
unless you ask for it explicitly:

    python scripts/build_powerbi_project.py            # creates powerbi/ if it does not exist yet
    python scripts/build_powerbi_project.py --force    # rebuilds it (any change made in Desktop is lost)

The definitions in this file (measures, relationships, page layouts) are also the
documentation of the model: documentation/08_fase7_power_bi.md is based on them.
"""

import argparse
import json
import re
import shutil
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings  # noqa: E402
from scripts.common import setup_logging  # noqa: E402

logger = setup_logging("build_powerbi_project")

NAME = "AQMI"
NAMESPACE = uuid.UUID("6f1c2a3e-1d5b-4c7e-9a40-3b1e5a7d9c11")    # deterministic ids: same input, same files

# Visual identity (documentation/08_fase7_power_bi.md, section "Identidad visual")
NAVY = "#0B1F3A"
NAVY_2 = "#16325C"
AERO = "#1F6FB2"
AERO_LIGHT = "#7FA7D6"
ANTHRACITE = "#1E2A3B"
GREY = "#5B6577"
GREY_LIGHT = "#9AA5B1"
BORDER = "#E1E6EE"
CANVAS = "#F3F5F8"
WHITE = "#FFFFFF"
GREEN = "#2E7D32"
AMBER = "#D99A00"
RED = "#C62828"


def guid(*parts: str) -> str:
    return str(uuid.uuid5(NAMESPACE, "/".join(parts)))


# =============================================================================
# 1. SEMANTIC MODEL
# =============================================================================
SPECIAL_WORDS = {"id": "ID", "mo": "MO", "po": "PO", "kpi": "KPI", "sql": "SQL", "capa": "CAPA", "6m": "6M",
                 "rca": "RCA", "qty": "Qty", "pct": "%"}


def friendly(column: str) -> str:
    """Column name shown in Power BI: snake_case from the CSV becomes 'Title Case'."""
    words = column.split("_")
    if words[0] == "n" and len(words) > 1:
        return "Number of " + " ".join(SPECIAL_WORDS.get(w, w.capitalize()) for w in words[1:])
    return " ".join(SPECIAL_WORDS.get(w, w.capitalize()) for w in words)


TABLE_DESCRIPTIONS = {
    "Dim_Date": "Calendar of the simulated period (01/11/2024 - 31/10/2026). Marked as date table.",
    "Dim_Department": "The six departments of AEROQ MRO.",
    "Dim_Employee": "Employees (department kept as text to avoid ambiguous relationship paths).",
    "Dim_Aircraft": "The fleet: aircraft, customer and operational status at the cut-off date.",
    "Dim_Material": "Material catalogue.",
    "Dim_Supplier": "Suppliers and their approval status at the cut-off date.",
    "Dim_Document": "Controlled documents and records, with their current revision and validity.",
    "Dim_IncidentCategory": "Categories of non-conformity.",
    "Dim_KPI": "The 19 indicators: definition, fictitious internal target and SQL reference value.",
    "Fact_Incidents": "One row per non-conformity.",
    "Fact_CAPA": "One row per corrective or preventive action.",
    "Fact_CAPA_Snapshot": "Actions not yet implemented at each month end (periodic snapshot).",
    "Fact_MaintenanceOrders": "One row per work order.",
    "Fact_Holds": "One row per work-order hold (material or documentation).",
    "Fact_MO_Materials": "One row per material line required by a work order.",
    "Fact_InventoryMovements": "One row per stock movement.",
    "Fact_StockSnapshot": "Stock of each active material at each month end, by state (periodic snapshot).",
    "Fact_StockCounts": "One row per stock count.",
    "Fact_PurchaseOrderLines": "One row per purchase order line.",
    "Fact_PO_Snapshot": "Purchase orders pending at each month end (periodic snapshot).",
    "Fact_DocumentVerifications": "One row per verification of a document or record.",
    "Fact_DocumentSnapshot": "Controlled documents in force at each month end (periodic snapshot).",
    "Fact_AuditEvents": "The audit trail: one row per recorded change.",
    "Fact_Lessons": "One row per lesson learned, from its proposal to its incorporation into a controlled document.",
    "Fact_KPI_Monthly": "Monthly KPI values as calculated by the SQL reference queries.",
    "Fact_ValidationResults": "Result of each of the 89 validation rules.",
    "Fact_ValidationFindings": "Records flagged by the validation rules.",
    "Model_Info": "One row: cut-off date, quality gate status and disclaimer.",
}

# (table, sorted column, sort-by column) - source (CSV) names
SORT_BY = [
    ("Dim_Date", "month_label", "year_month_num"),
    ("Dim_Date", "month_name", "month_number"),
    ("Dim_Date", "year_quarter", "year_quarter_num"),
    ("Fact_Incidents", "severity", "severity_order"),
    ("Fact_Incidents", "status", "status_order"),
    ("Fact_CAPA", "status", "status_order"),
    ("Fact_MaintenanceOrders", "status", "status_order"),
    ("Fact_Lessons", "status", "status_order"),
    ("Dim_KPI", "area", "area_order"),
    ("Dim_KPI", "kpi_name", "kpi_order"),
]

# (from table, from column, to table, to column, active) - source (CSV) names; "many" side first
RELATIONSHIPS = [
    ("Fact_Incidents", "detected_date", "Dim_Date", "date", True),
    ("Fact_Incidents", "closed_date", "Dim_Date", "date", False),
    ("Fact_Incidents", "category_id", "Dim_IncidentCategory", "category_id", True),
    ("Fact_Incidents", "responsible_department_id", "Dim_Department", "department_id", True),
    ("Fact_Incidents", "aircraft_id", "Dim_Aircraft", "aircraft_id", True),
    ("Fact_Incidents", "owner_id", "Dim_Employee", "employee_id", True),
    ("Fact_CAPA", "created_date", "Dim_Date", "date", True),
    ("Fact_CAPA", "due_date", "Dim_Date", "date", False),
    ("Fact_CAPA", "department_id", "Dim_Department", "department_id", True),
    ("Fact_CAPA", "responsible_id", "Dim_Employee", "employee_id", True),
    ("Fact_CAPA_Snapshot", "department_id", "Dim_Department", "department_id", True),
    ("Fact_CAPA_Snapshot", "responsible_id", "Dim_Employee", "employee_id", True),
    ("Fact_MaintenanceOrders", "opened_date", "Dim_Date", "date", True),
    ("Fact_MaintenanceOrders", "planned_end_date", "Dim_Date", "date", False),
    ("Fact_MaintenanceOrders", "actual_end_date", "Dim_Date", "date", False),
    ("Fact_MaintenanceOrders", "aircraft_id", "Dim_Aircraft", "aircraft_id", True),
    ("Fact_MaintenanceOrders", "responsible_department_id", "Dim_Department", "department_id", True),
    ("Fact_Holds", "start_date", "Dim_Date", "date", True),
    ("Fact_Holds", "aircraft_id", "Dim_Aircraft", "aircraft_id", True),
    ("Fact_Holds", "material_id", "Dim_Material", "material_id", True),
    ("Fact_MO_Materials", "required_by_date", "Dim_Date", "date", True),
    ("Fact_MO_Materials", "material_id", "Dim_Material", "material_id", True),
    ("Fact_MO_Materials", "aircraft_id", "Dim_Aircraft", "aircraft_id", True),
    ("Fact_InventoryMovements", "movement_date", "Dim_Date", "date", True),
    ("Fact_InventoryMovements", "material_id", "Dim_Material", "material_id", True),
    ("Fact_StockSnapshot", "material_id", "Dim_Material", "material_id", True),
    ("Fact_StockCounts", "count_date", "Dim_Date", "date", True),
    ("Fact_StockCounts", "material_id", "Dim_Material", "material_id", True),
    ("Fact_PurchaseOrderLines", "order_date", "Dim_Date", "date", True),
    ("Fact_PurchaseOrderLines", "supplier_id", "Dim_Supplier", "supplier_id", True),
    ("Fact_PurchaseOrderLines", "material_id", "Dim_Material", "material_id", True),
    ("Fact_PO_Snapshot", "supplier_id", "Dim_Supplier", "supplier_id", True),
    ("Fact_DocumentVerifications", "verification_date", "Dim_Date", "date", True),
    ("Fact_DocumentVerifications", "document_id", "Dim_Document", "document_id", True),
    ("Fact_DocumentVerifications", "verified_by", "Dim_Employee", "employee_id", True),
    ("Fact_DocumentSnapshot", "document_id", "Dim_Document", "document_id", True),
    ("Fact_DocumentSnapshot", "owner_department_id", "Dim_Department", "department_id", True),
    ("Fact_AuditEvents", "event_date", "Dim_Date", "date", True),
    ("Fact_AuditEvents", "changed_by", "Dim_Employee", "employee_id", True),
    ("Fact_Lessons", "proposed_date", "Dim_Date", "date", True),
    ("Fact_Lessons", "department_id", "Dim_Department", "department_id", True),
    ("Fact_KPI_Monthly", "kpi_id", "Dim_KPI", "kpi_id", True),
    ("Fact_ValidationFindings", "rule_id", "Fact_ValidationResults", "rule_id", True),
]

HIDDEN = re.compile(r"(_id$|_order$|_num$|^record_id$|^audit_id$|^movement_datetime$)")
VISIBLE_IDS = {("Dim_KPI", "kpi_id"), ("Fact_ValidationResults", "rule_id"), ("Fact_ValidationFindings", "rule_id"),
               ("Fact_KPI_Monthly", "kpi_id")}

MEASURES_TABLE = "_Measures"

# Each measure: (display folder, name, format string, description, DAX expression)
MEASURES = [
    # ------------------------------------------------------------------ helpers
    ("9. Helpers", "Cut-off Date", "dd mmm yyyy", "Cut-off date of the data (31/10/2026).",
     "MAX ( Model_Info[As Of Date] )"),
    ("9. Helpers", "Selected Date", "dd mmm yyyy",
     "Last date of the period selected in the report, never later than the cut-off date.",
     """VAR _max = MAX ( Dim_Date[Date] )
VAR _asof = [Cut-off Date]
RETURN IF ( ISBLANK ( _max ), _asof, MIN ( _max, _asof ) )"""),
    ("9. Helpers", "Snapshot Month End", "dd mmm yyyy",
     "Last month end on or before the selected date: the date at which 'state' KPIs are measured.",
     """VAR _d = [Selected Date]
VAR _eom = EOMONTH ( _d, 0 )
RETURN IF ( _eom = _d, _d, EOMONTH ( _d, -1 ) )"""),
    ("9. Helpers", "Data As Of Label", None, "Subtitle shown on every page.",
     """"Data as of " & FORMAT ( [Cut-off Date], "dd mmm yyyy" ) & "  ·  Synthetic data  ·  Fictitious company\""""),

    # ------------------------------------------------------------------ quality
    ("1. Quality", "Total Quality Incidents", "#,0", "QUA-01. Non-conformities detected in the period (cancelled excluded).",
     """COALESCE (
    CALCULATE ( COUNTROWS ( Fact_Incidents ), Fact_Incidents[Is Cancelled] = 0 ),
    0
)"""),
    ("1. Quality", "Open Non-Conformities", "#,0", "QUA-02. Non-conformities open at the end of the selected period.",
     """VAR _d = [Selected Date]
RETURN
    COALESCE (
        CALCULATE (
            COUNTROWS ( Fact_Incidents ),
            REMOVEFILTERS ( Dim_Date ),
            Fact_Incidents[Is Cancelled] = 0,
            Fact_Incidents[Detected Date] <= _d,
            ISBLANK ( Fact_Incidents[Closed Date] ) || Fact_Incidents[Closed Date] > _d
        ),
        0
    )"""),
    ("1. Quality", "Non-Conformity Rate", "0.0", "QUA-03. Non-conformities per 100 work orders completed.",
     "DIVIDE ( [Total Quality Incidents] * 100, [Completed Orders] )"),
    ("1. Quality", "Non-Conformities Closed", "#,0", "Non-conformities closed in the period (by closing date).",
     """CALCULATE (
    COUNTROWS ( Fact_Incidents ),
    USERELATIONSHIP ( Fact_Incidents[Closed Date], Dim_Date[Date] ),
    Fact_Incidents[Status] = "CLOSED"
)"""),
    ("1. Quality", "Resolution Days (Sum)", "#,0", "Sum of the days to close the non-conformities closed in the period.",
     """CALCULATE (
    SUM ( Fact_Incidents[Resolution Days] ),
    USERELATIONSHIP ( Fact_Incidents[Closed Date], Dim_Date[Date] ),
    Fact_Incidents[Status] = "CLOSED"
)"""),
    ("1. Quality", "Average Resolution Time", "0.0", "QUA-05. Average days from detection to closure.",
     "DIVIDE ( [Resolution Days (Sum)], [Non-Conformities Closed] )"),
    ("1. Quality", "RCA Coverage (Critical & Major)", "0.0%",
     "Share of critical and major non-conformities with a root-cause analysis.",
     """DIVIDE (
    CALCULATE (
        [Total Quality Incidents],
        KEEPFILTERS ( Fact_Incidents[Severity] IN { "CRITICAL", "MAJOR" } ),
        Fact_Incidents[Has RCA] = 1
    ),
    CALCULATE ( [Total Quality Incidents], KEEPFILTERS ( Fact_Incidents[Severity] IN { "CRITICAL", "MAJOR" } ) )
)"""),
    ("1. Quality", "Analysed Non-Conformities", "#,0", "Non-conformities with an Ishikawa (6M) root cause.",
     """CALCULATE (
    COUNTROWS ( Fact_Incidents ),
    Fact_Incidents[Is Cancelled] = 0,
    KEEPFILTERS ( Fact_Incidents[Root Cause 6M] <> "NOT ANALYSED" )
)"""),
    ("1. Quality", "Open NC Age (days)", "#,0", "Age in days of each non-conformity open at the cut-off date.",
     """CALCULATE (
    IF ( MAX ( Fact_Incidents[Is Open] ) = 1, MAX ( Fact_Incidents[Age Days] ) ),
    REMOVEFILTERS ( Dim_Date )
)"""),

    # ------------------------------------------------------------------ CAPA
    ("2. CAPA", "Corrective Actions Due", "#,0", "Corrective actions whose due date falls in the period.",
     """VAR _asof = [Cut-off Date]
RETURN
    CALCULATE (
        COUNTROWS ( Fact_CAPA ),
        USERELATIONSHIP ( Fact_CAPA[Due Date], Dim_Date[Date] ),
        Fact_CAPA[Action Type] = "CORRECTIVE",
        Fact_CAPA[Is Cancelled] = 0,
        Fact_CAPA[Due Date] <= _asof
    )"""),
    ("2. CAPA", "Corrective Actions Due On Time", "#,0", "Of the actions due in the period, those implemented by their due date.",
     """VAR _asof = [Cut-off Date]
RETURN
    CALCULATE (
        COUNTROWS ( Fact_CAPA ),
        USERELATIONSHIP ( Fact_CAPA[Due Date], Dim_Date[Date] ),
        Fact_CAPA[Action Type] = "CORRECTIVE",
        Fact_CAPA[Is Cancelled] = 0,
        Fact_CAPA[Due Date] <= _asof,
        Fact_CAPA[Completed By Due] = 1
    )"""),
    ("2. CAPA", "Corrective Action Closure Rate", "0.0%", "QUA-04. Corrective actions implemented by their due date.",
     "DIVIDE ( [Corrective Actions Due On Time], [Corrective Actions Due] )"),
    ("2. CAPA", "Overdue Corrective Actions", "#,0",
     "QUA-06. Corrective actions past their due date (as it was then) and not implemented, at the snapshot date.",
     """VAR _s = [Snapshot Month End]
RETURN
    COALESCE (
        CALCULATE (
            COUNTROWS ( Fact_CAPA_Snapshot ),
            Fact_CAPA_Snapshot[Snapshot Date] = _s,
            Fact_CAPA_Snapshot[Action Type] = "CORRECTIVE",
            Fact_CAPA_Snapshot[Is Overdue] = 1
        ),
        0
    )"""),
    ("2. CAPA", "Actions Pending Implementation", "#,0", "Corrective and preventive actions not yet implemented at the snapshot date.",
     """VAR _s = [Snapshot Month End]
RETURN
    COALESCE (
        CALCULATE ( COUNTROWS ( Fact_CAPA_Snapshot ), Fact_CAPA_Snapshot[Snapshot Date] = _s ),
        0
    )"""),
    ("2. CAPA", "Actions Created", "#,0", "Actions created in the period (cancelled excluded).",
     "CALCULATE ( COUNTROWS ( Fact_CAPA ), Fact_CAPA[Is Cancelled] = 0 )"),
    ("2. CAPA", "Effectiveness Rate", "0.0%", "Of the actions whose effectiveness was verified, share found effective.",
     """DIVIDE (
    CALCULATE ( COUNTROWS ( Fact_CAPA ), Fact_CAPA[Effectiveness Result] = "EFFECTIVE" ),
    CALCULATE ( COUNTROWS ( Fact_CAPA ), Fact_CAPA[Effectiveness Result] IN { "EFFECTIVE", "NOT_EFFECTIVE" } )
)"""),
    ("2. CAPA", "Rescheduled Actions", "#,0", "Actions whose due date was extended at least once.",
     """COALESCE (
    CALCULATE ( COUNTROWS ( Fact_CAPA ), Fact_CAPA[Was Rescheduled] = 1, Fact_CAPA[Is Cancelled] = 0 ),
    0
)"""),
    ("2. CAPA", "Open Action Days Overdue", "#,0", "Days overdue of each open action at the cut-off date (0 = within its due date).",
     """CALCULATE (
    IF ( MAX ( Fact_CAPA[Is Open] ) = 1, MAX ( Fact_CAPA[Days Overdue] ) ),
    REMOVEFILTERS ( Dim_Date )
)"""),
    ("2. CAPA", "Open Action Progress", "0%", "Latest progress reported for each open action.",
     """CALCULATE (
    IF ( MAX ( Fact_CAPA[Is Open] ) = 1, DIVIDE ( MAX ( Fact_CAPA[Latest Progress %] ), 100 ) ),
    REMOVEFILTERS ( Dim_Date )
)"""),

    # ------------------------------------------------------------------ documents
    ("3. Documents", "Controlled Documents In Force", "#,0", "Controlled documents with a revision in force at the snapshot date.",
     """VAR _s = [Snapshot Month End]
RETURN
    COALESCE (
        CALCULATE ( COUNTROWS ( Fact_DocumentSnapshot ), Fact_DocumentSnapshot[Snapshot Date] = _s ),
        0
    )"""),
    ("3. Documents", "Compliant Documents", "#,0", "Controlled documents within their review date at the snapshot date.",
     """VAR _s = [Snapshot Month End]
RETURN
    COALESCE (
        CALCULATE (
            COUNTROWS ( Fact_DocumentSnapshot ),
            Fact_DocumentSnapshot[Snapshot Date] = _s,
            Fact_DocumentSnapshot[Is Compliant] = 1
        ),
        0
    )"""),
    ("3. Documents", "Document Compliance Rate", "0.0%", "DOC-01. Controlled documents within their review date.",
     "DIVIDE ( [Compliant Documents], [Controlled Documents In Force] )"),
    ("3. Documents", "Expired Documents", "#,0", "DOC-03. Controlled documents past their review date at the snapshot date.",
     """VAR _s = [Snapshot Month End]
RETURN
    COALESCE (
        CALCULATE (
            COUNTROWS ( Fact_DocumentSnapshot ),
            Fact_DocumentSnapshot[Snapshot Date] = _s,
            Fact_DocumentSnapshot[Is Expired] = 1
        ),
        0
    )"""),
    ("3. Documents", "Routine Verifications", "#,0", "Document and record checks, internal audits excluded.",
     """COALESCE (
    CALCULATE ( COUNTROWS ( Fact_DocumentVerifications ), Fact_DocumentVerifications[Is Routine] = 1 ),
    0
)"""),
    ("3. Documents", "Routine Verification Discrepancies", "#,0", "Routine checks that found a discrepancy.",
     """COALESCE (
    CALCULATE (
        COUNTROWS ( Fact_DocumentVerifications ),
        Fact_DocumentVerifications[Is Routine] = 1,
        Fact_DocumentVerifications[Is Error] = 1
    ),
    0
)"""),
    ("3. Documents", "Documentation Error Rate", "0.0%", "DOC-02. Routine checks that found a discrepancy.",
     "DIVIDE ( [Routine Verification Discrepancies], [Routine Verifications] )"),
    ("3. Documents", "Discrepancy Rate (All Verifications)", "0.0%", "Verifications with a discrepancy, all types (for the breakdown by type).",
     """DIVIDE (
    CALCULATE ( COUNTROWS ( Fact_DocumentVerifications ), Fact_DocumentVerifications[Is Error] = 1 ),
    COUNTROWS ( Fact_DocumentVerifications )
)"""),
    ("3. Documents", "Material Issues", "#,0", "Material issued to work orders.",
     """COALESCE (
    CALCULATE ( COUNTROWS ( Fact_InventoryMovements ), Fact_InventoryMovements[Movement Type] = "ISSUE" ),
    0
)"""),
    ("3. Documents", "Traceable Issues", "#,0", "Issues with work order, lot, serial number and certificate where required.",
     """COALESCE (
    CALCULATE (
        COUNTROWS ( Fact_InventoryMovements ),
        Fact_InventoryMovements[Movement Type] = "ISSUE",
        Fact_InventoryMovements[Is Traceable] = 1
    ),
    0
)"""),
    ("3. Documents", "Traceability Compliance", "0.0%", "DOC-04. Issues with complete traceability data.",
     "DIVIDE ( [Traceable Issues], [Material Issues] )"),
    ("3. Documents", "Expired Document Days Overdue", "#,0", "Days past the review date of each expired document (cut-off date).",
     """CALCULATE (
    MAX ( Dim_Document[Days Overdue] ),
    KEEPFILTERS ( Dim_Document[Validity Status] = "REVIEW_OVERDUE" )
)"""),

    # ------------------------------------------------------------------ inventory
    ("4. Inventory", "Cycle Counts", "#,0", "Cycle counts made in the period (opening counts excluded).",
     "COALESCE ( CALCULATE ( COUNTROWS ( Fact_StockCounts ), Fact_StockCounts[Count Type] = \"CYCLE\" ), 0 )"),
    ("4. Inventory", "Accurate Counts", "#,0", "Cycle counts that matched the stock recorded in the system.",
     """COALESCE (
    CALCULATE (
        COUNTROWS ( Fact_StockCounts ),
        Fact_StockCounts[Count Type] = "CYCLE",
        Fact_StockCounts[Has Difference] = 0
    ),
    0
)"""),
    ("4. Inventory", "Inventory Accuracy", "0.0%", "INV-01. Cycle counts that matched the system.",
     "DIVIDE ( [Accurate Counts], [Cycle Counts] )"),
    ("4. Inventory", "Active Materials", "#,0", "Active materials at the snapshot date.",
     """VAR _s = [Snapshot Month End]
RETURN
    COALESCE (
        CALCULATE ( COUNTROWS ( Fact_StockSnapshot ), Fact_StockSnapshot[Snapshot Date] = _s ),
        0
    )"""),
    ("4. Inventory", "Materials Below Minimum", "#,0", "Active materials with available stock below their minimum.",
     """VAR _s = [Snapshot Month End]
RETURN
    COALESCE (
        CALCULATE (
            COUNTROWS ( Fact_StockSnapshot ),
            Fact_StockSnapshot[Snapshot Date] = _s,
            Fact_StockSnapshot[Is Below Min] = 1
        ),
        0
    )"""),
    ("4. Inventory", "Stock Availability", "0.0%", "INV-02. Active materials with available stock at or above their minimum.",
     "DIVIDE ( [Active Materials] - [Materials Below Minimum], [Active Materials] )"),
    ("4. Inventory", "Material Lines Required", "#,0", "Material lines of work orders required in the period.",
     """VAR _asof = [Cut-off Date]
RETURN
    CALCULATE (
        COUNTROWS ( Fact_MO_Materials ),
        Fact_MO_Materials[Is Cancelled Order] = 0,
        NOT ISBLANK ( Fact_MO_Materials[Was Short] ),
        Fact_MO_Materials[Required By Date] <= _asof
    )"""),
    ("4. Inventory", "Material Lines Short", "#,0", "Material lines not available on the required date.",
     """VAR _asof = [Cut-off Date]
RETURN
    CALCULATE (
        COUNTROWS ( Fact_MO_Materials ),
        Fact_MO_Materials[Is Cancelled Order] = 0,
        Fact_MO_Materials[Was Short] = 1,
        Fact_MO_Materials[Required By Date] <= _asof
    )"""),
    ("4. Inventory", "Material Shortage Rate", "0.0%", "INV-03. Material lines not available on the required date.",
     "DIVIDE ( [Material Lines Short], [Material Lines Required] )"),
    ("4. Inventory", "Pending Purchase Orders", "#,0", "INV-04. Purchase orders sent and not fully received at the snapshot date.",
     """VAR _s = [Snapshot Month End]
RETURN
    COALESCE (
        CALCULATE ( DISTINCTCOUNT ( Fact_PO_Snapshot[PO ID] ), Fact_PO_Snapshot[Snapshot Date] = _s ),
        0
    )"""),
    ("4. Inventory", "Available Qty (Below Minimum)", "#,0.##", "Available stock of the materials below their minimum.",
     """VAR _s = [Snapshot Month End]
RETURN
    CALCULATE (
        SUM ( Fact_StockSnapshot[Available Qty] ),
        Fact_StockSnapshot[Snapshot Date] = _s,
        Fact_StockSnapshot[Is Below Min] = 1
    )"""),
    ("4. Inventory", "Minimum Stock (Below Minimum)", "#,0.##", "Minimum stock of the materials below their minimum.",
     """VAR _s = [Snapshot Month End]
RETURN
    CALCULATE (
        MAX ( Fact_StockSnapshot[Min Stock Qty] ),
        Fact_StockSnapshot[Snapshot Date] = _s,
        Fact_StockSnapshot[Is Below Min] = 1
    )"""),
    ("4. Inventory", "In Receiving Inspection (Below Minimum)", "#,0.##", "Stock in receiving inspection of the materials below their minimum.",
     """VAR _s = [Snapshot Month End]
RETURN
    CALCULATE (
        SUM ( Fact_StockSnapshot[Quarantine Qty] ),
        Fact_StockSnapshot[Snapshot Date] = _s,
        Fact_StockSnapshot[Is Below Min] = 1
    )"""),
    ("4. Inventory", "PO Lines Received", "#,0", "Purchase order lines fully received (by order date).",
     "CALCULATE ( COUNTROWS ( Fact_PurchaseOrderLines ), Fact_PurchaseOrderLines[Is Received] = 1 )"),
    ("4. Inventory", "PO Lines On Time", "#,0", "Lines fully received on or before the promised date.",
     """CALCULATE (
    COUNTROWS ( Fact_PurchaseOrderLines ),
    Fact_PurchaseOrderLines[Is Received] = 1,
    Fact_PurchaseOrderLines[Is On Time] = 1
)"""),
    ("4. Inventory", "On-Time Delivery Rate", "0.0%", "Supplier lines received on time (complement to the KPIs).",
     "DIVIDE ( [PO Lines On Time], [PO Lines Received] )"),

    # ------------------------------------------------------------------ maintenance
    ("5. Maintenance", "Orders Opened", "#,0", "Work orders opened in the period (cancelled excluded).",
     """COALESCE (
    CALCULATE ( COUNTROWS ( Fact_MaintenanceOrders ), Fact_MaintenanceOrders[Is Cancelled] = 0 ),
    0
)"""),
    ("5. Maintenance", "Completed Orders", "#,0", "Work orders completed in the period (by actual end date).",
     """COALESCE (
    CALCULATE (
        COUNTROWS ( Fact_MaintenanceOrders ),
        USERELATIONSHIP ( Fact_MaintenanceOrders[Actual End Date], Dim_Date[Date] ),
        Fact_MaintenanceOrders[Is Cancelled] = 0,
        NOT ISBLANK ( Fact_MaintenanceOrders[Actual End Date] )
    ),
    0
)"""),
    ("5. Maintenance", "Orders Due", "#,0", "Work orders planned to finish in the period.",
     """VAR _asof = [Cut-off Date]
RETURN
    CALCULATE (
        COUNTROWS ( Fact_MaintenanceOrders ),
        USERELATIONSHIP ( Fact_MaintenanceOrders[Planned End Date], Dim_Date[Date] ),
        Fact_MaintenanceOrders[Is Cancelled] = 0,
        Fact_MaintenanceOrders[Planned End Date] <= _asof
    )"""),
    ("5. Maintenance", "Orders Due On Time", "#,0", "Of the orders due in the period, those completed by the planned date.",
     """VAR _asof = [Cut-off Date]
RETURN
    CALCULATE (
        COUNTROWS ( Fact_MaintenanceOrders ),
        USERELATIONSHIP ( Fact_MaintenanceOrders[Planned End Date], Dim_Date[Date] ),
        Fact_MaintenanceOrders[Is Cancelled] = 0,
        Fact_MaintenanceOrders[Planned End Date] <= _asof,
        Fact_MaintenanceOrders[Completed By Planned] = 1
    )"""),
    ("5. Maintenance", "Maintenance Order Completion Rate", "0.0%", "MNT-01. Work orders completed by the planned date.",
     "DIVIDE ( [Orders Due On Time], [Orders Due] )"),
    ("5. Maintenance", "Delay Days (Sum)", "#,0", "Sum of the days of delay of the orders completed in the period.",
     """CALCULATE (
    SUM ( Fact_MaintenanceOrders[Delay Days] ),
    USERELATIONSHIP ( Fact_MaintenanceOrders[Actual End Date], Dim_Date[Date] ),
    Fact_MaintenanceOrders[Is Cancelled] = 0,
    NOT ISBLANK ( Fact_MaintenanceOrders[Actual End Date] )
)"""),
    ("5. Maintenance", "Average Maintenance Delay", "0.0", "MNT-02. Average days of delay of completed orders (on time = 0).",
     "DIVIDE ( [Delay Days (Sum)], [Completed Orders] )"),
    ("5. Maintenance", "Open Work Orders", "#,0", "Work orders open at the end of the selected period.",
     """VAR _d = [Selected Date]
RETURN
    COALESCE (
        CALCULATE (
            COUNTROWS ( Fact_MaintenanceOrders ),
            REMOVEFILTERS ( Dim_Date ),
            Fact_MaintenanceOrders[Is Cancelled] = 0,
            Fact_MaintenanceOrders[Opened Date] <= _d,
            ISBLANK ( Fact_MaintenanceOrders[Actual End Date] ) || Fact_MaintenanceOrders[Actual End Date] > _d
        ),
        0
    )"""),
    ("5. Maintenance", "Work Orders Blocked by Material", "#,0", "MNT-03. Work orders stopped by a material hold at the end of the selected period.",
     """VAR _d = [Selected Date]
RETURN
    COALESCE (
        CALCULATE (
            DISTINCTCOUNT ( Fact_Holds[MO ID] ),
            REMOVEFILTERS ( Dim_Date ),
            Fact_Holds[Hold Reason] = "MATERIAL",
            Fact_Holds[Start Date] <= _d,
            ISBLANK ( Fact_Holds[End Date] ) || Fact_Holds[End Date] > _d
        ),
        0
    )"""),
    ("5. Maintenance", "Work Orders Blocked by Documentation", "#,0",
     "MNT-04. Work orders stopped by a documentation hold at the end of the selected period.",
     """VAR _d = [Selected Date]
RETURN
    COALESCE (
        CALCULATE (
            DISTINCTCOUNT ( Fact_Holds[MO ID] ),
            REMOVEFILTERS ( Dim_Date ),
            Fact_Holds[Hold Reason] = "DOCUMENTATION",
            Fact_Holds[Start Date] <= _d,
            ISBLANK ( Fact_Holds[End Date] ) || Fact_Holds[End Date] > _d
        ),
        0
    )"""),
    ("5. Maintenance", "On-Time Rate (Completed Orders)", "0.0%", "Completed orders that finished by the planned date.",
     """DIVIDE (
    CALCULATE ( [Completed Orders], Fact_MaintenanceOrders[Completed By Planned] = 1 ),
    [Completed Orders]
)"""),
    ("5. Maintenance", "Active Hold Days", "#,0", "Days each active hold has lasted at the cut-off date.",
     """CALCULATE (
    IF ( MAX ( Fact_Holds[Is Active] ) = 1, MAX ( Fact_Holds[Hold Days] ) ),
    REMOVEFILTERS ( Dim_Date )
)"""),
    ("5. Maintenance", "Material Hold Days (Total)", "#,0", "Days work orders opened in the period spent stopped by material.",
     "CALCULATE ( SUM ( Fact_MaintenanceOrders[Material Hold Days] ), Fact_MaintenanceOrders[Is Cancelled] = 0 )"),
    ("5. Maintenance", "Unscheduled Share", "0.0%", "Share of work orders that were unscheduled.",
     """DIVIDE (
    CALCULATE ( [Orders Opened], KEEPFILTERS ( Fact_MaintenanceOrders[Maintenance Type] = "UNSCHEDULED" ) ),
    [Orders Opened]
)"""),

    # ------------------------------------------------------------------ aircraft
    ("6. Aircraft", "Fleet Size", "#,0", "Aircraft in the selection.", "COUNTROWS ( Dim_Aircraft )"),
    ("6. Aircraft", "Aircraft In Maintenance", "#,0", "Aircraft with an open work order at the cut-off date.",
     """COALESCE (
    CALCULATE ( COUNTROWS ( Dim_Aircraft ), KEEPFILTERS ( Dim_Aircraft[Operational Status] = "IN_MAINTENANCE" ) ),
    0
)"""),

    # ------------------------------------------------------------------ audit & data quality
    ("7. Audit & Data Quality", "Audit Events", "#,0", "Changes recorded in the audit trail.",
     "COALESCE ( COUNTROWS ( Fact_AuditEvents ), 0 )"),
    ("7. Audit & Data Quality", "Audit Events (Label)", None,
     "Audit Events as text (e.g. 17,746): the new card visual abbreviates numbers (17K) whatever the format string.",
     'FORMAT ( [Audit Events], "#,0" )'),
    ("7. Audit & Data Quality", "Data Quality Score (Rules Passed)", "0.0%", "Validation rules passed / rules executed (Phase 5).",
     "DIVIDE ( MAX ( Model_Info[Data Quality Score] ), 100 )"),
    ("7. Audit & Data Quality", "Validation Rules Executed", "#,0", "Validation rules executed.", "MAX ( Model_Info[Rules Executed] )"),
    ("7. Audit & Data Quality", "Critical Rule Failures", "#,0", "CRITICAL validation rules with findings (must be 0).",
     "MAX ( Model_Info[Critical Failures] )"),
    ("7. Audit & Data Quality", "Planted Discrepancies Detected", None,
     "Discrepancies planted on purpose by the generator and detected by the rules.",
     """FORMAT ( MAX ( Model_Info[Planted Detected] ), "0" ) & " of " & FORMAT ( MAX ( Model_Info[Planted Expected] ), "0" )"""),
    ("7. Audit & Data Quality", "Validation Findings", "#,0", "Records flagged by the WARNING rules.",
     "COALESCE ( COUNTROWS ( Fact_ValidationFindings ), 0 )"),

    # ------------------------------------------------------------------ lessons learned (Phase 9)
    ("8. Lessons Learned", "Lessons Proposed", "#,0", "Lessons learned proposed in the period.",
     "COALESCE ( COUNTROWS ( Fact_Lessons ), 0 )"),
    ("8. Lessons Learned", "Lessons Approved", "#,0",
     "Lessons approved (incorporated or not) at the end of the selected period. A rejected lesson is never approved.",
     """VAR _d = [Selected Date]
RETURN
    COALESCE (
        CALCULATE (
            COUNTROWS ( Fact_Lessons ),
            REMOVEFILTERS ( Dim_Date ),
            NOT ISBLANK ( Fact_Lessons[Approved Date] ),
            Fact_Lessons[Approved Date] <= _d
        ),
        0
    )"""),
    ("8. Lessons Learned", "Lessons Incorporated", "#,0",
     "Approved lessons already incorporated into a controlled document at the end of the selected period.",
     """VAR _d = [Selected Date]
RETURN
    COALESCE (
        CALCULATE (
            COUNTROWS ( Fact_Lessons ),
            REMOVEFILTERS ( Dim_Date ),
            NOT ISBLANK ( Fact_Lessons[Incorporated Date] ),
            Fact_Lessons[Incorporated Date] <= _d
        ),
        0
    )"""),
    ("8. Lessons Learned", "Lesson Incorporation Rate", "0.0%",
     "LRN-01. Approved lessons already incorporated into a controlled document (fictitious internal target: 80%).",
     "DIVIDE ( [Lessons Incorporated], [Lessons Approved] )"),
    ("8. Lessons Learned", "Lessons Pending Incorporation", "#,0",
     "Approved lessons not yet incorporated into a controlled document at the end of the selected period.",
     "[Lessons Approved] - [Lessons Incorporated]"),
    ("8. Lessons Learned", "Lesson Days Pending", "#,0",
     "Days each approved lesson has been waiting for incorporation at the cut-off date.",
     """CALCULATE (
    IF ( MAX ( Fact_Lessons[Is Pending Incorporation] ) = 1, MAX ( Fact_Lessons[Days Pending] ) ),
    REMOVEFILTERS ( Dim_Date )
)"""),

    # ------------------------------------------------------------------ KPI framework
    ("0. KPI Framework", "KPI Value (Power BI)", "0.0",
     "Value of the KPI selected in Dim_KPI, calculated by the DAX measures (percentages as 0-100).",
     """SWITCH (
    SELECTEDVALUE ( Dim_KPI[KPI ID] ),
    "QUA-01", [Total Quality Incidents],
    "QUA-02", [Open Non-Conformities],
    "QUA-03", [Non-Conformity Rate],
    "QUA-04", [Corrective Action Closure Rate] * 100,
    "QUA-05", [Average Resolution Time],
    "QUA-06", [Overdue Corrective Actions],
    "DOC-01", [Document Compliance Rate] * 100,
    "DOC-02", [Documentation Error Rate] * 100,
    "DOC-03", [Expired Documents],
    "DOC-04", [Traceability Compliance] * 100,
    "INV-01", [Inventory Accuracy] * 100,
    "INV-02", [Stock Availability] * 100,
    "INV-03", [Material Shortage Rate] * 100,
    "INV-04", [Pending Purchase Orders],
    "MNT-01", [Maintenance Order Completion Rate] * 100,
    "MNT-02", [Average Maintenance Delay],
    "MNT-03", [Work Orders Blocked by Material],
    "MNT-04", [Work Orders Blocked by Documentation],
    "LRN-01", [Lesson Incorporation Rate] * 100
)"""),
    ("0. KPI Framework", "KPI Value (SQL)", "0.0", "Value of the KPI for the whole period, from its SQL reference query (Phase 6).",
     "SELECTEDVALUE ( Dim_KPI[SQL Value] )"),
    ("0. KPI Framework", "KPI Reconciliation", None,
     "Rule K03: the Power BI value must equal the SQL reference value (whole period, no filters).",
     """VAR _pbi = [KPI Value (Power BI)]
VAR _sql = [KPI Value (SQL)]
RETURN
    IF (
        HASONEVALUE ( Dim_KPI[KPI ID] ),
        IF ( ROUND ( _pbi, 1 ) = ROUND ( _sql, 1 ), "✔ Match", "✖ Check" )
    )"""),
    ("0. KPI Framework", "KPI Status", None, "Traffic light against the fictitious internal target of AEROQ MRO.",
     """VAR _value = [KPI Value (Power BI)]
VAR _v = ROUND ( _value, 1 )
VAR _t = SELECTEDVALUE ( Dim_KPI[Target] )
VAR _w = SELECTEDVALUE ( Dim_KPI[Warning] )
VAR _dir = SELECTEDVALUE ( Dim_KPI[Direction] )
RETURN
    SWITCH (
        TRUE (),
        NOT HASONEVALUE ( Dim_KPI[KPI ID] ), BLANK (),
        ISBLANK ( _value ), "NO DATA",
        ISBLANK ( _t ), "NO TARGET",
        _dir = "HIGHER_IS_BETTER", IF ( _v >= _t, "GREEN", IF ( _v >= _w, "AMBER", "RED" ) ),
        IF ( _v <= _t, "GREEN", IF ( _v <= _w, "AMBER", "RED" ) )
    )"""),
    ("0. KPI Framework", "KPI Status Color", None, "Colour of the traffic light (used by conditional formatting).",
     f"""SWITCH (
    [KPI Status],
    "GREEN", "{GREEN}",
    "AMBER", "{AMBER}",
    "RED", "{RED}",
    "{GREY_LIGHT}"
)"""),
    ("0. KPI Framework", "KPI Status Label", None, "Traffic light as text.",
     """SWITCH (
    [KPI Status],
    "GREEN", "● On target",
    "AMBER", "● Warning",
    "RED", "● Off target",
    "NO DATA", "no data",
    "NO TARGET", "— monitoring",
    BLANK ()
)"""),
    ("0. KPI Framework", "KPI Display Value", None, "KPI value formatted with its unit.",
     """VAR _v = [KPI Value (Power BI)]
VAR _u = SELECTEDVALUE ( Dim_KPI[Unit] )
RETURN
    IF (
        HASONEVALUE ( Dim_KPI[KPI ID] ),
        IF (
            ISBLANK ( _v ),
            "no data",
            SWITCH (
                _u,
                "%", FORMAT ( _v, "0.0" ) & "%",
                "days", FORMAT ( _v, "0.0" ) & " days",
                "count", FORMAT ( _v, "#,0" ),
                FORMAT ( _v, "0.0" )
            )
        )
    )"""),
]


def quote(name: str) -> str:
    """TMDL object name: plain if simple, otherwise in single quotes."""
    return name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) else "'" + name.replace("'", "''") + "'"


M_TYPES = {"int64": "Int64.Type", "double": "type number", "date": "type date", "dateTime": "type datetime",
           "string": "type text"}
TMDL_TYPES = {"int64": "int64", "double": "double", "date": "dateTime", "dateTime": "dateTime", "string": "string"}


def column_format(table: str, column: str, kind: str) -> str | None:
    if kind == "date":
        return "dd mmm yyyy"
    if kind == "dateTime":
        return "dd mmm yyyy hh:nn"
    if kind == "int64":
        return "0" if HIDDEN.search(column) or column in ("year", "random_seed") else "#,0"
    if kind == "double":
        return "#,0.00" if column.endswith(("_value", "_cost")) else "#,0.##"
    return None


def table_tmdl(table: str, info: dict) -> str:
    sort_map = {(t, c): s for t, c, s in SORT_BY if t == table}
    lines = [f"/// {TABLE_DESCRIPTIONS.get(table, table)}", f"table {quote(table)}"]
    if table == "Dim_Date":
        lines.append("\tdataCategory: Time")
    lines.append("")
    for col in info["columns"]:
        source, kind = col["name"], col["type"]
        lines.append(f"\tcolumn {quote(friendly(source))}")
        lines.append(f"\t\tdataType: {TMDL_TYPES[kind]}")
        if table == "Dim_Date" and source == "date":
            lines.append("\t\tisKey")
        if HIDDEN.search(source) and (table, source) not in VISIBLE_IDS:
            lines.append("\t\tisHidden")
        fmt = column_format(table, source, kind)
        if fmt:
            lines.append(f"\t\tformatString: {fmt}")
        lines.append("\t\tsummarizeBy: none")
        lines.append(f"\t\tsourceColumn: {source}")
        if (table, source) in sort_map:
            lines.append(f"\t\tsortByColumn: {quote(friendly(sort_map[(table, source)]))}")
        lines.append("")
        if kind == "date":
            lines.append("\t\tannotation UnderlyingDateTimeDataType = Date")
            lines.append("")
    typed = ", ".join(f'{{"{c["name"]}", {M_TYPES[c["type"]]}}}' for c in info["columns"])
    m = [
        "let",
        f'    Source = Csv.Document(File.Contents(DataFolder & "{table}.csv"), '
        '[Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),',
        "    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),",
        '    EmptyAsNull = Table.TransformColumns(Promoted, {}, each if _ = "" then null else _),',
        f'    Typed = Table.TransformColumnTypes(EmptyAsNull, {{{typed}}}, "en-US")',
        "in",
        "    Typed",
    ]
    lines.append(f"\tpartition {quote(table)} = m")
    lines.append("\t\tmode: import")
    lines.append("\t\tqueryGroup: Tables")
    lines.append("\t\tsource =")
    lines += ["\t\t\t\t" + line for line in m]
    lines += ["", "\tannotation PBI_ResultType = Table", ""]
    return "\n".join(lines)


def measures_tmdl() -> str:
    lines = ["/// All DAX measures of AQMI, grouped in display folders. Definitions: documentation/08_fase7_power_bi.md",
             f"table {MEASURES_TABLE}", ""]
    for folder, name, fmt, description, expression in MEASURES:
        lines.append(f"\t/// {description}")
        body = [line for line in expression.strip().splitlines() if line.strip()]
        if len(body) == 1:
            lines.append(f"\tmeasure {quote(name)} = {body[0]}")
        else:
            lines.append(f"\tmeasure {quote(name)} =")
            lines += ["\t\t\t" + line for line in body]
        if fmt:
            lines.append(f"\t\tformatString: {fmt}")
        lines.append(f"\t\tdisplayFolder: {folder}")
        lines.append("")
    lines += [
        "\tcolumn Placeholder",
        "\t\tdataType: string",
        "\t\tisHidden",
        "\t\tsummarizeBy: none",
        "\t\tsourceColumn: Placeholder",
        "",
        f"\tpartition {MEASURES_TABLE} = m",
        "\t\tmode: import",
        "\t\tsource =",
        "\t\t\t\tlet",
        "\t\t\t\t    Source = #table(type table [Placeholder = text], {})",
        "\t\t\t\tin",
        "\t\t\t\t    Source",
        "",
        "\tannotation PBI_ResultType = Table",
        "",
    ]
    return "\n".join(lines)


def build_semantic_model(root: Path, schema: dict, data_folder: str) -> None:
    sm = root / f"{NAME}.SemanticModel"
    definition = sm / "definition"
    (definition / "tables").mkdir(parents=True)
    write_json(sm / ".platform", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": NAME},
        "config": {"version": "2.0", "logicalId": guid("semanticModel")}})
    write_json(sm / "definition.pbism", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2", "settings": {"qnaEnabled": False}})
    write_text(definition / "database.tmdl", "database\n\tcompatibilityLevel: 1601\n")
    tables = list(schema) + [MEASURES_TABLE]
    query_order = json.dumps(["DataFolder"] + tables)
    model = [
        "model Model",
        "\tculture: en-US",
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
        "\tdiscourageImplicitMeasures",
        "\tsourceQueryCulture: en-US",
        "\tdataAccessOptions",
        "\t\tlegacyRedirects",
        "\t\treturnErrorValuesAsNull",
        "",
        "queryGroup Parameters",
        "",
        "\tannotation PBI_QueryGroupOrder = 0",
        "",
        "queryGroup Tables",
        "",
        "\tannotation PBI_QueryGroupOrder = 1",
        "",
        "annotation __PBI_TimeIntelligenceEnabled = 0",
        "",
        f"annotation PBI_QueryOrder = {query_order}",
        "",
    ] + [f"ref table {quote(t)}" for t in tables] + [""]
    write_text(definition / "model.tmdl", "\n".join(model))
    write_text(definition / "expressions.tmdl", "\n".join([
        f'expression DataFolder = "{data_folder}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]',
        "\tqueryGroup: Parameters",
        "",
        "\tannotation PBI_ResultType = Text",
        "",
    ]))
    rel = []
    for frm, fcol, to, tcol, active in RELATIONSHIPS:
        rel.append(f"relationship {guid('rel', frm, fcol, to, tcol)}")
        if not active:
            rel.append("\tisActive: false")
        rel.append(f"\tfromColumn: {quote(frm)}.{quote(friendly(fcol))}")
        rel.append(f"\ttoColumn: {quote(to)}.{quote(friendly(tcol))}")
        rel.append("")
    write_text(definition / "relationships.tmdl", "\n".join(rel))
    for table, info in schema.items():
        write_text(definition / "tables" / f"{table}.tmdl", table_tmdl(table, info))
    write_text(definition / "tables" / f"{MEASURES_TABLE}.tmdl", measures_tmdl())


# =============================================================================
# 2. REPORT
# =============================================================================
SCHEMA_BASE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
VC_SCHEMA = f"{SCHEMA_BASE}/visualContainer/2.1.0/schema.json"
PAGE_SCHEMA = f"{SCHEMA_BASE}/page/1.4.0/schema.json"
THEME_FILE = "AQMI_Theme.json"
FONT = "Segoe UI"
FONT_SEMIBOLD = "Segoe UI Semibold"


# ---------------------------------------------------------------- expression helpers
def lit(value: str) -> dict:
    return {"expr": {"Literal": {"Value": value}}}


def text(value: str) -> dict:
    return lit("'" + value.replace("'", "''") + "'")


def num(value: float) -> dict:
    return lit(f"{value}D")


def integer(value: int) -> dict:
    return lit(f"{value}L")


def boolean(value: bool) -> dict:
    return lit("true" if value else "false")


def color(hex_code: str) -> dict:
    return {"solid": {"color": lit(f"'{hex_code}'")}}


def measure_color(measure: str) -> dict:
    return {"solid": {"color": {"expr": {"Measure": {"Expression": {"SourceRef": {"Entity": MEASURES_TABLE}},
                                                     "Property": measure}}}}}


def M(name: str) -> tuple:                       # a measure
    return ("M", MEASURES_TABLE, name)


def C(table: str, column: str) -> tuple:         # a column (CSV name, converted to the Power BI name)
    return ("C", table, friendly(column))


def field_expr(ref: tuple) -> dict:
    kind, entity, prop = ref
    key = "Measure" if kind == "M" else "Column"
    return {key: {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def projection(ref: tuple, active: bool = False, label: str | None = None) -> dict:
    kind, entity, prop = ref
    p = {"field": field_expr(ref), "queryRef": f"{entity}.{prop}", "nativeQueryRef": prop}
    if active:
        p["active"] = True
    if label:
        p["displayName"] = label
    return p


def role(refs: list, category: bool = False) -> dict:
    out = []
    for ref in refs:
        label = None
        if isinstance(ref, tuple) and len(ref) == 4:          # (kind, entity, prop, label)
            ref, label = ref[:3], ref[3]
        out.append(projection(ref, active=category and ref[0] == "C", label=label))
    return {"projections": out}


def L_(ref: tuple, label: str) -> tuple:         # a field with a column header / legend label
    return ref + (label,)


def title_objects(title: str | None, subtitle: str | None = None) -> dict:
    if title is None:
        return {"title": [{"properties": {"show": boolean(False)}}]}
    props = {"show": boolean(True), "text": text(title), "fontSize": num(11), "fontColor": color(ANTHRACITE),
             "fontFamily": text(FONT_SEMIBOLD)}
    out = {"title": [{"properties": props}]}
    if subtitle:
        out["subTitle"] = [{"properties": {"show": boolean(True), "text": text(subtitle), "fontSize": num(9),
                                           "fontColor": color(GREY)}}]
    return out


def container(name: str, x: float, y: float, w: float, h: float, z: int, visual: dict) -> dict:
    return {"$schema": VC_SCHEMA, "name": name,
            "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
            "visual": visual}


# ---------------------------------------------------------------- visual builders
def v_textbox(paragraphs: list[list[tuple]]) -> dict:
    """paragraphs = [[(text, size_pt, colour, font), ...], ...]"""
    paras = [{"textRuns": [{"value": t, "textStyle": {"fontFamily": f, "fontSize": f"{s}pt", "color": c}}
                           for t, s, c, f in runs]} for runs in paragraphs]
    return {"visualType": "textbox",
            "objects": {"general": [{"properties": {"paragraphs": paras}}]},
            "visualContainerObjects": {"title": [{"properties": {"show": boolean(False)}}],
                                       "background": [{"properties": {"show": boolean(False)}}],
                                       "border": [{"properties": {"show": boolean(False)}}],
                                       "visualHeader": [{"properties": {"show": boolean(False)}}],
                                       # no inner padding: avoids a scroll bar when the text fills the box
                                       "padding": [{"properties": {side: num(0) for side in
                                                                   ("top", "bottom", "left", "right")}}]}}


def v_rectangle(fill: str) -> dict:
    return {"visualType": "shape",
            "objects": {"shape": [{"properties": {"tileShape": text("rectangle")}}],
                        "fill": [{"properties": {"show": boolean(False)}}],
                        "outline": [{"properties": {"show": boolean(False)}}]},
            "visualContainerObjects": {
                "background": [{"properties": {"show": boolean(True), "color": color(fill), "transparency": num(0)}}],
                "title": [{"properties": {"show": boolean(False)}}],
                "border": [{"properties": {"show": boolean(False)}}],
                "dropShadow": [{"properties": {"show": boolean(False)}}],
                "visualHeader": [{"properties": {"show": boolean(False)}}]}}


def v_nav_button(label: str, target_page: str, current: bool) -> dict:
    bg, fg = (AERO, WHITE) if current else (NAVY, "#C9D3E0")
    return {"visualType": "actionButton",
            "objects": {
                "icon": [{"properties": {"shapeType": text("blank")}, "selector": {"id": "default"}},
                         {"properties": {"show": boolean(False)}}],
                "outline": [{"properties": {"show": boolean(False)}}],
                "fill": [{"properties": {"show": boolean(True)}},
                         {"properties": {"fillColor": color(bg), "transparency": num(0)}, "selector": {"id": "default"}},
                         {"properties": {"fillColor": color(NAVY_2 if not current else AERO), "transparency": num(0)},
                          "selector": {"id": "hover"}}],
                "text": [{"properties": {"show": boolean(True)}},
                         {"properties": {"text": text(label), "fontColor": color(fg), "fontSize": num(9.5),
                                         "fontFamily": text(FONT_SEMIBOLD if current else FONT),
                                         "horizontalAlignment": text("left"), "leftMargin": num(12)},
                          "selector": {"id": "default"}},
                         {"properties": {"fontColor": color(WHITE)}, "selector": {"id": "hover"}}]},
            "visualContainerObjects": {
                "visualLink": [{"properties": {"show": boolean(True), "type": text("PageNavigation"),
                                               "navigationSection": text(target_page)}}],
                "title": [{"properties": {"show": boolean(False)}}],
                "background": [{"properties": {"show": boolean(False)}}],
                "border": [{"properties": {"show": boolean(False)}}],
                "visualHeader": [{"properties": {"show": boolean(False)}}]}}


def v_slicer(ref: tuple, title: str) -> dict:
    return {"visualType": "slicer",
            "query": {"queryState": {"Values": role([ref], category=True)}},
            "objects": {"data": [{"properties": {"mode": text("Dropdown")}}],
                        "header": [{"properties": {"show": boolean(True), "text": text(title), "fontColor": color(GREY),
                                                   "textSize": num(9)}}],
                        "general": [{"properties": {"selfFilterEnabled": boolean(True)}}]},
            "visualContainerObjects": {"title": [{"properties": {"show": boolean(False)}}],
                                       "visualHeader": [{"properties": {"show": boolean(False)}}]}}


def v_cards(measures: list[tuple]) -> dict:
    return {"visualType": "cardVisual",
            "query": {"queryState": {"Data": role(measures)}},
            "objects": {
                "layout": [{"properties": {"orientation": num(0), "columnCount": integer(len(measures)),
                                           "customizePadding": boolean(False), "cellPadding": integer(10),
                                           "alignment": text("middle"), "style": text("Cards")}}],
                "value": [{"properties": {"fontColor": color(NAVY), "fontSize": num(24),
                                          "fontFamily": text(FONT_SEMIBOLD)}, "selector": {"id": "default"}}],
                "label": [{"properties": {"fontColor": color(GREY), "fontSize": num(9)}, "selector": {"id": "default"}}],
                "accentBar": [{"properties": {"show": boolean(True), "color": color(AERO)}, "selector": {"id": "default"}}],
                "outline": [{"properties": {"show": boolean(True), "lineColor": color(BORDER)}, "selector": {"id": "default"}}],
                "shadowCustom": [{"properties": {"show": boolean(False)}, "selector": {"id": "default"}}]},
            "visualContainerObjects": {"title": [{"properties": {"show": boolean(False)}}],
                                       "background": [{"properties": {"show": boolean(False)}}],
                                       "border": [{"properties": {"show": boolean(False)}}]}}


def v_chart(kind: str, category: tuple, y: list, title: str, subtitle: str | None = None, series: tuple | None = None,
            y2: list | None = None, sort: tuple | None = None, descending: bool = True, labels: bool = False,
            axis_width: int | None = None) -> dict:
    state = {"Category": role([category], category=True), "Y": role(y)}
    if series:
        state["Series"] = role([series])
    if y2:
        state["Y2"] = role(y2)
    query = {"queryState": state}
    if sort:
        query["sortDefinition"] = {"sort": [{"field": field_expr(sort), "direction": "Descending" if descending else "Ascending"}],
                                   "isDefaultSort": True}
    objects = {}
    if labels:
        objects["labels"] = [{"properties": {"show": boolean(True), "fontSize": num(8), "color": color(GREY)}}]
    if axis_width:   # maximum share of the visual (%) for the category labels, so long names are not cut (Phase 9)
        objects["categoryAxis"] = [{"properties": {"maxMarginFactor": integer(axis_width)}}]
    if kind in ("clusteredBarChart", "clusteredColumnChart") and not series:
        objects["dataPoint"] = [{"properties": {"fill": color(AERO)}}]
    if kind == "lineClusteredColumnComboChart":
        objects["dataPoint"] = [{"properties": {"fill": color(AERO_LIGHT)}, "selector": {"metadata": f"{y[0][1]}.{y[0][2]}"}},
                                {"properties": {"fill": color(NAVY)}, "selector": {"metadata": f"{y2[0][1]}.{y2[0][2]}"}}]
    visual = {"visualType": kind, "query": query, "visualContainerObjects": title_objects(title, subtitle)}
    if objects:
        visual["objects"] = objects
    return visual


def v_table(fields: list, title: str, subtitle: str | None = None, sort: tuple | None = None, descending: bool = True,
            color_rules: list | None = None) -> dict:
    query = {"queryState": {"Values": role(fields)}}
    if sort:
        query["sortDefinition"] = {"sort": [{"field": field_expr(sort), "direction": "Descending" if descending else "Ascending"}],
                                   "isDefaultSort": True}
    objects = {"total": [{"properties": {"totals": boolean(False)}}]}
    if color_rules:
        objects["values"] = [{"properties": {"fontColor": measure_color(colour_measure)},
                              "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}],
                                           "metadata": f"{MEASURES_TABLE}.{target}"}}
                             for target, colour_measure in color_rules]
    return {"visualType": "tableEx", "query": query, "objects": objects,
            "visualContainerObjects": title_objects(title, subtitle)}


# ---------------------------------------------------------------- pages
PAGES = [
    ("p01executive", "Executive Overview"),
    ("p02quality", "Quality Performance"),
    ("p03capa", "Corrective Actions"),
    ("p04documents", "Document Control"),
    ("p05inventory", "Materials & Inventory"),
    ("p06maintenance", "Maintenance Production"),
    ("p07aircraft", "Aircraft Overview"),
    ("p08audit", "Audit & Traceability"),
]
PAGE_SUBTITLES = {
    "p01executive": "Company-wide view: key indicators against fictitious internal targets",
    "p02quality": "Non-conformities: volume, severity, recurring problems and root causes",
    "p03capa": "Corrective and preventive actions: backlog, deadlines and effectiveness",
    "p04documents": "Document validity, verification discrepancies and traceability",
    "p05inventory": "Stock availability, count accuracy, shortages and supplier delivery",
    "p06maintenance": "Work orders: on-time completion, delays and blocked orders",
    "p07aircraft": "Fleet comparison and individual aircraft",
    "p08audit": "Audit trail, data validation and KPI reconciliation",
}
PERIOD_SLICER = (C("Dim_Date", "period_year_label"), "Period")

# Grid (canvas 1280 x 720; sidebar 0-200)
X0, W = 216, 1048
LEFT_W, RIGHT_X, RIGHT_W = 628, 856, 408
CARDS_Y, CARDS_H = 76, 96
MAIN_Y, MAIN_H = 184, 260
BOTTOM_Y, BOTTOM_H = 456, 252
LESSON_CARDS_H = 84                       # lessons learned block, Corrective Actions page (Phase 9)


def page_content(page: str) -> list[tuple]:
    """Visuals of each page: (name, x, y, w, h, visual)."""
    D = lambda c: C("Dim_Date", c)                       # noqa: E731
    month = D("month_label")
    if page == "p01executive":
        return [
            ("slicer1", 1060, 14, 204, 52, v_slicer(*PERIOD_SLICER)),
            ("cards", X0, CARDS_Y, W, CARDS_H, v_cards([M("Open Non-Conformities"), M("Overdue Corrective Actions"),
                                                        M("Document Compliance Rate"), M("Stock Availability"),
                                                        L_(M("Maintenance Order Completion Rate"), "Order Completion Rate")])),
            ("trend", X0, MAIN_Y, LEFT_W, MAIN_H, v_chart(
                "lineClusteredColumnComboChart", month, [M("Total Quality Incidents")],
                "Non-conformities per month", "Columns: detected · Line: per 100 completed work orders",
                y2=[M("Non-Conformity Rate")])),
            ("scorecard", RIGHT_X, MAIN_Y, RIGHT_W, MAIN_H + 12 + BOTTOM_H, v_table(
                [L_(C("Dim_KPI", "kpi_id"), "KPI"), L_(C("Dim_KPI", "kpi_name"), "Indicator"),
                 L_(M("KPI Display Value"), "Value"), L_(C("Dim_KPI", "target_label"), "Target*"),
                 L_(M("KPI Status Label"), "Status")],
                "KPI scorecard", "*Fictitious internal targets of AEROQ MRO, not regulatory thresholds",
                color_rules=[("KPI Status Label", "KPI Status Color")])),
            ("openNC", X0, BOTTOM_Y, LEFT_W, BOTTOM_H, v_table(
                [L_(C("Fact_Incidents", "incident_number"), "Non-conformity"), C("Fact_Incidents", "severity"),
                 C("Fact_Incidents", "status"), L_(C("Dim_IncidentCategory", "category_name"), "Category"),
                 L_(C("Dim_Department", "department_code"), "Dept."), L_(M("Open NC Age (days)"), "Age (days)")],
                "Open non-conformities", "At the cut-off date · oldest first", sort=M("Open NC Age (days)"))),
        ]
    if page == "p02quality":
        return [
            ("slicer1", 852, 14, 204, 52, v_slicer(*PERIOD_SLICER)),
            ("slicer2", 1060, 14, 204, 52, v_slicer(C("Dim_Department", "department_label"), "Department")),
            ("cards", X0, CARDS_Y, W, CARDS_H, v_cards([M("Total Quality Incidents"), M("Open Non-Conformities"),
                                                        M("Non-Conformity Rate"), M("Average Resolution Time"),
                                                        M("RCA Coverage (Critical & Major)")])),
            ("bySeverity", X0, MAIN_Y, LEFT_W, MAIN_H, v_chart(
                "columnChart", month, [M("Total Quality Incidents")], "Non-conformities per month, by severity",
                series=C("Fact_Incidents", "severity"))),
            ("pareto", RIGHT_X, MAIN_Y, RIGHT_W, MAIN_H, v_chart(
                "clusteredBarChart", C("Dim_IncidentCategory", "category_name"), [M("Total Quality Incidents")],
                "Recurring problems by category", "Pareto: highest first", sort=M("Total Quality Incidents"),
                labels=True, axis_width=45)),
            ("resolution", X0, BOTTOM_Y, LEFT_W, BOTTOM_H, v_chart(
                "clusteredColumnChart", C("Dim_Department", "department_code"), [M("Average Resolution Time")],
                "Average resolution time by department (days)", "Non-conformities closed in the period",
                sort=M("Average Resolution Time"), labels=True)),
            ("rootCause", RIGHT_X, BOTTOM_Y, RIGHT_W, BOTTOM_H, v_chart(
                "clusteredBarChart", C("Fact_Incidents", "root_cause_6m"), [M("Analysed Non-Conformities")],
                "Root causes (Ishikawa 6M)", "Non-conformities with a root-cause analysis",
                sort=M("Analysed Non-Conformities"), labels=True)),
        ]
    if page == "p03capa":
        return [
            ("slicer1", 852, 14, 204, 52, v_slicer(*PERIOD_SLICER)),
            ("slicer2", 1060, 14, 204, 52, v_slicer(C("Dim_Department", "department_label"), "Department")),
            ("cards", X0, CARDS_Y, W, CARDS_H, v_cards([L_(M("Actions Pending Implementation"), "Pending Implementation"),
                                                        M("Overdue Corrective Actions"),
                                                        M("Corrective Action Closure Rate"), M("Effectiveness Rate"),
                                                        M("Rescheduled Actions")])),
            ("byStatus", X0, MAIN_Y, LEFT_W, MAIN_H, v_chart(
                "clusteredColumnChart", C("Fact_CAPA", "status"), [M("Actions Created")],
                "Actions by status and type", "Actions created in the period", series=C("Fact_CAPA", "action_type"),
                labels=True)),
            ("backlog", RIGHT_X, MAIN_Y, RIGHT_W, MAIN_H, v_chart(
                "lineChart", month, [M("Actions Pending Implementation"), M("Overdue Corrective Actions")],
                "Action backlog at each month end", "Pending implementation · overdue corrective actions")),
            ("openActions", X0, BOTTOM_Y, LEFT_W, BOTTOM_H, v_table(
                [L_(C("Fact_CAPA", "action_number"), "Action"),
                 C("Fact_CAPA", "title"), L_(C("Dim_Employee", "full_name"), "Responsible"),
                 L_(C("Dim_Department", "department_code"), "Dept."), C("Fact_CAPA", "due_date"),
                 L_(M("Open Action Progress"), "Progress"), L_(M("Open Action Days Overdue"), "Days overdue")],
                "Open actions", "At the cut-off date · most overdue first", sort=M("Open Action Days Overdue"))),
            # Lessons learned block (Phase 9): the last step of the improvement cycle
            ("lessonCards", RIGHT_X, BOTTOM_Y, RIGHT_W, LESSON_CARDS_H, v_cards(
                [L_(M("Lesson Incorporation Rate"), "Incorporation Rate"),
                 L_(M("Lessons Pending Incorporation"), "Pending Incorporation")])),
            ("lessons", RIGHT_X, BOTTOM_Y + LESSON_CARDS_H + 12, RIGHT_W, BOTTOM_H - LESSON_CARDS_H - 12, v_table(
                [L_(C("Fact_Lessons", "lesson_number"), "Lesson"), C("Fact_Lessons", "status"),
                 L_(C("Fact_Lessons", "incorporated_in"), "Incorporated in"),
                 L_(M("Lesson Days Pending"), "Days pending")],
                "Lessons learned", "Pending incorporation first · target ≥ 80% (fictitious)",
                sort=M("Lesson Days Pending"))),
        ]
    if page == "p04documents":
        return [
            ("slicer1", 852, 14, 204, 52, v_slicer(*PERIOD_SLICER)),
            ("slicer2", 1060, 14, 204, 52, v_slicer(C("Dim_Document", "document_type"), "Document type")),
            ("cards", X0, CARDS_Y, W, CARDS_H, v_cards([M("Document Compliance Rate"), M("Expired Documents"),
                                                        M("Documentation Error Rate"), M("Traceability Compliance"),
                                                        M("Routine Verifications")])),
            ("compliance", X0, MAIN_Y, LEFT_W, MAIN_H, v_chart(
                "lineClusteredColumnComboChart", month, [M("Expired Documents")],
                "Document compliance at each month end", "Columns: expired documents · Line: compliance rate",
                y2=[M("Document Compliance Rate")])),
            ("byType", RIGHT_X, MAIN_Y, RIGHT_W, MAIN_H, v_chart(
                "clusteredBarChart", C("Fact_DocumentVerifications", "verification_type"),
                [M("Discrepancy Rate (All Verifications)")], "Verifications with discrepancies, by type",
                "Internal audits target risk areas: excluded from DOC-02", sort=M("Discrepancy Rate (All Verifications)"),
                labels=True, axis_width=45)),
            ("expired", X0, BOTTOM_Y, W, BOTTOM_H, v_table(
                [L_(C("Dim_Document", "document_code"), "Document"), C("Dim_Document", "title"),
                 L_(C("Dim_Document", "document_type"), "Type"), L_(C("Dim_Document", "owner_department_code"), "Owner"),
                 L_(C("Dim_Document", "current_revision"), "Revision"), C("Dim_Document", "review_due_date"),
                 L_(M("Expired Document Days Overdue"), "Days overdue")],
                "Documents past their review date", "At the cut-off date · most overdue first",
                sort=M("Expired Document Days Overdue"))),
        ]
    if page == "p05inventory":
        return [
            ("slicer1", 852, 14, 204, 52, v_slicer(*PERIOD_SLICER)),
            ("slicer2", 1060, 14, 204, 52, v_slicer(C("Dim_Material", "material_class"), "Material class")),
            ("cards", X0, CARDS_Y, W, CARDS_H, v_cards([M("Stock Availability"), M("Materials Below Minimum"),
                                                        M("Inventory Accuracy"), M("Material Shortage Rate"),
                                                        M("Pending Purchase Orders")])),
            ("accuracy", X0, MAIN_Y, LEFT_W, MAIN_H, v_chart(
                "lineChart", month, [M("Inventory Accuracy"), M("Material Shortage Rate")],
                "Inventory accuracy and material shortages per month",
                "Counting procedure revised in August 2025")),
            ("suppliers", RIGHT_X, MAIN_Y, RIGHT_W, MAIN_H, v_chart(
                "clusteredBarChart", C("Dim_Supplier", "supplier_code"), [M("On-Time Delivery Rate")],
                "Supplier on-time delivery", "Lowest first · lines fully received", sort=M("On-Time Delivery Rate"),
                descending=False, labels=True)),
            ("belowMin", X0, BOTTOM_Y, W, BOTTOM_H, v_table(
                [L_(C("Dim_Material", "part_number"), "Part number"), C("Dim_Material", "description"),
                 L_(C("Dim_Material", "material_class"), "Class"), L_(C("Dim_Material", "unit_of_measure"), "Unit"),
                 L_(M("Available Qty (Below Minimum)"), "Available"), L_(M("Minimum Stock (Below Minimum)"), "Minimum"),
                 L_(M("In Receiving Inspection (Below Minimum)"), "In inspection")],
                "Materials below minimum stock", "At the end of the selected period",
                sort=M("Available Qty (Below Minimum)"), descending=False)),
        ]
    if page == "p06maintenance":
        return [
            ("slicer1", 852, 14, 204, 52, v_slicer(*PERIOD_SLICER)),
            ("slicer2", 1060, 14, 204, 52, v_slicer(C("Fact_MaintenanceOrders", "maintenance_type"), "Maintenance type")),
            ("cards", X0, CARDS_Y, W, CARDS_H, v_cards([M("Open Work Orders"),
                                                        L_(M("Maintenance Order Completion Rate"), "Order Completion Rate"),
                                                        M("Average Maintenance Delay"),
                                                        L_(M("Work Orders Blocked by Material"), "Blocked by Material"),
                                                        L_(M("Work Orders Blocked by Documentation"), "Blocked by Documentation")])),
            ("completion", X0, MAIN_Y, LEFT_W, MAIN_H, v_chart(
                "lineClusteredColumnComboChart", month, [M("Completed Orders")],
                "Work orders completed and on-time rate", "Columns: completed · Line: completed by the planned date",
                y2=[M("Maintenance Order Completion Rate")])),
            ("holdImpact", RIGHT_X, MAIN_Y, RIGHT_W, MAIN_H, v_chart(
                "clusteredBarChart", C("Fact_MaintenanceOrders", "material_hold_group"),
                [M("On-Time Rate (Completed Orders)")], "Impact of material shortages",
                "On-time completion of orders with and without a material hold", labels=True)),
            ("blocked", X0, BOTTOM_Y, W, BOTTOM_H, v_table(
                [L_(C("Fact_Holds", "mo_number"), "Work order"), L_(C("Dim_Aircraft", "registration"), "Aircraft"),
                 L_(C("Fact_Holds", "hold_reason"), "Reason"), L_(C("Dim_Material", "part_number"), "Material"),
                 L_(C("Fact_Holds", "document_code"), "Document"), L_(C("Fact_Holds", "start_date"), "Since"),
                 L_(M("Active Hold Days"), "Days"), C("Fact_Holds", "comment")],
                "Work orders blocked", "At the cut-off date · longest first", sort=M("Active Hold Days"))),
        ]
    if page == "p07aircraft":
        return [
            ("slicer1", 852, 14, 204, 52, v_slicer(*PERIOD_SLICER)),
            ("slicer2", 1060, 14, 204, 52, v_slicer(C("Dim_Aircraft", "registration"), "Aircraft")),
            ("cards", X0, CARDS_Y, W, CARDS_H, v_cards([M("Fleet Size"), M("Aircraft In Maintenance"), M("Orders Opened"),
                                                        M("Unscheduled Share"), M("Total Quality Incidents")])),
            ("byAircraft", X0, MAIN_Y, LEFT_W, MAIN_H, v_chart(
                "columnChart", C("Dim_Aircraft", "registration"), [M("Orders Opened")],
                "Work orders by aircraft and maintenance type", series=C("Fact_MaintenanceOrders", "maintenance_type"),
                sort=M("Orders Opened"))),
            ("monthly", RIGHT_X, MAIN_Y, RIGHT_W, MAIN_H, v_chart(
                "lineChart", month, [M("Orders Opened")], "Work orders opened per month",
                "Select an aircraft to see its own history")),
            ("fleet", X0, BOTTOM_Y, W, BOTTOM_H, v_table(
                [L_(C("Dim_Aircraft", "registration"), "Aircraft"), L_(C("Dim_Aircraft", "aircraft_model"), "Model"),
                 L_(C("Dim_Aircraft", "customer_name"), "Customer"), L_(C("Dim_Aircraft", "operational_status"), "Status"),
                 L_(M("Orders Opened"), "Orders"), L_(M("Unscheduled Share"), "Unscheduled"),
                 L_(M("Maintenance Order Completion Rate"), "On time"), L_(M("Average Maintenance Delay"), "Avg delay (d)"),
                 L_(M("Material Hold Days (Total)"), "Material hold days"), L_(M("Total Quality Incidents"), "Non-conformities")],
                "Fleet comparison", "Selected period", sort=M("Orders Opened"))),
        ]
    if page == "p08audit":
        return [
            ("slicer1", 852, 14, 204, 52, v_slicer(C("Fact_AuditEvents", "table_name"), "Table")),
            ("slicer2", 1060, 14, 204, 52, v_slicer(C("Fact_AuditEvents", "record_ref"), "Record")),
            ("cards", X0, CARDS_Y, W, CARDS_H, v_cards([L_(M("Data Quality Score (Rules Passed)"), "Data Quality Score"), L_(M("Validation Rules Executed"), "Rules executed"), L_(M("Critical Rule Failures"), "Critical failures"),
                                                        M("Planted Discrepancies Detected"), L_(M("Audit Events (Label)"), "Audit Events")])),
            ("trail", X0, MAIN_Y, LEFT_W, MAIN_H + 12 + BOTTOM_H, v_table(
                [L_(C("Fact_AuditEvents", "event_datetime"), "When"), L_(C("Fact_AuditEvents", "record_ref"), "Record"),
                 L_(C("Fact_AuditEvents", "change_label"), "Change"), L_(C("Dim_Employee", "full_name"), "Who")],
                "Audit trail", "Select a record above to rebuild its full history",
                sort=C("Fact_AuditEvents", "event_datetime"), descending=False)),
            ("reconciliation", RIGHT_X, MAIN_Y, RIGHT_W, 300, v_table(
                [L_(C("Dim_KPI", "kpi_id"), "KPI"), L_(M("KPI Value (SQL)"), "SQL"), L_(M("KPI Value (Power BI)"), "Power BI"),
                 L_(M("KPI Reconciliation"), "Check")],
                "K03 · Power BI vs SQL reference", "Whole period · both values must match")),
            ("findings", RIGHT_X, MAIN_Y + 312, RIGHT_W, MAIN_H + BOTTOM_H - 300, v_table(
                [L_(C("Fact_ValidationFindings", "rule_id"), "Rule"), L_(C("Fact_ValidationFindings", "record_ref"), "Record"),
                 C("Fact_ValidationFindings", "detail")],
                "Validation findings to review", "WARNING rules (89 rules executed)")),
        ]
    raise ValueError(page)


def chrome(page: str, title: str) -> list[tuple]:
    """Sidebar, navigation and header common to all pages."""
    items = [
        ("sidebar", 0, 0, 200, 720, v_rectangle(NAVY)),
        ("brand", 12, 14, 180, 78, v_textbox([[("AQMI", 22, WHITE, FONT_SEMIBOLD)],
                                               [("AEROQ MRO · Quality Office", 9, AERO_LIGHT, FONT)]])),
        ("footer", 12, 628, 180, 80, v_textbox([[("Synthetic data · fictitious company", 8, GREY_LIGHT, FONT)],
                                                [("Portfolio project. Not a certified system.", 8, GREY_LIGHT, FONT)]])),
        ("header", X0, 8, 620, 66, v_textbox([[(title, 17, NAVY, FONT_SEMIBOLD)],
                                               [(PAGE_SUBTITLES[page] + "  ·  Data as of 31 Oct 2026", 9, GREY, FONT)]])),
    ]
    for i, (target, label) in enumerate(PAGES):
        items.append((f"nav{i + 1:02d}", 12, 104 + i * 44, 188, 36, v_nav_button(label, target, target == page)))
    return items


# Charts whose axis must not show the "(Blank)" member. It appears when fact rows have
# no date for the relationship used by a measure (e.g. orders not finished yet), or
# no aircraft (non-conformities not related to an aircraft).
NOT_BLANK_AXES = {
    **{key: ("Dim_Date", "Month Label") for key in [
        ("p01executive", "trend"), ("p02quality", "bySeverity"), ("p03capa", "backlog"),
        ("p04documents", "compliance"), ("p05inventory", "accuracy"), ("p06maintenance", "completion"),
        ("p07aircraft", "monthly")]},
    ("p07aircraft", "byAircraft"): ("Dim_Aircraft", "Registration"),
}


def not_blank_filter(entity: str, prop: str, visual_id: str) -> dict:
    """Visual-level 'is not blank' filter on the axis column."""
    col = lambda src: {"Column": {"Expression": {"SourceRef": src}, "Property": prop}}
    return {
        "name": uuid.uuid5(uuid.NAMESPACE_URL, f"aqmi/{visual_id}/notblank").hex[:20],
        "field": col({"Entity": entity}),
        "type": "Advanced",
        "filter": {"Version": 2, "From": [{"Name": "x", "Entity": entity, "Type": 0}],
                   "Where": [{"Condition": {"Not": {"Expression": {"Comparison": {
                       "ComparisonKind": 0, "Left": col({"Source": "x"}),
                       "Right": {"Literal": {"Value": "null"}}}}}}}]},
        "howCreated": "Auto",
    }


def build_report(root: Path) -> None:
    rp = root / f"{NAME}.Report"
    definition = rp / "definition"
    (definition / "pages").mkdir(parents=True)
    write_json(rp / ".platform", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": NAME},
        "config": {"version": "2.0", "logicalId": guid("report")}})
    write_json(rp / "definition.pbir", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": f"../{NAME}.SemanticModel"}}})
    write_json(definition / "version.json", {
        "$schema": f"{SCHEMA_BASE}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    write_json(definition / "report.json", {
        "$schema": f"{SCHEMA_BASE}/report/3.3.0/schema.json",
        "themeCollection": {
            "baseTheme": {"name": "CY24SU10", "reportVersionAtImport": {"visual": "1.8.97", "report": "2.0.97", "page": "1.3.97"},
                          "type": "SharedResources"},
            "customTheme": {"name": THEME_FILE, "reportVersionAtImport": {"visual": "1.8.100", "report": "2.0.100", "page": "1.3.100"},
                            "type": "RegisteredResources"}},
        "objects": {"outspacePane": [{"properties": {"expanded": boolean(False), "visible": boolean(True)}}]},
        "resourcePackages": [
            {"name": "SharedResources", "type": "SharedResources",
             "items": [{"name": "CY24SU10", "path": "BaseThemes/CY24SU10.json", "type": "BaseTheme"}]},
            {"name": "RegisteredResources", "type": "RegisteredResources",
             "items": [{"name": THEME_FILE, "path": THEME_FILE, "type": "CustomTheme"}]}],
        "settings": {"useStylableVisualContainerHeader": True, "defaultFilterActionIsDataFilter": True,
                     "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True,
                     "allowInlineExploration": True, "useEnhancedTooltips": True,
                     # numbers and dates always in English (US), whatever the viewer's locale
                     "locale": "en-US", "defaultDisplayUnitsToNone": True}})
    write_json(definition / "pages" / "pages.json", {
        "$schema": f"{SCHEMA_BASE}/pagesMetadata/1.0.0/schema.json",
        "pageOrder": [p for p, _ in PAGES], "activePageName": PAGES[0][0]})
    for page, title in PAGES:
        folder = definition / "pages" / page
        (folder / "visuals").mkdir(parents=True)
        write_json(folder / "page.json", {
            "$schema": PAGE_SCHEMA, "name": page, "displayName": title, "displayOption": "FitToPage",
            "height": 720, "width": 1280,
            "objects": {"background": [{"properties": {"color": color(CANVAS), "transparency": num(0)}}],
                        "outspace": [{"properties": {"color": color("#E9EDF2")}}]}})
        z = 0
        for name, x, y, w, h, visual in chrome(page, title) + page_content(page):
            z += 1000
            item = container(name, x, y, w, h, z, visual)
            if (page, name) in NOT_BLANK_AXES:
                item["filterConfig"] = {"filters": [not_blank_filter(*NOT_BLANK_AXES[(page, name)], f"{page}/{name}")]}
            write_json(folder / "visuals" / name / "visual.json", item)
    theme_dir = rp / "StaticResources" / "RegisteredResources"
    theme_dir.mkdir(parents=True)
    write_json(theme_dir / THEME_FILE, theme())


def theme() -> dict:
    solid = lambda c: {"solid": {"color": c}}     # noqa: E731
    return {
        "name": "AQMI Aero",
        "dataColors": [AERO, NAVY, AERO_LIGHT, GREY, GREEN, AMBER, RED, GREY_LIGHT, "#3E8FD8", "#264A73"],
        "background": WHITE, "foreground": ANTHRACITE, "tableAccent": AERO,
        "good": GREEN, "neutral": AMBER, "bad": RED, "maximum": AERO, "center": AMBER, "minimum": RED, "null": GREY_LIGHT,
        "textClasses": {
            "callout": {"fontSize": 24, "fontFace": FONT_SEMIBOLD, "color": NAVY},
            "title": {"fontSize": 11, "fontFace": FONT_SEMIBOLD, "color": ANTHRACITE},
            "header": {"fontSize": 11, "fontFace": FONT_SEMIBOLD, "color": ANTHRACITE},
            "label": {"fontSize": 9, "fontFace": FONT, "color": GREY}},
        "visualStyles": {
            "*": {"*": {
                "title": [{"show": True, "fontFamily": FONT_SEMIBOLD, "fontSize": 11, "fontColor": solid(ANTHRACITE)}],
                "subTitle": [{"fontFamily": FONT, "fontSize": 9, "fontColor": solid(GREY)}],
                "background": [{"show": True, "color": solid(WHITE), "transparency": 0}],
                "border": [{"show": True, "color": solid(BORDER), "radius": 6}],
                "dropShadow": [{"show": False}],
                "padding": [{"top": 8, "bottom": 8, "left": 10, "right": 10}],
                "categoryAxis": [{"fontSize": 8, "labelColor": solid(GREY), "showAxisTitle": False}],
                "valueAxis": [{"fontSize": 8, "labelColor": solid(GREY), "showAxisTitle": False,
                               "gridlineColor": solid(BORDER), "gridlineStyle": "dotted"}],
                "legend": [{"show": True, "position": "Top", "fontSize": 8, "labelColor": solid(GREY)}]}},
            "page": {"*": {"background": [{"color": solid(CANVAS), "transparency": 0}],
                           "outspace": [{"color": solid("#E9EDF2")}]}},
            "tableEx": {"*": {
                "columnHeaders": [{"backColor": solid(NAVY), "fontColor": solid(WHITE), "fontFamily": FONT_SEMIBOLD,
                                   "fontSize": 9, "wordWrap": True}],
                "values": [{"fontSize": 9, "fontFamily": FONT, "backColorSecondary": solid("#F6F8FB")}],
                "grid": [{"gridHorizontal": True, "gridHorizontalColor": solid(BORDER), "rowPadding": 3}]}},
            "slicer": {"*": {"items": [{"fontSize": 9}], "background": [{"show": True, "color": solid(WHITE)}]}}}}


# =============================================================================
# 3. PROJECT
# =============================================================================
def write_json(path: Path, content: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content if content.endswith("\n") else content + "\n", encoding="utf-8")


def build(out_dir: Path = settings.POWERBI_DIR, schema_path: Path = settings.POWERBI_DATA_DIR / "_schema.json",
          data_folder: str | None = None, force: bool = False) -> Path:
    if not schema_path.exists():
        raise FileNotFoundError("data/processed/_schema.json not found: run 'python scripts/export_powerbi.py' first")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    targets = [out_dir / f"{NAME}.pbip", out_dir / f"{NAME}.SemanticModel", out_dir / f"{NAME}.Report"]
    if any(t.exists() for t in targets):
        if not force:
            raise FileExistsError("The Power BI project already exists. Use --force to rebuild it "
                                  "(changes made in Power BI Desktop would be lost).")
        for t in targets:
            shutil.rmtree(t) if t.is_dir() else t.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)
    if data_folder is None:
        data_folder = str(settings.POWERBI_DATA_DIR) + ("\\" if "\\" in str(settings.POWERBI_DATA_DIR) else "/")
    write_json(out_dir / f"{NAME}.pbip", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0", "artifacts": [{"report": {"path": f"{NAME}.Report"}}],
        "settings": {"enableAutoRecovery": True}})
    write_text(out_dir / ".gitignore", "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n")
    build_semantic_model(out_dir, schema, data_folder)
    build_report(out_dir)
    return out_dir / f"{NAME}.pbip"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the AQMI Power BI project (.pbip)")
    parser.add_argument("--force", action="store_true", help="rebuild the project even if it already exists")
    parser.add_argument("--data-folder", help="folder with the CSV files, as Power BI will see it "
                                              "(default: data/processed of this project)")
    args = parser.parse_args()
    try:
        path = build(data_folder=args.data_folder, force=args.force)
    except (FileNotFoundError, FileExistsError) as error:
        logger.error("%s", error)
        return 1
    logger.info("Power BI project written: %s", path.relative_to(settings.PROJECT_ROOT))
    logger.info("Open it with Power BI Desktop (double-click AQMI.pbip)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
