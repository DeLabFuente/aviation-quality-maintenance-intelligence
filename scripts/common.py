"""
AQMI — Shared helpers used by every script.

* setup_logging():   writes messages to the screen and to logs/aqmi.log
* get_connection():  opens the database with foreign keys switched ON
* check_sqlite_version(): stops early if SQLite is too old for STRICT tables
"""

import logging
import sqlite3
from pathlib import Path

from config import settings


def setup_logging(name: str = "aqmi") -> logging.Logger:
    """Return a logger that writes to the console and to logs/aqmi.log."""
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:          # already configured (e.g. when called twice)
        return logger

    logger.setLevel(logging.INFO)
    file_format = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
    console_format = logging.Formatter("%(levelname)-7s | %(message)s")

    file_handler = logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    return logger


def get_connection(db_path: Path = settings.DATABASE_PATH) -> sqlite3.Connection:
    """
    Open the SQLite database and switch foreign-key checking ON.

    IMPORTANT: SQLite does NOT check foreign keys unless this PRAGMA is run
    on every new connection. Always open the database through this function.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def check_sqlite_version() -> None:
    """Raise an error if the SQLite library is older than the project needs."""
    current = tuple(int(part) for part in sqlite3.sqlite_version.split("."))
    if current < settings.MIN_SQLITE_VERSION:
        required = ".".join(str(n) for n in settings.MIN_SQLITE_VERSION)
        raise RuntimeError(
            f"SQLite {sqlite3.sqlite_version} is too old. AQMI needs SQLite {required} "
            f"or later (for STRICT tables). Please install a recent Python version."
        )
