"""SQLite data layer for Spendly.

Provides a small, dependency-free wrapper over the standard library's
``sqlite3`` module. Foreign keys are enabled on every connection, and
all queries are parameterized.
"""

import os
import sqlite3
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash


# Project root = parent of the ``database`` package directory.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "spendly.db")


def get_db() -> sqlite3.Connection:
    """Open a SQLite connection to ``spendly.db`` with sensible defaults.

    - ``row_factory = sqlite3.Row`` so rows can be accessed like dicts.
    - ``PRAGMA foreign_keys = ON`` so FK constraints are enforced.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create the ``users`` and ``expenses`` tables if they don't exist.

    Safe to call multiple times — uses ``CREATE TABLE IF NOT EXISTS``.
    """
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db() -> None:
    """Insert a demo user and sample expenses for development.

    Idempotent: if the ``users`` table is non-empty, this is a no-op.
    """
    conn = get_db()
    try:
        existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing:
            return

        password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash),
        )
        user_id = cursor.lastrowid

        # 8 sample expenses spread across the current month, covering all 7
        # fixed categories (Food appears twice).
        today = datetime.now().date()
        samples = [
            (350, "Food", -1, "Lunch at office canteen"),
            (120, "Transport", -2, "Auto to client meeting"),
            (2400, "Bills", -5, "Electricity bill"),
            (550, "Health", -7, "Pharmacy restock"),
            (799, "Entertainment", -9, "Movie tickets"),
            (1299, "Shopping", -12, "New running shoes"),
            (200, "Other", -15, "Misc household items"),
            (180, "Food", -18, "Groceries"),
        ]
        for amount, category, day_offset, description in samples:
            date_str = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            conn.execute(
                """
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, amount, category, date_str, description),
            )

        conn.commit()
    finally:
        conn.close()