from __future__ import annotations

import sqlite3


SCHEMA = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL
);
"""


def build_fixture() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    connection.executemany(
        "INSERT INTO users (id, username, role) VALUES (?, ?, ?)",
        [
            (1, "alice", "user"),
            (2, "bob", "user"),
            (3, "admin", "admin"),
        ],
    )
    connection.commit()
    return connection
