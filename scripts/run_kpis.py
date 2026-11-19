"""
AQMI — Phase 6: calculate the 19 indicators (KPIs) and check them.

(18 indicators in Phase 6; LRN-01 Lesson Incorporation Rate added in Phase 9.)

What it does:
    1. Reads every indicator in sql/kpi/ (one file per KPI; the header of each
       file gives its definition, unit and fictitious internal target).
    2. Runs each query. Every KPI returns one row per month and one TOTAL row,
       with the same four columns: period, numerator, denominator, value.
    3. Checks the results with the indicator rules (K):
         K01  every percentage is between 0 and 100 (and nothing is negative)
         K02  a zero denominator gives "no data", never 0 %
         K04  the parts add up to the total (months = whole period;
              incidents by category, severity and department = total incidents)
         K05  each "state at a date" indicator, rebuilt from the history, gives at
              the cut-off date the same value as the current state of the data
       (K03, Power BI = SQL, is checked in Phase 9.)
    4. Writes three reports in reports/:
         kpi_report.md     readable summary with the traffic lights
         kpi_summary.csv   one row per KPI (headline value, target, status)
         kpi_values.csv    one row per KPI and month (for Excel and Power BI)
    5. Returns an error code if a KPI cannot be calculated or a K rule fails.

How to run it (from the main project folder, with the virtual environment active):
    python scripts/run_kpis.py
"""

import csv
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings  # noqa: E402
from scripts.common import get_connection, setup_logging  # noqa: E402

logger = setup_logging("run_kpis")

HEADER = re.compile(r"^-- (\w+): (.*)$")
AREAS = ["Quality", "Document control", "Inventory", "Maintenance", "Continuous improvement"]
STATUS_ICON = {"GREEN": "🟢", "AMBER": "🟡", "RED": "🔴", "NO_TARGET": "—", "NO_DATA": "no data"}


@dataclass
class KPI:
    kpi_id: str
    name: str
    name_es: str
    area: str
    kpi_type: str          # FLOW or SNAPSHOT
    unit: str              # count, %, days, per 100 orders
    direction: str         # HIGHER_IS_BETTER, LOWER_IS_BETTER, NEUTRAL
    target: float | None   # fictitious internal target of AEROQ MRO
    warning: float | None  # fictitious internal warning level
    tables: str
    question: str
    sql: str
    path: Path
    rows: list = field(default_factory=list)   # dicts: period, numerator, denominator, value
    error: str | None = None

    @property
    def is_ratio(self) -> bool:
        return self.unit != "count"

    @property
    def total(self) -> dict | None:
        return next((r for r in self.rows if r["period"] == "TOTAL"), None)

    @property
    def months(self) -> list:
        return [r for r in self.rows if r["period"] != "TOTAL"]


def _number(text: str) -> float | None:
    text = text.strip()
    return None if text.startswith("none") else float(text.split()[0])


def load_kpis(directory: Path = settings.SQL_KPI_DIR) -> list[KPI]:
    """Read every KPI file and its definition header."""
    kpis = []
    for path in sorted(directory.glob("*.sql")):
        text = path.read_text(encoding="utf-8")
        meta = {}
        for line in text.splitlines():
            match = HEADER.match(line)
            if not match:
                break
            meta[match.group(1)] = match.group(2).strip()
        required = {"kpi", "name", "name_es", "area", "type", "unit", "direction", "target", "warning",
                    "tables", "question"}
        if required - meta.keys():
            raise ValueError(f"{path.name}: header without {sorted(required - meta.keys())}")
        if meta["type"] not in ("FLOW", "SNAPSHOT"):
            raise ValueError(f"{path.name}: unknown type {meta['type']}")
        if meta["direction"] not in ("HIGHER_IS_BETTER", "LOWER_IS_BETTER", "NEUTRAL"):
            raise ValueError(f"{path.name}: unknown direction {meta['direction']}")
        if meta["area"] not in AREAS:
            raise ValueError(f"{path.name}: unknown area {meta['area']}")
        kpis.append(KPI(meta["kpi"], meta["name"], meta["name_es"], meta["area"], meta["type"], meta["unit"],
                        meta["direction"], _number(meta["target"]), _number(meta["warning"]), meta["tables"],
                        meta["question"], text, path))
    ids = [k.kpi_id for k in kpis]
    duplicated = {i for i in ids if ids.count(i) > 1}
    if duplicated:
        raise ValueError(f"Duplicated KPI ids: {sorted(duplicated)}")
    # Indicators added after Phase 6 (area "Continuous improvement", Phase 9) go after the
    # original 18, so the order of those does not change in the reports and in Power BI.
    kpis.sort(key=lambda k: k.area == "Continuous improvement")
    return kpis


