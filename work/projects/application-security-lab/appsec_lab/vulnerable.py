from __future__ import annotations

import sqlite3


def lookup_user_vulnerable(
    connection: sqlite3.Connection,
    username: str,
) -> list[dict[str, object]]:
    """Intentionally vulnerable local-only fixture.

    Untrusted input is interpolated into SQL text. This file exists only to
    preserve the before-state for the controlled security regression witness.
    """
    query = f"SELECT id, username, role FROM users WHERE username = '{username}'"
    rows = connection.execute(query).fetchall()
    return [dict(row) for row in rows]
