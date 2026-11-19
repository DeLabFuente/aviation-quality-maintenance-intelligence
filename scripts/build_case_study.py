"""
AQMI — Case study: one non-conformity from detection to verified closure.

Writes documentation/case_study_nonconformity.md (in English, for the GitHub
portfolio) from the database, so that every date, name and figure in the case
study comes from the data and can be checked. The timeline is produced by the
same business query used in Phase 5 (sql/queries/01_nonconformity_full_history.sql).

The test suite rebuilds the case study and checks that the file in the
repository is identical, so the document can never drift away from the data.

How to run it (from the main project folder, with the virtual environment active):
    python scripts/build_case_study.py

Expected result:
    INFO    | Case study written: documentation/case_study_nonconformity.md (NC-2025-0021)
"""

import sqlite3
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings  # noqa: E402
from scripts.common import get_connection, setup_logging  # noqa: E402

logger = setup_logging("build_case_study")

OUTPUT = settings.PROJECT_ROOT / "documentation" / "case_study_nonconformity.md"
HISTORY_QUERY = settings.SQL_QUERIES_DIR / "01_nonconformity_full_history.sql"


def fmt(value: str | None) -> str:
    """ISO date (or date-time) -> 21 Mar 2025."""
    if not value:
        return "—"
    return date.fromisoformat(value[:10]).strftime("%d %b %Y")


def days(start: str, end: str) -> int:
    return (date.fromisoformat(end[:10]) - date.fromisoformat(start[:10])).days


def label(code: str | None) -> str:
    return code.replace("_", " ").capitalize() if code else "—"


def collect(conn: sqlite3.Connection) -> dict:
    conn.row_factory = sqlite3.Row
    timeline = [dict(r) for r in conn.execute(HISTORY_QUERY.read_text(encoding="utf-8"))]
    number = next(r["reference"] for r in timeline if r["item"] == "Non-conformity")
    nc = dict(conn.execute("""
        SELECT i.*, c.category_name_en, a.registration, a.fleet_number, m.mo_number, m.maintenance_type,
               d.document_code, d.title AS document_title, r.revision_code, dep.department_name,
               e1.first_name || ' ' || e1.last_name AS detected_by_name,
               e2.first_name || ' ' || e2.last_name AS owner_name
        FROM Quality_Incidents i
        JOIN Incident_Categories c USING (category_id)
        LEFT JOIN Aircraft a ON a.aircraft_id = i.aircraft_id
        LEFT JOIN Maintenance_Orders m ON m.mo_id = i.mo_id
        LEFT JOIN Document_Revisions r ON r.revision_id = i.revision_id
        LEFT JOIN Documents d ON d.document_id = r.document_id
        JOIN Departments dep ON dep.department_id = i.responsible_department_id
        JOIN Employees e1 ON e1.employee_id = i.detected_by
        JOIN Employees e2 ON e2.employee_id = i.owner_id
        WHERE i.incident_number = ?""", (number,)).fetchone())
    rca = [dict(r) for r in conn.execute("""
        SELECT r.*, e.first_name || ' ' || e.last_name AS analyst
        FROM Root_Cause_Analyses r JOIN Employees e ON e.employee_id = r.analyzed_by
        WHERE r.incident_id = ? ORDER BY r.analysis_date""", (nc["incident_id"],))]
    actions = [dict(r) for r in conn.execute("""
        SELECT a.*, e1.first_name || ' ' || e1.last_name AS responsible,
               e2.first_name || ' ' || e2.last_name AS verifier
        FROM CAPA_Actions a
        JOIN Employees e1 ON e1.employee_id = a.responsible_id
        LEFT JOIN Employees e2 ON e2.employee_id = a.verified_by
        WHERE a.incident_id = ? ORDER BY a.action_number""", (nc["incident_id"],))]
    # Effect of the measure: record checks made on each revision of the form
    effect = [dict(r) for r in conn.execute("""
        SELECT r.revision_code, r.effective_date, COUNT(*) AS checks,
               SUM(v.result <> 'CONFORM') AS discrepancies
        FROM Document_Verifications v
        JOIN Document_Revisions r USING (revision_id)
        WHERE r.document_id = (SELECT document_id FROM Document_Revisions WHERE revision_id = ?)
          AND v.verification_type = 'RECORD_VS_SOURCE'
        GROUP BY r.revision_code, r.effective_date ORDER BY r.revision_code""", (nc["revision_id"],))]
    return {"nc": nc, "rca": rca, "actions": actions, "timeline": timeline, "effect": effect}


