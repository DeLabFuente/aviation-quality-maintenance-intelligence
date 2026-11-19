"""
AQMI — Phase 7: export the analytical model (star schema) for Power BI.

What it does:
    1. QUALITY GATE: runs the 82 validations and the KPI checks first. If either
       fails, nothing is exported, so Power BI never shows unchecked data.
    2. Runs every query in sql/analytics/ (one file per table of the star schema:
       Dim_* are the dimensions, Fact_* the facts) and writes one CSV per table.
    3. Adds the tables that come from the controls themselves:
         Dim_KPI, Fact_KPI_Monthly             the 18 indicators as calculated in SQL
         Fact_ValidationResults / Findings     the result of the 82 validation rules
         Model_Info                            cut-off date, gate status, disclaimer
    4. Writes data/processed/_schema.json: the columns and data type of every
       table. The Power BI project and the tests use it.

Output folder: data/processed/  (Power BI reads the CSV files from there)

How to run it (from the main project folder, with the virtual environment active):
    python scripts/export_powerbi.py
"""

import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings  # noqa: E402
from scripts.common import get_connection, setup_logging  # noqa: E402
from scripts.run_kpis import AREAS, run_kpis, status  # noqa: E402
from scripts.run_validations import GROUPS, run_validations  # noqa: E402

logger = setup_logging("export_powerbi")

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
INTEGER = re.compile(r"^-?\d+$")
DECIMAL = re.compile(r"^-?\d+(\.\d+)?([eE][-+]?\d+)?$")

DISCLAIMER = ("AEROQ MRO is a fictitious company. All data is synthetic. Targets are fictitious internal "
              "targets, not regulatory thresholds. Not a certified system.")


def _text(value) -> str:
    """CSV representation: empty for NULL, ISO dates as stored, '.' as decimal separator."""
    if value is None:
        return ""
    if isinstance(value, float):
        return repr(round(value, 6)) if value != int(value) else str(int(value)) if abs(value) < 1e15 else repr(value)
    return str(value)


# Decimal columns by name, so their type does not depend on the values of one data set
# (a quantity column that happens to be all whole numbers is still a decimal column).
ALWAYS_DECIMAL = re.compile(r"(_qty|_value|_cost|^quantity|^value|^target|^warning|^numerator|^denominator|"
                            r"^sql_value|^sql_numerator|^sql_denominator|^data_quality_score)$")


def infer_type(values: list[str], name: str = "") -> str:
    """Data type of a column, inferred from its values: int64, double, date, dateTime or string."""
    filled = [v for v in values if v != ""]
    if ALWAYS_DECIMAL.search(name) and all(DECIMAL.match(v) for v in filled):
        return "double"
    if not filled:
        return "string"
    for kind, pattern in (("date", DATE), ("dateTime", DATETIME), ("int64", INTEGER), ("double", DECIMAL)):
        if all(pattern.match(v) for v in filled):
            if kind == "int64" and any(len(v.lstrip("-")) > 15 for v in filled):
                return "string"
            return kind
    return "string"


