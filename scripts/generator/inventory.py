"""
AQMI generator — Module D: materials, lots, stock movements, purchasing and stock counts.

Stock is tracked lot by lot and bucket by bucket (QUARANTINE, AVAILABLE,
RESERVED, BLOCKED, NON_CONFORMING), exactly as the database records it.
Quantities use multiples of 0.25 so that decimal sums are always exact.
"""

import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from config import generator_parameters as P
from scripts.generator import catalogs as C
from scripts.generator.engine import add_workdays, fmt_d, fmt_dt, next_workday

BUCKETS = ("QUARANTINE", "AVAILABLE", "BLOCKED", "NON_CONFORMING")


@dataclass
class Lot:
    number: str
    serial: str | None
    cert: str | None
    expiry: date | None
    received: datetime
    buckets: dict = field(default_factory=lambda: {b: 0.0 for b in BUCKETS})
    reserved: dict = field(default_factory=dict)          # mo_id -> qty


@dataclass
class Material:
    id: int
    pn: str
    description: str
    cls: str
    uom: str
    serialized: bool
    shelf_life: bool
    cert_required: bool
    tag: str
    lead: int
    cost: float
    supplier: object
    min_stock: float = 0.0
    reorder: float = 1.0
    lots: list = field(default_factory=list)
    open_lines: list = field(default_factory=list)
    waiting: list = field(default_factory=list)          # (mo, line) waiting for stock
    last_late: tuple | None = None                       # (po_line, delivery date) of the last late delivery

    @property
    def integer(self) -> bool:
        return self.uom in ("EA", "KIT")

    def bucket(self, name: str) -> float:
        return sum(lot.buckets[name] for lot in self.lots)

    def available(self) -> float:
        return self.bucket("AVAILABLE")

    def on_order(self) -> float:
        return sum(line.qty - line.received for line in self.open_lines if not line.cancelled)

    def waiting_qty(self) -> float:
        return sum(line.qty + line.excess for _, line in self.waiting)


@dataclass
class POLine:
    id: int
    po_id: int
    material: Material
    supplier: object
    qty: float
    promised: date
    urgency: str
    received: float = 0.0
    cancelled: bool = False


def round_qty(material: Material, qty: float) -> float:
    if material.integer:
        return float(max(1, math.ceil(qty)))
    return max(0.25, math.ceil(qty * 4) / 4)