def render(data: dict) -> str:
    nc, rca, actions, timeline, effect = data["nc"], data["rca"], data["actions"], data["timeline"], data["effect"]
    total_days = days(nc["detected_date"], nc["closed_date"])
    on_target = nc["closed_date"] <= nc["target_closure_date"]
    out = [
        f"# Case study — {nc['incident_number']}: from detection to verified closure", "",
        "> **Synthetic data.** AEROQ MRO is a fictitious company and every person, aircraft and record below is "
        "synthetic. This document is generated from the AQMI database by `scripts/build_case_study.py`; "
        "every date and figure can be checked with the queries indicated.", "",
        "This case follows one non-conformity through the whole quality cycle: detection, investigation, "
        "root-cause analysis, corrective action, effectiveness verification and formal closure. It also "
        "checks, with data, whether the action worked.", "",
        "## 1. The finding", "",
        "| Field | Value |", "|---|---|",
        f"| Non-conformity | **{nc['incident_number']}** — {nc['title']} |",
        f"| Category / severity / priority | {nc['category_name_en']} · {label(nc['severity'])} · {nc['priority']} |",
        f"| Detected | {fmt(nc['detected_date'])}, during a {label(nc['detection_source']).lower()}, "
        f"by {nc['detected_by_name']} |",
        f"| Related records | Aircraft {nc['registration']} ({nc['fleet_number']}) · maintenance order "
        f"{nc['mo_number']} ({label(nc['maintenance_type']).lower()}) · document {nc['document_code']} "
        f"{nc['revision_code']} ({nc['document_title']}) |",
        f"| Responsible department / owner | {nc['department_name']} · {nc['owner_name']} |",
        f"| Target closure date | {fmt(nc['target_closure_date'])} |", "",
        f"{nc['description']}", "",
        "## 2. Investigation and root cause", "",
    ]
    for r in rca:
        method = "Ishikawa (cause-and-effect) diagram" if r["method"] == "ISHIKAWA" else "5 Why analysis"
        out.append(f"- **Method:** {method}, by {r['analyst']} on {fmt(r['analysis_date'])}.")
        if r["ishikawa_category"]:
            out.append(f"- **Cause category:** {label(r['ishikawa_category'])} (the way the work is done, "
                       "not the people or the material)." if r["ishikawa_category"] == "METHOD"
                       else f"- **Cause category:** {label(r['ishikawa_category'])}.")
        whys = [r[f"why_{i}"] for i in range(1, 6) if r[f"why_{i}"]]
        for i, why in enumerate(whys, start=1):
            out.append(f"  {i}. Why? {why}")
        out.append(f"- **Root cause:** {r['root_cause_statement']}")
    out += ["", "## 3. Action plan", "",
            "| Action | Type | What | Responsible | Due | Completed |", "|---|---|---|---|---|---|"]
    for a in actions:
        out.append(f"| {a['action_number']} | {label(a['action_type'])} | **{a['title']}.** {a['description']} | "
                   f"{a['responsible']} | {fmt(a['due_date'])} | {fmt(a['completed_date'])} |")
    out += ["", "## 4. Effectiveness verification and closure", ""]
    for a in actions:
        if a["effectiveness_result"]:
            out.append(f"- {a['action_number']} was verified on {fmt(a['effectiveness_check_date'])} by "
                       f"{a['verifier']}: **{label(a['effectiveness_result'])}** — {a['effectiveness_comment']}")
    out += [f"- The non-conformity was closed on {fmt(nc['closed_date'])}: {nc['closure_summary']}",
            f"- From detection to closure: **{total_days} days**, "
            f"{'before' if on_target else 'after'} the target closure date ({fmt(nc['target_closure_date'])}).", "",
            "The action was closed only **after** an independent effectiveness check, and the non-conformity only "
            "after its action. The database enforces this order: its constraints reject closing an action "
            "without an effectiveness result, a check date and a verifier, and the verifier cannot be the person "
            "responsible for the action. Validation rules then check the dates of the whole cycle.", "",
            "## 5. Did it work? What the data shows", "",
            f"Record-versus-source checks of work order closure records, by revision of form {nc['document_code']}:", "",
            "| Form revision | In force from | Records checked | With discrepancies | Rate |", "|---|---|---|---|---|"]
    for e in effect:
        rate = 100.0 * e["discrepancies"] / e["checks"] if e["checks"] else 0.0
        out.append(f"| {e['revision_code']} | {fmt(e['effective_date'])} | {e['checks']} | "
                   f"{e['discrepancies']} | {rate:.1f} % |")
    out += ["", "The discrepancy rate fell by about two thirds after the redesigned form came into force. "
            "In this synthetic dataset the pattern was introduced on purpose, so that the dashboards have a "
            "documented cause and effect to show (see section 4 of the [Phase 4 document](05_fase4_datos_sinteticos.md), "
            "in Spanish). In a real organisation the same comparison is the evidence that the action was effective.", "",
            "## 6. Full audit trail", "",
            "The creation and every field change of the non-conformity and of its action come from `Audit_Log`, "
            "which database triggers write on every insert and update, so no change can bypass the log. The "
            "root-cause analysis and the progress updates come from their own tables.", "",
            "| When | Item | Reference | Event | Who |", "|---|---|---|---|---|"]
    for t in timeline:
        event = (t["event"] or "").replace("|", "/")
        out.append(f"| {t['moment'][:16]} | {t['item']} | {t['reference']} | {event} | {t['who'] or '—'} |")
    out += ["", "## 7. How to reproduce it", "",
            "- **SQL:** run [`sql/queries/01_nonconformity_full_history.sql`](../sql/queries/01_nonconformity_full_history.sql) "
            "on `database/aqmi.db` (for example in DB Browser for SQLite). Write another number in the first lines "
            "to follow any other non-conformity.",
            f"- **Power BI:** page *Audit & Traceability*: choose *Quality_Incidents* in the *Table* filter and "
            f"{nc['incident_number']} in the *Record* filter. The *Audit trail* table shows the history of the "
            "non-conformity record.",
            "- **Regenerate this document:** `python scripts/build_case_study.py`.", ""]
    return "\n".join(out)


def build(db_path: Path = settings.DATABASE_PATH, output: Path = OUTPUT) -> str:
    with get_connection(db_path) as conn:
        data = collect(conn)
    text = render(data)
    output.write_text(text, encoding="utf-8", newline="\n")
    return data["nc"]["incident_number"]


def main() -> int:
    if not settings.DATABASE_PATH.exists():
        logger.error("Database not found. Run scripts/run_pipeline.py first.")
        return 1
    number = build()
    logger.info(f"Case study written: {OUTPUT.relative_to(settings.PROJECT_ROOT).as_posix()} ({number})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