# ------------------------------------------------------------------ values
def status(kpi: KPI, value) -> str:
    """Traffic light against the fictitious internal target."""
    if value is None:
        return "NO_DATA"
    if kpi.target is None or kpi.direction == "NEUTRAL":
        return "NO_TARGET"
    if kpi.direction == "HIGHER_IS_BETTER":
        return "GREEN" if value >= kpi.target else "AMBER" if value >= kpi.warning else "RED"
    return "GREEN" if value <= kpi.target else "AMBER" if value <= kpi.warning else "RED"


def combine(kpi: KPI, rows: list) -> float | None:
    """Value of a KPI over several months (used for the year-on-year comparison)."""
    if not rows:
        return None
    if kpi.kpi_type == "SNAPSHOT":
        return rows[-1]["value"]                       # state at the end of the last month
    numerator = sum(r["numerator"] for r in rows)
    if not kpi.is_ratio:
        return numerator
    denominator = sum(r["denominator"] for r in rows)
    if denominator == 0:
        return None
    factor = 1 if kpi.unit == "days" else 100
    return round(factor * numerator / denominator, 1)


def years(kpi: KPI) -> tuple:
    """Year 1 = first 12 months of the period, year 2 = last 12 months."""
    months = kpi.months
    return combine(kpi, months[:12]), combine(kpi, months[-12:])


def trend(kpi: KPI, year1, year2) -> str:
    if year1 is None or year2 is None or year1 == year2:
        return "="
    if kpi.direction == "NEUTRAL":
        return "↑" if year2 > year1 else "↓"
    better = (year2 > year1) == (kpi.direction == "HIGHER_IS_BETTER")
    return ("↑" if year2 > year1 else "↓") + (" better" if better else " worse")


def fmt(kpi: KPI, value) -> str:
    if value is None:
        return "no data"
    if kpi.unit == "count":
        return f"{value:g}"
    if kpi.unit == "%":
        return f"{value:.1f} %"
    if kpi.unit == "days":
        return f"{value:.1f} days"
    return f"{value:.1f}"


# ------------------------------------------------------------------ K rules
def check_k01(kpis: list[KPI]) -> list[tuple]:
    """K01: every percentage is between 0 and 100; no value is negative."""
    out = []
    for k in kpis:
        for r in k.rows:
            v = r["value"]
            if v is None:
                continue
            if v < 0:
                out.append((k.kpi_id, r["period"], f"negative value {v}"))
            elif k.unit == "%" and v > 100:
                out.append((k.kpi_id, r["period"], f"percentage above 100: {v}"))
    return out


def check_k02(kpis: list[KPI]) -> list[tuple]:
    """K02: a zero denominator gives no value ("no data"), never 0 %."""
    out = []
    for k in kpis:
        for r in k.rows:
            if not k.is_ratio:
                if r["denominator"] is not None or r["value"] != r["numerator"]:
                    out.append((k.kpi_id, r["period"], "a count must have no denominator and value = numerator"))
            elif r["denominator"] in (0, None) and r["value"] is not None:
                out.append((k.kpi_id, r["period"], f"denominator {r['denominator']} but value {r['value']}"))
            elif r["denominator"] and r["value"] is None:
                out.append((k.kpi_id, r["period"], "denominator > 0 but no value"))
    return out


