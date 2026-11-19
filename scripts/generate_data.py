"""
AQMI — Phase 4: generate the coherent synthetic data of AEROQ MRO.

What it does, in order:
    1. Rebuilds the empty database (same as scripts/build_database.py).
    2. Runs the simulation of 24 months of activity (01/11/2024 – 31/10/2026).
       Then, with a separate random generator, adds the lessons learned (Phase 9)
       without changing any record created by the simulation.
    3. Runs SQLite's integrity and foreign-key checks.
    4. Exports every table to data/synthetic/<table>.csv (UTF-8, readable in Excel).
    5. Writes data/synthetic/planted_discrepancies.csv: the small number of
       deliberate errors that the validations of Phase 5 must detect.
    6. Prints the number of records created in each table.

How to run it (from the main project folder, with the virtual environment active):
    python scripts/generate_data.py
"""

import csv
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings  # noqa: E402
from scripts.build_database import build_database  # noqa: E402
from scripts.common import get_connection, setup_logging  # noqa: E402
from scripts.generator.lessons import LessonsLearned  # noqa: E402
from scripts.generator.world import World  # noqa: E402

logger = setup_logging("generate_data")

SYNTHETIC_DIR = settings.PROJECT_ROOT / "data" / "synthetic"

TABLES = [
    "System_Parameters", "Departments", "Employees", "Customers", "Aircraft", "Suppliers",
    "Materials", "Documents", "Document_Revisions", "Maintenance_Orders",
    "Maintenance_Order_Materials", "Maintenance_Order_Documents", "Maintenance_Order_Holds",
    "Purchase_Orders", "Purchase_Order_Lines", "Incident_Categories", "Quality_Incidents",
    "Document_Verifications", "Root_Cause_Analyses", "CAPA_Actions", "CAPA_Progress_Updates",
    "Stock_Counts", "Inventory_Movements", "Lessons_Learned", "Audit_Log",
]


def generate(db_path: Path = settings.DATABASE_PATH, seed: int = settings.RANDOM_SEED,
             export_dir: Path | None = SYNTHETIC_DIR) -> dict:
    """Build the database, simulate the period and return the row counts and planted discrepancies."""
    build_database(db_path)
    conn = get_connection(db_path)
    try:
        started = time.perf_counter()
        world = World(conn, seed)
        world.build()
        world.run()
        conn.commit()
        logger.info("Simulation finished: %s events in %.1f s", world.engine.events_run,
                    time.perf_counter() - started)
        lessons = LessonsLearned(conn, seed).generate()     # Phase 9: after the simulation, own random generator
        conn.commit()
        logger.info("Lessons learned generated: %d", lessons)

        if conn.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("Integrity check failed")
        fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
        if fk_errors:
            raise RuntimeError(f"Foreign key errors: {fk_errors[:5]}")

        counts = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLES}
        if export_dir is not None:
            _export(conn, export_dir, world.planted)
    finally:
        conn.close()
    return {"counts": counts, "planted": world.planted}


def _export(conn, export_dir: Path, planted: list) -> None:
    export_dir.mkdir(parents=True, exist_ok=True)
    for table in TABLES:
        cursor = conn.execute(f"SELECT * FROM {table} ORDER BY 1")
        with open(export_dir / f"{table}.csv", "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow([column[0] for column in cursor.description])
            writer.writerows(cursor)
    with open(export_dir / "planted_discrepancies.csv", "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["kind", "table", "reference", "date", "description"])
        writer.writeheader()
        writer.writerows(planted)
    logger.info("CSV files written to %s", export_dir.relative_to(settings.PROJECT_ROOT))


def main() -> int:
    try:
        result = generate()
    except Exception as error:
        logger.exception("GENERATION FAILED: %s", error)
        return 1
    logger.info("Records per table:")
    for table, count in result["counts"].items():
        logger.info("  %-30s %7d", table, count)
    logger.info("Planted discrepancies (to be detected in Phase 5): %d", len(result["planted"]))
    logger.info("GENERATION OK -> %s", settings.DATABASE_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
