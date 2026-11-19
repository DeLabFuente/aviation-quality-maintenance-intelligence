"""
AQMI — Phase 3: build the operational database.

What it does, in order:
    1. Checks that the installed SQLite supports STRICT tables.
    2. Deletes the previous database/aqmi.db, if it exists (it is always rebuilt
       from the SQL files, so nothing is lost).
    3. Creates the 25 tables          (sql/schema/01_tables.sql)
    4. Creates the indexes            (sql/schema/02_indexes.sql)
    5. Generates and creates triggers (sql/schema/03_triggers.sql)
    6. Loads the reference catalogues (sql/schema/04_reference_data.sql)
    7. Writes the system parameters   (cut-off date, seed... from config/settings.py)
    8. Creates the business views     (sql/views/*.sql, in file-name order)
    9. Runs SQLite's own integrity checks and prints a summary.

How to run it (from the main project folder, with the virtual environment active):
    python scripts/build_database.py
"""

import sys
from pathlib import Path

# Make the main project folder importable (so that "config" and "scripts" are found).
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import sqlite3  # noqa: E402

from config import settings  # noqa: E402
from scripts.common import check_sqlite_version, get_connection, setup_logging  # noqa: E402
from scripts.trigger_builder import build_trigger_sql  # noqa: E402

logger = setup_logging("build_database")


def _run_sql_file(conn: sqlite3.Connection, file_name: str) -> None:
    path = settings.SQL_SCHEMA_DIR / file_name
    logger.info("Running %s", path.relative_to(settings.PROJECT_ROOT))
    conn.executescript(path.read_text(encoding="utf-8"))


def _write_system_parameters(conn: sqlite3.Connection) -> None:
    parameters = [
        ("AS_OF_DATE", settings.AS_OF_DATE,
         "Cut-off date. 'Overdue', 'expired' and 'open' are measured against this date."),
        ("PERIOD_START", settings.PERIOD_START, "First day of simulated activity."),
        ("RANDOM_SEED", str(settings.RANDOM_SEED), "Seed of the synthetic data generator."),
        ("SCHEMA_VERSION", settings.SCHEMA_VERSION, "Version of the database structure."),
        ("DATA_DISCLAIMER", settings.DATA_DISCLAIMER, "Synthetic data notice."),
    ]
    conn.executemany(
        "INSERT INTO System_Parameters (parameter_key, parameter_value, description) VALUES (?, ?, ?)",
        parameters,
    )
    logger.info("System parameters written (AS_OF_DATE = %s)", settings.AS_OF_DATE)


def _summary(conn: sqlite3.Connection) -> dict:
    def count(kind: str) -> int:
        return conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type = ? AND name NOT LIKE 'sqlite_%'", (kind,)
        ).fetchone()[0]

    return {
        "tables": count("table"),
        "indexes": count("index"),
        "triggers": count("trigger"),
        "views": count("view"),
        "departments": conn.execute("SELECT COUNT(*) FROM Departments").fetchone()[0],
        "incident_categories": conn.execute("SELECT COUNT(*) FROM Incident_Categories").fetchone()[0],
        "system_parameters": conn.execute("SELECT COUNT(*) FROM System_Parameters").fetchone()[0],
    }


def build_database(db_path: Path = settings.DATABASE_PATH) -> dict:
    """Build the database at db_path and return a summary dictionary."""
    check_sqlite_version()
    logger.info("SQLite version %s", sqlite3.sqlite_version)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        logger.info("Removing previous database %s", db_path.name)
        db_path.unlink()

    conn = get_connection(db_path)
    try:
        _run_sql_file(conn, "01_tables.sql")
        _run_sql_file(conn, "02_indexes.sql")

        trigger_sql = build_trigger_sql(conn)
        settings.GENERATED_TRIGGERS_FILE.write_text(trigger_sql, encoding="utf-8")
        logger.info("Generated %s", settings.GENERATED_TRIGGERS_FILE.relative_to(settings.PROJECT_ROOT))
        conn.executescript(trigger_sql)

        _run_sql_file(conn, "04_reference_data.sql")
        _write_system_parameters(conn)
        for view_file in sorted(settings.SQL_VIEWS_DIR.glob("*.sql")):
            logger.info("Running %s", view_file.relative_to(settings.PROJECT_ROOT))
            conn.executescript(view_file.read_text(encoding="utf-8"))
        conn.commit()

        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
        if integrity != "ok" or fk_errors:
            raise RuntimeError(f"Integrity check failed: {integrity}; foreign key errors: {fk_errors}")

        summary = _summary(conn)
    finally:
        conn.close()

    logger.info("Integrity check: ok | Foreign key check: ok")
    logger.info(
        "Database built: %(tables)s tables, %(indexes)s indexes, %(triggers)s triggers, %(views)s views, "
        "%(departments)s departments, %(incident_categories)s incident categories, "
        "%(system_parameters)s system parameters",
        summary,
    )
    return summary


def main() -> int:
    try:
        build_database()
    except Exception as error:  # show a clear message instead of a long traceback
        logger.error("BUILD FAILED: %s", error)
        return 1
    logger.info("BUILD OK -> %s", settings.DATABASE_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
