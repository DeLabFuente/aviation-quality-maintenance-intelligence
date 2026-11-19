"""
AQMI — Reference catalogues for the synthetic data generator.

Everything in this file is INVENTED for the fictitious company AEROQ MRO:
names, part numbers, document titles and texts. Nothing comes from a real
organisation, a real aircraft manufacturer or military sources.
Descriptions are deliberately generic and administrative: AQMI controls
information, not engineering.
"""

# -----------------------------------------------------------------------------
# People (fictitious Spanish names; any resemblance to real people is chance)
# -----------------------------------------------------------------------------
FIRST_NAMES = [
    "Alejandro", "Ana", "Andrés", "Beatriz", "Carlos", "Carmen", "Cristina", "David",
    "Elena", "Enrique", "Eva", "Fernando", "Francisco", "Gloria", "Ignacio", "Inés",
    "Javier", "Jorge", "José", "Laura", "Lucía", "Luis", "Manuel", "María", "Marta",
    "Miguel", "Natalia", "Nuria", "Pablo", "Patricia", "Pedro", "Pilar", "Raúl",
    "Rocío", "Rosa", "Sergio", "Silvia", "Teresa", "Víctor", "Yolanda",
]

LAST_NAMES = [
    "García", "Martínez", "López", "Sánchez", "Pérez", "Gómez", "Martín", "Jiménez",
    "Ruiz", "Hernández", "Moreno", "Muñoz", "Álvarez", "Romero", "Alonso", "Gutiérrez",
    "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez", "Serrano",
    "Blanco", "Molina", "Morales", "Suárez", "Ortega", "Delgado", "Castro", "Ortiz",
    "Rubio", "Marín", "Sanz", "Núñez", "Iglesias", "Medina", "Garrido", "Cortés",
]

# (department code, job title, number of people, is head of department)
STAFFING = [
    ("DIR", "General Manager", 1, True),
    ("DIR", "Operations Manager", 1, False),
    ("DIR", "Administration Officer", 1, False),
    ("QUA", "Head of Quality", 1, True),
    ("QUA", "Quality Auditor", 2, False),
    ("QUA", "Quality Inspector", 3, False),
    ("QUA", "Quality Analyst", 1, False),
    ("DOC", "Head of Document Control", 1, True),
    ("DOC", "Document Controller", 3, False),
    ("DOC", "Technical Records Clerk", 1, False),
    ("PRD", "Head of Production Planning & Control", 1, True),
    ("PRD", "Production Planner", 3, False),
    ("PRD", "Production Control Clerk", 3, False),
    ("MNT", "Head of Maintenance", 1, True),
    ("MNT", "Maintenance Supervisor", 3, False),
    ("MNT", "Maintenance Technician", 9, False),
    ("LOG", "Head of Logistics", 1, True),
    ("LOG", "Storekeeper", 4, False),
    ("LOG", "Buyer", 3, False),
    ("LOG", "Logistics Clerk", 1, False),
]

# New hires during the simulated period: (hire date, department, job title)
NEW_HIRES = [
    ("2025-04-07", "QUA", "Quality Inspector"),
    ("2025-09-01", "LOG", "Storekeeper"),
]

# One person leaves: the first holder of this job title (termination date, notice date)
TERMINATION = {"job_title": "Quality Inspector", "notice_date": "2026-03-02", "termination_date": "2026-03-31"}

# -----------------------------------------------------------------------------
# Customers and fleet (fictitious names, impossible registrations EC-Q00)
# -----------------------------------------------------------------------------
CUSTOMERS = [
    ("CUS-01", "Vetaro Medevac", "HEMS", "ES"),
    ("CUS-02", "Calvera Aerial Works", "AERIAL_WORK", "ES"),
    ("CUS-03", "Nortia Air Shuttle", "PASSENGER_TRANSPORT", "PT"),
    ("CUS-04", "Ostrana Private Wings", "PRIVATE", "ES"),
]

