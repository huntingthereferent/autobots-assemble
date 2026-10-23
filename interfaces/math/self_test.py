"""Unstupid self-test: finite construction -> probe -> observation -> return.

Run from repository root:
    python -m interfaces.math.self_test
"""
import json
import unittest
from dataclasses import asdict

from work.arc_like_maze.math import World, inverse_candidates
from interfaces.math.closed_loop import run, finite_world_executor
from interfaces.math.probe_selector import select_probe


def exercise() -> dict:
    candidates = inverse_candidates()
    reference = World(3, (0, 1, 2))
    selected = select_probe(candidates)
    if selected.actions is None:
        raise AssertionError("candidate set produced no distinguishing probe")
    results = []
    for world in candidates:
        outcome = run(candidates, finite_world_executor(world), max_rounds=9)
        if world not in outcome.survivors:
            raise AssertionError("actual finite world was eliminated")
        if outcome.status != "INDISTINGUISHABLE_WITHIN_HORIZON":
            raise AssertionError(f"unexpected stop: {outcome.status}")
        results.append({
            "world_phi": list(world.phi),
            "status": outcome.status,
            "remaining": len(outcome.survivors),
            "rounds": [asdict(item) for item in outcome.rounds],
        })
    missing = run(candidates, lambda actions: (9, 9, 9))
    if missing.status != "MODEL_SET_EXHAUSTED":
        raise AssertionError("out-of-model observation was not preserved")
    return {
        "kind": "finite_in_memory_self_test",
        "candidate_count": len(candidates),
        "initial_probe": selected.actions,
        "reference_phi": list(reference.phi),
        "world_runs": results,
        "out_of_model_status": missing.status,
        "external_world_tested": False,
        "ai_adapter_tested": False,
    }


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover("interfaces/math", pattern="test_*.py")
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    if not outcome.wasSuccessful():
        raise SystemExit(1)
    print(json.dumps(exercise(), indent=2))
