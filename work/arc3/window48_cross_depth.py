"""Independent original-source verification for WORLD48 cross-depth observations.

A research observation is NOT a rooted-collision win certificate. Both paths,
prefix depths and every reported relation are replayed from the original
finite CombinedWorld laws. The distinct victory certificate schema stays intact.
"""
from __future__ import annotations

import json
from pathlib import Path

from work.arc3.window48_challenges import SCOPE, rooted_roster
from work.arc_like_maze.window_combined import family

SCHEMA = "original-window48-cross-depth-observation/v1"
SOURCE = "work/arc_like_maze/window_combined.py"
ROOT = (0, 0, 0)


def _index(state: tuple[int, int, int]) -> int:
    return state[0] * 9 + state[1] * 3 + state[2]


def source_prefix_states(law_ids: list[int], word: str) -> list[list[int]]:
    """Source-replay each actual prefix, including empty root; no extrapolation."""
    states = [ROOT, ROOT]
    recorded = [[0, 0]]
    laws = family()
    for action in word:
        states = [laws[law_ids[k]].step(states[k], action) for k in range(2)]
        recorded.append([_index(states[0]), _index(states[1])])
    return recorded


def build_observation(challenge_id: int, words: list[str],
                      selected_depths: list[int]) -> dict:
    """Compute a bounded canonical observation from recorded original law actions."""
    roster = rooted_roster()
    if type(challenge_id) is not int or not 0 <= challenge_id < len(roster):
        raise ValueError("unknown original WORLD48 challenge")
    if type(words) is not list or len(words) != 2:
        raise ValueError("two original A/B action words required")
    if any(type(w) is not str or len(w) > 128 or any(x not in "AB" for x in w) for w in words):
        raise ValueError("unbounded or invalid original source action word")
    if (type(selected_depths) is not list or len(selected_depths) != 2 or
            any(type(d) is not int or not 0 <= d <= len(words[k])
                for k, d in enumerate(selected_depths))):
        raise ValueError("selected steps must be actual recorded prefixes")

    law_ids = roster[challenge_id]["law_ids"]
    histories = [source_prefix_states(law_ids, word) for word in words]
    count = 0
    first = None
    for i, a in enumerate(histories[0]):
        for j, b in enumerate(histories[1]):
            if (a[0] == b[0] and a[1] != b[1] and
                    words[0][:i] != words[1][:j]):
                count += 1
                if first is None or (i + j, i) < (sum(first), first[0]):
                    first = [i, j]
    return {
        "schema": SCHEMA,
        "scope": SCOPE,
        "source": SOURCE,
        "challenge_id": challenge_id,
        "law_ids": law_ids,
        "words": words,
        "selected_depths": selected_depths,
        "selected_states": [histories[k][selected_depths[k]] for k in range(2)],
        "pair_count": len(histories[0]) * len(histories[1]),
        "candidate_count": count,
        "first_candidate": None if first is None else {
            "depths": first,
            "states": [histories[k][first[k]] for k in range(2)],
        },
    }


def verify_observation(data: dict) -> dict:
    """Reject fabricated claims; independently regenerate every reported field."""
    if type(data) is not dict or data.get("schema") != SCHEMA:
        raise ValueError("not an original-source cross-depth observation")
    try:
        expected = build_observation(
            data["challenge_id"], data["words"], data["selected_depths"]
        )
    except (KeyError, TypeError, IndexError) as exc:
        raise ValueError("malformed original-source observation") from exc
    if data != expected:
        raise ValueError("cross-depth report did not replay against original source")
    a, b = expected["selected_states"]
    words = expected["words"]
    i, j = expected["selected_depths"]
    return {
        "verified": True,
        "scope": SCOPE,
        "challenge_id": expected["challenge_id"],
        "candidate": a[0] == b[0] and a[1] != b[1] and words[0][:i] != words[1][:j],
        "candidate_count": expected["candidate_count"],
        "first_candidate": expected["first_candidate"],
        "win_certificate": False,
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Original WORLD48 cross-depth observation verifier")
    parser.add_argument("--verify", type=Path, required=True, help="JSON exported by WORLD48 Cross-depth view")
    args = parser.parse_args()
    report = json.loads(args.verify.read_text(encoding="utf8"))
    print(json.dumps(verify_observation(report), indent=2))


if __name__ == "__main__":
    main()