# (registration, category, model, customer code, year, contract start, contract end)
AIRCRAFT = [
    ("EC-Q01", "LIGHT_TWIN", "LT-200", "CUS-01", 2014, "2021-03-01", None),
    ("EC-Q02", "LIGHT_TWIN", "LT-200", "CUS-01", 2016, "2021-03-01", None),
    ("EC-Q03", "LIGHT_TWIN", "LT-200", "CUS-01", 2018, "2022-01-15", None),
    ("EC-Q04", "LIGHT_TWIN", "LT-200", "CUS-01", 2011, "2020-06-01", "2026-03-31"),
    ("EC-Q05", "LIGHT_TWIN", "LT-200", "CUS-04", 2019, "2023-05-02", None),
    ("EC-Q06", "LIGHT_SINGLE", "LS-100", "CUS-02", 2009, "2019-04-01", None),
    ("EC-Q07", "LIGHT_SINGLE", "LS-100", "CUS-02", 2008, "2019-04-01", None),
    ("EC-Q08", "LIGHT_SINGLE", "LS-100", "CUS-02", 2013, "2020-09-01", None),
    ("EC-Q09", "LIGHT_SINGLE", "LS-100", "CUS-02", 2017, "2022-06-01", None),
    ("EC-Q10", "MEDIUM_TWIN", "MT-300", "CUS-03", 2015, "2021-11-02", None),
    ("EC-Q11", "MEDIUM_TWIN", "MT-300", "CUS-03", 2020, "2023-02-01", None),
    ("EC-Q12", "MEDIUM_TWIN", "MT-300", "CUS-01", 2022, "2025-06-02", None),
]
# The contract end of EC-Q04 is notified to the system on this date:
CONTRACT_END_NOTICE = {"EC-Q04": "2026-01-15"}

# -----------------------------------------------------------------------------
# Suppliers (invented names built from syllables)
# -----------------------------------------------------------------------------
SUPPLIER_PREFIXES = ["Al", "Bel", "Cor", "Dar", "Fen", "Gal", "Hal", "Ir", "Jor", "Kel",
                     "Lor", "Mar", "Nor", "Or", "Par", "Ros", "Sel", "Tor", "Val", "Zor"]
SUPPLIER_MIDDLES = ["ta", "ve", "ri", "no", "ma", "lo", "sa", "du", "pe", "xi"]
SUPPLIER_SUFFIXES = ["Aero Supply", "Components", "Aviation Parts", "Technical Supplies",
                     "Aero Logistics", "Industrial", "Repair Services", "Aero Distribution"]
SUPPLIER_COUNTRIES = ["ES"] * 10 + ["FR", "FR", "DE", "DE", "IT", "GB", "NL", "PT", "US"]

