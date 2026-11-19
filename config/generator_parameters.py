"""
AQMI — Parameters of the synthetic data generator (Phase 4).

All rates, probabilities and targets below are FICTITIOUS values chosen for
the imaginary company AEROQ MRO. They are not industry benchmarks and they are
not regulatory requirements. Changing them changes the story the data tells.
"""

# -----------------------------------------------------------------------------
# Maintenance orders
# -----------------------------------------------------------------------------
# Days between scheduled inspections, by aircraft category (with +/- 20 % random spread)
SCHEDULED_INTERVAL_DAYS = {"LIGHT_SINGLE": 52, "LIGHT_TWIN": 46, "MEDIUM_TWIN": 40}
# Probability of an unscheduled order per aircraft and working day
UNSCHEDULED_DAILY_PROB = 0.043
# Story: one aircraft has clearly more unscheduled maintenance than the rest
HIGH_UNSCHEDULED_AIRCRAFT = "EC-Q07"
HIGH_UNSCHEDULED_FACTOR = 2.3
# Probability of a modification order per aircraft and month
MODIFICATION_MONTHLY_PROB = 0.17
# Planned duration in working days (min, max) by maintenance type
PLANNED_DURATION_DAYS = {"SCHEDULED": (4, 12), "UNSCHEDULED": (1, 5), "MODIFICATION": (6, 16)}
# Number of material lines per order (min, max) by maintenance type
MATERIAL_LINES = {"SCHEDULED": (2, 4), "UNSCHEDULED": (1, 3), "MODIFICATION": (2, 4)}
# Probability that the work takes longer than planned, and extra working days
WORK_OVERRUN_PROB = 0.22
WORK_OVERRUN_DAYS = (1, 4)
MO_CANCELLATION_PROB = 0.02
# Probability of an administrative maintenance issue (incident category MNT) per order
MNT_ISSUE_PROB = 0.055
# Probability of an extra unit issued and returned unused (RETURN movement)
EXCESS_ISSUE_PROB = 0.03
# Probability that the customer reports a records problem after the order is closed
CUSTOMER_FEEDBACK_PROB = 0.02
# Random documentation hold (missing technical data at start) per order
DOC_HOLD_PROB = 0.025

# -----------------------------------------------------------------------------
# Purchasing and suppliers
# -----------------------------------------------------------------------------
NORMAL_LATE_PROB = 0.15
NORMAL_LATE_DAYS = (1, 5)
EARLY_PROB = 0.10
PARTIAL_DELIVERY_PROB = 0.10
RECEIVING_REJECT_PROB = 0.025
PO_CANCELLATION_PROB = 0.03
# Story: a supplier with poor delivery performance until an improvement plan takes effect
LATE_SUPPLIER_CODE = "SUP-006"
LATE_SUPPLIER_LATE_PROB = 0.80
LATE_SUPPLIER_LATE_DAYS = (4, 15)
# Urgent orders: fraction of the standard lead time promised by the supplier
URGENT_LEAD_FACTOR = {"URGENT": 0.5, "AOG": 0.25}
# A supply incident is raised when an urgent/AOG order waits more than this many days
SUPPLY_INCIDENT_MIN_HOLD_DAYS = 5
# A buyer raises a supply incident for a delivery this many days late (with some probability)
LATE_DELIVERY_INCIDENT_DAYS = 7
LATE_DELIVERY_INCIDENT_PROB = 0.25

# -----------------------------------------------------------------------------
# Stock counts
# -----------------------------------------------------------------------------
CYCLE_COUNTS_PER_WEEK = 4
COUNT_DISCREPANCY_PROB = 0.05
# Story: standard parts have more count differences until the counting procedure is revised
STANDARD_PART_DISCREPANCY_PROB = 0.24
COUNT_PROCEDURE_DOC = "PRO-LOG-004"

# -----------------------------------------------------------------------------
# Documents and records reviews
# -----------------------------------------------------------------------------
REVIEW_SKIPPED_PROB = 0.06          # periodic review forgotten (document becomes overdue)
REVIEW_NEW_REVISION_PROB = 0.40     # periodic review leads to a new revision
REVIEW_NONCONFORM_PROB = 0.045
REVIEW_MINOR_PROB = 0.08
PRE_USE_CHECK_PROB = 0.10           # documents checked before use on an order
# Story: the work order closure record form causes recording errors until redesigned
CLOSURE_FORM_DOC = "FRM-PRD-004"
RECORD_NONCONFORM_PROB_BEFORE = 0.13
RECORD_NONCONFORM_PROB_AFTER = 0.02
RECORD_MINOR_PROB = 0.05
INTERNAL_AUDIT_MONTHS = (2, 5, 8, 11)
MANAGEMENT_REVIEW_MONTHS = (1, 4, 7, 10)

# -----------------------------------------------------------------------------
# Quality incidents and CAPA (fictitious internal practice)
# -----------------------------------------------------------------------------
INCIDENT_CANCELLATION_PROB = 0.02
RCA_PROB_MINOR = 0.30
SECOND_CORRECTIVE_ACTION_PROB = 0.25      # CRITICAL / MAJOR incidents
PREVENTIVE_FROM_INCIDENT_PROB = 0.10      # MAJOR / CRITICAL incidents
CAPA_DUE_DAYS = {"CRITICAL": (10, 20), "MAJOR": (20, 40), "MINOR": (25, 50), "OBSERVATION": (30, 60)}
CAPA_SLOW_PROB = 0.25                     # actions that take much longer than planned
CAPA_EXTENSION_PROB = 0.35                # an overdue action gets its due date extended
CAPA_NOT_EFFECTIVE_PROB = 0.08
EFFECTIVENESS_CHECK_DAYS = (20, 50)

# -----------------------------------------------------------------------------
# Lessons learned (Phase 9). Generated AFTER the simulation with a separate random
# generator, so they never change the data above. Fictitious internal practice.
# -----------------------------------------------------------------------------
LESSONS_RANDOM_SALT = "lessons-learned"   # the lessons generator uses the seed + this text
LESSON_PROB_EFFECTIVE = 0.35              # effective actions that leave a lesson (NOT_EFFECTIVE: all)
LESSON_PROPOSAL_DAYS = (1, 10)            # working days from the action closure to the proposal
LESSON_DECISION_DAYS = (3, 15)            # working days from the proposal to the approval or rejection
LESSON_REJECTION_PROB = 0.10            # only lessons from effective actions can be rejected
LESSON_COMPANY_SCOPE_PROB = 0.25          # lessons that apply to the whole company
LESSON_LEFT_PENDING_PROB = 0.15           # approved lessons nobody has incorporated yet
LESSON_INCORPORATION_WINDOW_DAYS = 180    # a document revision later than this is not linked to the lesson

# -----------------------------------------------------------------------------
# Planted discrepancies (WARNING level) to prove that the controls detect them
# -----------------------------------------------------------------------------
PLANTED_OBSOLETE_REVISION_LINKS = 3
PLANTED_RECEIPTS_WITHOUT_CERTIFICATE = 2
PLANTED_FALSE_MATERIAL_HOLDS = 2
PLANTED_INCIDENTS_WITHOUT_LINKS = 2
