"""
AQMI generator — Module B (Phase 9): lessons learned.

A lesson records what AEROQ MRO learned while dealing with an action, and the
change it recommends, so that the same problem does not appear somewhere else.
It is the last step of the improvement cycle:

    non-conformity -> root cause -> action -> effectiveness check -> LESSON -> controlled document revised

Lessons learned are a general quality-management practice that the fictitious
company applies voluntarily. They are not presented as a regulatory requirement.

How the data is generated (design approved in Phase 9)
    * AFTER the main simulation has finished, reading only what it produced.
    * With its OWN random generator, so the numbers drawn here never change the
      main simulation: every record that existed before Phase 9 stays exactly
      the same (a test checks it), and so do the 18 KPIs, the case study and the
      published screenshots.
    * Only closed actions whose effectiveness was verified can leave a lesson.
      Every action found NOT_EFFECTIVE leaves one (what did not work is also
      learned); a fraction of the effective ones do.
    * An approved lesson is incorporated into a revision of a controlled
      document that came into force after the approval. If no such revision
      exists yet, the lesson stays approved and pending incorporation.
    * Story: the lesson of NC-2025-0021 is incorporated into FRM-PRD-004 R01,
      the redesigned form that was the corrective action itself.
    * Every insert and update goes through the normal tables, so the audit
      triggers record the whole history in Audit_Log.
"""

import random
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from config import generator_parameters as P
from scripts.generator.engine import add_workdays, fmt_d, fmt_dt, parse_d

# ---------------------------------------------------------------------------- texts
# (title, lesson_text, recommendation) by incident category. {action} is the action title.
LESSON_TEXTS = {
    "DOC": ("Document errors reach the point of use",
            "Errors in documents were only found when the document was used. The action ({action}) "
            "was effective.",
            "Check new and revised documents against their source before they are released."),
    "REC": ("Records are more accurate when filled in at the time of the task",
            "Recording errors appeared when data was transcribed later from memory or notes. "
            "The action ({action}) was effective.",
            "Record data at the time of the task and make mandatory fields evident on every form."),
    "INV": ("Count differences come from open bins and unrecorded movements",
            "Stock differences were traced to movements not recorded at the time they happened. "
            "The action ({action}) was effective.",
            "Record every stock movement when it happens and keep standard parts in closed bins."),
    "MNC": ("Non-conforming material must be segregated at once",
            "Non-conforming items stayed mixed with serviceable stock until they were identified. "
            "The action ({action}) was effective.",
            "Segregate and label suspect material immediately and record the decision in the system."),
    "PRC": ("Procedure changes need a briefing, not only a new revision",
            "Staff kept following the previous practice after the procedure changed. "
            "The action ({action}) was effective.",
            "Brief affected staff on every procedure revision and keep the attendance record."),
    "TRC": ("Traceability depends on withdrawing obsolete copies",
            "Obsolete copies at the point of use broke the traceability of records. "
            "The action ({action}) was effective.",
            "Withdraw obsolete copies when a revision comes into force and verify every point of use."),
    "MNT": ("Missing records are found late when orders are closed in a hurry",
            "Incomplete work order records were detected at closure, not during the work. "
            "The action ({action}) was effective.",
            "Review the work order records before the order is completed, not only at closure."),
    "SUP": ("Late deliveries must be escalated before they block work orders",
            "Supply problems became work order holds because late deliveries were not followed up early. "
            "The action ({action}) was effective.",
            "Follow up urgent purchase orders before the promised date and escalate early."),
    "TREND": ("Trend reviews find problems before they become non-conformities",
              "The management review trend analysis detected a pattern before it produced findings. "
              "The preventive action ({action}) was effective.",
              "Keep the monthly trend review and record the preventive actions it produces."),
}
# Used when the action was verified as NOT_EFFECTIVE: the lesson is about what did not work.
# The text is chosen from the kind of action (its first word), so it always fits the action.
NOT_EFFECTIVE_TEXTS = {
    "BRIEFING": ("Briefing alone did not prevent recurrence",
                 "The action ({action}) relied on informing the staff, and the same problem appeared again.",
                 "Combine briefings with a change in the form or the procedure that makes the error difficult."),
    "CORRECTION": ("Correcting the affected item does not remove the cause",
                   "The action ({action}) fixed the affected items but the problem recurred: "
                   "the root cause was not removed.",
                   "Check that every corrective action acts on the root cause before it is approved."),
    "OTHER": ("Effectiveness must be planned and measured with data",
              "The action ({action}) was implemented, but the follow-up data showed the problem again.",
              "Define how effectiveness will be measured when the action is planned."),
}
CORRECTION_WORDS = ("Correct", "Complete", "Adjust", "Quarantine", "Withdraw", "Expedite", "Follow-up: Correct",
                    "Follow-up: Complete", "Follow-up: Adjust", "Follow-up: Quarantine", "Follow-up: Withdraw",
                    "Follow-up: Expedite")
