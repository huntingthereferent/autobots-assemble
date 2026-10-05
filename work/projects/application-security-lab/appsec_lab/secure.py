from __future__ import annotations

import sqlite3


def lookup_user(
    connection: sqlite3.Connection,
    username: str,
) -> list[dict[str, object]]:
    """Lookup a user while preserving the SQL code/data boundary."""
    rows = connection.execute(
        "SELECT id, username, role FROM users WHERE username = ?",
        (username,),
    ).fetchall()
    return [dict(row) for row in rows]