def check_k04(kpis: list[KPI], conn) -> list[tuple]:
    """K04: the parts add up to the total."""
    out = []
    for k in kpis:
        if k.kpi_type != "FLOW" or k.total is None:
            continue
        for column in ("numerator", "denominator"):
            if k.total[column] is None:
                continue
            parts = round(sum(r[column] for r in k.months), 6)
            if parts != round(k.total[column], 6):
                out.append((k.kpi_id, "TOTAL", f"sum of months {column} {parts} <> total {k.total[column]}"))
    qua01 = next((k for k in kpis if k.kpi_id == "QUA-01"), None)
    if qua01 is not None and qua01.total is not None:
        for label, column in [("category", "category_id"), ("severity", "severity"),
                              ("department", "responsible_department_id")]:
            parts = conn.execute(f"""SELECT SUM(n) FROM (
                    SELECT {column}, COUNT(*) AS n FROM Quality_Incidents
                    WHERE status <> 'CANCELLED'
                      AND detected_date BETWEEN (SELECT period_start FROM vw_parameters)
                                            AND (SELECT as_of_date FROM vw_parameters)
                    GROUP BY {column})""").fetchone()[0]
            if parts != qua01.total["value"]:
                out.append(("QUA-01", "TOTAL", f"incidents by {label} add up to {parts}, total is {qua01.total['value']}"))
    return out


# SNAPSHOT KPI -> (numerator, denominator) of the same state taken from the current-state views
CURRENT_STATE = {
    "QUA-02": "SELECT SUM(is_open), NULL FROM vw_incident_status WHERE status <> 'CANCELLED'",
    "QUA-06": "SELECT SUM(is_overdue), NULL FROM vw_capa_status WHERE action_type = 'CORRECTIVE'",
    "DOC-01": "SELECT SUM(validity_status = 'VALID'), SUM(validity_status IN ('VALID', 'REVIEW_OVERDUE')) "
              "FROM vw_document_status",
    "DOC-03": "SELECT SUM(validity_status = 'REVIEW_OVERDUE'), NULL FROM vw_document_status",
    "INV-02": "SELECT SUM(s.is_below_min = 0), COUNT(*) FROM vw_stock_by_bucket s "
              "JOIN Materials m USING (material_id) WHERE m.is_active = 1",
    "INV-04": "SELECT SUM(is_pending), NULL FROM vw_po_status",
    "MNT-03": "SELECT SUM(is_blocked_by_material), NULL FROM vw_mo_status",
    "MNT-04": "SELECT SUM(is_blocked_by_documentation), NULL FROM vw_mo_status",
    "LRN-01": "SELECT SUM(status = 'INCORPORATED'), SUM(status IN ('APPROVED', 'INCORPORATED')) FROM Lessons_Learned",
}


def check_k05(kpis: list[KPI], conn) -> list[tuple]:
    """K05: the history, rebuilt at the cut-off date, equals the current state."""
    out = []
    for k in kpis:
        if k.kpi_type != "SNAPSHOT" or k.total is None:
            continue
        if k.kpi_id not in CURRENT_STATE:
            out.append((k.kpi_id, "TOTAL", "no current-state reference defined"))
            continue
        numerator, denominator = conn.execute(CURRENT_STATE[k.kpi_id]).fetchone()
        numerator = numerator or 0
        if (k.total["numerator"], k.total["denominator"]) != (numerator, denominator):
            out.append((k.kpi_id, "TOTAL", f"history gives {k.total['numerator']}/{k.total['denominator']}, "
                                           f"current state gives {numerator}/{denominator}"))
    return out


K_RULES = [
    ("K01", "Every percentage is between 0 and 100; no value is negative"),
    ("K02", "A zero denominator gives 'no data', never 0 %"),
    ("K04", "The parts add up to the total"),
    ("K05", "Each state-at-a-date KPI, rebuilt from history, equals the current state at the cut-off date"),
]