# -----------------------------------------------------------------------------
# Materials — exactly 100 fictitious references
# tag: family used to decide which kind of maintenance order uses the material
# (description, class, unit, serialized, shelf life, tag, lead time days, unit cost EUR)
# -----------------------------------------------------------------------------
def _materials() -> list[tuple]:
    m = []
    consumables = [
        ("Engine oil – synthetic, grade A", "L", 1, "FLUID", 10, 24.0),
        ("Engine oil – synthetic, grade B", "L", 1, "FLUID", 10, 27.0),
        ("Hydraulic fluid – type H1", "L", 1, "FLUID", 12, 31.0),
        ("Gearbox oil – type T1", "L", 1, "FLUID", 12, 35.0),
        ("Grease – general purpose, type G1", "KG", 1, "FLUID", 9, 42.0),
        ("Grease – high temperature, type G2", "KG", 1, "FLUID", 14, 68.0),
        ("Sealant kit – fuel tank, type S1", "KIT", 1, "SHOP", 18, 74.0),
        ("Sealant kit – general purpose, type S2", "KIT", 1, "SHOP", 12, 39.0),
        ("Corrosion inhibitor compound", "L", 1, "SHOP", 10, 28.0),
        ("Cleaning solvent – type C1", "L", 0, "SHOP", 7, 9.5),
        ("Adhesive kit – structural, type A1", "KIT", 1, "RAW", 15, 56.0),
        ("Primer – epoxy, type P1", "L", 1, "RAW", 15, 44.0),
        ("Lockwire – stainless, 0.8 mm", "M", 0, "HARDWARE", 8, 0.9),
        ("Lint-free wipes – pack of 50", "EA", 0, "SHOP", 5, 6.5),
        ("Masking tape – roll", "EA", 0, "SHOP", 5, 3.2),
    ]
    for desc, uom, sl, tag, lead, cost in consumables:
        m.append((desc, "CONSUMABLE", uom, 0, sl, tag, lead, cost))

    standard = []
    for size in (3, 4, 5, 6, 8):
        standard.append((f"Bolt – hex head, size {size}", 0, 0.45 + size * 0.1))
    for size in (3, 4, 5, 6, 8):
        standard.append((f"Nut – self-locking, size {size}", 0, 0.30 + size * 0.06))
    for size in (3, 4, 5, 6, 8):
        standard.append((f"Washer – flat, size {size}", 0, 0.08 + size * 0.02))
    for size in (3, 4, 5):
        standard.append((f"Screw – countersunk, size {size}", 0, 0.35 + size * 0.05))
    for size in (1, 2, 3):
        standard.append((f"Cotter pin – size {size}", 0, 0.12))
    for size in (3, 4):
        standard.append((f"Rivet – solid, size {size}", 0, 0.06))
    for size in (3, 4):
        standard.append((f"Rivet – blind, size {size}", 0, 0.22))
    for size in ("010", "012", "014", "016", "018", "020"):
        standard.append((f"O-ring – size {size}", 1, 0.85))
    for size in (1, 2, 3):
        standard.append((f"Hose clamp – size {size}", 0, 1.9))
    standard.append(("Cable tie – pack of 100", 0, 7.5))
    for size in (1, 2):
        standard.append((f"Packing ring – size {size}", 0, 1.4))
    for size in (2, 3):
        standard.append((f"Spring pin – size {size}", 0, 0.25))
    standard.append(("Shim – laminated, type L1", 0, 12.0))
    for desc, sl, cost in standard:
        tag = "SEAL" if desc.startswith(("O-ring", "Packing")) else "HARDWARE"
        m.append((desc, "STANDARD_PART", "EA", 0, sl, tag, 7, round(cost, 2)))

    components = [
        ("Oil filter element – type A", 0, "FILTER", 21, 62.0),
        ("Oil filter element – type B", 0, "FILTER", 21, 71.0),
        ("Fuel filter element – type A", 0, "FILTER", 21, 58.0),
        ("Fuel filter element – type B", 0, "FILTER", 21, 66.0),
        ("Hydraulic filter element – type A", 0, "FILTER", 25, 94.0),
        ("Air filter element – type A", 0, "FILTER", 18, 47.0),
        ("Cabin air filter element", 0, "FILTER", 18, 39.0),
        ("Bearing – ball, type B1", 0, "COMP", 30, 145.0),
        ("Bearing – ball, type B2", 0, "COMP", 30, 162.0),
        ("Bearing – roller, type R1", 0, "COMP", 35, 210.0),
        ("Seal kit – actuator, type K1", 0, "COMP", 28, 118.0),
        ("Seal kit – actuator, type K2", 0, "COMP", 28, 131.0),
        ("Brush set – starter generator", 0, "ELEC", 30, 186.0),
        ("Lamp – position light", 0, "ELEC", 14, 38.0),
        ("Lamp – landing light", 0, "ELEC", 14, 96.0),
        ("Lamp – cabin light", 0, "ELEC", 14, 22.0),
        ("Hose assembly – hydraulic, type H1", 0, "COMP", 35, 265.0),
        ("Hose assembly – hydraulic, type H2", 0, "COMP", 35, 289.0),
        ("Hose assembly – fuel, type F1", 0, "COMP", 35, 240.0),
        ("Sensor – temperature, type T1", 0, "ELEC", 40, 410.0),
        ("Sensor – pressure, type P1", 1, "ROTABLE", 45, 1450.0),
        ("Valve – check, type V1", 0, "COMP", 40, 330.0),
        ("Valve – solenoid, type V2", 0, "COMP", 40, 520.0),
        ("Switch – micro, type S1", 0, "ELEC", 21, 64.0),
        ("Fuse – 5 A", 0, "ELEC", 10, 4.8),
        ("Fuse – 10 A", 0, "ELEC", 10, 4.8),
        ("Relay – type R1", 0, "ELEC", 21, 88.0),
        ("Battery – main, type B", 1, "ROTABLE", 45, 2350.0),
        ("Starter generator – type SG", 1, "ROTABLE", 60, 8900.0),
        ("Servo actuator – type SA", 1, "ROTABLE", 75, 7400.0),
        ("Fuel pump – type FP", 1, "ROTABLE", 60, 5200.0),
        ("Damper assembly – type D", 1, "ROTABLE", 70, 6100.0),
        ("Display unit – type AD", 1, "ROTABLE", 80, 9800.0),
        ("Pitot-static probe – type PS", 1, "ROTABLE", 50, 2900.0),
        ("Windshield wiper blade", 0, "COMP", 21, 54.0),
        ("Drive belt – type DB1", 0, "COMP", 21, 76.0),
        ("Gasket – exhaust, type E1", 0, "SEAL", 18, 33.0),
    ]
    for desc, serial, tag, lead, cost in components:
        m.append((desc, "COMPONENT", "EA", serial, 0, tag, lead, cost))

    raw = [
        ("Aluminium sheet 1.0 mm – 1 x 2 m", "EA", 14, 86.0),
        ("Aluminium sheet 1.6 mm – 1 x 2 m", "EA", 14, 112.0),
        ("Aluminium tube 10 mm", "M", 14, 9.5),
        ("Steel tube 8 mm", "M", 14, 12.0),
        ("Electrical cable AWG 20", "M", 10, 1.1),
        ("Electrical cable AWG 22", "M", 10, 0.9),
        ("Heat-shrink sleeve 6 mm", "M", 7, 1.6),
        ("Fibreglass cloth", "M", 12, 18.0),
    ]
    for desc, uom, lead, cost in raw:
        m.append((desc, "RAW_MATERIAL", uom, 0, 0, "RAW", lead, cost))
    return m


