"""Explicit local CP30 synthetic native-owner capture; never contacts external owners.

Requires an already reconstructed and reviewed CP30 source root. Running
historical Python executes trusted local code, not a sandboxed verifier.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from systems.workspace.native_owner_observation import observe_native_owners


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Observe CP30 native-local synthetic owner pins")
    ap.add_argument("--native-source-dir", type=Path, required=True)
    ap.add_argument("--audit", action="store_true", help="Explicitly run native two-pass selected-route audit")
    args = ap.parse_args(argv)
    source = args.native_source_dir.resolve(strict=True)
    # Only a trusted local operator should select and execute this CP30 source.
    sys.path.insert(0, str(source))
    from test_ab_chatbot_route_bound_task import RouteBoundTaskTests
    helper = RouteBoundTaskTests("runTest")
    refresh, *_ = helper.fixture()
    tasks = {
        "admitted": helper.task(refresh, "left", required_edges=[{"state":[1,0,0],"action":"B"}]),
        "unproved": helper.task(refresh, "left", required_edges=[{"state":[0,1,2],"action":"B"}]),
    }
    result = observe_native_owners(native_source_root=source,
                                  source_capture=lambda: tasks,
                                  allow_native_audit=args.audit)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
