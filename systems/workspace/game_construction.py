"""Game Construction Adapter v0: source-owned tiny game + replayable evidence.

One explicitly invoked local witness, not an AI scheduler or a mathematical A/B model.
No network access; no implicit Workstation task admission.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

VERSION = "game-construction-v0"
ACTIONS = frozenset({"up", "down", "left", "right", "interact"})


def canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(data: Any) -> str:
    return sha256(canonical(data).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class GameSpec:
    width: int = 4
    height: int = 3
    start: tuple[int, int] = (0, 1)
    target: tuple[int, int] = (2, 1)

    def validate(self) -> None:
        if isinstance(self.width, bool) or isinstance(self.height, bool) or not isinstance(self.width, int) or not isinstance(self.height, int):
            raise ValueError("dimensions must be integers")
        if not (1 <= self.width <= 64 and 1 <= self.height <= 64):
            raise ValueError("dimensions must be in 1..64")
        for label, xy in (("start", self.start), ("target", self.target)):
            if not isinstance(xy, tuple) or len(xy) != 2 or any(isinstance(v, bool) or not isinstance(v, int) for v in xy):
                raise ValueError(f"{label} must be an integer pair")
            if not (0 <= xy[0] < self.width and 0 <= xy[1] < self.height):
                raise ValueError(f"{label} outside the world")
        if self.start == self.target:
            raise ValueError("player cannot start on the target")


@dataclass(frozen=True)
class GameState:
    x: int
    y: int
    collected: bool = False
    turns: int = 0


def first_state(spec: GameSpec) -> GameState:
    spec.validate()
    return GameState(*spec.start)


def transition(spec: GameSpec, state: GameState, action: str) -> tuple[GameState, str]:
    """One bounded, deterministic transition; blocked moves are witnessed too."""
    spec.validate()
    if action not in ACTIONS:
        raise ValueError("unknown action")
    dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0), "interact": (0, 0)}[action]
    if action == "interact":
        adjacent = abs(spec.target[0] - state.x) + abs(spec.target[1] - state.y) == 1
        new_collected = state.collected or adjacent
        verdict = "already-collected" if state.collected else ("collected" if adjacent else "out-of-reach")
        return GameState(state.x, state.y, new_collected, state.turns + 1), verdict
    nx, ny = state.x + dx, state.y + dy
    if not (0 <= nx < spec.width and 0 <= ny < spec.height):
        return GameState(state.x, state.y, state.collected, state.turns + 1), "blocked-by-boundary"
    return GameState(nx, ny, state.collected, state.turns + 1), "moved"


def _spec_dict(spec: GameSpec) -> dict[str, Any]:
    spec.validate()
    return asdict(spec)


def run_actions(actions: list[str], spec: GameSpec | None = None) -> dict[str, Any]:
    """Return a self-contained trace. Does not write or auto-admit tasks."""
    spec = spec or GameSpec()
    state = first_state(spec)
    root = digest({"version": VERSION, "spec": _spec_dict(spec)})
    records: list[dict[str, Any]] = []
    parent_hash = root
    if len(actions) > 10000:
        raise ValueError("trace too long")
    for index, action in enumerate(actions, 1):
        before = asdict(state)
        state, verdict = transition(spec, state, action)
        row: dict[str, Any] = {"step": index, "action": action, "before": before,
                               "after": asdict(state), "verdict": verdict, "previous_hash": parent_hash}
        row["hash"] = digest(row)
        records.append(row)
        parent_hash = row["hash"]
    return {"version": VERSION, "spec": _spec_dict(spec), "root_hash": root,
            "steps": records, "final": asdict(state), "head_hash": parent_hash,
            "solved": state.collected, "evidence_depth": "executed-local-simulation"}


def _required_keys(obj: Mapping[str, Any], expected: set[str], name: str) -> None:
    if not isinstance(obj, dict) or set(obj) != expected:
        raise ValueError(f"{name} has unexpected or missing keys")


def verify_trace(trace: dict[str, Any]) -> dict[str, Any]:
    """Check exact trace envelope/hash-chain and replay actions through native rules.

    Same-implementation replay: not an independent physical or mathematical proof.
    Raises ValueError on any disagreement; no silent repair.
    """
    _required_keys(trace, {"version", "spec", "root_hash", "steps", "final", "head_hash", "solved", "evidence_depth"}, "trace")
    if trace["version"] != VERSION or trace["evidence_depth"] != "executed-local-simulation":
        raise ValueError("unsupported evidence version/depth")
    obj = trace["spec"]
    _required_keys(obj, {"width", "height", "start", "target"}, "spec")
    if not isinstance(obj["start"], (list, tuple)) or not isinstance(obj["target"], (list, tuple)):
        raise ValueError("invalid coordinate representations")
    spec = GameSpec(obj["width"], obj["height"], tuple(obj["start"]), tuple(obj["target"]))
    spec.validate()
    root = digest({"version": VERSION, "spec": _spec_dict(spec)})
    if trace["root_hash"] != root:
        raise ValueError("root hash mismatch")
    steps = trace["steps"]
    if not isinstance(steps, list) or len(steps) > 10000:
        raise ValueError("invalid steps")
    state = first_state(spec)
    previous = root
    for index, row in enumerate(steps, 1):
        _required_keys(row, {"step", "action", "before", "after", "verdict", "previous_hash", "hash"}, f"step {index}")
        if type(row["step"]) is not int or row["step"] != index or row["previous_hash"] != previous:
            raise ValueError(f"broken step ancestry at {index}")
        if row["before"] != asdict(state):
            raise ValueError(f"before-state mismatch at {index}")
        try:
            state, verdict = transition(spec, state, row["action"])
        except (ValueError, TypeError) as exc:
            raise ValueError(f"invalid action at {index}") from exc
        if row["after"] != asdict(state) or row["verdict"] != verdict:
            raise ValueError(f"native replay mismatch at {index}")
        check = {k: v for k, v in row.items() if k != "hash"}
        if row["hash"] != digest(check):
            raise ValueError(f"step hash mismatch at {index}")
        previous = row["hash"]
    if trace["head_hash"] != previous or trace["final"] != asdict(state) or type(trace["solved"]) is not bool or trace["solved"] != state.collected:
        raise ValueError("final result mismatch")
    return {"valid": True, "steps_verified": len(steps), "head_hash": previous,
            "solved": state.collected, "witness": "native-same-implementation-replay"}


def verify_browser_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Verify browser-reported actions/observations by local native replay.

    Browser observations are user-supplied, not independently authenticated.
    """
    _required_keys(receipt, {"version", "actions", "observations"}, "browser receipt")
    if receipt["version"] != VERSION or not isinstance(receipt["actions"], list) or not isinstance(receipt["observations"], list):
        raise ValueError("browser receipt malformed")
    trace = run_actions(receipt["actions"])
    if len(trace["steps"]) != len(receipt["observations"]):
        raise ValueError("observation count mismatch")
    for row, observation in zip(trace["steps"], receipt["observations"]):
        _required_keys(observation, {"action", "after", "verdict"}, "browser observation")
        if observation != {k: row[k] for k in ("action", "after", "verdict")}:
            raise ValueError("browser observation disagrees with native replay")
    return {"valid": True, "steps_verified": len(trace["steps"]),
            "solved": trace["solved"], "native_trace": trace}