MATERIALS = _materials()
assert len(MATERIALS) == 100, len(MATERIALS)

# Probability weights of each material family by maintenance type
USAGE_WEIGHTS = {
    "SCHEDULED":    {"FLUID": 6, "FILTER": 5, "HARDWARE": 4, "SEAL": 3, "SHOP": 2, "ELEC": 1, "COMP": 0.6, "ROTABLE": 0.05, "RAW": 0},
    "UNSCHEDULED":  {"FLUID": 2, "FILTER": 1, "HARDWARE": 3, "SEAL": 2, "SHOP": 1, "ELEC": 3, "COMP": 3, "ROTABLE": 0.45, "RAW": 0.2},
    "MODIFICATION": {"FLUID": 0.5, "FILTER": 0, "HARDWARE": 4, "SEAL": 1, "SHOP": 2, "ELEC": 2, "COMP": 0.5, "ROTABLE": 0.05, "RAW": 5},
}

# -----------------------------------------------------------------------------
# Documents — exactly 250
# -----------------------------------------------------------------------------
PROCEDURES = {
    "QUA": ["Quality system manual – AEROQ MRO", "Control of non-conformities", "Root cause analysis",
            "Corrective and preventive actions", "Internal audit programme", "Management review",
            "Control of quality records", "Competence assessment of staff",
            "Internal occurrence and hazard reporting", "Supplier evaluation and monitoring"],
    "DOC": ["Document control", "Control of technical data", "Technical records management",
            "Archiving and retention of records", "Distribution of controlled copies",
            "Electronic records and backups"],
    "LOG": ["Receiving inspection of materials", "Storage and segregation of materials",
            "Quarantine and non-conforming material", "Cycle counting and inventory adjustments",
            "Shelf-life control", "Purchasing and expediting", "Tool store control",
            "Shipping and returns to suppliers"],
    "PRD": ["Maintenance order planning", "Work package preparation", "Production control and follow-up",
            "Work order closure and records review", "Material requests for maintenance orders",
            "Planning of aircraft inputs", "Priority management (AOG and urgent orders)",
            "Customer communication of delays"],
    "MNT": ["Maintenance task execution", "Shift and task handover", "Tooling and equipment use",
            "Independent inspection records", "Ground run coordination", "Foreign object prevention",
            "Component removal and installation records", "Workshop housekeeping"],
}

