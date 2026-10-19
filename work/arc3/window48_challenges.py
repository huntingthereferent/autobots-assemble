"""Source-owned rooted-collision game challenges for the 48 F3 laws.

The worlds are the original CombinedWorld family, not visual approximations.
An objective is fulfilled only when two separately observed rooted action
words COLLIDE in one source world and SPLIT in the other. Any witness is
allowed; suggested examples are regenerated from the original rooted BFS.
"""
from __future__ import annotations

from work.arc_like_maze.window_combined import family, rooted_conflict

CHALLENGE_SCHEMA = "original-window48-rooted-collision-certificate/v1"
SCOPE = "finite-mathematical-source-only"
ROOT = (0, 0, 0)


def rooted_roster() -> list[dict]:
    laws = family()
    if len(laws) != 48:
        raise AssertionError("original source cardinality changed")
    result = []
    # Preserve the first 16 c=0 source challenge IDs exactly; saved certificates
    # and browser-local progress from the original release remain valid.
    # Continue through charts c=1 and c=2, visiting each concrete source law.
    # These are three charts of 16 rooted classes, NOT 48 rooted classes.
    for chart in (0, 1, 2):
        reps = [i for i, w in enumerate(laws) if w.coefficient == chart]
        if len(reps) != 16:
            raise AssertionError("original source chart cardinality changed")
        for position, first in enumerate(reps):
            second = reps[(position + 1) % len(reps)]
            # The final oriented pair requires source/target reversal to expose
            # the rooted obstruction; this matches historical challenge 15.
            if position == 15:
                first, second = second, first
            if first == second:
                raise AssertionError("source challenge must compare distinct classes")
            witness = rooted_conflict(laws[first], laws[second])
            if witness is None:
                first, second = second, first
                witness = rooted_conflict(laws[first], laws[second])
            if witness is None:
                raise AssertionError("original rooted classes have no distinguishing witness")
            path_a, path_b, source_state, target_a, target_b = witness
            assert laws[first].apply(ROOT, path_a) == source_state
            assert laws[first].apply(ROOT, path_b) == source_state
            assert target_a != target_b
            assert laws[second].apply(ROOT, path_a) == target_a
            assert laws[second].apply(ROOT, path_b) == target_b
            result.append({
                "id": len(result),
                "law_ids": [first, second],
                "objective": "rooted-collision-left-split-right",
                "example_words": [path_a, path_b],
                "example_source_endpoint": list(source_state),
                "example_target_endpoints": [list(target_a), list(target_b)],
            })
    if len(result) != 48 or {first for x in result for first in x["law_ids"]} != set(range(48)):
        raise AssertionError("every original concrete law must be a playable source challenge")
    return result

def _index(state) -> int:
    if len(state) != 3 or any(type(x) is not int or x not in range(3) for x in state):
        raise ValueError("invalid exact F3 source state")
    return state[0] * 9 + state[1] * 3 + state[2]


def _replay(laws, law_ids, trial):
    if type(trial) is not dict or set(trial) != {"actions", "events", "final"}:
        raise ValueError("challenge trial has different provenance shape")
    actions = trial["actions"]
    events = trial["events"]
    if (type(actions) is not str or len(actions) > 128 or
            any(a not in "AB" for a in actions) or
            type(events) is not list or len(events) != len(actions)):
        raise ValueError("invalid or unbounded rooted action word")
    state = [ROOT, ROOT]
    for n, (action, event) in enumerate(zip(actions, events)):
        if type(event) is not dict or set(event) != {"action", "before", "after"}:
            raise ValueError("challenge event shape changed")
        before = [_index(s) for s in state]
        state = [laws[law_ids[i]].step(state[i], action) for i in range(2)]
        after = [_index(s) for s in state]
        if event != {"action": action, "before": before, "after": after}:
            raise ValueError(f"original mathematical source refuted action event {n}")
    actual = [_index(s) for s in state]
    if trial["final"] != actual:
        raise ValueError("challenge final state not produced by original source")
    return actual


def check_rooted_paths(law_ids: list[int], path_a: str, path_b: str) -> dict:
    if (type(law_ids) is not list or len(law_ids) != 2 or
            any(type(n) is not int or not 0 <= n < 48 for n in law_ids)):
        raise ValueError("exact original source law IDs required")
    for word in (path_a, path_b):
        if type(word) is not str or len(word) > 128 or any(a not in "AB" for a in word):
            raise ValueError("exact bounded A/B path required")
    laws = family()
    endpoints = []
    for path in (path_a, path_b):
        endpoints.append([_index(laws[i].apply(ROOT, path)) for i in law_ids])
    left_collides = endpoints[0][0] == endpoints[1][0]
    right_splits = endpoints[0][1] != endpoints[1][1]
    passed = path_a != path_b and left_collides and right_splits
    return {"left_collides": left_collides, "right_splits": right_splits,
            "passed": passed, "endpoints": endpoints}


def verify_certificate(cert: dict) -> dict:
    """Independently reproduce both observed browser paths from original Python."""
    if (type(cert) is not dict or
            set(cert) != {"schema", "scope", "challenge_id", "law_ids", "trials", "verdict"} or
            cert["schema"] != CHALLENGE_SCHEMA or cert["scope"] != SCOPE):
        raise ValueError("not an original WORLD48 challenge certificate")
    cid = cert["challenge_id"]
    roster = rooted_roster()
    if type(cid) is not int or not 0 <= cid < len(roster):
        raise ValueError("unknown or forged challenge id")
    ids = cert["law_ids"]
    if ids != roster[cid]["law_ids"]:
        raise ValueError("challenge pair is not source-owned")
    trials = cert["trials"]
    if type(trials) is not list or len(trials) != 2:
        raise ValueError("two independent rooted path replays required")
    laws = family()
    finals = [_replay(laws, ids, trial) for trial in trials]
    computed = check_rooted_paths(ids, trials[0]["actions"], trials[1]["actions"])
    if computed["endpoints"] != finals:
        raise ValueError("source path endpoints inconsistent")
    outcome = {k: computed[k] for k in ("left_collides", "right_splits", "passed")}
    if type(cert["verdict"]) is not dict or cert["verdict"] != outcome:
        raise ValueError("challenge claim does not match original mathematics")
    return {"verified": True, "passed": computed["passed"],
            "challenge_id": cid, "law_ids": ids,
            "paths": [x["actions"] for x in trials],
            "endpoints": finals}


def main() -> None:
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path,
                        default=Path("docs/window48_challenges.json"))
    args = parser.parse_args()
    result = {"schema": "original-window48-rooted-challenge-roster/v1",
              "source": "work/arc_like_maze/window_combined.py",
              "scope": SCOPE, "challenges": rooted_roster()}
    if args.check:
        if not args.out.is_file() or json.loads(args.out.read_text()) != result:
            raise SystemExit("original rooted collision challenges differ from source")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print(f"WORLD48 rooted challenges: {len(result['challenges'])} source witnesses verified")


if __name__ == "__main__":
    main()
