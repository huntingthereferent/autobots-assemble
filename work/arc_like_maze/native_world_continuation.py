"""Source-native fast A/B observation across existing 48-law mathematical worlds.

This is a bounded experiment over the original CombinedWorld.step operations,
not a new definition of the language referent or an open-ended grammar inventor.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from dataclasses import dataclass
from .window_combined import family, CombinedWorld

ORIGIN = (0, 0, 0)
OPERATORS = ("A", "B")
SCHEMA = "native-ab-world-continuation/v1"


def run(*, law_ids=(0, 1), actions="AB", repeat=1, budget=100000):
    worlds = family()
    if not isinstance(law_ids, (tuple, list)) or not law_ids or len(set(law_ids)) != len(law_ids):
        raise ValueError("choose distinct existing world IDs")
    if any(type(i) is not int or not 0 <= i < len(worlds) for i in law_ids):
        raise ValueError("world ID outside the original family")
    if type(actions) is not str or not actions or any(a not in OPERATORS for a in actions):
        raise ValueError("nonempty exact A/B action word required")
    if type(repeat) is not int or repeat < 1 or len(actions) * repeat > budget:
        raise ValueError("explicit positive bounded feed required")
    states = [ORIGIN for _ in law_ids]
    seen = [{ORIGIN: 0} for _ in law_ids]
    transitions = [set() for _ in law_ids]
    events = []
    first_split = None
    for index in range(len(actions) * repeat):
        action = actions[index % len(actions)]
        before = tuple(states)
        after = tuple(worlds[i].step(states[k], action) for k, i in enumerate(law_ids))
        novelty = tuple(s not in seen[k] for k, s in enumerate(after))
        for k, s in enumerate(after):
            seen[k].setdefault(s, index + 1)
            transitions[k].add((before[k], action, s))
        if first_split is None and len(set(after)) > 1:
            first_split = index + 1
        events.append({"index": index + 1, "action": action,
                       "before": [list(s) for s in before],
                       "after": [list(s) for s in after],
                       "new_state": list(novelty)})
        states = list(after)
    payload = {"schema": SCHEMA, "scope": "original-window48-depth3",
               "law_ids": list(law_ids), "feed": {"word": actions, "repeat": repeat},
               "initial": list(ORIGIN), "events": events,
               "final": [list(s) for s in states],
               "observations": {"first_coordinate_split_step": first_split,
                                "distinct_states": [len(s) for s in seen],
                                "distinct_labeled_edges": [len(s) for s in transitions]}}
    payload["sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def verify(receipt):
    if type(receipt) is not dict or set(receipt) != {"schema", "scope", "law_ids", "feed", "initial", "events", "final", "observations", "sha256"}:
        raise ValueError("unexpected receipt fields")
    digest = receipt["sha256"]
    raw = {k: v for k, v in receipt.items() if k != "sha256"}
    if hashlib.sha256(json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()).hexdigest() != digest:
        raise ValueError("receipt integrity mismatch")
    feed = receipt["feed"]
    expected = run(law_ids=tuple(receipt["law_ids"]), actions=feed["word"], repeat=feed["repeat"])
    if receipt != expected:
        raise ValueError("source-native replay disagrees with receipt")
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--laws", type=int, nargs="+", default=[0, 1])
    p.add_argument("--word", default="AB")
    p.add_argument("--repeat", type=int, default=1000)
    p.add_argument("--budget", type=int, default=100000)
    p.add_argument("--out")
    p.add_argument("--verify")
    a = p.parse_args()
    if a.verify:
        with open(a.verify, encoding="utf8") as f:
            verify(json.load(f))
        print("VERIFIED: bounded native A/B replay")
        return
    result = run(law_ids=tuple(a.laws), actions=a.word, repeat=a.repeat, budget=a.budget)
    content = json.dumps(result, indent=2) + "\n"
    if a.out:
        with open(a.out, "w", encoding="utf8") as f:
            f.write(content)
    else:
        print(content)


if __name__ == "__main__":
    main()