FORMS = {
    "QUA": ["Non-conformity report", "Root cause analysis worksheet", "Corrective action plan",
            "Internal audit checklist", "Audit finding report", "Effectiveness verification record",
            "Management review minutes", "Training record"],
    "DOC": ["Document change request", "Document review record", "Controlled copy distribution list",
            "Records transfer sheet", "Technical data revision log", "Document withdrawal notice"],
    "LOG": ["Goods receipt note", "Receiving inspection record", "Quarantine label",
            "Non-conforming material tag", "Cycle count sheet", "Stock adjustment form",
            "Purchase requisition", "Shelf-life monitoring sheet", "Return to supplier note"],
    "PRD": ["Work order opening sheet", "Material request", "Work package checklist",
            "Work order closure record", "Delay report", "Planning board update",
            "Hold notification", "Records review checklist", "Customer work summary"],
    "MNT": ["Task card (generic)", "Tool control sheet", "Shift handover log", "Ground run log",
            "Foreign object inspection checklist", "Component change record",
            "Consumables usage record", "Workshop inspection checklist"],
}

WI_SYSTEMS = ["Engine", "Main rotor", "Tail rotor", "Transmission", "Fuel system",
              "Hydraulic system", "Electrical system", "Landing gear", "Airframe", "Avionics"]
WI_TASKS = ["scheduled inspection package", "component replacement", "servicing",
            "functional check", "corrosion control", "records preparation", "ground run preparation"]

TDR_GROUPS = ["General", "Airframe", "Main rotor", "Tail rotor", "Transmission", "Engine",
              "Fuel system", "Hydraulic system", "Electrical system", "Lighting", "Avionics",
              "Landing gear", "Flight controls", "Cabin", "Fire protection", "Instruments",
              "Ice and rain protection", "Doors and windows", "Cargo hook", "Navigation",
              "Communications"]
TDR_MODELS = ["LS-100", "LT-200", "MT-300"]

ACR_TYPES = ["Logbook index", "Component status record", "Modification record"]

# Review interval (months) by document type — FICTITIOUS internal policy of AEROQ MRO
REVIEW_INTERVAL_MONTHS = {"PROCEDURE": 24, "WORK_INSTRUCTION": 24, "FORM": 36, "TECHNICAL_DATA_REF": 12}

# -----------------------------------------------------------------------------
# Maintenance order descriptions (administrative, no technical content)
# -----------------------------------------------------------------------------
MO_DESCRIPTIONS = {
    "SCHEDULED": ["Scheduled inspection – package A", "Scheduled inspection – package B",
                  "Scheduled inspection – package C", "Periodic servicing and records update",
                  "Calendar inspection and component status review"],
    "UNSCHEDULED": ["Defect rectification reported by operator", "Component replacement after defect report",
                    "Troubleshooting following crew report", "Unscheduled inspection after event report",
                    "Replacement of time-expired consumable item"],
    "MODIFICATION": ["Embodiment of customer cabin modification", "Installation of optional equipment",
                     "Modification of electrical installation", "Structural repair per approved data"],
}

