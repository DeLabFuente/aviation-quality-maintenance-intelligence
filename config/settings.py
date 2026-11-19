"""
AQMI — Project settings.

All paths and fixed parameters of the project live in this file, so that no
other script has to "guess" where things are. If you need to change the cut-off
date or the database location, change it here and only here.
"""

from pathlib import Path

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
# PROJECT_ROOT is the main project folder (the one that contains README.md).
# It is calculated from the location of this file, so the project works in
# any folder on any computer.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "aqmi.db"

SQL_SCHEMA_DIR = PROJECT_ROOT / "sql" / "schema"
SCHEMA_FILES = [
    "01_tables.sql",
    "02_indexes.sql",
    # 03_triggers.sql is generated automatically by scripts/trigger_builder.py
    "04_reference_data.sql",
]
GENERATED_TRIGGERS_FILE = SQL_SCHEMA_DIR / "03_triggers.sql"
SQL_VIEWS_DIR = PROJECT_ROOT / "sql" / "views"            # business views (Phase 5)
SQL_VALIDATION_DIR = PROJECT_ROOT / "sql" / "validation"  # one file per business rule (Phase 5)
SQL_QUERIES_DIR = PROJECT_ROOT / "sql" / "queries"        # example business queries (Phase 5)
SQL_KPI_DIR = PROJECT_ROOT / "sql" / "kpi"                # one reference query per KPI (Phase 6)
SQL_ANALYTICS_DIR = PROJECT_ROOT / "sql" / "analytics"    # star schema for Power BI (Phase 7)
POWERBI_DATA_DIR = PROJECT_ROOT / "data" / "processed"    # CSV files read by Power BI (Phase 7)
POWERBI_DIR = PROJECT_ROOT / "powerbi"                    # Power BI project (.pbip) (Phase 7)
REPORTS_DIR = PROJECT_ROOT / "reports"

LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "aqmi.log"

# -----------------------------------------------------------------------------
# Data parameters (decision D4, Phase 1)
# -----------------------------------------------------------------------------
PERIOD_START = "2024-11-01"   # first day of simulated activity
AS_OF_DATE = "2026-10-31"     # cut-off date: "overdue" and "expired" are measured against it
RANDOM_SEED = 145             # fixed seed: same seed => exactly the same synthetic data

SCHEMA_VERSION = "1.1.0"   # 1.1.0: Lessons_Learned table (Phase 9)

DATA_DISCLAIMER = (
    "AEROQ MRO is a fictitious company. All data in this database is synthetic "
    "and was generated for a portfolio project. It does not describe any real "
    "organisation, aircraft, person or approval."
)

# -----------------------------------------------------------------------------
# Technical requirements
# -----------------------------------------------------------------------------
# STRICT tables need SQLite 3.37.0 or later.
MIN_SQLITE_VERSION = (3, 37, 0)
