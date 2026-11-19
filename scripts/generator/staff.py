"""
AQMI generator — Master data: employees, customers, aircraft and suppliers.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta

from config import generator_parameters as P
from scripts.generator import catalogs as C
from scripts.generator.engine import fmt_d, fmt_dt, parse_d


@dataclass
class Employee:
    id: int
    code: str
    dept: str
    title: str
    head: bool
    hire: date
    termination: date | None = None
    leaving: bool = False


@dataclass
class Aircraft:
    id: int
    registration: str
    category: str
    model: str
    customer: str
    contract_start: date
    contract_end: date | None
    stop_new_orders: date | None = None


@dataclass
class Supplier:
    id: int
    code: str
    name: str
    status: str
    improved: bool = False          # story: late supplier after its improvement plan
    material_ids: list = field(default_factory=list)


class MasterData:
    """Creates and keeps the master data in memory for the rest of the simulation."""

    def __init__(self, world):
        self.w = world
        self.employees: list[Employee] = []
        self.by_id: dict[int, Employee] = {}
        self.aircraft: list[Aircraft] = []
        self.customers: dict[str, int] = {}
        self.suppliers: list[Supplier] = []
        self.supplier_by_code: dict[str, Supplier] = {}
        self._employee_seq = 0

    # ------------------------------------------------------------------ people
    def _new_name(self, used: set) -> tuple[str, str]:
        rng = self.w.rng
        while True:
            first = rng.choice(C.FIRST_NAMES)
            last = f"{rng.choice(C.LAST_NAMES)} {rng.choice(C.LAST_NAMES)}"
            if (first, last) not in used:
                used.add((first, last))
                return first, last

    def _insert_employee(self, dept: str, title: str, head: bool, hire: date, created_at: str) -> Employee:
        self._employee_seq += 1
        code = f"EMP-{self._employee_seq:03d}"
        first, last = self._new_name(self._used_names)
        emp_id = self.w.engine.insert("Employees", {
            "employee_code": code, "first_name": first, "last_name": last,
            "department_id": self.w.dept_id[dept], "job_title": title,
            "is_department_head": int(head), "email": f"{code.lower()}@aeroq-mro.example",
            "hire_date": fmt_d(hire), "created_at": created_at,
        })
        emp = Employee(emp_id, code, dept, title, head, hire)
        self.employees.append(emp)
        self.by_id[emp_id] = emp
        return emp

    def create_employees(self) -> None:
        rng = self.w.rng
        self._used_names = set()
        for dept, title, count, head in C.STAFFING:
            for _ in range(count):
                # Heads were hired early, so they can sign historical document revisions
                start = date(2004, 1, 1) if head else date(2008, 1, 1)
                end = date(2011, 12, 31) if head else date(2023, 12, 31)
                hire = start + timedelta(days=rng.randint(0, (end - start).days))
                self._insert_employee(dept, title, head, hire, self.w.go_live_ts)

        for hire_text, dept, title in C.NEW_HIRES:
            hire = parse_d(hire_text)
            self.w.engine.schedule(self.w.engine.at(hire, 8, 0), self._hire, dept, title, hire)

        leaver = next(e for e in self.employees if e.title == C.TERMINATION["job_title"])
        notice = parse_d(C.TERMINATION["notice_date"])
        self.w.engine.schedule(self.w.engine.at(notice, 9, 15), self._give_notice, leaver,
                               parse_d(C.TERMINATION["termination_date"]))

    def _hire(self, dept: str, title: str, hire: date) -> None:
        self._insert_employee(dept, title, False, hire, fmt_dt(self.w.engine.now))

    def _give_notice(self, emp: Employee, termination: date) -> None:
        emp.leaving = True
        emp.termination = termination
        self.w.engine.update("Employees", "employee_id", emp.id, self.head("DIR"),
                             {"termination_date": fmt_d(termination)})
        # Hand over open work before the last day
        handover = self.w.engine.at(termination, 10, 0) - timedelta(days=7)
        self.w.engine.schedule(handover, self.w.quality.reassign_work, emp)

    def is_active(self, emp: Employee, day: date) -> bool:
        return emp.hire <= day and (emp.termination is None or day <= emp.termination)

    def pick(self, dept: str, titles=None, exclude=(), heads: bool | None = False) -> int:
        """Pick an active employee of a department (optionally of given job titles)."""
        day = self.w.engine.today
        candidates = [e for e in self.employees
                      if e.dept == dept and self.is_active(e, day) and not e.leaving
                      and e.id not in exclude
                      and (titles is None or e.title in titles)
                      and (heads is None or e.head == heads)]
        if not candidates:  # fall back to anybody active in the department
            candidates = [e for e in self.employees
                          if e.dept == dept and self.is_active(e, day) and e.id not in exclude]
        return self.w.rng.choice(candidates).id

    def pick_hired_before(self, dept: str, day: date, heads: bool | None = False, exclude=()) -> int:
        """Pick an employee of the department who already worked there on a past date."""
        candidates = [e for e in self.employees if e.dept == dept and e.hire <= day
                      and (heads is None or e.head == heads) and e.id not in exclude]
        if not candidates:
            candidates = [e for e in self.employees if e.dept == dept and e.hire <= day
                          and e.id not in exclude]
        return self.w.rng.choice(candidates).id

    def head(self, dept: str) -> int:
        return next(e.id for e in self.employees if e.dept == dept and e.head)

    # ------------------------------------------------------- customers & fleet
    def create_customers_and_aircraft(self) -> None:
        engine = self.w.engine
        for code, name, op_type, country in C.CUSTOMERS:
            self.customers[code] = engine.insert("Customers", {
                "customer_code": code, "customer_name": name, "operation_type": op_type,
                "country_code": country, "created_at": self.w.go_live_ts, "created_by": self.head("DIR"),
            })
        for index, (reg, category, model, customer, year, start, end) in enumerate(C.AIRCRAFT, start=1):
            start_date = parse_d(start)
            aircraft = Aircraft(0, reg, category, model, customer, start_date, None)
            if start_date <= self.w.period_start:
                self._insert_aircraft(aircraft, index, year, self.w.go_live_ts)
            else:
                engine.schedule(engine.at(start_date, 8, 5), self._join_aircraft, aircraft, index, year)
            if end:
                notice = parse_d(C.CONTRACT_END_NOTICE[reg])
                aircraft.stop_new_orders = notice
                engine.schedule(engine.at(notice, 11, 0), self._end_contract, aircraft, parse_d(end))
            self.aircraft.append(aircraft)

    def _insert_aircraft(self, aircraft: Aircraft, index: int, year: int, created_at: str) -> None:
        aircraft.id = self.w.engine.insert("Aircraft", {
            "registration": aircraft.registration, "fleet_number": f"AQ-H{index:02d}",
            "aircraft_category": aircraft.category, "aircraft_model": aircraft.model,
            "serial_number": f"SN-{aircraft.model[:2]}{1000 + index * 37}",
            "customer_id": self.customers[aircraft.customer], "year_of_manufacture": year,
            "contract_start_date": fmt_d(aircraft.contract_start),
            "created_at": created_at, "created_by": self.head("PRD"),
        })

    def _join_aircraft(self, aircraft: Aircraft, index: int, year: int) -> None:
        self._insert_aircraft(aircraft, index, year, fmt_dt(self.w.engine.now))
        self.w.documents.create_aircraft_records(aircraft)
        self.w.maintenance.plan_aircraft(aircraft)

    def _end_contract(self, aircraft: Aircraft, end: date) -> None:
        aircraft.contract_end = end
        self.w.engine.update("Aircraft", "aircraft_id", aircraft.id, self.head("DIR"),
                             {"contract_end_date": fmt_d(end)})

    def under_contract(self, aircraft: Aircraft, day: date) -> bool:
        if aircraft.id == 0 or day < aircraft.contract_start:
            return False
        if aircraft.stop_new_orders and day >= aircraft.stop_new_orders:
            return False
        return aircraft.contract_end is None or day <= aircraft.contract_end

    # ---------------------------------------------------------------- suppliers
    def create_suppliers(self) -> None:
        rng = self.w.rng
        used = set()
        types = ["DISTRIBUTOR"] * 16 + ["MANUFACTURER"] * 12 + ["REPAIR_STATION"] * 6 + ["SERVICE_PROVIDER"] * 6
        rng.shuffle(types)
        for n in range(1, 41):
            while True:
                name = (f"{rng.choice(C.SUPPLIER_PREFIXES)}{rng.choice(C.SUPPLIER_MIDDLES)} "
                        f"{rng.choice(C.SUPPLIER_SUFFIXES)}")
                if name not in used:
                    used.add(name)
                    break
            code = f"SUP-{n:03d}"
            status = ("APPROVED" if n <= 30 else "CONDITIONAL" if n <= 34
                      else "SUSPENDED" if n <= 36 else "INACTIVE")
            approval = date(2015, 1, 1) + timedelta(days=rng.randint(0, 3000))
            suspended = (approval + timedelta(days=rng.randint(200, 900))) if status == "SUSPENDED" else None
            if suspended and suspended >= self.w.period_start:
                suspended = self.w.period_start - timedelta(days=rng.randint(30, 300))
            next_eval = self.w.period_start + timedelta(days=rng.randint(30, 360))
            if n <= 34 and types[n - 1] == "SERVICE_PROVIDER":
                types[n - 1] = "DISTRIBUTOR"     # suppliers of parts must sell parts
            supplier_id = self.w.engine.insert("Suppliers", {
                "supplier_code": code, "supplier_name": name, "country_code": rng.choice(C.SUPPLIER_COUNTRIES),
                "supplier_type": types[n - 1], "approval_status": status, "approval_date": fmt_d(approval),
                "suspended_date": fmt_d(suspended) if suspended else None,
                "next_evaluation_date": fmt_d(next_eval),
                "contact_email": f"orders@{code.lower()}.example",
                "created_at": self.w.go_live_ts, "created_by": self.head("LOG"),
            })
            supplier = Supplier(supplier_id, code, name, status)
            self.suppliers.append(supplier)
            self.supplier_by_code[code] = supplier

    def parts_suppliers(self) -> list[Supplier]:
        """Suppliers that can receive orders (approved or conditional)."""
        return [s for s in self.suppliers if s.status in ("APPROVED", "CONDITIONAL")]

    def set_supplier_status(self, supplier: Supplier, status: str, actor: int) -> None:
        supplier.status = status
        self.w.engine.update("Suppliers", "supplier_id", supplier.id, actor, {"approval_status": status})

    def is_late_supplier(self, supplier: Supplier) -> bool:
        return supplier.code == P.LATE_SUPPLIER_CODE and not supplier.improved
