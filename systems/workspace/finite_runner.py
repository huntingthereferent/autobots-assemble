"""Fixed invocation of an explicitly selected Correspondence Process edition.

A separate Python process executes trusted local edition source. This is NOT
an operating-system sandbox. Only run editions whose code has been reviewed.
"""
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
from typing import Any

# The child imports original finite sources from the selected private edition.
# Do not insert host-repository paths or fall back to installed worker versions.
_CHILD = r'''
import json, os, sys
from pathlib import Path
edition=Path(sys.argv[1]).resolve(strict=True)
sys.path.insert(0,str(edition))
from finite_goal_priority import Law
from finite_required_edge_guard import preflight
payload=json.load(sys.stdin)
old,new=Law(tuple(payload['old_phi'])),Law(tuple(payload['new_phi']))
req=(tuple(payload['required_state']),payload['required_action'])
results=[preflight(old,new,tuple(words),req) for words in payload['candidate_words']]
print(json.dumps({'verdicts':results,'child_pid':os.getpid()}))
'''


def run_edition(edition: Path, inputs: dict[str, Any], *, timeout: int = 10) -> dict[str, Any]:
    if not edition.is_dir() or edition.is_symlink():
        raise ValueError("edition is not an ordinary directory")
    try:
        out = subprocess.run([sys.executable, "-I", "-c", _CHILD, str(edition)],
                             input=json.dumps(inputs, sort_keys=True), text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=edition, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("bounded worker process timed out") from exc
    if out.returncode:
        raise RuntimeError(f"worker process exited nonzero ({out.returncode}); no result admitted")
    if len(out.stdout) > 16384:
        raise ValueError("worker produced oversized output")
    try:
        row = json.loads(out.stdout)
    except ValueError as exc:
        raise ValueError("worker returned invalid JSON") from exc
    if not isinstance(row, dict) or set(row) != {"verdicts", "child_pid"} or not isinstance(row["verdicts"], list) or type(row["child_pid"]) is not int:
        raise ValueError("worker returned unexpected result")
    return row
