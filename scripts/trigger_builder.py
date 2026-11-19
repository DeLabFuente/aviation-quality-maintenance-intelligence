"""
AQMI — Automatic generation of the control and audit triggers.

Why generate them instead of writing them by hand?
    The audit triggers must list every field of every table. Writing about
    100 triggers by hand would be repetitive and, worse, someone could add a
    field to a table and forget to audit it. Here the triggers are built from
    the real structure of the database, so they can never get out of sync.

The generated SQL is also saved to sql/schema/03_triggers.sql so that anyone
can read exactly what runs inside the database.

Triggers generated (rule codes from documentation/03_reglas_de_negocio.md):
    trg_<table>_no_delete     G09  No physical deletes on any table.
    trg_<table>_no_update     G08  Immutable tables: movements, progress updates, audit log.
    trg_<table>_update_guard  ---  Every update sets updated_at/updated_by, in chronological
                                   order, without touching the id or the creation data.
    trg_<table>_audit_insert  A01  Writes an INSERT event to Audit_Log.
    trg_<table>_audit_update  A02  Writes one UPDATE event per changed field to Audit_Log.
"""

import sqlite3

# Tables whose records can never be modified once written.
IMMUTABLE_TABLES = ("Inventory_Movements", "CAPA_Progress_Updates", "Audit_Log")

# Columns that are not audited field by field (they describe the change itself).
NOT_AUDITED_COLUMNS = {"created_at", "created_by", "updated_at", "updated_by"}

INDENT = "    "


def _list_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid"
    ).fetchall()
    return [row[0] for row in rows]


def _columns(conn: sqlite3.Connection, table: str) -> list[tuple[str, bool]]:
    """Return (column_name, is_primary_key) for every column of the table."""
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [(row[1], row[5] == 1) for row in rows]


def _no_delete(table: str) -> str:
    return (
        f"CREATE TRIGGER trg_{table.lower()}_no_delete\n"
        f"BEFORE DELETE ON {table}\n"
        f"BEGIN\n"
        f"{INDENT}SELECT RAISE(ABORT, 'AQMI G09: physical deletes are not allowed on {table}. "
        f"Cancel or deactivate the record instead.');\n"
        f"END;\n"
    )


def _no_update(table: str) -> str:
    return (
        f"CREATE TRIGGER trg_{table.lower()}_no_update\n"
        f"BEFORE UPDATE ON {table}\n"
        f"BEGIN\n"
        f"{INDENT}SELECT RAISE(ABORT, 'AQMI G08: {table} records cannot be modified. "
        f"Record a correcting entry instead.');\n"
        f"END;\n"
    )


def _update_guard(table: str, pk: str) -> str:
    return (
        f"CREATE TRIGGER trg_{table.lower()}_update_guard\n"
        f"BEFORE UPDATE ON {table}\n"
        f"WHEN NEW.updated_at IS NULL\n"
        f"  OR NEW.updated_by IS NULL\n"
        f"  OR NEW.updated_at < NEW.created_at\n"
        f"  OR (OLD.updated_at IS NOT NULL AND NEW.updated_at < OLD.updated_at)\n"
        f"  OR NEW.created_at IS NOT OLD.created_at\n"
        f"  OR NEW.created_by IS NOT OLD.created_by\n"
        f"  OR NEW.{pk} IS NOT OLD.{pk}\n"
        f"BEGIN\n"
        f"{INDENT}SELECT RAISE(ABORT, 'AQMI: every update of {table} must set updated_at and "
        f"updated_by in chronological order, and must not change the id or the creation data.');\n"
        f"END;\n"
    )


def _audit_insert(table: str, pk: str) -> str:
    return (
        f"CREATE TRIGGER trg_{table.lower()}_audit_insert\n"
        f"AFTER INSERT ON {table}\n"
        f"BEGIN\n"
        f"{INDENT}INSERT INTO Audit_Log (event_datetime, table_name, record_id, action, changed_by, source)\n"
        f"{INDENT}VALUES (NEW.created_at, '{table}', NEW.{pk}, 'INSERT', NEW.created_by, 'TRIGGER');\n"
        f"END;\n"
    )


def _audit_update(table: str, pk: str, fields: list[str]) -> str:
    statements = []
    for field in fields:
        statements.append(
            f"{INDENT}INSERT INTO Audit_Log (event_datetime, table_name, record_id, action,\n"
            f"{INDENT}                       field_name, old_value, new_value, changed_by, source)\n"
            f"{INDENT}SELECT NEW.updated_at, '{table}', NEW.{pk}, 'UPDATE', '{field}',\n"
            f"{INDENT}       CAST(OLD.{field} AS TEXT), CAST(NEW.{field} AS TEXT), NEW.updated_by, 'TRIGGER'\n"
            f"{INDENT}WHERE OLD.{field} IS NOT NEW.{field};\n"
        )
    return (
        f"CREATE TRIGGER trg_{table.lower()}_audit_update\n"
        f"AFTER UPDATE ON {table}\n"
        f"BEGIN\n" + "".join(statements) + "END;\n"
    )


def build_trigger_sql(conn: sqlite3.Connection) -> str:
    """Inspect the tables of the database and return the SQL of all triggers."""
    parts = [
        "-- =============================================================================\n"
        "-- AQMI — Aviation Quality & Maintenance Intelligence\n"
        "-- File:    sql/schema/03_triggers.sql\n"
        "-- GENERATED AUTOMATICALLY by scripts/trigger_builder.py — DO NOT EDIT BY HAND.\n"
        "-- It is rebuilt every time scripts/build_database.py runs.\n"
        "-- =============================================================================\n"
    ]

    for table in _list_tables(conn):
        columns = _columns(conn, table)
        names = [name for name, _ in columns]
        pk = next(name for name, is_pk in columns if is_pk)

        parts.append(f"\n-- ----------------------------------------------------------------------------\n"
                     f"-- {table}\n"
                     f"-- ----------------------------------------------------------------------------\n")
        parts.append(_no_delete(table))

        if table in IMMUTABLE_TABLES:
            parts.append(_no_update(table))

        is_audited = "created_at" in names and "created_by" in names
        if is_audited:
            parts.append(_audit_insert(table, pk))

        if is_audited and "updated_at" in names and table not in IMMUTABLE_TABLES:
            audited_fields = [n for n in names if n not in NOT_AUDITED_COLUMNS and n != pk]
            parts.append(_update_guard(table, pk))
            parts.append(_audit_update(table, pk, audited_fields))

    return "\n".join(parts)
