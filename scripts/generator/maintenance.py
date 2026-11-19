"""
AQMI generator — Module E: maintenance orders, material lines, documents used and holds.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta

from config import generator_parameters as P
from scripts.generator import catalogs as C
from scripts.generator.engine import add_workdays, fmt_d, fmt_dt, is_workday, next_workday


@dataclass
class Line:
    id: int
    material: object
    qty: float
    excess: float = 0.0
    reserved: bool = False
    issued: bool = False
    waiting: bool = False
    allocation: list = field(default_factory=list)


@dataclass
class Order:
    id: int
    number: str
    aircraft: object
    mo_type: str
    priority: str
    opened: date
    planner: int
    status: str = "OPEN"
    lines: list = field(default_factory=list)
    links: dict = field(default_factory=dict)        # role -> (document, revision)
    holds: dict = field(default_factory=dict)        # reason -> (hold_id, start date)
    remaining_work: int = 1
    working: bool = False
    work_since: date | None = None
    token: int = 0
    obsolete_link: dict | None = None                # planted: {"revision": ..., "detect": bool}
    incidents: list = field(default_factory=list)

    @property
    def finished(self) -> bool:
        return self.status in ("COMPLETED", "CLOSED", "CANCELLED")


def workdays_between(start: date, end: date) -> int:
    days, current = 0, start
    while current < end:
        current += timedelta(days=1)
        if is_workday(current):
            days += 1
    return days


class Maintenance:
    def __init__(self, world):
        self.w = world
        self.orders: list[Order] = []

    # ------------------------------------------------------------ planning
    def plan_all(self) -> None:
        for aircraft in self.w.master.aircraft:
            if aircraft.id:
                self.plan_aircraft(aircraft)

    def plan_aircraft(self, aircraft) -> None:
        """Pre-plan the arrival of every order of one aircraft over the whole period."""
        engine, rng = self.w.engine, self.w.rng
        first_day = max(engine.today, aircraft.contract_start)
        last_day = self.w.as_of

        interval = P.SCHEDULED_INTERVAL_DAYS[aircraft.category]
        day = first_day + timedelta(days=rng.randint(0, interval))
        while day <= last_day:
            opening = next_workday(day)
            engine.schedule(engine.work_time(opening, 8, 10), self.open_order, aircraft, "SCHEDULED")
            day += timedelta(days=round(interval * rng.uniform(0.8, 1.2)))

        rate = P.UNSCHEDULED_DAILY_PROB * (P.HIGH_UNSCHEDULED_FACTOR
                                           if aircraft.registration == P.HIGH_UNSCHEDULED_AIRCRAFT else 1)
        day = first_day
        while day <= last_day:
            if is_workday(day) and rng.random() < rate:
                engine.schedule(engine.work_time(day, 8, 14), self.open_order, aircraft, "UNSCHEDULED")
            day += timedelta(days=1)

        month_start = date(first_day.year, first_day.month, 1)
        while month_start <= last_day:
            if rng.random() < P.MODIFICATION_MONTHLY_PROB:
                day = next_workday(month_start + timedelta(days=rng.randint(0, 25)))
                if first_day <= day <= last_day:
                    engine.schedule(engine.work_time(day, 8, 11), self.open_order, aircraft, "MODIFICATION")
            month_start = date(month_start.year + month_start.month // 12, month_start.month % 12 + 1, 1)

    # ------------------------------------------------------------ opening
    def open_order(self, aircraft, mo_type: str) -> None:
        engine, rng, master, docs, inv = self.w.engine, self.w.rng, self.w.master, self.w.documents, self.w.inventory
        if not master.under_contract(aircraft, engine.today):
            return
        planner = master.pick("PRD", titles=["Production Planner"])
        if mo_type == "UNSCHEDULED":
            priority = rng.choices(["ROUTINE", "URGENT", "AOG"], weights=[45, 40, 15])[0]
        else:
            priority = "ROUTINE"
        duration = rng.randint(*P.PLANNED_DURATION_DAYS[mo_type])
        planned_end = add_workdays(engine.today, duration)
        now_ts = fmt_dt(engine.now)
        mo_id = engine.insert("Maintenance_Orders", {
            "mo_number": engine.next_number("WO", engine.today.year), "aircraft_id": aircraft.id,
            "maintenance_type": mo_type, "work_description": rng.choice(C.MO_DESCRIPTIONS[mo_type]),
            "priority": priority,
            "responsible_department_id": self.w.dept_id["PRD" if mo_type == "MODIFICATION" else "MNT"],
            "planner_id": planner, "opened_date": fmt_d(engine.today), "planned_end_date": fmt_d(planned_end),
            "status": "OPEN", "created_at": now_ts, "created_by": planner,
        })
        mo = Order(mo_id, "", aircraft, mo_type, priority, engine.today, planner)
        mo.remaining_work = duration + (rng.randint(*P.WORK_OVERRUN_DAYS) if rng.random() < P.WORK_OVERRUN_PROB else 0)
        self.orders.append(mo)

        # Material lines
        for material in inv.choose_materials(mo_type, rng.randint(*P.MATERIAL_LINES[mo_type])):
            qty = inv.qty_for(material)
            line_id = engine.insert("Maintenance_Order_Materials", {
                "mo_id": mo_id, "material_id": material.id, "qty_required": qty,
                "required_by_date": fmt_d(engine.today), "created_at": now_ts, "created_by": planner,
            })
            excess = 1.0 if (material.integer and not material.serialized
                             and rng.random() < P.EXCESS_ISSUE_PROB) else 0.0
            mo.lines.append(Line(line_id, material, qty, excess))

        # Documents used: work instruction, technical data, closure form, aircraft logbook
        documents = {
            "WORK_INSTRUCTION": rng.choice(docs.of_type("WORK_INSTRUCTION")),
            "TECHNICAL_DATA": rng.choice(docs.tdr_for(aircraft.model)),
            "FORM": docs.by_code[P.CLOSURE_FORM_DOC],
            "RECORD": docs.aircraft_logbook(aircraft),
        }
        for role, doc in documents.items():
            revision = doc.current
            if (role == "WORK_INSTRUCTION" and doc.previous and engine.today >= date(2025, 2, 1)
                    and rng.random() < 0.03
                    and self.w.planted_count("OBSOLETE_REVISION_LINK") < P.PLANTED_OBSOLETE_REVISION_LINKS):
                revision = doc.previous[-1]
                detect = self.w.planted_count("OBSOLETE_REVISION_LINK") < 2
                mo.obsolete_link = {"revision": revision, "detect": detect, "detected": False}
                self.w.plant("OBSOLETE_REVISION_LINK", "Maintenance_Orders", mo_id,
                             f"Work order linked to superseded revision {doc.code} {revision.code}"
                             + (" (detected at records review)" if detect else " (not detected)"))
            engine.insert("Maintenance_Order_Documents", {
                "mo_id": mo_id, "revision_id": revision.id, "usage_role": role,
                "linked_date": fmt_d(engine.today), "created_at": now_ts, "created_by": planner,
            })
            mo.links[role] = (doc, revision)

        if rng.random() < P.PRE_USE_CHECK_PROB:
            doc, revision = mo.links["WORK_INSTRUCTION"]
            checker = master.pick("QUA", titles=["Quality Inspector"])
            docs.add_verification(revision.id, mo_id, "PRE_USE_CHECK", checker, "CONFORM")

        if rng.random() < P.MO_CANCELLATION_PROB:
            engine.schedule(engine.at(engine.today, 15, rng.randint(0, 50)), self.cancel_order, mo)
        engine.schedule(engine.later_today(30, 120), self.start_order, mo)
        if rng.random() < P.MNT_ISSUE_PROB:
            issue_day = add_workdays(engine.today, rng.randint(0, max(0, duration - 1)))
            engine.schedule(engine.work_time(issue_day, 10, 15), self._maintenance_issue, mo)

    # ------------------------------------------------------------ start, holds and work
    def start_order(self, mo: Order) -> None:
        if mo.finished:
            return
        engine, rng, inv, docs = self.w.engine, self.w.rng, self.w.inventory, self.w.documents
        for line in mo.lines:
            if not inv.try_reserve(mo, line):
                line.waiting = True
                line.material.waiting.append((mo, line))
                inv.request_urgent(mo, line)

        waiting = [line for line in mo.lines if line.waiting]
        if waiting:
            self.add_hold(mo, "MATERIAL", material=waiting[0].material,
                          comment=f"Material {waiting[0].material.pn} not available at start of work")
        elif (engine.today >= date(2025, 2, 1) and rng.random() < 0.03
              and self.w.planted_count("FALSE_MATERIAL_HOLD") < P.PLANTED_FALSE_MATERIAL_HOLDS):
            material = mo.lines[0].material
            self.add_hold(mo, "MATERIAL", material=material,
                          comment=f"Material {material.pn} not available at start of work")
            self.w.plant("FALSE_MATERIAL_HOLD", "Maintenance_Orders", mo.id,
                         f"Material hold recorded while {material.pn} was available")
            end_day = add_workdays(engine.today, rng.randint(1, 2))
            engine.schedule(engine.work_time(end_day, 9, 12), self.end_hold, mo, "MATERIAL")

        wi_doc, _ = mo.links["WORK_INSTRUCTION"]
        if docs.is_overdue(wi_doc, engine.today) and rng.random() < 0.6:
            incident = None
            if rng.random() < 0.5:
                incident = self.w.quality.create_incident(
                    "DOC", detected_by=mo.planner, source="PRODUCTION",
                    links={"revision_id": wi_doc.current.id, "mo_id": mo.id, "aircraft_id": mo.aircraft.id})
            self.add_hold(mo, "DOCUMENTATION", document=wi_doc, incident=incident,
                          comment=f"{wi_doc.code} overdue for review – expedited review requested")
            docs.request_expedited_review(wi_doc, callback=lambda: self.end_hold(mo, "DOCUMENTATION"))
        elif rng.random() < P.DOC_HOLD_PROB:
            tdr_doc, _ = mo.links["TECHNICAL_DATA"]
            self.add_hold(mo, "DOCUMENTATION", document=tdr_doc,
                          comment=f"Applicable data from {tdr_doc.code} not available in the work package")
            end_day = add_workdays(engine.today, rng.randint(1, 3))
            engine.schedule(engine.work_time(end_day, 9, 15), self.end_hold, mo, "DOCUMENTATION")

        self.set_status(mo, "ON_HOLD" if mo.holds else "IN_PROGRESS", mo.planner)
        if not mo.holds:
            self.begin_work(mo)

    def set_status(self, mo: Order, status: str, actor: int, extra: dict | None = None) -> None:
        if mo.status == status and not extra:
            return
        mo.status = status
        self.w.engine.update("Maintenance_Orders", "mo_id", mo.id, actor, dict(extra or {}, status=status))

    def add_hold(self, mo: Order, reason: str, material=None, document=None, incident=None, comment="") -> None:
        engine = self.w.engine
        if reason in mo.holds:
            return
        hold_id = engine.insert("Maintenance_Order_Holds", {
            "mo_id": mo.id, "hold_reason": reason,
            "material_id": material.id if material else None,
            "document_id": document.id if document else None,
            "incident_id": incident.id if incident else None,
            "start_date": fmt_d(engine.today), "comment": comment, "raised_by": mo.planner,
            "created_at": fmt_dt(engine.now), "created_by": mo.planner,
        })
        mo.holds[reason] = (hold_id, engine.today)
        if mo.working:
            elapsed = workdays_between(mo.work_since, engine.today)
            mo.remaining_work = max(1, mo.remaining_work - elapsed)
            mo.working = False
            mo.token += 1

    def end_hold(self, mo: Order, reason: str) -> None:
        if reason not in mo.holds or mo.finished:
            return
        engine = self.w.engine
        hold_id, start = mo.holds.pop(reason)
        engine.update("Maintenance_Order_Holds", "hold_id", hold_id, mo.planner, {"end_date": fmt_d(engine.today)})
        if reason == "MATERIAL":
            self._check_supply_incident(mo, start)
        if not mo.holds:
            self.set_status(mo, "IN_PROGRESS", mo.planner)
            self.begin_work(mo)

    def begin_work(self, mo: Order) -> None:
        engine, rng = self.w.engine, self.w.rng
        mo.working = True
        mo.work_since = engine.today
        mo.token += 1
        for line in mo.lines:
            if line.reserved and not line.issued:
                day = engine.today if engine.now.hour < 12 else add_workdays(engine.today, 1)
                engine.schedule(engine.work_time(day, 12, 15) if day == engine.today else engine.work_time(day, 8, 11),
                                self.issue_line, mo, line)
        finish = add_workdays(engine.today, mo.remaining_work)
        engine.schedule(engine.work_time(finish, 15, 16), self.complete_order, mo, mo.token)

    def issue_line(self, mo: Order, line: Line) -> None:
        if mo.status == "CANCELLED" or line.issued or not line.reserved:
            return
        self.w.inventory.issue(mo, line)

    def on_stock_available(self, material) -> None:
        engine = self.w.engine
        for mo, line in list(material.waiting):
            if mo.finished:
                material.waiting.remove((mo, line))
                continue
            if not self.w.inventory.try_reserve(mo, line):
                break                                     # first come, first served
            material.waiting.remove((mo, line))
            line.waiting = False
            if not any(l.waiting for l in mo.lines) and "MATERIAL" in mo.holds:
                engine.schedule(engine.later_today(10, 60), self.end_hold, mo, "MATERIAL")

    # ------------------------------------------------------------ completion and closure
    def complete_order(self, mo: Order, token: int) -> None:
        if token != mo.token or mo.finished:
            return
        engine, rng = self.w.engine, self.w.rng
        for line in mo.lines:
            if line.reserved and not line.issued:
                self.w.inventory.issue(mo, line)
        supervisor = self.w.master.pick("MNT", titles=["Maintenance Supervisor"])
        mo.working = False
        self.set_status(mo, "COMPLETED", supervisor, {"actual_end_date": fmt_d(engine.today)})
        for line in mo.lines:
            if line.excess:
                self.w.inventory.return_excess(mo, line)
        review_day = add_workdays(engine.today, rng.randint(1, 8))
        engine.schedule(engine.work_time(review_day, 9, 15), self.records_review, mo)

    def records_review(self, mo: Order) -> None:
        """Production control checks the order records against their source documents."""
        engine, rng, master, docs = self.w.engine, self.w.rng, self.w.master, self.w.documents
        reviewer = (master.pick("PRD", titles=["Production Control Clerk"]) if rng.random() < 0.7
                    else master.pick("QUA", titles=["Quality Inspector"]))
        links = {"mo_id": mo.id, "aircraft_id": mo.aircraft.id}

        if mo.obsolete_link and mo.obsolete_link["detect"] and not mo.obsolete_link["detected"]:
            revision = mo.obsolete_link["revision"]
            incident = self.w.quality.create_incident("TRC", detected_by=reviewer, source="DOCUMENT_VERIFICATION",
                                                      links=dict(links, revision_id=revision.id),
                                                      title="Superseded revision used on work order")
            docs.add_verification(revision.id, mo.id, "RECORD_VS_SOURCE", reviewer, "NON_CONFORM",
                                  "Work order prepared with a superseded revision of the work instruction",
                                  incident.id)
            mo.obsolete_link["detected"] = True
            mo.incidents.append(incident)

        form_doc, form_revision = mo.links["FORM"]
        fixed = docs.closure_form_fixed_seq
        bad_form = fixed is None or form_revision.seq < fixed
        probability = P.RECORD_NONCONFORM_PROB_BEFORE if bad_form else P.RECORD_NONCONFORM_PROB_AFTER
        roll = rng.random()
        if roll < probability:
            category = "REC" if rng.random() < 0.75 else "TRC"
            incident = self.w.quality.create_incident(category, detected_by=reviewer,
                                                      source="DOCUMENT_VERIFICATION",
                                                      links=dict(links, revision_id=form_revision.id))
            docs.add_verification(form_revision.id, mo.id, "RECORD_VS_SOURCE", reviewer, "NON_CONFORM",
                                  "Record on the work order does not match the source document", incident.id)
            mo.incidents.append(incident)
        elif roll < probability + P.RECORD_MINOR_PROB:
            docs.add_verification(form_revision.id, mo.id, "RECORD_VS_SOURCE", reviewer, "MINOR_DISCREPANCY",
                                  "Minor transcription error, corrected at review")
        else:
            docs.add_verification(form_revision.id, mo.id, "RECORD_VS_SOURCE", reviewer, "CONFORM")
        self.close_order(mo, reviewer)

    def close_order(self, mo: Order, reviewer: int) -> None:
        engine = self.w.engine
        if any(i.severity == "CRITICAL" and not i.closed for i in mo.incidents):
            day = add_workdays(engine.today, 5)               # rule M13: wait for the critical incident
            engine.schedule(engine.work_time(day, 9, 15), self.close_order, mo, reviewer)
            return
        self.set_status(mo, "CLOSED", reviewer, {"closed_date": fmt_d(engine.today), "closed_by": reviewer})
        if self.w.rng.random() < P.CUSTOMER_FEEDBACK_PROB:
            day = add_workdays(engine.today, self.w.rng.randint(3, 15))
            engine.schedule(engine.work_time(day, 9, 16), self._customer_feedback, mo)

    def _customer_feedback(self, mo: Order) -> None:
        """The customer reports a problem with the records delivered with the aircraft."""
        category = self.w.rng.choice(["REC", "REC", "MNT"])
        _, form_revision = mo.links["FORM"]
        self.w.quality.create_incident(category, detected_by=self.w.master.pick("PRD", titles=["Production Planner"]),
                                       source="CUSTOMER",
                                       links={"mo_id": mo.id, "aircraft_id": mo.aircraft.id,
                                              "revision_id": form_revision.id})

    def cancel_order(self, mo: Order) -> None:
        if mo.finished or any(line.issued for line in mo.lines):
            return
        engine = self.w.engine
        for line in mo.lines:
            if line.waiting:
                line.material.waiting.remove((mo, line))
                line.waiting = False
        for reason in list(mo.holds):
            hold_id, _ = mo.holds.pop(reason)
            engine.update("Maintenance_Order_Holds", "hold_id", hold_id, mo.planner,
                          {"end_date": fmt_d(engine.today)})
        mo.token += 1
        mo.working = False
        self.set_status(mo, "CANCELLED", mo.planner,
                        {"cancellation_reason": "Customer withdrew the request before work started"})
        for line in mo.lines:
            if line.reserved:
                self.w.inventory.unreserve(mo, line)

    # ------------------------------------------------------------ incidents raised by production
    def _maintenance_issue(self, mo: Order) -> None:
        if mo.finished:
            return
        supervisor = self.w.master.pick("MNT", titles=["Maintenance Supervisor"])
        incident = self.w.quality.create_incident("MNT", detected_by=supervisor, source="PRODUCTION",
                                                  links={"mo_id": mo.id, "aircraft_id": mo.aircraft.id})
        mo.incidents.append(incident)

    def _check_supply_incident(self, mo: Order, hold_start: date) -> None:
        engine, rng = self.w.engine, self.w.rng
        waited = (engine.today - hold_start).days
        urgent = mo.priority in ("URGENT", "AOG")
        if waited < (P.SUPPLY_INCIDENT_MIN_HOLD_DAYS if urgent else 10):
            return
        for line in mo.lines:
            late = line.material.last_late
            if late and hold_start <= late[1] <= engine.today and rng.random() < (0.85 if urgent else 0.4):
                po_line = late[0]
                incident = self.w.quality.create_incident(
                    "SUP", detected_by=self.w.master.pick("LOG", titles=["Buyer"]), source="SUPPLIER",
                    links={"supplier_id": po_line.supplier.id, "po_line_id": po_line.id,
                           "material_id": line.material.id, "mo_id": mo.id, "aircraft_id": mo.aircraft.id},
                    context={"supplier": po_line.supplier.code, "mo": f"order of {mo.aircraft.registration}"})
                mo.incidents.append(incident)
                return