def run_kpis(db_path: Path = settings.DATABASE_PATH, report_dir: Path | None = settings.REPORTS_DIR) -> dict:
    """Calculate and check every KPI. Returns a summary dictionary."""
    kpis = load_kpis()
    conn = get_connection(db_path)
    try:
        expected_periods = [r[0] for r in conn.execute("SELECT period FROM vw_kpi_periods ORDER BY period")]
        as_of = conn.execute("SELECT as_of_date FROM vw_parameters").fetchone()[0]
        for k in kpis:
            try:
                cursor = conn.execute(k.sql)
                columns = [d[0] for d in cursor.description]
                if columns != ["period", "numerator", "denominator", "value"]:
                    raise ValueError(f"unexpected columns {columns}")
                k.rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                if [r["period"] for r in k.rows] != expected_periods:
                    raise ValueError("the periods returned do not match vw_kpi_periods")
            except Exception as error:   # a KPI that cannot be calculated is a failure of the control
                k.error = str(error)
                k.rows = []
                logger.error("KPI %s could not be calculated: %s", k.kpi_id, error)
        valid = [k for k in kpis if not k.error]
        checks = {
            "K01": check_k01(valid),
            "K02": check_k02(valid),
            "K04": check_k04(valid, conn),
            "K05": check_k05(valid, conn),
        }
    finally:
        conn.close()

    errors = [k for k in kpis if k.error]
    summary = {
        "as_of": as_of,
        "kpis": kpis,
        "checks": checks,
        "n_errors": len(errors),
        "gate_passed": not errors and not any(checks.values()),
    }
    if report_dir is not None:
        _write_reports(summary, report_dir)
    return summary


