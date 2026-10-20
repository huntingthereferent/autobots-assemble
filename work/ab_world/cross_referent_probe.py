"""Read-only cross-referent observation in existing native sources.

This is NOT a general world engine. Each system keeps its own native rules.
The experiment asks whether W13 movement and NIH knowledge availability can
vary independently, with World48 only an optional separate math observation.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from systems.workspace import game_construction as w13
from systems.workspace import nih_scope_native as scope_native
from systems.workspace import nih_prototype_native as prototype_host
from systems.workspace.nih_prototype_worker_source import prototype_worker

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "network/tests/fixtures/nih_scope_example.json"
KNOWN = ("2026-01-04", "2026-01-06")
ACTIONS = ("left", "right")
TARGET = "2026-01-04"


def source_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def temporal_observations(scope: dict) -> dict:
    """Run the ORIGINAL emitted synthetic Python, check against the host scope."""
    dataset = {
        "synthetic": True,
        "observations": scope["observations"],
        "functional_predicates": ["has-status"],
    }
    with TemporaryDirectory(prefix="ab-world-nih-readonly-") as td:
        p = Path(td)
        program = p / "temporal_query.py"
        data = p / "temporal_dataset.json"
        program.write_text(prototype_worker.ENGINE, encoding="utf8")
        data.write_text(json.dumps(dataset, sort_keys=True), encoding="utf8")
        answers = {}
        for cutoff in KNOWN:
            raw = subprocess.run(
                [sys.executable, "-I", str(program), str(data)],
                input=json.dumps({"known_at": cutoff, "target_at": TARGET}),
                text=True, capture_output=True, timeout=5, check=True,
            )
            result = json.loads(raw.stdout)
            host = prototype_host.oracle(scope, ["has-status"], known=cutoff, target=TARGET)
            if result["temporal_ids"] != host["temporal_ids"]:
                raise ValueError("temporal program differs from original scope oracle")
            if result["future_leakage_ids"] != host["future_leakage_ids"]:
                raise ValueError("future availability differs from original scope oracle")
            if result["clinical_verdict"] != "NOT_EVALUATED":
                raise ValueError("synthetic data promoted into a clinical claim")
            answers[cutoff] = result
        # A deliberately invalid date must be refused by the original executable.
        invalid = subprocess.run(
            [sys.executable, "-I", str(program), str(data)],
            input=json.dumps({"known_at": "2026-02-30", "target_at": TARGET}),
            text=True, capture_output=True, timeout=5, check=False,
        )
        if invalid.returncode == 0:
            raise ValueError("original temporal program accepted invalid evidence time")
    if (answers[KNOWN[0]]["temporal_ids"] != ["prior-note"] or
        answers[KNOWN[0]]["future_leakage_ids"] != ["delayed-result"] or
        answers[KNOWN[1]]["temporal_ids"] != ["delayed-result", "prior-note"] or
        answers[KNOWN[1]]["future_leakage_ids"]):
        raise ValueError("frozen fictional historical-availability anchor changed")
    return answers


def optional_world48() -> dict:
    """A separate exact mathematical observation, not an NIH requirement."""
    from work.arc3.window48_world_export import state_index, verify_receipt
    from work.arc_like_maze import window_combined
    laws = window_combined.family()
    if len(laws) != 48:
        raise ValueError("original Window48 law family changed")
    before = [state_index((0, 0, 0))] * 2
    after = [state_index(laws[i].step((0, 0, 0), "A")) for i in (0, 1)]
    receipt = {
        "schema": "original-window48-depth3-browser-receipt/v1",
        "scope": "finite-mathematical-source-only",
        "law_ids": [0, 1], "root_index": 0, "actions": "A",
        "events": [{"action": "A", "before": before, "after": after}],
        "final": after,
    }
    witness = verify_receipt(receipt)
    if witness["valid"] is not True or witness["final"] != after:
        raise ValueError("original Window48 replay rejected its own source event")
    return {
        "receipt": receipt, "source_replay": witness,
        "source_sha256": source_digest(Path(window_combined.__file__)),
        "nih_capacity_inferred": False,
    }


def run(*, with_world48: bool = False) -> dict:
    """Four actual crossed source computations, no source or journal mutations."""
    if type(with_world48) is not bool:
        raise ValueError("World48 must be an explicit optional control")
    paths = {
        "w13": Path(w13.__file__),
        "nih_scope": Path(scope_native.__file__),
        "nih_independent_oracle": Path(prototype_host.__file__),
        "nih_emitted_builder": Path(prototype_worker.__file__),
        "nih_fixture": FIXTURE,
    }
    before_hashes = {key: source_digest(path) for key, path in paths.items()}
    raw_scope = json.loads(FIXTURE.read_text(encoding="utf8"))
    scope = scope_native.validate_scope(raw_scope)
    if not scope["synthetic"] or scope["query_at"] != KNOWN[0] or scope["target_at"] != TARGET:
        raise ValueError("declared original synthetic source boundary changed")
    answers = temporal_observations(scope)
    spec = w13.GameSpec()
    initial = w13.first_state(spec)
    if asdict(initial) != {"x": 0, "y": 1, "collected": False, "turns": 0}:
        raise ValueError("original W13 start differs")
    game = {}
    for action in ACTIONS:
        state, verdict = w13.transition(spec, initial, action)
        game[action] = {"before": asdict(initial), "action": action,
                        "after": asdict(state), "verdict": verdict}
    if (game["left"]["verdict"] != "blocked-by-boundary" or
        game["left"]["after"] != {"x": 0, "y": 1, "collected": False, "turns": 1} or
        game["right"]["verdict"] != "moved" or
        game["right"]["after"] != {"x": 1, "y": 1, "collected": False, "turns": 1}):
        raise ValueError("W13 finite source movement differs")
    crossed = [
        {"game_action": action, "known_at": cutoff,
         "w13": game[action], "nih": answers[cutoff]}
        for action in ACTIONS for cutoff in KNOWN
    ]
    if not (
        crossed[0]["w13"] == crossed[1]["w13"] and
        crossed[2]["w13"] == crossed[3]["w13"] and
        crossed[0]["nih"] == crossed[2]["nih"] and
        crossed[1]["nih"] == crossed[3]["nih"]
    ):
        raise ValueError("unjustified cross-domain dependence")
    world48 = optional_world48() if with_world48 else None
    if before_hashes != {key: source_digest(path) for key, path in paths.items()}:
        raise ValueError("an original source changed during the read-only experiment")
    return {
        "schema": "ab-cross-referent-native-observation/v1",
        "source_sha256": before_hashes,
        "temporal_program_sha256": sha256(prototype_worker.ENGINE.encode()).hexdigest(),
        "cases": crossed,
        "world48_optional_observation": world48,
        "bounded_observation": True,
        "w13_nih_independence_on_tested_inputs": True,
        "nih_original_historical_versions_authenticated": False,
        "physical_measurements_witnessed": False,
        "general_world_completed": False,
        "new_workstation_jobs": 0,
    }


def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--with-world48", action="store_true")
    args = p.parse_args()
    print(json.dumps(run(with_world48=args.with_world48), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