# -----------------------------------------------------------------------------
# Quality incident templates by category
# Each: titles, Ishikawa category, 5-why chains, root-cause statements,
#       corrective action texts. All generic and administrative.
# -----------------------------------------------------------------------------
INCIDENT_TEMPLATES = {
    "DOC": {
        "titles": ["Controlled document issued without approval record",
                   "Document review overdue at point of use",
                   "Incorrect cross-reference in work instruction",
                   "Missing page in controlled copy"],
        "ishikawa": "METHOD",
        "whys": [["The document reached the user with an error", "The review step was skipped",
                  "The reviewer was not notified of the due date", "Due dates were tracked manually",
                  "No automatic reminder existed in the document register"]],
        "root": ["Document review due dates were tracked manually, without reminders.",
                 "The change request did not require a second check before issue."],
        "actions": ["Correct and reissue the affected document", "Add review reminders to the document register",
                    "Brief document controllers on the issue checklist"],
    },
    "REC": {
        "titles": ["Work order closure record incomplete", "Part number recorded incorrectly on work order",
                   "Missing signature on task record", "Date discrepancy between task record and system",
                   "Quantity issued not recorded on work order"],
        "ishikawa": "METHOD",
        "whys": [["The record did not match the source document", "A field was left blank",
                  "The form layout did not show the field as mandatory",
                  "The form had not been reviewed after the last process change",
                  "Form design was not part of the change process"]],
        "root": ["The work order closure form does not make mandatory fields evident.",
                 "Records were transcribed at the end of the shift instead of at the time of the task."],
        "actions": ["Correct the affected record against the source document",
                    "Review the record with the author and check the other records of the same week",
                    "Brief production staff on contemporaneous recording"],
    },
    "INV": {
        "titles": ["Cycle count difference on {pn}", "Unrecorded consumption of {pn}",
                   "Stock location mismatch for {pn}"],
        "ishikawa": "METHOD",
        "whys": [["Physical stock differed from system stock", "An issue was not recorded",
                  "Small parts were taken from open bins", "Open bins were allowed for standard parts",
                  "The counting procedure did not cover open-bin parts"]],
        "root": ["Standard parts were taken from open bins without an issue record.",
                 "The cycle-count procedure did not define how to handle open-bin parts."],
        "actions": ["Adjust stock and investigate the last movements", "Close open bins for standard parts",
                    "Revise the cycle-count procedure for standard parts"],
    },
    "MNC": {
        "titles": ["Received item without legible identification", "Damaged packaging on receipt",
                   "Certificate data does not match item received", "Shelf-life information missing on receipt"],
        "ishikawa": "MATERIAL",
        "whys": [["The item failed receiving inspection", "The supplier shipped a non-conforming item",
                  "The supplier's dispatch check failed", "The requirement was not stated on the order",
                  "Purchase order notes were not standardised"]],
        "root": ["Supplier dispatch checks did not detect the non-conformity.",
                 "Purchase order requirements were not stated clearly to the supplier."],
        "actions": ["Quarantine and return or scrap the item", "Request a corrective action from the supplier",
                    "Standardise purchase order quality requirements"],
    },
    "PRC": {
        "titles": ["Procedure step not followed: {proc}", "Records not completed as required by {proc}",
                   "Tool control sheet not used during task", "Quarantine area access not controlled"],
        "ishikawa": "MANPOWER",
        "whys": [["A procedure step was not followed", "The person was not aware of the latest revision",
                  "The revision briefing was not recorded", "Briefings depended on the shift supervisor",
                  "No structured briefing process existed"]],
        "root": ["Changes to procedures were not briefed in a structured way.",
                 "The procedure step was not practical in the current workflow."],
        "actions": ["Brief the affected staff and record attendance", "Introduce a structured revision briefing",
                    "Review the practicality of the procedure step"],
    },
    "TRC": {
        "titles": ["Superseded revision used on work order", "Lot number not recorded on work order",
                   "Material issued without traceable lot reference"],
        "ishikawa": "METHOD",
        "whys": [["The record could not be traced to its origin", "An obsolete copy was available at point of use",
                  "Obsolete copies were not withdrawn", "Withdrawal depended on the user",
                  "The distribution list was not used at withdrawal"]],
        "root": ["Obsolete copies were not withdrawn from points of use.",
                 "Lot references were not transferred from the issue note to the work order."],
        "actions": ["Withdraw obsolete copies and verify all points of use",
                    "Add lot-reference check to the records review", "Brief staff on traceability requirements"],
    },
    "MNT": {
        "titles": ["Task card step not signed", "Tooling calibration label expired",
                   "Work order opened without complete work package", "Handover log not completed",
                   "Ground equipment unavailable delaying task"],
        "ishikawa": "MANPOWER",
        "whys": [["The administrative step was missed", "The workload peaked during the shift",
                  "Two orders were handled in parallel", "Planning did not level the workload",
                  "Planning did not consider administrative time"]],
        "root": ["Workload peaks led to administrative steps being missed.",
                 "Work packages were released before all documents were collected."],
        "actions": ["Complete the missing record and verify similar orders", "Level the workload in the planning board",
                    "Add a work-package completeness check before release"],
    },
    "SUP": {
        "titles": ["Late delivery from {supplier} delaying {mo}", "Incomplete delivery from {supplier}",
                   "Delivery date not met by {supplier}"],
        "ishikawa": "MATERIAL",
        "whys": [["The material arrived after the promised date", "The supplier had no stock",
                  "The supplier did not inform of the delay", "No expediting contact was made",
                  "Expediting was not scheduled for urgent orders"]],
        "root": ["The supplier did not communicate stock shortages in time.",
                 "Urgent orders were not expedited systematically."],
        "actions": ["Expedite open orders with the supplier", "Request a recovery plan from the supplier",
                    "Introduce systematic expediting of urgent orders"],
    },
}

