from __future__ import annotations

import json
from pathlib import Path

from .db import build_fixture
from .secure import lookup_user
from .vulnerable import lookup_user_vulnerable


CONTROLLED_INPUT = "' OR 1=1 --"


def build_report() -> dict:
    vulnerable_db = build_fixture()
    vulnerable_rows = lookup_user_vulnerable(vulnerable_db, CONTROLLED_INPUT)

    secure_db = build_fixture()
    secure_rows = lookup_user(secure_db, CONTROLLED_INPUT)

    normal_db = build_fixture()
    normal_rows = lookup_user(normal_db, "alice")

    return {
        "finding": {
            "class": "SQL injection",
            "category": "OWASP Injection",
            "scope": "owned local SQLite fixture",
            "trust_boundary": "untrusted username input -> SQL query",
        },
        "before": {
            "implementation": "string interpolation",
            "controlled_input": CONTROLLED_INPUT,
            "rows_returned": len(vulnerable_rows),
            "vulnerable": len(vulnerable_rows) > 1,
        },
        "remediation": {
            "control": "parameterized SQL",
            "implementation": "placeholder + bound parameter",
        },
        "after": {
            "controlled_input_rows_returned": len(secure_rows),
            "normal_lookup_rows_returned": len(normal_rows),
            "normal_lookup_username": normal_rows[0]["username"] if normal_rows else None,
            "regression_blocked": len(secure_rows) == 0 and len(normal_rows) == 1,
        },
    }


def write_report(path: str | Path) -> dict:
    report = build_report()
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