def write_table(folder: Path, name: str, columns: list[str], rows: list[list]) -> dict:
    texts = [[_text(v) for v in row] for row in rows]
    with open(folder / f"{name}.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(texts)
    types = {}
    for i, column in enumerate(columns):
        types[column] = infer_type([row[i] for row in texts], column)
    return {"rows": len(rows), "columns": [{"name": c, "type": types[c]} for c in columns]}


def export(db_path: Path = settings.DATABASE_PATH, out_dir: Path = settings.POWERBI_DATA_DIR,
           validations: dict | None = None, kpis: dict | None = None) -> dict:
    """Write the star schema. Returns the schema dictionary (table -> rows, columns)."""
    validations = validations or run_validations(db_path, report_dir=None)
    kpis = kpis or run_kpis(db_path, report_dir=None)
    if not validations["gate_passed"] or not kpis["gate_passed"]:
        raise RuntimeError("Quality gate or KPI checks failed: nothing is exported to Power BI")

    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.csv"):
        old.unlink()
    schema = {}
    conn = get_connection(db_path)
    try:
        for path in sorted(settings.SQL_ANALYTICS_DIR.glob("*.sql")):
            name = path.stem.split("_", 1)[1]            # 10_Fact_Incidents -> Fact_Incidents
            cursor = conn.execute(path.read_text(encoding="utf-8"))
            columns = [d[0] for d in cursor.description]
            schema[name] = write_table(out_dir, name, columns, cursor.fetchall())
        as_of, period_start = conn.execute("SELECT as_of_date, period_start FROM vw_parameters").fetchone()
    finally:
        conn.close()

    # --- the indicators, as calculated by the SQL reference queries (Phase 6)
    valid = [k for k in kpis["kpis"] if not k.error]
    rows = []
    for order, k in enumerate(valid, start=1):
        total = k.total
        symbol = "" if k.target is None else ("≥ " if k.direction == "HIGHER_IS_BETTER" else "≤ ")
        unit = {"%": " %", "days": " days", "count": "", "per 100 orders": ""}[k.unit]
        target_label = "—" if k.target is None else f"{symbol}{k.target:g}{unit}"
        rows.append([k.kpi_id, k.name, k.name_es, k.area, AREAS.index(k.area) + 1, order, k.kpi_type, k.unit,
                     k.direction, k.target, k.warning, target_label, total["value"], total["numerator"],
                     total["denominator"], status(k, total["value"])])
    schema["Dim_KPI"] = write_table(out_dir, "Dim_KPI", [
        "kpi_id", "kpi_name", "kpi_name_es", "area", "area_order", "kpi_order", "kpi_type", "unit", "direction",
        "target", "warning", "target_label", "sql_value", "sql_numerator", "sql_denominator", "sql_status"], rows)

    rows = []
    for k in valid:
        for r in k.months:
            year, month = map(int, r["period"].split("-"))
            month_end = (datetime(year + month // 12, month % 12 + 1, 1) - datetime.resolution).date().isoformat()
            rows.append([k.kpi_id, r["period"], month_end, r["numerator"], r["denominator"], r["value"],
                         status(k, r["value"])])
    schema["Fact_KPI_Monthly"] = write_table(out_dir, "Fact_KPI_Monthly", [
        "kpi_id", "period", "month_end", "numerator", "denominator", "value", "status"], rows)

    # --- the validation results (Phase 5)
    rules = validations["rules"]
    schema["Fact_ValidationResults"] = write_table(out_dir, "Fact_ValidationResults", [
        "rule_id", "rule_group", "title", "severity", "result", "findings"],
        [[r.rule_id, f"{r.rule_id[0]} · {GROUPS[r.rule_id[0]]}", r.title, r.severity, r.result, len(r.findings)]
         for r in rules])
    schema["Fact_ValidationFindings"] = write_table(out_dir, "Fact_ValidationFindings", [
        "rule_id", "severity", "record_ref", "detail"],
        [[r.rule_id, r.severity, f[0], f[1]] for r in rules for f in r.findings])

    reconciliation = validations["reconciliation"] or []
    schema["Model_Info"] = write_table(out_dir, "Model_Info", [
        "as_of_date", "period_start", "generated_at", "random_seed", "rules_executed", "rules_passed",
        "rules_with_warnings", "critical_failures", "planted_expected", "planted_detected", "data_quality_score",
        "quality_gate", "kpi_checks", "disclaimer"],
        [[as_of, period_start, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), settings.RANDOM_SEED,
          validations["n_rules"], validations["n_passed"], validations["n_warnings"],
          validations["n_critical_failures"], sum(r["expected"] for r in reconciliation),
          sum(r["detected"] for r in reconciliation), validations["data_quality_score"],
          "PASSED" if validations["gate_passed"] else "FAILED", "PASSED" if kpis["gate_passed"] else "FAILED",
          DISCLAIMER]])

    (out_dir / "_schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")
    return schema


def main() -> int:
    if not settings.DATABASE_PATH.exists():
        logger.error("Database not found. Run 'python scripts/run_pipeline.py' first.")
        return 1
    try:
        schema = export()
    except RuntimeError as error:
        logger.error("%s", error)
        return 1
    for name, info in schema.items():
        logger.info("  %-26s %6d rows  %2d columns", name, info["rows"], len(info["columns"]))
    logger.info("Power BI data written to %s (%d tables)",
                settings.POWERBI_DATA_DIR.relative_to(settings.PROJECT_ROOT), len(schema))
    logger.info("EXPORT OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