REJECTION_REASONS = [
    "Already covered by the current revision of the procedure; no change needed.",
    "Isolated case; the recommendation would add work without reducing risk.",
    "Duplicates a lesson already approved for the same process.",
]
STORY_TEXT = ("Mandatory fields must be evident on forms",
              "Recording errors on work order closure records fell after the form was redesigned to make "
              "mandatory fields evident (CA-2025-0028).",
              "Apply the same design rule to every form when it is revised: highlight mandatory fields "
              "and brief the users.")

DOC_TYPES = ("PROCEDURE", "WORK_INSTRUCTION", "FORM")


@dataclass
class Plan:
    """The life of one lesson, decided before anything is written."""
    action_id: int
    number: str
    title: str
    lesson_text: str
    recommendation: str
    dept_id: int
    scope: str
    proposed: datetime
    proposed_by: int
    events: list = field(default_factory=list)    # (datetime, actor, values)


class LessonsLearned:
    def __init__(self, conn, seed: int):
        self.conn = conn
        # Own random generator: drawing numbers here never changes the main simulation.
        self.rng = random.Random(f"{seed}/{P.LESSONS_RANDOM_SALT}")
        self.as_of = parse_d(self._param("AS_OF_DATE"))
        self.heads = dict(conn.execute(
            "SELECT d.department_code, e.employee_id FROM Employees e JOIN Departments d USING (department_id) "
            "WHERE e.is_department_head = 1"))
        self.dept_code = {i: c for c, i in conn.execute("SELECT department_code, department_id FROM Departments")}
        self.employment = {e: (parse_d(h), parse_d(t) if t else None) for e, h, t in conn.execute(
            "SELECT employee_id, hire_date, termination_date FROM Employees")}
        self._numbers: dict = {}
        self.created = 0

    def _param(self, key: str) -> str:
        return self.conn.execute("SELECT parameter_value FROM System_Parameters WHERE parameter_key = ?",
                                 (key,)).fetchone()[0]

    # ---------------------------------------------------------------- helpers
    def _employed(self, employee: int, day: date) -> bool:
        hire, termination = self.employment[employee]
        return hire <= day and (termination is None or day <= termination)

    def _moment(self, day: date, first_hour: int = 9, last_hour: int = 16) -> datetime:
        return datetime.combine(day, time(self.rng.randint(first_hour, last_hour), self.rng.randint(0, 59)))

    def _next_number(self, year: int) -> str:
        self._numbers[year] = self._numbers.get(year, 0) + 1
        return f"LL-{year}-{self._numbers[year]:04d}"

    def _decider(self, proposer: int) -> int:
        """The Head of Quality decides; if the Head of Quality proposed, the General Manager decides."""
        return self.heads["QUA"] if proposer != self.heads["QUA"] else self.heads["DIR"]

    # ---------------------------------------------------------------- revisions
    def _story_revision(self, action) -> int | None:
        """Revision of the closure form produced by the redesign action itself (NC-2025-0021)."""
        row = self.conn.execute(
            "SELECT r.revision_id FROM Document_Revisions r JOIN Documents d USING (document_id) "
            "WHERE d.document_code = ? AND r.effective_date BETWEEN ? AND ? ORDER BY r.revision_seq LIMIT 1",
            (P.CLOSURE_FORM_DOC, action["created_date"], action["closed_date"])).fetchone()
        return row[0] if row else None

    def _revision_after(self, dept_code: str, approved: date):
        """First revision of a controlled document of the department that came into force after the approval."""
        rows = self.conn.execute(f"""
            SELECT r.revision_id, r.effective_date, r.superseded_date
              FROM Document_Revisions r JOIN Documents d USING (document_id)
              JOIN Departments dep ON dep.department_id = d.owner_department_id
             WHERE dep.department_code = ? AND d.is_controlled = 1
               AND d.document_type IN ({", ".join("?" for _ in DOC_TYPES)})
               AND r.lifecycle_status IN ('CURRENT', 'SUPERSEDED')
               AND r.effective_date > ? AND r.effective_date <= ?
             ORDER BY r.effective_date, r.revision_id""",
            (dept_code, *DOC_TYPES, fmt_d(approved),
             fmt_d(min(self.as_of, approved + timedelta(days=P.LESSON_INCORPORATION_WINDOW_DAYS))))).fetchall()
        if not rows:
            return None
        return self.rng.choice(rows[:3])

    # ---------------------------------------------------------------- planning
    def _actions(self) -> list[dict]:
        cursor = self.conn.execute("""
            SELECT a.action_id, a.action_number, a.action_type, a.origin, a.title, a.department_id,
                   a.responsible_id, a.verified_by, a.created_date, a.closed_date, a.effectiveness_result,
                   c.category_code, i.incident_number
              FROM CAPA_Actions a
              LEFT JOIN Quality_Incidents i ON i.incident_id = a.incident_id
              LEFT JOIN Incident_Categories c ON c.category_id = i.category_id
             WHERE a.status = 'CLOSED' AND a.effectiveness_result IS NOT NULL
             ORDER BY a.closed_date, a.action_id""")
        columns = [d[0] for d in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def _texts(self, action: dict, story: bool) -> tuple:
        if story:
            return STORY_TEXT
        if action["effectiveness_result"] == "NOT_EFFECTIVE":
            name = action["title"]
            kind = ("BRIEFING" if "brief" in name.lower() or "training" in name.lower()
                    else "CORRECTION" if name.startswith(CORRECTION_WORDS) else "OTHER")
            title, text, recommendation = NOT_EFFECTIVE_TEXTS[kind]
        else:
            title, text, recommendation = LESSON_TEXTS[action["category_code"] or "TREND"]
        return title[:120], text.format(action=action["title"]), recommendation

    def _plan(self, action: dict, story: bool) -> Plan | None:
        rng = self.rng
        closed = parse_d(action["closed_date"])
        proposed_day = add_workdays(closed, rng.randint(*P.LESSON_PROPOSAL_DAYS))
        if proposed_day > self.as_of:
            return None                                   # not proposed yet at the cut-off date
        candidates = [e for e in (action["responsible_id"], action["verified_by"]) if self._employed(e, proposed_day)]
        if not candidates:
            return None
        proposer = candidates[0] if story or rng.random() < 0.6 or len(candidates) == 1 else candidates[1]
        title, text, recommendation = self._texts(action, story)
        scope = "COMPANY" if story or rng.random() < P.LESSON_COMPANY_SCOPE_PROB else "DEPARTMENT"
        plan = Plan(action["action_id"], "", title, text, recommendation,
                    action["department_id"], scope, self._moment(proposed_day), proposer)

        decision_day = add_workdays(proposed_day, rng.randint(*P.LESSON_DECISION_DAYS))
        if decision_day > self.as_of:
            return plan                                   # still PROPOSED
        decider = self._decider(proposer)
        decided = self._moment(decision_day)
        # A lesson from an action that did not work is always kept; others can be rejected.
        if not story and action["effectiveness_result"] == "EFFECTIVE" and rng.random() < P.LESSON_REJECTION_PROB:
            plan.events.append((decided, decider, {
                "status": "REJECTED", "rejected_date": fmt_d(decision_day), "rejected_by": decider,
                "rejection_reason": rng.choice(REJECTION_REASONS)}))
            return plan
        plan.events.append((decided, decider, {
            "status": "APPROVED", "approved_date": fmt_d(decision_day), "approved_by": decider}))

        # Incorporation into a controlled document (recorded by Document Control)
        recorder = self.heads["DOC"]
        if story:
            revision = self._story_revision(action)
            if revision is not None:
                plan.events.append((decided + timedelta(minutes=rng.randint(20, 90)), recorder, {
                    "status": "INCORPORATED", "incorporated_date": fmt_d(decision_day),
                    "incorporated_revision_id": revision}))
            return plan
        if rng.random() < P.LESSON_LEFT_PENDING_PROB:
            return plan                                   # approved, nobody has revised the document yet
        target_dept = "QUA" if scope == "COMPANY" else self.dept_code[action["department_id"]]
        found = self._revision_after(target_dept, decision_day)
        if found is None:
            return plan                                   # approved, pending incorporation
        revision_id, effective, superseded = found
        day = parse_d(effective) + timedelta(days=rng.randint(0, 3))
        last = min(self.as_of, parse_d(superseded) - timedelta(days=1)) if superseded else self.as_of
        if last < parse_d(effective):
            return plan                                   # that revision was in force for less than a day
        day = min(day, last)
        plan.events.append((self._moment(day), recorder, {
            "status": "INCORPORATED", "incorporated_date": fmt_d(day), "incorporated_revision_id": revision_id}))
        return plan

    # ---------------------------------------------------------------- writing
    def generate(self) -> int:
        """Plan every lesson, then write all the facts in chronological order."""
        story_number = self.conn.execute(
            "SELECT a.action_number FROM CAPA_Actions a WHERE a.title LIKE ? ORDER BY a.action_id LIMIT 1",
            (f"Redesign the work order closure record {P.CLOSURE_FORM_DOC}%",)).fetchone()
        plans = []
        for action in self._actions():
            story = story_number is not None and action["action_number"] == story_number[0]
            if not story and action["effectiveness_result"] == "EFFECTIVE" \
                    and self.rng.random() >= P.LESSON_PROB_EFFECTIVE:
                continue
            plan = self._plan(action, story)
            if plan is not None:
                plans.append(plan)

        # Numbers follow the order of proposal, as in a real register (LL-<year>-0001, 0002...)
        plans.sort(key=lambda p: (p.proposed, p.action_id))
        for plan in plans:
            plan.number = self._next_number(plan.proposed.year)

        facts = []                                        # (when, order, plan, actor, values or None)
        for k, plan in enumerate(plans):
            facts.append((plan.proposed, k, 0, plan, plan.proposed_by, None))
            for j, (when, actor, values) in enumerate(plan.events, start=1):
                facts.append((when, k, j, plan, actor, values))
        facts.sort(key=lambda f: (f[0], f[1], f[2]))

        ids = {}
        for when, k, _, plan, actor, values in facts:
            if values is None:
                cursor = self.conn.execute(
                    "INSERT INTO Lessons_Learned (lesson_number, action_id, title, lesson_text, recommendation, "
                    "department_id, scope, status, proposed_date, proposed_by, created_at, created_by) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, 'PROPOSED', ?, ?, ?, ?)",
                    (plan.number, plan.action_id, plan.title, plan.lesson_text, plan.recommendation, plan.dept_id,
                     plan.scope, fmt_d(plan.proposed.date()), plan.proposed_by, fmt_dt(when), plan.proposed_by))
                ids[k] = cursor.lastrowid
                self.created += 1
            else:
                values = dict(values, updated_at=fmt_dt(when), updated_by=actor)
                assignments = ", ".join(f"{column} = ?" for column in values)
                self.conn.execute(f"UPDATE Lessons_Learned SET {assignments} WHERE lesson_id = ?",
                                  (*values.values(), ids[k]))
        return self.created