SEVERITY_BY_CATEGORY = {   # weights for CRITICAL, MAJOR, MINOR, OBSERVATION
    "DOC": (1, 20, 55, 24), "REC": (1, 22, 62, 15), "INV": (1, 25, 60, 14), "MNC": (6, 40, 44, 10),
    "PRC": (2, 28, 45, 25), "TRC": (8, 42, 45, 5), "MNT": (3, 25, 52, 20), "SUP": (5, 40, 45, 10),
}

# Fictitious internal targets of AEROQ MRO (days to close by severity) — NOT regulatory
TARGET_CLOSURE_DAYS = {"CRITICAL": 45, "MAJOR": 75, "MINOR": 90, "OBSERVATION": 30}

PREVENTIVE_TREND_ACTIONS = [
    ("QUA", "Trend review of recording errors by shift", "Analyse recording errors by shift and brief the shift with most errors."),
    ("LOG", "Review minimum stock levels of fast movers", "Recalculate minimum stock levels for the ten most used references."),
    ("PRD", "Reduce administrative delays at work order closure", "Analyse closure times and remove waiting steps."),
    ("DOC", "Review of documents approaching their review date", "Plan the review of documents due in the next quarter."),
    ("MNT", "Workload levelling between shifts", "Compare workload between shifts and adjust the planning rules."),
    ("QUA", "Refresher briefing on non-conformity reporting", "Brief all departments on how and when to report a non-conformity."),
    ("LOG", "Supplier delivery performance review", "Review on-time delivery of the main suppliers and agree improvement plans."),
    ("PRD", "Review of work package completeness at release", "Sample released work packages and check completeness."),
]
