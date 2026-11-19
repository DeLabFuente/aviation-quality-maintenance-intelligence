"""
AQMI — Simulation engine.

The generator is a small "discrete-event simulation": every fact of the
company (an order is opened, a part is received, an action is closed...) is an
event with a date and time. Events are kept in a queue and executed strictly
in chronological order. Because of that:

  * stock is always calculated at the right moment (no negative stock),
  * every update happens after the previous one (the audit triggers require it),
  * the audit trail that the triggers write looks exactly like a real one.
"""

import heapq
import itertools
from collections import defaultdict
from datetime import date, datetime, time, timedelta

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def fmt_dt(value: datetime) -> str:
    return value.strftime(DATETIME_FORMAT)


def fmt_d(value) -> str:
    return value.strftime("%Y-%m-%d")


def parse_d(text: str) -> date:
    return datetime.strptime(text, "%Y-%m-%d").date()


def is_workday(day: date) -> bool:
    return day.weekday() < 5


def next_workday(day: date) -> date:
    while not is_workday(day):
        day += timedelta(days=1)
    return day


def add_workdays(day: date, n: int) -> date:
    """Add n working days (Monday–Friday) to a date."""
    current = day
    step = 1 if n >= 0 else -1
    remaining = abs(n)
    while remaining > 0:
        current += timedelta(days=step)
        if is_workday(current):
            remaining -= 1
    return current


class Engine:
    """Clock, event queue, numbering and database write helpers."""

    def __init__(self, conn, rng, start: date, end: date):
        self.conn = conn
        self.rng = rng
        self.start = datetime.combine(start, time(0, 0))
        self.end = datetime.combine(end, time(23, 59, 59))
        self.now = self.start
        self._queue: list = []
        self._seq = itertools.count()
        self._numbers: dict = defaultdict(int)
        self.events_run = 0

    # -- time helpers ---------------------------------------------------------
    @property
    def today(self) -> date:
        return self.now.date()

    def at(self, day: date, hour: int, minute: int = 0) -> datetime:
        return datetime.combine(day, time(hour, minute))

    def work_time(self, day: date, first_hour: int = 8, last_hour: int = 16) -> datetime:
        """A random time during working hours on the given day."""
        return self.at(day, self.rng.randint(first_hour, last_hour), self.rng.randint(0, 59))

    def later_today(self, minutes_min: int = 5, minutes_max: int = 90) -> datetime:
        """A moment a few minutes after 'now' (never earlier)."""
        return self.now + timedelta(minutes=self.rng.randint(minutes_min, minutes_max))

    # -- event queue ------------------------------------------------------------
    def schedule(self, when: datetime, action, *args) -> None:
        """Queue an action. Events in the past run 'now'; events after the cut-off never run."""
        if when < self.now:
            when = self.now
        if when <= self.end:
            heapq.heappush(self._queue, (when, next(self._seq), action, args))

    def run(self) -> None:
        while self._queue:
            when, _, action, args = heapq.heappop(self._queue)
            self.now = when
            action(*args)
            self.events_run += 1

    # -- numbering --------------------------------------------------------------
    def next_number(self, prefix: str, year: int, width: int = 4) -> str:
        self._numbers[(prefix, year)] += 1
        return f"{prefix}-{year}-{self._numbers[(prefix, year)]:0{width}d}"

    # -- database helpers -------------------------------------------------------
    def insert(self, table: str, values: dict) -> int:
        columns = ", ".join(values)
        placeholders = ", ".join("?" for _ in values)
        cursor = self.conn.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", tuple(values.values()))
        return cursor.lastrowid

    def update(self, table: str, pk_column: str, pk_value: int, actor: int, values: dict) -> None:
        """Update a record, stamping updated_at = now and updated_by = actor."""
        values = dict(values, updated_at=fmt_dt(self.now), updated_by=actor)
        assignments = ", ".join(f"{column} = ?" for column in values)
        self.conn.execute(f"UPDATE {table} SET {assignments} WHERE {pk_column} = ?",
                          (*values.values(), pk_value))
