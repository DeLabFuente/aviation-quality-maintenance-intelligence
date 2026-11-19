"""
AQMI — Phase 5: run the 82 business-rule validations (the quality gate).

What it does:
    1. Reads every rule in sql/validation/ (one file per rule; the header of
       each file gives its id, title and severity).
    2. Runs each query against the database. A query returns one row per record
       that breaks the rule.
    3. Reconciles the WARNING findings with the discrepancies planted on purpose
       by the generator (data/synthetic/planted_discrepancies.csv): every planted
       discrepancy must be detected, and nothing else must appear in those rules.
    4. Writes three reports in reports/:
         validation_report.md     readable summary
         validation_results.csv   one row per rule
         validation_findings.csv  one row per record found
    5. QUALITY GATE: returns an error code if any CRITICAL rule fails, if any rule
       cannot run, or if the planted discrepancies are not detected exactly.

How to run it (from the main project folder, with the virtual environment active):
    python scripts/run_validations.py
"""

import csv
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings  # noqa: E402
from scripts.common import get_connection, setup_logging  # noqa: E402

logger = setup_logging("run_validations")

PLANTED_FILE = settings.PROJECT_ROOT / "data" / "synthetic" / "planted_discrepancies.csv"
# Which rule must detect each kind of planted discrepancy
PLANTED_RULE = {
    "OBSOLETE_REVISION_LINK": "M09",
    "RECEIPT_WITHOUT_CERTIFICATE": "I09",
    "FALSE_MATERIAL_HOLD": "M08",
    "INCIDENT_WITHOUT_LINKS": "Q08",
}
GROUPS = {"G": "General", "D": "Document control", "M": "Maintenance orders", "I": "Materials & inventory",
          "Q": "Non-conformities", "C": "CAPA", "A": "Audit & traceability"}
HEADER = re.compile(r"^-- (\w+): (.*)$")


@dataclass
class Rule:
    rule_id: str
    title: str
    severity: str
    rule_type: str
    enforced_by: str
    sql: str
    path: Path
    findings: list = field(default_factory=list)
    error: str | None = None
    seconds: float = 0.0

    @property
    def result(self) -> str:
        if self.error:
            return "ERROR"
        if not self.findings:
            return "PASS"
        return "FAIL" if self.severity == "CRITICAL" else "WARNING"


def load_rules(directory: Path = settings.SQL_VALIDATION_DIR) -> list[Rule]:
    """Read every rule file and its metadata header."""
    rules = []
    for path in sorted(directory.glob("*.sql")):
        text = path.read_text(encoding="utf-8")
        meta = {}
        for line in text.splitlines():
            match = HEADER.match(line)
            if not match:
                break
            meta[match.group(1)] = match.group(2).strip()
        missing = {"rule", "title", "severity"} - meta.keys()
        if missing:
            raise ValueError(f"{path.name}: header without {sorted(missing)}")
        if meta["severity"] not in ("CRITICAL", "WARNING"):
            raise ValueError(f"{path.name}: unknown severity {meta['severity']}")
        rules.append(Rule(meta["rule"], meta["title"], meta["severity"], meta.get("type", ""),
                          meta.get("enforced_by", ""), text, path))
    ids = [r.rule_id for r in rules]
    duplicated = {i for i in ids if ids.count(i) > 1}
    if duplicated:
        raise ValueError(f"Duplicated rule ids: {sorted(duplicated)}")
    return rules


def load_planted(path: Path = PLANTED_FILE) -> list[dict] | None:
    if not path.exists():
        return None
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def reconcile(rules: list[Rule], planted: list[dict]) -> list[dict]:
    """Compare what the rules found with what the generator planted."""
    by_id = {r.rule_id: r for r in rules}
    rows = []
    for kind, rule_id in PLANTED_RULE.items():
        expected = {p["reference"] for p in planted if p["kind"] == kind}
        found = {f[0] for f in by_id[rule_id].findings}
        rows.append({
            "kind": kind, "rule": rule_id, "expected": len(expected),
            "detected": len(expected & found), "missed": sorted(expected - found),
            "unexpected": sorted(found - expected),
        })
    return rows


