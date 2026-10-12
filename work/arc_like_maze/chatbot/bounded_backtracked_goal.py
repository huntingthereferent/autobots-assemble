"""Bounded rooted-path backtracking followed by selected finite union extension.

Standalone mathematical witness. A and B denote only the two finite
generators in finite_goal_priority.py; they are not a definition of A/B.
"""
from collections import deque
from dataclasses import dataclass
from finite_goal_priority import Law, ROOT

@dataclass(frozen=True)
class BacktrackResult:
    status: str
    goal: tuple
    goal_word: str | None
    mapped_goal: tuple | None
    candidate_words: tuple[str, ...]
    rejected_prefixes: tuple
    rejected_extensions: tuple
    paired_states: tuple
    admitted_edges: tuple
    explored_prefixes: int
    truncated: bool

def discover_and_extend(old: Law, new: Law, goal: tuple, *, depth: int = 6,
                        max_prefixes: int = 250, max_paths: int = 4):
    if not isinstance(old, Law) or not isinstance(new, Law):
        raise TypeError("two finite law objects required")
    if (type(depth) is not int or not 0 <= depth <= 8 or
            type(max_prefixes) is not int or not 1 <= max_prefixes <= 2000 or
            type(max_paths) is not int or not 1 <= max_paths <= 8):
        raise ValueError("invalid finite search limits")
    if (type(goal) is not tuple or len(goal) != 3 or
            any(type(i) is not int or i not in (0, 1, 2) for i in goal)):
        raise ValueError("goal outside F3^3")
    frontier = deque([("", (ROOT,), (ROOT,))])
    matches, rejected = [], []
    explored = 0
    truncated = False
    while frontier:
        if explored >= max_prefixes:
            truncated = True
            break
        word, original, changed = frontier.popleft()
        explored += 1
        if original[-1] == goal:
            matches.append((word, original, changed))
        if len(word) == depth:
            continue
        forward, reverse = dict(zip(original, changed)), dict(zip(changed, original))
        for action in "AB":
            u, v = old.step(original[-1], action), new.step(changed[-1], action)
            if (u in forward and forward[u] != v) or (v in reverse and reverse[v] != u):
                i = next((i for i, s in enumerate(original) if s == u), None)
                if i is None:
                    i = next(i for i, s in enumerate(changed) if s == v)
                left, right = word[:i], word + action
                eo, en = old.follow(left) == old.follow(right), new.follow(left) == new.follow(right)
                assert eo != en
                rejected.append((left, right, eo, en))
            else:
                frontier.append((word + action, original + (u,), changed + (v,)))
    if not matches:
        return BacktrackResult("UNKNOWN_SEARCH_LIMIT" if truncated else "GOAL_OUTSIDE_DEPTH",
                               goal, None, None, (), tuple(rejected), (), (), (), explored, truncated)
    forward, reverse, paths = {}, {}, []
    edges = {}
    for word, original, changed in sorted(matches, key=lambda p: (len(p[0]), p[0]))[:max_paths]:
        if any((s in forward and forward[s] != n) or
               (n in reverse and reverse[n] != s) for s, n in zip(original, changed)):
            continue
        paths.append(word)
        for s, n in zip(original, changed):
            forward[s], reverse[n] = n, s
        for i, action in enumerate(word):
            s, t = original[i:i+2]
            ns, nt = changed[i:i+2]
            edges[(s, action)] = (s, action, t, ns, nt)
    assert paths
    seed_word = paths[0]
    exclusions = []
    queue = [(s, a) for s in sorted(forward) for a in "AB" if (s, a) not in edges]
    for s, a in queue:
        if (s, a) in edges:
            continue
        ns = forward[s]
        t, nt = old.step(s, a), new.step(ns, a)
        if (t in forward and forward[t] != nt) or (nt in reverse and reverse[nt] != t):
            exclusions.append((s, a, t, ns, nt))
            continue
        if t not in forward:
            forward[t], reverse[nt] = nt, t
            queue.extend((t, a) for a in "AB")
        edges[(s, a)] = (s, a, t, ns, nt)
    for s, a, t, ns, nt in edges.values():
        assert forward[s] == ns and forward[t] == nt
        assert old.step(s, a) == t and new.step(ns, a) == nt
    assert old.follow(seed_word) == goal and new.follow(seed_word) == forward[goal]
    return BacktrackResult("GOAL_CARRIED_FINITE_WITNESS", goal, seed_word, forward[goal],
                           tuple(paths), tuple(rejected), tuple(exclusions),
                           tuple(sorted(forward.items())), tuple(sorted(edges.values())),
                           explored, truncated)

if __name__ == "__main__":
    old, new = Law((0, 0, 1)), Law((1, 0, 1))
    r = discover_and_extend(old, new, (1, 1, 2))
    print(r.status, r.goal_word, "image", r.mapped_goal,
          "states", len(r.paired_states), "edges", len(r.admitted_edges),
          "excluded", len(r.rejected_extensions), "truncated", r.truncated)