def verify_expanded_browser_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Validate every expanded field, then delegate to the original strict verifier.

    This compatibility boundary does not authorize missing, contradicted or
    extra observations. The browser receipt remains unchanged and unauthenticated.
    """
    _required_keys(receipt, {"version", "spec", "actions", "observations", "final"},
                   "expanded browser receipt")
    _required_keys(receipt["spec"], {"width", "height", "start", "target"},
                   "expanded browser spec")
    _required_keys(receipt["final"], {"x", "y", "collected", "turns"},
                   "expanded browser final")
    if not isinstance(receipt["observations"], list):
        raise ValueError("expanded browser observations must be a list")
    canonical_observations = []
    for index, observation in enumerate(receipt["observations"], 1):
        _required_keys(observation, {"action", "before", "after", "verdict"},
                       f"expanded browser observation {index}")
        _required_keys(observation["before"], {"x", "y", "collected", "turns"},
                       f"expanded browser before {index}")
        canonical_observations.append({k: observation[k] for k in ("action", "after", "verdict")})

    # Only the original strict format crosses this boundary. No evidence is
    # synthesized: every projected field comes directly from the receipt.
    projected = {"version": receipt["version"], "actions": receipt["actions"],
                 "observations": canonical_observations}
    proof = verify_browser_receipt(projected)
    native_trace = proof["native_trace"]

    # Check *all* extension fields against native replay; neither unsupported
    # worlds nor tampered before/final states are silently projected away.
    if canonical(receipt["spec"]) != canonical(native_trace["spec"]):
        raise ValueError("expanded browser spec disagrees with native replay")
    for index, (observation, step) in enumerate(zip(receipt["observations"], native_trace["steps"]), 1):
        if canonical(observation["before"]) != canonical(step["before"]):
            raise ValueError(f"expanded browser before disagrees with native replay at {index}")
    if canonical(receipt["final"]) != canonical(native_trace["final"]):
        raise ValueError("expanded browser final disagrees with native replay")
    return proof


LANE_DEFINITIONS = (
    ("game-coordination", "Game coordination", "Construct one game without losing return points"),
    ("game-world", "Game world", "State, actors, actions, and consequences"),
    ("game-build", "Game implementation", "Executable game world and runtime"),
    ("game-witness", "Game witness", "Reproduce and verify claimed transitions"),
)


def bootstrap_workspace(journal: Path, *, actor_id: str = "james") -> dict[str, Any]:
    """Explicit bridge to existing WorkspaceStore. No handoff-runtime admission."""
    from systems.workspace.store import WorkspaceStore

    store = WorkspaceStore(journal)
    existing = {lane.lane_id: lane for lane in store.lanes()}
    # Validate the entire requested scope before creating any new lane.
    if any(existing[lane_id].actor_id != actor_id for lane_id, _, _ in LANE_DEFINITIONS if lane_id in existing):
        raise ValueError("existing lane actor conflicts with requested actor")
    created: list[str] = []
    for lane_id, label, referent in LANE_DEFINITIONS:
        if lane_id in existing:
            continue
        store.open_lane(lane_id, label=label, referent=referent,
                        actor_id=actor_id, sources=("docs/GAME_CONSTRUCTION_HARNESS.md",))
        created.append(lane_id)
    connections = { (c.from_lane, c.to_lane, c.relation) for c in store.links() }
    for a, b, relation in (
        ("game-world", "game-build", "world interface, no evidence transfer"),
        ("game-build", "game-witness", "candidate executable, unverified until replay"),
        ("game-witness", "game-coordination", "verified bounded result return"),
    ):
        if (a, b, relation) not in connections:
            store.connect(a, b, relation=relation)
    if store.focused_lane() != "game-coordination":
        store.set_focus("game-coordination")
    return {"created_lanes": created, "total_game_lanes": 4,
            "focus": store.focused_lane(), "journal": str(journal)}


def record_game_witness(journal: Path, trace_path: Path) -> dict[str, Any]:
    """Explicitly attach existing trace evidence to existing witness lane only."""
    from systems.workspace.store import WorkspaceStore

    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    proof = verify_trace(trace)
    store = WorkspaceStore(journal)
    store.get_lane("game-witness")  # must already be bootstrapped
    store.record_movement("game-witness", changes=f"replayed {proof['steps_verified']} game actions; solved={proof['solved']}",
                          preserved="world rule contract; earlier workspace lanes unchanged",
                          next_movement="coordinate next bounded world relation",
                          evidence_refs=(f"sha256:{sha256(trace_path.read_bytes()).hexdigest()}", f"path:{trace_path}"))
    return {"recorded": True, **proof}


def main() -> None:
    parser = argparse.ArgumentParser(description="Opt-in game construction witness; no scheduler")
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("demo", help="run a tiny fixed game and show trace, no disk writes")
    d.add_argument("--actions", nargs="+", default=["right", "interact"])
    r = sub.add_parser("run", help="run provided actions and explicitly write evidence")
    r.add_argument("--actions", nargs="+", required=True)
    r.add_argument("--out", required=True, type=Path)
    v = sub.add_parser("verify", help="replay exact saved trace")
    v.add_argument("--trace", required=True, type=Path)
    b = sub.add_parser("verify-browser", help="replay a browser-exported observation receipt")
    b.add_argument("--receipt", required=True, type=Path)
    be = sub.add_parser("verify-browser-expanded", help="check expanded fields, then use original strict native replay")
    be.add_argument("--receipt", required=True, type=Path)
    bs = sub.add_parser("bootstrap-workspace", help="explicitly add four lanes to existing private journal")
    bs.add_argument("--journal", required=True, type=Path)
    rw = sub.add_parser("record-workspace", help="explicitly record verified trace on witness lane")
    rw.add_argument("--journal", required=True, type=Path)
    rw.add_argument("--trace", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "demo":
        output = run_actions(args.actions)
    elif args.command == "run":
        output = run_actions(args.actions)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        output = {"file": str(args.out), "verification": verify_trace(output)}
    elif args.command == "verify":
        output = verify_trace(json.loads(args.trace.read_text(encoding="utf-8")))
    elif args.command == "verify-browser":
        proof = verify_browser_receipt(json.loads(args.receipt.read_text(encoding="utf-8")))
        output = {k: v for k, v in proof.items() if k != "native_trace"}
    elif args.command == "verify-browser-expanded":
        proof = verify_expanded_browser_receipt(json.loads(args.receipt.read_text(encoding="utf-8")))
        output = {k: v for k, v in proof.items() if k != "native_trace"}
    elif args.command == "bootstrap-workspace":
        output = bootstrap_workspace(args.journal)
    else:
        output = record_game_witness(args.journal, args.trace)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