class Inventory:
    def __init__(self, world):
        self.w = world
        self.materials: list[Material] = []
        self.lot_seq = 0
        self.cert_seq = 0
        self.serial_seq = 0
        self.count_pointer = 0
        self.count_procedure_revised = False       # story: cycle-count procedure revision
        self.pos: dict[int, list] = {}             # po_id -> list of POLine

    # ------------------------------------------------------------ catalogue
    def create_materials(self) -> None:
        rng, engine, master = self.w.rng, self.w.engine, self.w.master
        suppliers = master.parts_suppliers()
        main_suppliers = suppliers[:18]            # most parts come from a core group of suppliers
        late = master.supplier_by_code[P.LATE_SUPPLIER_CODE]
        family_base = {"CONSUMABLE": 1100, "STANDARD_PART": 2200, "COMPONENT": 3300, "RAW_MATERIAL": 4400}
        family_count: dict[str, int] = {}
        for index, (desc, cls, uom, serial, sl, tag, lead, cost) in enumerate(C.MATERIALS):
            family_count[cls] = family_count.get(cls, 0) + 1
            pn = f"AQ-{family_base[cls] + family_count[cls] * 7:04d}-{rng.randint(1, 9):02d}"
            if tag in ("FILTER", "SEAL", "FLUID") and index % 3 == 0:
                supplier = late                    # story: the late supplier sells frequently used items
            else:
                supplier = rng.choice(main_suppliers if rng.random() < 0.85 else suppliers)
            cert = cls == "COMPONENT" or tag == "FLUID" or sl == 1
            self.materials.append(Material(0, pn, desc, cls, uom, bool(serial), bool(sl), cert,
                                           tag, lead, cost, supplier))

        # Minimum stock and reorder quantity from the expected demand (fictitious stock policy)
        expected = self.w.expected_monthly_demand(self.materials)
        for m in self.materials:
            monthly = expected[m.pn]
            lead_months = m.lead / 30.4
            if m.serialized:
                m.min_stock = 1.0 if monthly > 0 else 0.0
                m.reorder = 1.0
            else:
                safety = 2.0 if m.cls == "COMPONENT" else 1.0
                m.min_stock = round_qty(m, max(monthly * (lead_months * 1.5 + 0.75), safety))
                m.reorder = round_qty(m, max(monthly * 6, m.min_stock))
            m.id = engine.insert("Materials", {
                "part_number": m.pn, "description": m.description, "material_class": m.cls,
                "unit_of_measure": m.uom, "preferred_supplier_id": m.supplier.id,
                "standard_lead_time_days": m.lead, "min_stock_qty": m.min_stock, "reorder_qty": m.reorder,
                "unit_cost": m.cost, "is_serialized": int(m.serialized),
                "is_shelf_life_controlled": int(m.shelf_life),
                "requires_release_certificate": int(m.cert_required),
                "created_at": self.w.go_live_ts, "created_by": master.head("LOG"),
            })
            m.supplier.material_ids.append(m.id)

    def qty_for(self, m: Material) -> float:
        rng = self.w.rng
        if m.serialized:
            return 1.0
        if m.uom == "L":
            return rng.choice([1.0, 1.5, 2.0, 2.5, 3.0, 4.0])
        if m.uom == "KG":
            return rng.choice([0.25, 0.5, 0.75, 1.0])
        if m.uom == "M":
            return rng.choice([1.0, 2.0, 3.0]) if m.tag == "HARDWARE" else rng.choice([1.0, 2.0, 3.0, 5.0, 8.0])
        if m.uom == "KIT":
            return 1.0
        if m.tag == "HARDWARE":
            return float(rng.randint(2, 12))
        if m.tag == "SEAL":
            return float(rng.randint(1, 6))
        if m.tag == "SHOP" or m.cls == "RAW_MATERIAL":
            return float(rng.randint(1, 3))
        return float(rng.choice([1, 1, 1, 2]))

    @staticmethod
    def mean_qty(m: Material) -> float:
        if m.serialized:
            return 1.0
        return {"L": 2.33, "KG": 0.625, "KIT": 1.0}.get(m.uom, None) or (
            2.0 if m.uom == "M" and m.tag == "HARDWARE" else 3.8 if m.uom == "M"
            else 7.0 if m.tag == "HARDWARE" else 3.5 if m.tag == "SEAL"
            else 2.0 if (m.tag == "SHOP" or m.cls == "RAW_MATERIAL") else 1.25)

    def choose_materials(self, mo_type: str, k: int) -> list[Material]:
        weights_by_tag = C.USAGE_WEIGHTS[mo_type]
        tag_sizes: dict[str, int] = {}
        for m in self.materials:
            tag_sizes[m.tag] = tag_sizes.get(m.tag, 0) + 1
        pool = [m for m in self.materials if weights_by_tag[m.tag] > 0]
        weights = [weights_by_tag[m.tag] / tag_sizes[m.tag] for m in pool]
        chosen = []
        for _ in range(min(k, len(pool))):
            pick = self.w.rng.choices(pool, weights=weights)[0]
            index = pool.index(pick)
            pool.pop(index)
            weights.pop(index)
            chosen.append(pick)
        return chosen

    # ------------------------------------------------------------ movements
    def _move(self, m: Material, lot: Lot | None, mtype: str, qty: float, src: str | None, dst: str | None,
              actor: int, mo_id=None, po_line_id=None, incident_id=None, count_id=None, reason=None) -> None:
        engine = self.w.engine
        engine.insert("Inventory_Movements", {
            "movement_number": engine.next_number("MV", engine.today.year, 5),
            "movement_datetime": fmt_dt(engine.now), "material_id": m.id, "movement_type": mtype,
            "quantity": float(qty), "from_bucket": src, "to_bucket": dst,
            "mo_id": mo_id, "po_line_id": po_line_id, "incident_id": incident_id, "stock_count_id": count_id,
            "lot_number": lot.number if lot else None, "serial_number": lot.serial if lot else None,
            "certificate_ref": lot.cert if lot else None,
            "shelf_life_expiry_date": fmt_d(lot.expiry) if lot and lot.expiry else None,
            "reason": reason, "performed_by": actor,
            "created_at": fmt_dt(engine.now), "created_by": actor,
        })
        if lot is None:
            return
        if src == "RESERVED":
            lot.reserved[mo_id] = lot.reserved.get(mo_id, 0.0) - qty
        elif src:
            lot.buckets[src] -= qty
        if dst == "RESERVED":
            lot.reserved[mo_id] = lot.reserved.get(mo_id, 0.0) + qty
        elif dst:
            lot.buckets[dst] += qty

    def _new_lot(self, m: Material, received: datetime, cert_missing: bool = False) -> Lot:
        rng = self.w.rng
        self.lot_seq += 1
        self.cert_seq += 1
        serial = None
        if m.serialized:
            self.serial_seq += 1
            serial = f"SN{m.pn[3:7]}-{self.serial_seq:05d}"
        expiry = (received.date() + timedelta(days=rng.randint(540, 1080))) if m.shelf_life else None
        lot = Lot(number=f"L{received:%y%m}-{self.lot_seq:05d}", serial=serial,
                  cert=None if cert_missing else f"CRT-{m.supplier.code[4:]}-{self.cert_seq:05d}",
                  expiry=expiry, received=received)
        m.lots.append(lot)
        return lot

    def storekeeper(self) -> int:
        return self.w.master.pick("LOG", titles=["Storekeeper"])

    # ------------------------------------------------------------ opening stock
    def create_opening_stock(self) -> None:
        engine, rng = self.w.engine, self.w.rng
        for m in self.materials:
            qty = round_qty(m, m.min_stock + m.reorder * rng.uniform(0.4, 1.1))
            if m.serialized:
                qty = float(max(1, int(m.min_stock) + rng.randint(0, 1)))
            counter = self.storekeeper()
            count_id = engine.insert("Stock_Counts", {
                "count_number": engine.next_number("SC", engine.today.year),
                "material_id": m.id, "count_datetime": fmt_dt(engine.now), "count_type": "OPENING",
                "system_qty": 0.0, "counted_qty": qty, "counted_by": counter,
                "comment": "Opening balance counted at system go-live",
                "created_at": fmt_dt(engine.now), "created_by": counter,
            })
            received = engine.now - timedelta(days=rng.randint(20, 200))
            parts = [1.0] * int(qty) if m.serialized else (
                [qty] if qty < 4 or rng.random() < 0.5 else self._split(m, qty))
            for part in parts:
                lot = self._new_lot(m, received)
                self._move(m, lot, "ADJUSTMENT_IN", part, None, "AVAILABLE", counter,
                           count_id=count_id, reason="Opening balance at system go-live")

    @staticmethod
    def _split(m: Material, qty: float) -> list[float]:
        first = math.floor(qty * 0.6) if m.integer else math.floor(qty * 0.6 * 4) / 4
        first = max(first, 1.0 if m.integer else 0.25)
        return [float(first), float(qty - first)]

    # ------------------------------------------------------------ reservations and issues
    def try_reserve(self, mo, line) -> bool:
        m = line.material
        need = line.qty + line.excess
        today = self.w.engine.today
        usable = [lot for lot in sorted(m.lots, key=lambda l: l.received)
                  if lot.buckets["AVAILABLE"] > 0 and (lot.expiry is None or lot.expiry > today + timedelta(days=30))]
        on_hand = sum(lot.buckets["AVAILABLE"] for lot in usable)
        if line.excess and line.qty <= on_hand < need:
            line.excess, need = 0.0, line.qty         # no spare unit when stock is just enough
        if on_hand < need:
            return False
        actor = self.storekeeper()
        remaining = need
        for lot in usable:
            if remaining <= 0:
                break
            take = min(lot.buckets["AVAILABLE"], remaining)
            self._move(m, lot, "RESERVE", take, "AVAILABLE", "RESERVED", actor, mo_id=mo.id)
            line.allocation.append((lot, take))
            remaining -= take
        line.reserved = True
        return True

    def issue(self, mo, line) -> None:
        actor = self.storekeeper()
        for lot, qty in line.allocation:
            self._move(line.material, lot, "ISSUE", qty, "RESERVED", None, actor, mo_id=mo.id)
        line.issued = True

    def unreserve(self, mo, line) -> None:
        actor = self.storekeeper()
        for lot, qty in line.allocation:
            self._move(line.material, lot, "UNRESERVE", qty, "RESERVED", "AVAILABLE", actor, mo_id=mo.id)
        line.allocation, line.reserved = [], False
        self.w.maintenance.on_stock_available(line.material)

    def return_excess(self, mo, line) -> None:
        lot = line.allocation[-1][0]
        actor = self.storekeeper()
        self._move(line.material, lot, "RETURN", float(line.excess), None, "QUARANTINE", actor, mo_id=mo.id)
        engine = self.w.engine
        day = add_workdays(engine.today, 1)
        engine.schedule(engine.work_time(day, 8, 11), self._release, line.material, [lot])

    # ------------------------------------------------------------ purchasing
    def _position(self, m: Material) -> float:
        return m.available() + m.bucket("QUARANTINE") + m.on_order() - m.waiting_qty()

    def replenishment_check(self) -> None:
        """Weekly stock review. When a supplier must be ordered from, other references of the same
        supplier that are close to their minimum are added to the same order (joint replenishment)."""
        triggered = {}
        for m in self.materials:
            position = self._position(m)
            if position < m.min_stock or (m.min_stock == 0 and position < 0):
                triggered.setdefault(m.supplier.code, m.supplier)
        for supplier in triggered.values():
            items = []
            for m in self.materials:
                if m.supplier is not supplier:
                    continue
                position = self._position(m)
                if position < m.min_stock + 0.5 * m.reorder and (m.min_stock > 0 or position < 0):
                    items.append((m, round_qty(m, max(m.reorder, m.min_stock - position))))
            if items:
                self.create_po(supplier, items, "ROUTINE")
        self._schedule_replenishment()

    def _schedule_replenishment(self) -> None:
        engine = self.w.engine
        day = engine.today + timedelta(days=1)
        while day.weekday() != 0:                    # every Monday
            day += timedelta(days=1)
        engine.schedule(engine.at(day, 7, 30), self.replenishment_check)

    def request_urgent(self, mo, line) -> None:
        m = line.material
        coverage = m.available() + m.bucket("QUARANTINE") + m.on_order() - m.waiting_qty()
        if coverage >= 0:
            return                                   # stock already on order will cover the need
        urgency = mo.priority if mo.priority in ("URGENT", "AOG") else "URGENT"
        self.create_po(m.supplier, [(m, round_qty(m, max(-coverage, m.reorder)))], urgency, mo=mo)

    def create_po(self, supplier, items, urgency: str, mo=None) -> None:
        engine, rng = self.w.engine, self.w.rng
        buyer = self.w.master.pick("LOG", titles=["Buyer"])
        now_ts = fmt_dt(engine.now)
        po_id = engine.insert("Purchase_Orders", {
            "po_number": engine.next_number("PO", engine.today.year), "supplier_id": supplier.id,
            "order_date": fmt_d(engine.today), "urgency": urgency, "buyer_id": buyer,
            "created_at": now_ts, "created_by": buyer,
        })
        lines = []
        for number, (m, qty) in enumerate(items, start=1):
            factor = P.URGENT_LEAD_FACTOR.get(urgency, 1.0)
            promised = next_workday(engine.today + timedelta(days=max(1, round(m.lead * factor))))
            line_id = engine.insert("Purchase_Order_Lines", {
                "po_id": po_id, "line_number": number, "material_id": m.id, "qty_ordered": float(qty),
                "unit_price": round(m.cost * rng.uniform(0.95, 1.08), 2), "promised_date": fmt_d(promised),
                "mo_id": mo.id if mo else None, "created_at": now_ts, "created_by": buyer,
            })
            line = POLine(line_id, po_id, m, supplier, float(qty), promised, urgency)
            m.open_lines.append(line)
            lines.append(line)
            self._schedule_deliveries(line)
        self.pos[po_id] = lines
        if urgency == "ROUTINE" and rng.random() < P.PO_CANCELLATION_PROB:
            day = add_workdays(engine.today, rng.randint(2, 4))
            engine.schedule(engine.at(day, 12, 30), self._cancel_po, po_id, buyer)

    def _schedule_deliveries(self, line: POLine) -> None:
        engine, rng, master = self.w.engine, self.w.rng, self.w.master
        roll = rng.random()
        if master.is_late_supplier(line.supplier):
            delay = rng.randint(*P.LATE_SUPPLIER_LATE_DAYS) if roll < P.LATE_SUPPLIER_LATE_PROB else 0
        elif roll < P.NORMAL_LATE_PROB:
            delay = rng.randint(*P.NORMAL_LATE_DAYS)
        elif roll < P.NORMAL_LATE_PROB + P.EARLY_PROB:
            delay = -rng.randint(1, 3)
        else:
            delay = 0
        delivery = next_workday(max(engine.today + timedelta(days=1), line.promised + timedelta(days=delay)))
        m = line.material
        if (not m.serialized and line.qty >= 2 and rng.random() < P.PARTIAL_DELIVERY_PROB):
            first = math.floor(line.qty * 0.6) if m.integer else math.floor(line.qty * 0.6 * 4) / 4
            shipments = [(delivery, float(first)),
                         (next_workday(delivery + timedelta(days=rng.randint(3, 10))), float(line.qty - first))]
        else:
            shipments = [(delivery, line.qty)]
        for day, qty in shipments:
            engine.schedule(engine.work_time(day, 9, 15), self._receive, line, qty)

    def _cancel_po(self, po_id: int, buyer: int) -> None:
        lines = self.pos[po_id]
        if any(line.received > 0 for line in lines):
            return
        self.w.engine.update("Purchase_Orders", "po_id", po_id, buyer,
                             {"cancelled_date": fmt_d(self.w.engine.today)})
        for line in lines:
            line.cancelled = True
            line.material.open_lines.remove(line)

    def _receive(self, line: POLine, qty: float) -> None:
        if line.cancelled:
            return
        engine, rng = self.w.engine, self.w.rng
        m = line.material
        actor = self.storekeeper()
        cert_missing = (m.cert_required and engine.today >= date(2025, 3, 1) and rng.random() < 0.04
                        and self.w.planted_count("RECEIPT_WITHOUT_CERTIFICATE") < P.PLANTED_RECEIPTS_WITHOUT_CERTIFICATE)
        units = [1.0] * int(qty) if m.serialized else [qty]
        lots = []
        for unit_qty in units:
            lot = self._new_lot(m, engine.now, cert_missing=cert_missing)
            self._move(m, lot, "RECEIPT", unit_qty, None, "QUARANTINE", actor, po_line_id=line.id)
            lots.append(lot)
        if cert_missing:
            number = self.w.conn.execute(
                "SELECT movement_number FROM Inventory_Movements WHERE lot_number = ? AND movement_type = 'RECEIPT'",
                (lots[0].number,)).fetchone()[0]
            self.w.plant("RECEIPT_WITHOUT_CERTIFICATE", "Inventory_Movements", number,
                         f"Receipt of {m.pn} recorded without certificate reference")
        line.received += qty
        if line.received >= line.qty:
            m.open_lines.remove(line)
        if engine.today > line.promised:
            m.last_late = (line, engine.today)
            if ((engine.today - line.promised).days >= P.LATE_DELIVERY_INCIDENT_DAYS
                    and rng.random() < P.LATE_DELIVERY_INCIDENT_PROB):
                self.w.quality.create_incident(
                    "SUP", detected_by=self.w.master.pick("LOG", titles=["Buyer"]), source="SUPPLIER",
                    links={"supplier_id": line.supplier.id, "po_line_id": line.id, "material_id": m.id},
                    context={"supplier": line.supplier.code, "mo": "stock replenishment"},
                    title=f"Delivery date not met by {line.supplier.code}")
        day = add_workdays(engine.today, 1)
        engine.schedule(engine.work_time(day, 8, 10), self._inspect, m, lots, line)

    def _inspect(self, m: Material, lots: list, line: POLine) -> None:
        engine, rng = self.w.engine, self.w.rng
        if rng.random() < P.RECEIVING_REJECT_PROB:
            inspector = self.w.master.pick("QUA", titles=["Quality Inspector"])
            incident = self.w.quality.create_incident(
                "MNC", detected_by=inspector, source="RECEIVING_INSPECTION",
                links={"material_id": m.id, "supplier_id": line.supplier.id, "po_line_id": line.id},
                context={"pn": m.pn})
            actor = self.storekeeper()
            for lot in lots:
                self._move(m, lot, "NONCONFORM", lot.buckets["QUARANTINE"], "QUARANTINE", "NON_CONFORMING",
                           actor, incident_id=incident.id)
            day = add_workdays(engine.today, rng.randint(3, 10))
            engine.schedule(engine.work_time(day, 9, 15), self._scrap, m, lots, incident.id)
        else:
            self._release(m, lots)

    def _release(self, m: Material, lots: list) -> None:
        actor = self.storekeeper()
        for lot in lots:
            qty = lot.buckets["QUARANTINE"]
            if qty > 0:
                self._move(m, lot, "INSPECTION_RELEASE", qty, "QUARANTINE", "AVAILABLE", actor)
        self.w.maintenance.on_stock_available(m)

    def _scrap(self, m: Material, lots: list, incident_id: int) -> None:
        actor = self.storekeeper()
        for lot in lots:
            qty = lot.buckets["NON_CONFORMING"]
            if qty > 0:
                self._move(m, lot, "SCRAP", qty, "NON_CONFORMING", None, actor, incident_id=incident_id,
                           reason="Rejected at receiving inspection – disposed / returned to supplier")

    # ------------------------------------------------------------ stock counts
    def cycle_count(self) -> None:
        """Weekly cycle count (Tuesdays, before work starts): a few references in rotation."""
        engine = self.w.engine
        for k in range(P.CYCLE_COUNTS_PER_WEEK):
            m = self.materials[self.count_pointer % len(self.materials)]
            self.count_pointer += 1
            engine.schedule(engine.at(engine.today, 7, 31 + k * 5), self._count, m)
        engine.schedule(engine.at(engine.today + timedelta(days=7), 7, 30), self.cycle_count)

    def _count(self, m: Material) -> None:
        engine, rng = self.w.engine, self.w.rng
        system = m.available()
        if m.serialized:
            probability = 0.0
        elif m.cls == "STANDARD_PART" and not self.count_procedure_revised:
            probability = P.STANDARD_PART_DISCREPANCY_PROB
        else:
            probability = P.COUNT_DISCREPANCY_PROB
        diff = 0.0
        if rng.random() < probability:
            step = 1.0 if m.integer else 0.25
            if system >= 2 * step and rng.random() < 0.7:
                max_units = int(min(5 if m.integer else 8, system / step))
                diff = -step * rng.randint(1, max(1, max_units))
            elif m.lots:
                diff = step * rng.randint(1, 3 if m.integer else 6)
        counted = system + diff
        counter = self.storekeeper()
        number = engine.next_number("SC", engine.today.year)
        count_id = engine.insert("Stock_Counts", {
            "count_number": number, "material_id": m.id, "count_datetime": fmt_dt(engine.now),
            "count_type": "CYCLE", "system_qty": float(system), "counted_qty": float(counted),
            "counted_by": counter,
            "comment": None if diff == 0 else ("Fewer units found than recorded" if diff < 0
                                               else "More units found than recorded"),
            "created_at": fmt_dt(engine.now), "created_by": counter,
        })
        if diff == 0:
            return
        reason = f"Cycle count adjustment {number}"
        if diff < 0:
            remaining = -diff
            for lot in sorted(m.lots, key=lambda l: l.received):
                if remaining <= 0:
                    break
                take = min(lot.buckets["AVAILABLE"], remaining)
                if take > 0:
                    self._move(m, lot, "ADJUSTMENT_OUT", take, "AVAILABLE", None, counter,
                               count_id=count_id, reason=reason)
                    remaining -= take
        else:
            lot = max(m.lots, key=lambda l: l.received)
            self._move(m, lot, "ADJUSTMENT_IN", diff, None, "AVAILABLE", counter, count_id=count_id, reason=reason)
            self.w.maintenance.on_stock_available(m)
        significant = abs(diff) >= (3 if m.integer else 1.0) or abs(diff) * m.cost >= 40
        if rng.random() < (0.85 if significant else 0.3):
            self.w.quality.create_incident("INV", detected_by=counter, source="STOCK_COUNT",
                                           links={"material_id": m.id}, context={"pn": m.pn})
