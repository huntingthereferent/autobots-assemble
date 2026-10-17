"""Registered bounded proposer for an observed factory-worker validation failure.

This is a real local subprocess that reads the original source + failed native
check and returns a candidate change. It is deterministic, not an AI model.
It neither writes files nor decides whether the change is accepted.
"""
from __future__ import annotations
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

BEFORE = "or not inputs['product']"
AFTER = "or not inputs['product'].strip()"


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("expected one explicit source file")
    source = Path(sys.argv[1])
    if source.name != "factory_machine_worker.py" or source.is_symlink() or not source.is_file():
        raise SystemExit("unsupported original worker source")
    observation = json.load(sys.stdin)
    if (set(observation) != {"exit_code", "stderr"}
            or observation["exit_code"] != 4
            or "BLANK_PRODUCT_ACCEPTED" not in observation["stderr"]):
        raise SystemExit("no independently observed blank-product failure")
    blob = source.read_bytes()
    if len(blob) > 25000:
        raise SystemExit("worker source budget exceeded")
    text = blob.decode("utf8")
    if text.count(BEFORE) != 1 or AFTER in text:
        raise SystemExit("expected source pattern missing or already repaired")
    print(json.dumps({
        "worker": "factory-blank-product-proposer/v1",
        "pid": os.getpid(),
        "target": source.name,
        "before": BEFORE,
        "after": AFTER,
        "source_sha256": sha256(blob).hexdigest(),
        "failure": "BLANK_PRODUCT_ACCEPTED",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
