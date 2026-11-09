"""SQLite connection handling and schema initialisation."""

import sqlite3

from .. import config


def get_connection() -> sqlite3.Connection:
    """Open a new SQLite connection."""
    return sqlite3.connect(config.DB_PATH)


def init_db() -> None:
    """Create the contacts table if it does not already exist."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                title TEXT,
                company TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                website TEXT,
                other_info TEXT,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                raw_email TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