def run_validations(db_path: Path = settings.DATABASE_PATH, report_dir: Path | None = settings.REPORTS_DIR,
                    planted: list[dict] | None = None) -> dict:
    """Run every rule. Returns a summary dictionary (see the keys at the end)."""
    rules = load_rules()
    if planted is None:
        planted = load_planted()
    started = time.perf_counter()
    conn = get_connection(db_path)
    try:
        as_of = conn.execute("SELECT parameter_value FROM System_Parameters WHERE parameter_key = 'AS_OF_DATE'").fetchone()[0]
        for rule in rules:
            t0 = time.perf_counter()
            try:
                rule.findings = [tuple(row) for row in conn.execute(rule.sql).fetchall()]
            except Exception as error:  # a rule that cannot run is a failure of the control itself
                rule.error = str(error)
                logger.error("Rule %s could not run: %s", rule.rule_id, error)
            rule.seconds = time.perf_counter() - t0
    finally:
        conn.close()

    reconciliation = reconcile(rules, planted) if planted is not None else None
    reconciliation_ok = reconciliation is None or all(not r["missed"] and not r["unexpected"] for r in reconciliation)
    critical_failures = [r for r in rules if r.result == "FAIL"]
    errors = [r for r in rules if r.result == "ERROR"]
    passed = [r for r in rules if r.result == "PASS"]
    summary = {
        "as_of": as_of,
        "rules": rules,
        "n_rules": len(rules),
        "n_passed": len(passed),
        "n_warnings": sum(r.result == "WARNING" for r in rules),
        "n_critical_failures": len(critical_failures),
        "n_errors": len(errors),
        "n_findings": sum(len(r.findings) for r in rules),
        "data_quality_score": round(100 * len(passed) / len(rules), 1),
        "reconciliation": reconciliation,
        "reconciliation_ok": reconciliation_ok,
        "gate_passed": not critical_failures and not errors and reconciliation_ok,
        "seconds": round(time.perf_counter() - started, 2),
    }
    if report_dir is not None:
        _write_reports(summary, db_path, report_dir)
    return summary


