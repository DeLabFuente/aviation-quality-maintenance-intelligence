"""
AQMI generator — The "world": connects all the modules and runs the simulation.
"""

import random
from datetime import timedelta

from config import generator_parameters as P
from config import settings
from scripts.generator import catalogs as C
from scripts.generator.documents import DocumentControl
from scripts.generator.engine import Engine, fmt_dt, parse_d
from scripts.generator.inventory import Inventory
from scripts.generator.maintenance import Maintenance
from scripts.generator.quality import Quality
from scripts.generator.staff import MasterData


class World:
    def __init__(self, conn, seed: int = settings.RANDOM_SEED):
        self.conn = conn
        self.rng = random.Random(seed)
        self.period_start = parse_d(settings.PERIOD_START)
        self.as_of = parse_d(settings.AS_OF_DATE)
        self.engine = Engine(conn, self.rng, self.period_start, self.as_of)
        self.go_live = self.engine.at(self.period_start, 8, 0)
        self.go_live_ts = fmt_dt(self.go_live)

        self.dept_id = dict(conn.execute("SELECT department_code, department_id FROM Departments"))
        self.category_id = dict(conn.execute("SELECT category_code, category_id FROM Incident_Categories"))

        self.master = MasterData(self)
        self.documents = DocumentControl(self)
        self.inventory = Inventory(self)
        self.maintenance = Maintenance(self)
        self.quality = Quality(self)
        self.planted: list[dict] = []

    # ------------------------------------------------------------ planted discrepancies
    def plant(self, kind: str, table: str, reference, description: str) -> None:
        """Record a deliberate discrepancy. The reference is the business code of the record."""
        code_column = {"Maintenance_Orders": ("mo_number", "mo_id"),
                       "Quality_Incidents": ("incident_number", "incident_id")}.get(table)
        if code_column and isinstance(reference, int):
            reference = self.conn.execute(f"SELECT {code_column[0]} FROM {table} WHERE {code_column[1]} = ?",
                                          (reference,)).fetchone()[0]
        self.planted.append({"kind": kind, "table": table, "reference": str(reference),
                             "date": self.engine.today.isoformat(), "description": description})

    def planted_count(self, kind: str) -> int:
        return sum(1 for p in self.planted if p["kind"] == kind)

    # ------------------------------------------------------------ demand estimate
    def expected_monthly_demand(self, materials) -> dict:
        """Expected monthly quantity of each material, used to set min stock and reorder qty."""
        orders = {"SCHEDULED": 0.0, "UNSCHEDULED": 0.0, "MODIFICATION": 0.0}
        for reg, category, *_ in C.AIRCRAFT:
            orders["SCHEDULED"] += 30.4 / P.SCHEDULED_INTERVAL_DAYS[category]
            factor = P.HIGH_UNSCHEDULED_FACTOR if reg == P.HIGH_UNSCHEDULED_AIRCRAFT else 1
            orders["UNSCHEDULED"] += P.UNSCHEDULED_DAILY_PROB * factor * 21.7
            orders["MODIFICATION"] += P.MODIFICATION_MONTHLY_PROB
        tag_sizes: dict = {}
        for m in materials:
            tag_sizes[m.tag] = tag_sizes.get(m.tag, 0) + 1
        demand = {m.pn: 0.0 for m in materials}
        for mo_type, n_orders in orders.items():
            weights = C.USAGE_WEIGHTS[mo_type]
            total = sum(weights[m.tag] / tag_sizes[m.tag] for m in materials)
            low, high = P.MATERIAL_LINES[mo_type]
            lines = n_orders * (low + high) / 2
            for m in materials:
                share = (weights[m.tag] / tag_sizes[m.tag]) / total
                demand[m.pn] += lines * share * self.inventory.mean_qty(m)
        return demand

    # ------------------------------------------------------------ build and run
    def build(self) -> None:
        engine = self.engine
        engine.now = self.go_live                       # system go-live: master data migration
        self.master.create_employees()
        self.master.create_customers_and_aircraft()
        self.master.create_suppliers()
        self.inventory.create_materials()
        self.documents.create_initial()
        engine.now = self.go_live + timedelta(minutes=30)
        self.inventory.create_opening_stock()

        self.maintenance.plan_all()
        self.quality.plan_recurring()
        self.inventory._schedule_replenishment()
        first_tuesday = self.period_start
        while first_tuesday.weekday() != 1:
            first_tuesday += timedelta(days=1)
        engine.schedule(engine.at(first_tuesday, 7, 30), self.inventory.cycle_count)

    def run(self) -> None:
        self.engine.run()
