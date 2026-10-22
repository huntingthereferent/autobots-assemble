"""Single-writer capacity -> qualification -> twin birth -> receipt controller.

Run from an authorized persistent host with two independently authenticated
accounts (source read token and destination gh login). No account creation, no
unbounded replication, no implicit transfer of native research claims.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from .digital_twin_factory import (
    SHA, _github_get, birth_decision, birth_twin, checked_repo, observe_account,
)


def _load_registry(path: Path) -> dict:
    if not path.exists():
        return {"schema": "digital-twin-registry/v1", "twins": []}
    item = json.loads(path.read_text(encoding="utf-8"))
    if (item.get("schema") != "digital-twin-registry/v1"
            or not isinstance(item.get("twins"), list)):
        raise ValueError("Unrecognized twin registry: refusing to overwrite")
    return item


def _save_registry(path: Path, registry: dict) -> None:
    # One controller writer only. A persistent host should enforce a process lock.
    path.parent.mkdir(parents=True, exist_ok=True)
    candidate = path.with_suffix(path.suffix + ".pending")
    if candidate.exists():
        raise FileExistsError("Pending registry update requires operator inspection")
    candidate.write_text(json.dumps(registry, sort_keys=True, indent=2) + "\n",
                         encoding="utf-8")
    candidate.replace(path)


def cycle(*, source: str, target: str, confirm: str, history: Path,
          registry_path: Path, source_token: str, cap: int = 20) -> dict:
    source_owner, _ = checked_repo(source)
    checked_repo(target)
    if target == source or confirm != target:
        raise PermissionError("Destination must be explicitly enrolled")
    if not source_token:
        raise PermissionError("FACTORY_SOURCE_TOKEN required")
    registry = _load_registry(registry_path)
    if any(entry.get("target") == target for entry in registry["twins"]):
        return {"state": "ALREADY_PROVISIONED", "target": target}
    # Until a first child is proven ready, another birth is not authorized.
    if any(entry.get("state") != "READY" for entry in registry["twins"]):
        return {"state": "BLOCKED_PENDING_TWIN_READINESS"}
    # A second child requires aggregate capacity measurement across all active
    # accounts. This first release explicitly refuses further births.
    if registry["twins"]:
        return {"state": "BLOCKED_AGGREGATE_CAPACITY_NOT_IMPLEMENTED"}
    history.parent.mkdir(parents=True, exist_ok=True)
    current = observe_account(source_owner, source_token, cap=cap)
    with history.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(current, sort_keys=True) + "\n")
    samples = [json.loads(line) for line in history.read_text(encoding="utf-8").splitlines()
               if line.strip()]
    decision = birth_decision(samples)
    if not decision["spawn"]:
        return {"state": "OBSERVING", "decision": decision, "observation": current}
    row = _github_get(f"/repos/{source}/commits/main", source_token)
    pin = row.get("sha")
    if not isinstance(pin, str) or not SHA.fullmatch(pin):
        raise ValueError("No verifiable source main SHA; refusing birth")
    receipt = birth_twin(source=source, target=target, source_sha=pin,
                         confirm=confirm)
    registry["twins"].append({
        "target": target, "parent": source, "source_main_sha": pin,
        "state": "PROVISIONED_ACTIONS_DISABLED", "receipt": receipt,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    _save_registry(registry_path, registry)
    return {"state": "TWIN_PROVISIONED", "target": target, "receipt": receipt}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one supervised factory cycle")
    parser.add_argument("--source", default="huntingthereferent/autobots-assemble")
    parser.add_argument("--target", default="aeren-research/autobots-assemble-twin-01")
    parser.add_argument("--confirm", required=True)
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--cap", type=int, default=20)
    args = parser.parse_args()
    result = cycle(source=args.source, target=args.target, confirm=args.confirm,
                   history=args.history, registry_path=args.registry,
                   source_token=os.environ.get("FACTORY_SOURCE_TOKEN", ""),
                   cap=args.cap)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
