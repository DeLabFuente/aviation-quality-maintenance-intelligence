"""
AQMI generator — Module C: documents, revisions, periodic reviews and verifications.
"""

import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta

from config import generator_parameters as P
from scripts.generator import catalogs as C
from scripts.generator.engine import add_workdays, fmt_d, fmt_dt, next_workday


def add_months(day: date, months: int) -> date:
    month = day.month - 1 + months
    year = day.year + month // 12
    month = month % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


@dataclass
class Revision:
    id: int
    code: str
    seq: int
    effective: date
    review_due: date | None
    prepared_by: int


@dataclass
class Document:
    id: int
    code: str
    doc_type: str
    dept: str
    title: str
    interval: int | None              # review interval in months (None = not controlled)
    aircraft: object = None
    current: Revision | None = None
    previous: list = field(default_factory=list)   # superseded revisions, oldest first
    draft: Revision | None = None
    review_token: int = 0
    on_valid: list = field(default_factory=list)   # callbacks waiting for the document to be valid


class DocumentControl:
    def __init__(self, world):
        self.w = world
        self.docs: list[Document] = []
        self.by_code: dict[str, Document] = {}
        # Story: revision number from which the redesigned closure form is in use (None = not yet)
        self.closure_form_fixed_seq: int | None = None

    # ------------------------------------------------------------ catalogue
    def create_initial(self) -> None:
        for dept, titles in C.PROCEDURES.items():
            for n, title in enumerate(titles, start=1):
                self._create(f"PRO-{dept}-{n:03d}", title, "PROCEDURE", dept)
        n = 0
        for system in C.WI_SYSTEMS:
            for task in C.WI_TASKS:
                n += 1
                self._create(f"WIN-MNT-{n:03d}", f"Work instruction – {system} – {task}", "WORK_INSTRUCTION", "MNT")
        for dept, titles in C.FORMS.items():
            for n, title in enumerate(titles, start=1):
                self._create(f"FRM-{dept}-{n:03d}", f"Form – {title}", "FORM", dept)
        n = 0
        for model in C.TDR_MODELS:
            for group in C.TDR_GROUPS:
                n += 1
                self._create(f"TDR-DOC-{n:03d}", f"Technical data reference – {model} – {group}",
                             "TECHNICAL_DATA_REF", "DOC")
        self._create("TDR-DOC-064", "Technical data reference – common – Standard practices",
                     "TECHNICAL_DATA_REF", "DOC")
        for aircraft in self.w.master.aircraft:
            if aircraft.id:
                self.create_aircraft_records(aircraft, at_go_live=True)

    def create_aircraft_records(self, aircraft, at_go_live: bool = False) -> None:
        base = sum(1 for d in self.docs if d.doc_type == "AIRCRAFT_RECORD")
        for k, record_type in enumerate(C.ACR_TYPES, start=1):
            self._create(f"ACR-DOC-{base + k:03d}", f"Aircraft record – {aircraft.registration} – {record_type}",
                         "AIRCRAFT_RECORD", "DOC", aircraft=aircraft, at_go_live=at_go_live)

    def _create(self, code, title, doc_type, dept, aircraft=None, at_go_live=True) -> Document:
        engine, rng, master = self.w.engine, self.w.rng, self.w.master
        interval = C.REVIEW_INTERVAL_MONTHS.get(doc_type)
        created_at = self.w.go_live_ts if at_go_live else fmt_dt(engine.now)
        creator = master.pick("DOC", titles=["Document Controller"])
        doc_id = engine.insert("Documents", {
            "document_code": code, "title": title, "document_type": doc_type,
            "owner_department_id": self.w.dept_id[dept],
            "aircraft_id": aircraft.id if aircraft else None,
            "is_controlled": int(interval is not None), "review_interval_months": interval,
            "created_at": created_at, "created_by": creator,
        })
        doc = Document(doc_id, code, doc_type, dept, title, interval, aircraft)
        self.docs.append(doc)
        self.by_code[code] = doc

        # Revision history up to the go-live (or the creation date)
        reference = self.w.period_start if at_go_live else engine.today
        if interval:
            span = int(interval * 30.4)
            current_effective = reference - timedelta(days=rng.randint(15, span - 10))
        elif at_go_live:
            current_effective = reference - timedelta(days=rng.randint(30, 1500))
        else:
            current_effective = reference
        n_previous = rng.choice([0, 0, 0, 1, 1, 1, 2, 3]) if at_go_live else 0
        effectives = [current_effective]
        for _ in range(n_previous):
            earlier = effectives[0] - timedelta(days=rng.randint(300, 900))
            if earlier < date(2016, 1, 1):
                break
            effectives.insert(0, earlier)

        for seq, effective in enumerate(effectives):
            is_current = seq == len(effectives) - 1
            issue = effective - timedelta(days=rng.randint(0, 10))
            prepared = master.pick_hired_before(dept, issue, heads=False)
            approved = master.pick_hired_before(dept, issue, heads=True, exclude={prepared})
            review_due = add_months(effective, interval) if interval else None
            superseded = None if is_current else effectives[seq + 1]
            rev_id = engine.insert("Document_Revisions", {
                "document_id": doc_id, "revision_code": f"R{seq:02d}", "revision_seq": seq,
                "issue_date": fmt_d(issue), "effective_date": fmt_d(effective),
                "review_due_date": fmt_d(review_due) if review_due else None,
                "superseded_date": fmt_d(superseded) if superseded else None,
                "lifecycle_status": "CURRENT" if is_current else "SUPERSEDED",
                "prepared_by": prepared, "approved_by": approved,
                "change_summary": "Initial issue" if seq == 0 else "Periodic review update",
                "created_at": created_at, "created_by": creator,
            })
            revision = Revision(rev_id, f"R{seq:02d}", seq, effective, review_due, prepared)
            if is_current:
                doc.current = revision
            else:
                doc.previous.append(revision)

        if interval:
            self._schedule_review(doc)
        return doc

    # ------------------------------------------------------------ periodic review
    def _schedule_review(self, doc: Document, expedite_days: int | None = None) -> None:
        rng, engine = self.w.rng, self.w.engine
        doc.review_token += 1
        if expedite_days is not None:
            day = add_workdays(engine.today, expedite_days)
        else:
            if rng.random() < P.REVIEW_SKIPPED_PROB:
                return                                   # forgotten review: document becomes overdue
            day = next_workday(doc.current.review_due + timedelta(days=rng.randint(-25, 30)))
        engine.schedule(engine.work_time(day, 9, 15), self._periodic_review, doc, doc.review_token)

    def is_overdue(self, doc: Document, day: date) -> bool:
        return bool(doc.interval and doc.current.review_due and doc.current.review_due < day)

    def request_expedited_review(self, doc: Document, callback=None) -> None:
        """Called when someone finds an overdue document at the point of use."""
        if callback:
            doc.on_valid.append(callback)
        if doc.draft is None:
            self._schedule_review(doc, expedite_days=self.w.rng.randint(1, 4))

    def _periodic_review(self, doc: Document, token: int) -> None:
        if token != doc.review_token or doc.draft is not None:
            return
        rng, engine, master = self.w.rng, self.w.engine, self.w.master
        reviewer = master.pick("DOC", titles=["Document Controller"])
        roll = rng.random()
        if roll < P.REVIEW_NONCONFORM_PROB:
            result = "NON_CONFORM"
        elif roll < P.REVIEW_NONCONFORM_PROB + P.REVIEW_MINOR_PROB:
            result = "MINOR_DISCREPANCY"
        else:
            result = "CONFORM"

        incident_id = None
        description = None
        if result != "CONFORM":
            description = rng.choice(["Reference to a superseded form found in the text",
                                      "Responsibilities section does not match the current organisation",
                                      "Approval record incomplete for the previous change",
                                      "Two steps described in an order that is no longer used"])
        if result == "NON_CONFORM":
            incident = self.w.quality.create_incident(
                "DOC", detected_by=reviewer, source="DOCUMENT_VERIFICATION",
                links={"revision_id": doc.current.id})
            incident_id = incident.id
        self.add_verification(doc.current.id, None, "PERIODIC_REVIEW", reviewer, result, description, incident_id)

        if result != "CONFORM" or rng.random() < P.REVIEW_NEW_REVISION_PROB:
            self.start_revision(doc, "Periodic review: content updated", author=reviewer)
        else:
            new_due = add_months(engine.today, doc.interval)
            doc.current.review_due = new_due
            engine.update("Document_Revisions", "revision_id", doc.current.id, reviewer,
                          {"review_due_date": fmt_d(new_due)})
            self._schedule_review(doc)
            self._notify_valid(doc)

    # ------------------------------------------------------------ revisions
    def start_revision(self, doc: Document, summary: str, author: int | None = None, on_active=None) -> None:
        """Prepare a new revision (DRAFT now, CURRENT on its effective date)."""
        engine, rng = self.w.engine, self.w.rng
        if doc.draft is not None:
            if on_active:
                doc.on_valid.append(on_active)
            return
        author = author or self.w.master.pick(doc.dept)
        seq = doc.current.seq + 1
        effective = add_workdays(engine.today, rng.randint(3, 10))
        rev_id = engine.insert("Document_Revisions", {
            "document_id": doc.id, "revision_code": f"R{seq:02d}", "revision_seq": seq,
            "issue_date": fmt_d(engine.today), "effective_date": fmt_d(effective),
            "review_due_date": fmt_d(add_months(effective, doc.interval)) if doc.interval else None,
            "lifecycle_status": "DRAFT", "prepared_by": author, "change_summary": summary,
            "created_at": fmt_dt(engine.now), "created_by": author,
        })
        doc.draft = Revision(rev_id, f"R{seq:02d}", seq, effective,
                             add_months(effective, doc.interval) if doc.interval else None, author)
        if on_active:
            doc.on_valid.append(on_active)
        engine.schedule(engine.at(effective, 7, 45), self._activate, doc)     # in force before work starts

    def _activate(self, doc: Document) -> None:
        engine, master = self.w.engine, self.w.master
        new, old = doc.draft, doc.current
        approver = master.pick(doc.dept, heads=True, exclude={new.prepared_by})
        engine.update("Document_Revisions", "revision_id", old.id, approver,
                      {"lifecycle_status": "SUPERSEDED", "superseded_date": fmt_d(engine.today)})
        engine.update("Document_Revisions", "revision_id", new.id, approver,
                      {"lifecycle_status": "CURRENT", "approved_by": approver})
        doc.previous.append(old)
        doc.current, doc.draft = new, None
        if doc.interval:
            self._schedule_review(doc)
        self._notify_valid(doc)

    def _notify_valid(self, doc: Document) -> None:
        callbacks, doc.on_valid = doc.on_valid, []
        for callback in callbacks:
            callback()

    # ------------------------------------------------------------ verifications
    def add_verification(self, revision_id, mo_id, verification_type, verified_by, result,
                         description=None, incident_id=None) -> int:
        engine = self.w.engine
        return engine.insert("Document_Verifications", {
            "verification_number": engine.next_number("DV", engine.today.year),
            "revision_id": revision_id, "mo_id": mo_id, "verification_type": verification_type,
            "verification_date": fmt_d(engine.today), "verified_by": verified_by, "result": result,
            "discrepancy_description": description, "incident_id": incident_id,
            "created_at": fmt_dt(engine.now), "created_by": verified_by,
        })

    # ------------------------------------------------------------ lookups
    def of_type(self, doc_type: str) -> list[Document]:
        return [d for d in self.docs if d.doc_type == doc_type]

    def tdr_for(self, model: str) -> list[Document]:
        return [d for d in self.docs if d.doc_type == "TECHNICAL_DATA_REF" and (model in d.title or "common" in d.title)]

    def aircraft_logbook(self, aircraft) -> Document:
        return next(d for d in self.docs if d.doc_type == "AIRCRAFT_RECORD"
                    and d.aircraft is aircraft and "Logbook" in d.title)