# ------------------------------------------------------------------ reports
def _write_reports(summary: dict, db_path: Path, report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    rules = summary["rules"]
    with open(report_dir / "validation_results.csv", "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["rule_id", "group", "title", "severity", "type", "enforced_by", "result", "findings", "error"])
        for r in rules:
            writer.writerow([r.rule_id, GROUPS[r.rule_id[0]], r.title, r.severity, r.rule_type, r.enforced_by,
                             r.result, len(r.findings), r.error or ""])
    with open(report_dir / "validation_findings.csv", "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["rule_id", "severity", "record_ref", "detail"])
        for r in rules:
            for record_ref, detail in r.findings:
                writer.writerow([r.rule_id, r.severity, record_ref, detail])
    (report_dir / "validation_report.md").write_text(_markdown(summary, db_path), encoding="utf-8")


def _markdown(s: dict, db_path: Path) -> str:
    rules = s["rules"]
    gate = "✅ PASSED" if s["gate_passed"] else "❌ FAILED"
    lines = [
        "# AQMI — Data Validation Report", "",
        "> Generated automatically by `scripts/run_validations.py`. AEROQ MRO is fictitious and all data is synthetic.", "",
        "| Item | Value |", "|---|---|",
        f"| Database | `{db_path.name}` |",
        f"| Data cut-off date | {s['as_of']} |",
        f"| Validation run | {datetime.now():%Y-%m-%d %H:%M} |",
        f"| Rules executed | {s['n_rules']} |",
        f"| **Quality gate** | **{gate}** |",
        f"| Critical failures | {s['n_critical_failures']} |",
        f"| Rules that could not run | {s['n_errors']} |",
        f"| Rules with warnings | {s['n_warnings']} |",
        f"| Records flagged | {s['n_findings']} |",
        f"| Data Quality Score (rules passed / rules executed) | {s['data_quality_score']} % |",
        "",
        "The quality gate passes when no CRITICAL rule fails, every rule runs, and the planted",
        "discrepancies are detected exactly. WARNING findings do not block the gate: they are",
        "the discrepancies a quality office must review.", "",
        "## Results by group", "",
        "| Group | Rules | Passed | Warnings | Critical failures |", "|---|---|---|---|---|",
    ]
    for prefix, name in GROUPS.items():
        group = [r for r in rules if r.rule_id.startswith(prefix)]
        lines.append(f"| {prefix} — {name} | {len(group)} | {sum(r.result == 'PASS' for r in group)} | "
                     f"{sum(r.result == 'WARNING' for r in group)} | {sum(r.result in ('FAIL', 'ERROR') for r in group)} |")

    lines += ["", "## Planted discrepancies", ""]
    if s["reconciliation"] is None:
        lines.append("No planted-discrepancy file was available for this run.")
    else:
        lines += ["The generator planted these discrepancies on purpose. The controls must find all of them, and nothing else.", "",
                  "| Kind | Rule | Planted | Detected | Missed | Unexpected | Result |", "|---|---|---|---|---|---|---|"]
        for row in s["reconciliation"]:
            ok = not row["missed"] and not row["unexpected"]
            lines.append(f"| {row['kind']} | {row['rule']} | {row['expected']} | {row['detected']} | "
                         f"{', '.join(row['missed']) or '—'} | {', '.join(row['unexpected']) or '—'} | {'✅' if ok else '❌'} |")

    lines += ["", "## Findings", ""]
    flagged = [r for r in rules if r.findings or r.error]
    if not flagged:
        lines.append("No findings.")
    for r in flagged:
        lines += [f"### {r.rule_id} — {r.title}", "",
                  f"Severity **{r.severity}** · Result **{r.result}** · {len(r.findings)} record(s)", ""]
        if r.error:
            lines += [f"Error: `{r.error}`", ""]
            continue
        lines += ["| Record | Detail |", "|---|---|"]
        for record_ref, detail in r.findings[:20]:
            lines.append(f"| {record_ref} | {detail} |")
        if len(r.findings) > 20:
            lines.append(f"| … | {len(r.findings) - 20} more in validation_findings.csv |")
        lines.append("")

    lines += ["## All rules", "", "| Rule | Title | Severity | Result | Records |", "|---|---|---|---|---|"]
    for r in rules:
        lines.append(f"| {r.rule_id} | {r.title} | {r.severity} | {r.result} | {len(r.findings)} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    if not settings.DATABASE_PATH.exists():
        logger.error("Database not found. Run 'python scripts/generate_data.py' first.")
        return 1
    s = run_validations()
    for r in s["rules"]:
        if r.findings or r.error:
            level = logger.error if r.result in ("FAIL", "ERROR") else logger.warning
            level("%s %-8s %-55s %d record(s)", r.rule_id, r.result, r.title[:55], len(r.findings))
    logger.info("Rules: %d | passed: %d | warnings: %d | critical failures: %d | errors: %d | %.2f s",
                s["n_rules"], s["n_passed"], s["n_warnings"], s["n_critical_failures"], s["n_errors"], s["seconds"])
    if s["reconciliation"] is not None:
        detected = sum(r["detected"] for r in s["reconciliation"])
        expected = sum(r["expected"] for r in s["reconciliation"])
        logger.info("Planted discrepancies detected: %d of %d (%s)", detected, expected,
                    "exact match" if s["reconciliation_ok"] else "MISMATCH")
    logger.info("Data Quality Score: %s %%", s["data_quality_score"])
    logger.info("Reports written to %s", settings.REPORTS_DIR.relative_to(settings.PROJECT_ROOT))
    if s["gate_passed"]:
        logger.info("QUALITY GATE PASSED")
        return 0
    logger.error("QUALITY GATE FAILED — data must not be exported to Power BI")
    return 1


if __name__ == "__main__":
    sys.exit(main())