# ------------------------------------------------------------------ reports
def _write_reports(s: dict, report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    kpis = [k for k in s["kpis"] if not k.error]
    with open(report_dir / "kpi_values.csv", "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["kpi_id", "kpi_name", "area", "unit", "period", "numerator", "denominator", "value", "status"])
        for k in kpis:
            for r in k.rows:
                writer.writerow([k.kpi_id, k.name, k.area, k.unit, r["period"], r["numerator"],
                                 r["denominator"], r["value"], status(k, r["value"])])
    with open(report_dir / "kpi_summary.csv", "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["kpi_id", "kpi_name", "kpi_name_es", "area", "type", "unit", "direction", "value",
                         "numerator", "denominator", "fictitious_target", "fictitious_warning", "status",
                         "year_1", "year_2"])
        for k in kpis:
            y1, y2 = years(k)
            writer.writerow([k.kpi_id, k.name, k.name_es, k.area, k.kpi_type, k.unit, k.direction,
                             k.total["value"], k.total["numerator"], k.total["denominator"], k.target, k.warning,
                             status(k, k.total["value"]), y1, y2])
    (report_dir / "kpi_report.md").write_text(_markdown(s), encoding="utf-8")


def _with_icon(kpi: KPI, value) -> str:
    icon = STATUS_ICON[status(kpi, value)]
    return fmt(kpi, value) if icon in ("—", "no data") else f"{icon} {fmt(kpi, value)}"


def _markdown(s: dict) -> str:
    kpis = [k for k in s["kpis"] if not k.error]
    gate = "✅ PASSED" if s["gate_passed"] else "❌ FAILED"
    first = kpis[0].months[0]["period"] if kpis else "—"
    lines = [
        "# AQMI — KPI Report", "",
        "> Generated automatically by `scripts/run_kpis.py`. AEROQ MRO is fictitious and all data is synthetic.",
        "> **Targets are fictitious internal targets of AEROQ MRO. They are not regulatory thresholds.**", "",
        "| Item | Value |", "|---|---|",
        f"| Period | {first} to {s['as_of'][:7]} (24 months) |",
        f"| Cut-off date | {s['as_of']} |",
        f"| Report run | {datetime.now():%Y-%m-%d %H:%M} |",
        f"| Indicators | {len(s['kpis'])} |",
        f"| **KPI checks (K rules)** | **{gate}** |", "",
        "**How to read the values.** *Flow* indicators (things that happen) are given for the whole 24-month",
        "period. *Snapshot* indicators (states such as open, overdue or blocked) are given at the cut-off date.",
        "Year 1 = first 12 months, year 2 = last 12 months.", "",
        "Traffic light: 🟢 target met · 🟡 between target and warning level · 🔴 beyond the warning level · — no target.", "",
    ]
    for area in AREAS:
        lines += [f"## {area}", "",
                  "| KPI | Indicator | Type | Value | Target (fictitious) | Status | Year 1 | Year 2 | Trend |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for k in [k for k in kpis if k.area == area]:
            value = k.total["value"]
            y1, y2 = years(k)
            target = "—" if k.target is None else ("≥ " if k.direction == "HIGHER_IS_BETTER" else "≤ ") + fmt(k, k.target)
            lines.append(f"| {k.kpi_id} | {k.name} | {k.kpi_type.title()} | **{fmt(k, value)}** | {target} | "
                         f"{STATUS_ICON[status(k, value)]} | {_with_icon(k, y1)} | {_with_icon(k, y2)} | {trend(k, y1, y2)} |")
        lines.append("")

    lines += ["## KPI checks", "",
              "| Rule | Check | Result | Findings |", "|---|---|---|---|"]
    for rule_id, text in K_RULES:
        findings = s["checks"][rule_id]
        lines.append(f"| {rule_id} | {text} | {'✅ PASS' if not findings else '❌ FAIL'} | {len(findings)} |")
    lines.append("| K03 | Power BI shows the same value as the SQL reference query | Phase 9 | — |")
    failures = [(r, f) for r, items in s["checks"].items() for f in items]
    errors = [k for k in s["kpis"] if k.error]
    if failures or errors:
        lines += ["", "### Problems found", "", "| Rule | KPI | Period | Detail |", "|---|---|---|---|"]
        for k in errors:
            lines.append(f"| — | {k.kpi_id} | — | Could not be calculated: `{k.error}` |")
        for rule_id, (kpi_id, period, detail) in failures:
            lines.append(f"| {rule_id} | {kpi_id} | {period} | {detail} |")

    lines += ["", "## Last 12 months", "",
              "Monthly values. The full series (24 months) is in `kpi_values.csv`.", ""]
    last = [r["period"] for r in kpis[0].months[-12:]] if kpis else []
    lines += ["| KPI | " + " | ".join(last) + " |", "|---|" + "---|" * len(last)]
    for k in kpis:
        by_period = {r["period"]: r["value"] for r in k.rows}
        cells = ["—" if by_period[p] is None else f"{by_period[p]:g}" for p in last]
        lines.append(f"| {k.kpi_id} | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    if not settings.DATABASE_PATH.exists():
        logger.error("Database not found. Run 'python scripts/run_pipeline.py' first.")
        return 1
    s = run_kpis()
    for k in s["kpis"]:
        if k.error:
            continue
        value = k.total["value"]
        logger.info("%s %-38s %14s  %s", k.kpi_id, k.name, fmt(k, value), status(k, value))
    for rule_id, findings in s["checks"].items():
        for kpi_id, period, detail in findings:
            logger.error("%s failed: %s %s %s", rule_id, kpi_id, period, detail)
    logger.info("KPI checks: %s", ", ".join(f"{r} {'ok' if not f else 'FAILED'}" for r, f in s["checks"].items()))
    logger.info("Reports written to %s", settings.REPORTS_DIR.relative_to(settings.PROJECT_ROOT))
    if s["gate_passed"]:
        logger.info("KPI CHECKS PASSED")
        return 0
    logger.error("KPI CHECKS FAILED — indicators must not be published")
    return 1


if __name__ == "__main__":
    sys.exit(main())
