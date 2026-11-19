"""
AQMI generator — Modules A and B: non-conformities, root-cause analysis and CAPA,
plus internal audits and management reviews (which produce findings and
preventive actions from trend analysis).
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta

from config import generator_parameters as P
from scripts.generator import catalogs as C
from scripts.generator.engine import add_workdays, fmt_d, fmt_dt, next_workday

CATEGORY_DEPARTMENT = {"DOC": "DOC", "REC": "PRD", "INV": "LOG", "MNC": "LOG",
                       "PRC": "QUA", "TRC": "QUA", "MNT": "MNT", "SUP": "LOG"}
SOURCE_TEXT = {
    "DOCUMENT_VERIFICATION": "during a document verification", "STOCK_COUNT": "during a cycle count",
    "RECEIVING_INSPECTION": "at receiving inspection", "PRODUCTION": "by production staff",
    "INTERNAL_AUDIT": "during an internal audit", "CUSTOMER": "by the customer", "SUPPLIER": "in supplier follow-up",
}


@dataclass
class Incident:
    id: int
    category: str
    severity: str
    dept: str
    owner: int
    detected: date
    status: str = "OPEN"
    actions: list = field(default_factory=list)
    closed: bool = False


@dataclass
class Action:
    id: int
    number: str
    action_type: str
    origin: str
    title: str
    dept: str
    responsible: int
    due: date
    incident: Incident | None
    status: str = "OPEN"
    extended: bool = False
    force_effective: bool = False
    on_complete: object = None
    on_closed: object = None


class Quality:
    def __init__(self, world):
        self.w = world
        self.incidents: list[Incident] = []
        self.actions: list[Action] = []
        self.form_story_started = False
        self._trend_pointer = 0

    # ------------------------------------------------------------ incidents
    def create_incident(self, category: str, detected_by: int, source: str, links: dict,
                        context: dict | None = None, title: str | None = None,
                        severity: str | None = None, dept: str | None = None) -> Incident:
        engine, rng, master = self.w.engine, self.w.rng, self.w.master
        template = C.INCIDENT_TEMPLATES[category]
        severity = severity or rng.choices(["CRITICAL", "MAJOR", "MINOR", "OBSERVATION"],
                                           weights=C.SEVERITY_BY_CATEGORY[category])[0]
        priority = {"CRITICAL": "P1", "MAJOR": rng.choice(["P1", "P2"]),
                    "MINOR": rng.choice(["P2", "P3"]), "OBSERVATION": "P3"}[severity]
        values = defaultdict(lambda: "the item", context or {})
        title = (title or rng.choice(template["titles"])).format_map(values)[:120]
        dept = dept or CATEGORY_DEPARTMENT[category]
        owner = master.pick(dept, heads=True if severity == "CRITICAL" else False)
        description = f"{title}. Detected {SOURCE_TEXT[source]}."
        containment = None
        if severity in ("CRITICAL", "MAJOR"):
            containment = rng.choice([
                "Affected records and items put on hold pending investigation.",
                "Affected material segregated and labelled; users informed.",
                "Work stopped on the affected step until the record is corrected.",
            ])
        target = engine.today + timedelta(days=C.TARGET_CLOSURE_DAYS[severity])
        incident_id = engine.insert("Quality_Incidents", {
            "incident_number": engine.next_number("NC", engine.today.year),
            "category_id": self.w.category_id[category], "severity": severity, "priority": priority,
            "detection_source": source, "title": title, "description": description,
            "detected_date": fmt_d(engine.today), "detected_by": detected_by,
            "responsible_department_id": self.w.dept_id[dept], "owner_id": owner,
            "aircraft_id": links.get("aircraft_id"), "mo_id": links.get("mo_id"),
            "revision_id": links.get("revision_id"), "material_id": links.get("material_id"),
            "supplier_id": links.get("supplier_id"), "po_line_id": links.get("po_line_id"),
            "containment_action": containment, "status": "OPEN", "target_closure_date": fmt_d(target),
            "created_at": fmt_dt(engine.now), "created_by": detected_by,
        })
        incident = Incident(incident_id, category, severity, dept, owner, engine.today)
        self.incidents.append(incident)

        if category in ("MNT", "PRC", "REC") and rng.random() < P.INCIDENT_CANCELLATION_PROB:
            day = add_workdays(engine.today, 1)
            engine.schedule(engine.work_time(day, 9, 12), self._cancel, incident)
        else:
            day = add_workdays(engine.today, rng.randint(1, 3))
            engine.schedule(engine.work_time(day, 9, 15), self._investigate, incident)
        return incident

    def _set_status(self, incident: Incident, status: str, actor: int, extra: dict | None = None) -> None:
        incident.status = status
        self.w.engine.update("Quality_Incidents", "incident_id", incident.id, actor, dict(extra or {}, status=status))

    def _cancel(self, incident: Incident) -> None:
        incident.closed = True
        self._set_status(incident, "CANCELLED", self.w.master.head("QUA"),
                         {"closed_date": fmt_d(self.w.engine.today)})

    def _investigate(self, incident: Incident) -> None:
        if incident.closed:
            return
        engine, rng = self.w.engine, self.w.rng
        self._set_status(incident, "UNDER_INVESTIGATION", incident.owner)
        if incident.severity == "OBSERVATION":
            day = add_workdays(engine.today, rng.randint(5, 20))
            engine.schedule(engine.work_time(day, 9, 16), self._close_observation, incident)
        else:
            day = add_workdays(engine.today, rng.randint(2, 8))
            engine.schedule(engine.work_time(day, 9, 15), self._analyse, incident)

    def _close_observation(self, incident: Incident) -> None:
        closer = self.w.master.pick("QUA", titles=["Head of Quality", "Quality Auditor"], heads=None)
        incident.closed = True
        self._set_status(incident, "CLOSED", closer, {
            "closed_date": fmt_d(self.w.engine.today), "closed_by": closer,
            "closure_summary": "Observation recorded and communicated to the department; no corrective action required.",
        })

    def _analyse(self, incident: Incident) -> None:
        engine, rng, master = self.w.engine, self.w.rng, self.w.master
        template = C.INCIDENT_TEMPLATES[incident.category]
        if incident.severity in ("CRITICAL", "MAJOR") or rng.random() < P.RCA_PROB_MINOR:
            method = rng.choices(["FIVE_WHYS", "ISHIKAWA", "FIVE_WHYS_AND_ISHIKAWA"], weights=[50, 15, 35])[0]
            whys = rng.choice(template["whys"])[: rng.randint(3, 5)] if method != "ISHIKAWA" else []
            analyst = incident.owner if rng.random() < 0.6 else master.pick("QUA", titles=["Quality Analyst"])
            engine.insert("Root_Cause_Analyses", {
                "incident_id": incident.id, "method": method,
                "ishikawa_category": template["ishikawa"] if method != "FIVE_WHYS" else None,
                **{f"why_{k}": (whys[k - 1] if k <= len(whys) else None) for k in range(1, 6)},
                "root_cause_statement": rng.choice(template["root"]),
                "analysis_date": fmt_d(engine.today), "analyzed_by": analyst,
                "created_at": fmt_dt(engine.now), "created_by": analyst,
            })
        self._set_status(incident, "ACTION_PLAN", incident.owner)

        # Corrective actions (story: the closure-form redesign)
        story = (incident.category == "REC" and not self.form_story_started
                 and engine.today >= date(2025, 4, 1))
        n_actions = 1 + int(incident.severity in ("CRITICAL", "MAJOR") and rng.random() < P.SECOND_CORRECTIVE_ACTION_PROB)
        for k in range(n_actions):
            if story and k == 0:
                self.form_story_started = True
                form = self.w.documents.by_code[P.CLOSURE_FORM_DOC]
                title = f"Redesign the work order closure record {form.code}"
                self.create_action("CORRECTIVE", "INCIDENT", incident, title,
                                   "Redesign the form so that mandatory fields are evident; brief production staff.",
                                   "PRD", incident.severity, force_effective=True,
                                   on_complete=lambda f=form: self.w.documents.start_revision(
                                       f, "Redesign: mandatory fields highlighted", on_active=self._form_fixed))
            else:
                title = template["actions"][k % len(template["actions"])]
                self.create_action("CORRECTIVE", "INCIDENT", incident, title, f"{title} (ref. incident).",
                                   incident.dept, incident.severity)
        if incident.severity in ("CRITICAL", "MAJOR") and rng.random() < P.PREVENTIVE_FROM_INCIDENT_PROB:
            title = template["actions"][-1]
            self.create_action("PREVENTIVE", "INCIDENT", incident, title,
                               f"Prevent recurrence in other areas: {title.lower()}.", "QUA", incident.severity)
        day = add_workdays(engine.today, rng.randint(0, 1))
        engine.schedule(engine.work_time(day, 15, 16) if day == engine.today else engine.work_time(day, 9, 12),
                        self._start_implementation, incident)

    def _start_implementation(self, incident: Incident) -> None:
        if incident.status == "ACTION_PLAN":
            self._set_status(incident, "IMPLEMENTATION", incident.owner)
            self._on_action_change(incident)

    def _on_action_change(self, incident: Incident | None) -> None:
        if incident is None or incident.closed or incident.status in ("OPEN", "UNDER_INVESTIGATION", "ACTION_PLAN"):
            return
        statuses = [a.status for a in incident.actions]
        if all(s == "CLOSED" for s in statuses):
            closer = self.w.master.pick("QUA", titles=["Head of Quality", "Quality Auditor"], heads=None)
            incident.closed = True
            measures = "; ".join(dict.fromkeys(a.title for a in incident.actions))
            self._set_status(incident, "CLOSED", closer, {
                "closed_date": fmt_d(self.w.engine.today), "closed_by": closer,
                "closure_summary": f"Measures adopted: {measures}."[:500]})
        elif all(s in ("COMPLETED", "CLOSED") for s in statuses):
            if incident.status != "EFFECTIVENESS_CHECK":
                self._set_status(incident, "EFFECTIVENESS_CHECK", incident.owner)
        elif incident.status == "EFFECTIVENESS_CHECK":
            self._set_status(incident, "IMPLEMENTATION", incident.owner)   # a follow-up action was opened

    # ------------------------------------------------------------ CAPA
    def create_action(self, action_type: str, origin: str, incident: Incident | None, title: str,
                      description: str, dept: str, severity: str, parent: Action | None = None,
                      force_effective: bool = False, on_complete=None, on_closed=None) -> Action:
        engine, rng, master = self.w.engine, self.w.rng, self.w.master
        responsible = master.pick(dept)
        due = next_workday(engine.today + timedelta(days=rng.randint(*P.CAPA_DUE_DAYS[severity])))
        prefix = "CA" if action_type == "CORRECTIVE" else "PA"
        number = engine.next_number(prefix, engine.today.year)
        creator = incident.owner if incident else master.head("QUA")
        action_id = engine.insert("CAPA_Actions", {
            "action_number": number, "action_type": action_type, "origin": origin,
            "incident_id": incident.id if incident else None, "parent_action_id": parent.id if parent else None,
            "title": title[:120], "description": description, "responsible_id": responsible,
            "department_id": self.w.dept_id[dept], "created_date": fmt_d(engine.today),
            "original_due_date": fmt_d(due), "due_date": fmt_d(due), "status": "OPEN",
            "created_at": fmt_dt(engine.now), "created_by": creator,
        })
        action = Action(action_id, number, action_type, origin, title[:120], dept, responsible, due, incident,
                        force_effective=force_effective, on_complete=on_complete, on_closed=on_closed)
        self.actions.append(action)
        if incident:
            incident.actions.append(action)

        planned = max(3, (due - engine.today).days)
        duration = planned * rng.uniform(0.5, 1.1)
        if not force_effective and rng.random() < P.CAPA_SLOW_PROB:
            duration *= rng.uniform(1.8, 3.2)
        duration = max(3, round(duration))
        finish = next_workday(engine.today + timedelta(days=duration))
        n_updates = max(1, duration // 12)
        for k in range(1, n_updates + 1):
            day = next_workday(engine.today + timedelta(days=round(duration * k / (n_updates + 1))))
            if day < finish:
                pct = min(90, round(100 * k / (n_updates + 1) / 5) * 5)
                engine.schedule(engine.work_time(day, 9, 13), self._progress, action, pct)
        engine.schedule(engine.at(due, 17, 30), self._due_check, action)
        engine.schedule(engine.work_time(finish, 14, 16), self._complete, action)
        return action

    def _progress(self, action: Action, pct: int) -> None:
        if action.status not in ("OPEN", "IN_PROGRESS"):
            return
        engine = self.w.engine
        engine.insert("CAPA_Progress_Updates", {
            "action_id": action.id, "update_date": fmt_d(engine.today), "progress_pct": pct,
            "comment": f"Implementation in progress ({pct} %)",
            "created_at": fmt_dt(engine.now), "created_by": action.responsible,
        })
        if action.status == "OPEN":
            action.status = "IN_PROGRESS"
            engine.update("CAPA_Actions", "action_id", action.id, action.responsible, {"status": "IN_PROGRESS"})

    def _due_check(self, action: Action) -> None:
        if action.status not in ("OPEN", "IN_PROGRESS") or action.extended:
            return
        if self.w.rng.random() < P.CAPA_EXTENSION_PROB:
            action.extended = True
            action.due = next_workday(action.due + timedelta(days=self.w.rng.randint(10, 30)))
            self.w.engine.update("CAPA_Actions", "action_id", action.id, self.w.master.head("QUA"),
                                 {"due_date": fmt_d(action.due)})

    def _complete(self, action: Action) -> None:
        if action.status not in ("OPEN", "IN_PROGRESS"):
            return
        engine, rng = self.w.engine, self.w.rng
        engine.insert("CAPA_Progress_Updates", {
            "action_id": action.id, "update_date": fmt_d(engine.today), "progress_pct": 100,
            "comment": "Action implemented", "created_at": fmt_dt(engine.now), "created_by": action.responsible,
        })
        action.status = "COMPLETED"
        engine.update("CAPA_Actions", "action_id", action.id, action.responsible,
                      {"status": "COMPLETED", "completed_date": fmt_d(engine.today)})
        if action.on_complete:
            action.on_complete()
        self._on_action_change(action.incident)
        day = next_workday(engine.today + timedelta(days=rng.randint(*P.EFFECTIVENESS_CHECK_DAYS)))
        engine.schedule(engine.work_time(day, 9, 15), self._verify_effectiveness, action)

    def _verify_effectiveness(self, action: Action) -> None:
        engine, rng, master = self.w.engine, self.w.rng, self.w.master
        verifier = master.pick("QUA", titles=["Head of Quality", "Quality Auditor", "Quality Analyst"],
                               heads=None, exclude={action.responsible})
        effective = action.force_effective or rng.random() >= P.CAPA_NOT_EFFECTIVE_PROB
        action.status = "CLOSED"
        engine.update("CAPA_Actions", "action_id", action.id, verifier, {
            "status": "CLOSED", "effectiveness_check_date": fmt_d(engine.today),
            "effectiveness_result": "EFFECTIVE" if effective else "NOT_EFFECTIVE",
            "effectiveness_comment": ("No recurrence observed since implementation." if effective
                                      else "Recurrence observed; a follow-up action is required."),
            "verified_by": verifier, "closed_date": fmt_d(engine.today),
        })
        if effective and action.on_closed:
            action.on_closed()
        if not effective:
            severity = "MAJOR" if action.incident is None else action.incident.severity
            self.create_action(action.action_type, action.origin, action.incident,
                               f"Follow-up: {action.title}"[:120],
                               "Reinforce the previous action, which was not effective.", action.dept,
                               severity, parent=action)
        self._on_action_change(action.incident)

    def reassign_work(self, leaving) -> None:
        """Hand over the open incidents and actions of an employee who is leaving."""
        engine, master = self.w.engine, self.w.master
        head = master.head("QUA")
        for incident in self.incidents:
            if not incident.closed and incident.owner == leaving.id:
                incident.owner = master.pick(incident.dept, exclude={leaving.id})
                engine.update("Quality_Incidents", "incident_id", incident.id, head, {"owner_id": incident.owner})
        for action in self.actions:
            if action.status in ("OPEN", "IN_PROGRESS", "COMPLETED") and action.responsible == leaving.id:
                action.responsible = master.pick(action.dept, exclude={leaving.id})
                engine.update("CAPA_Actions", "action_id", action.id, head, {"responsible_id": action.responsible})

    # ------------------------------------------------------------ stories
    def _form_fixed(self) -> None:
        form = self.w.documents.by_code[P.CLOSURE_FORM_DOC]
        self.w.documents.closure_form_fixed_seq = form.current.seq

    def _supplier_plan(self) -> None:
        master = self.w.master
        supplier = master.supplier_by_code[P.LATE_SUPPLIER_CODE]
        master.set_supplier_status(supplier, "CONDITIONAL", master.head("QUA"))

        def improved():
            supplier.improved = True

        def approved():
            master.set_supplier_status(supplier, "APPROVED", master.head("QUA"))

        self.create_action("PREVENTIVE", "TREND_ANALYSIS", None,
                           f"Supplier performance improvement plan – {supplier.code}",
                           "Agree a delivery recovery plan with the supplier and monitor on-time delivery monthly.",
                           "LOG", "MAJOR", force_effective=True, on_complete=improved, on_closed=approved)

    def _count_procedure_plan(self) -> None:
        procedure = self.w.documents.by_code[P.COUNT_PROCEDURE_DOC]
        inventory = self.w.inventory

        def revised():
            inventory.count_procedure_revised = True

        self.create_action("PREVENTIVE", "TREND_ANALYSIS", None,
                           f"Revise the cycle-count procedure for standard parts ({procedure.code})",
                           "Trend analysis shows repeated count differences on standard parts: close open bins "
                           "and define the counting method.", "LOG", "MAJOR", force_effective=True,
                           on_complete=lambda: self.w.documents.start_revision(
                               procedure, "Counting method for open-bin standard parts", on_active=revised))

    # ------------------------------------------------------------ recurring quality activities
    def plan_recurring(self) -> None:
        engine = self.w.engine
        year, month = self.w.period_start.year, self.w.period_start.month
        while date(year, month, 1) <= self.w.as_of:
            if month in P.INTERNAL_AUDIT_MONTHS:
                engine.schedule(engine.at(next_workday(date(year, month, 12)), 9, 0), self._internal_audit)
            if month in P.MANAGEMENT_REVIEW_MONTHS:
                engine.schedule(engine.at(next_workday(date(year, month, 18)), 10, 0), self._management_review)
            year, month = (year + 1, 1) if month == 12 else (year, month + 1)

    def _internal_audit(self) -> None:
        engine, rng, master, docs = self.w.engine, self.w.rng, self.w.master, self.w.documents
        auditor = master.pick("QUA", titles=["Quality Auditor"])
        procedures = rng.sample(docs.of_type("PROCEDURE"), rng.randint(4, 6))
        findings = rng.randint(1, 3)
        for k, doc in enumerate(procedures):
            engine.now = engine.now + timedelta(minutes=rng.randint(20, 50))
            if k < findings:
                planted = (engine.today >= date(2025, 5, 1)
                           and self.w.planted_count("INCIDENT_WITHOUT_LINKS") < P.PLANTED_INCIDENTS_WITHOUT_LINKS
                           and k == 0)
                incident = self.create_incident("PRC", detected_by=auditor, source="INTERNAL_AUDIT",
                                                links={} if planted else {"revision_id": doc.current.id},
                                                context={"proc": doc.code}, dept=doc.dept)
                if planted:
                    self.w.plant("INCIDENT_WITHOUT_LINKS", "Quality_Incidents", incident.id,
                                 "Audit finding recorded without reference to the audited procedure")
                docs.add_verification(doc.current.id, None, "INTERNAL_AUDIT", auditor, "NON_CONFORM",
                                      f"Audit finding: requirement of {doc.code} not met", incident.id)
            else:
                docs.add_verification(doc.current.id, None, "INTERNAL_AUDIT", auditor, "CONFORM")

    def _management_review(self) -> None:
        engine, rng = self.w.engine, self.w.rng
        today = engine.today
        if today.year == 2025 and today.month == 10:
            self._supplier_plan()
        if today.year == 2025 and today.month == 7:
            self._count_procedure_plan()
        for _ in range(rng.randint(1, 2)):
            dept, title, description = C.PREVENTIVE_TREND_ACTIONS[self._trend_pointer % len(C.PREVENTIVE_TREND_ACTIONS)]
            self._trend_pointer += 1
            engine.now = engine.now + timedelta(minutes=rng.randint(10, 30))
            self.create_action("PREVENTIVE", "TREND_ANALYSIS", None, title, description, dept, "MINOR")
