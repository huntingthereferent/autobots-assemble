"""Compare completed finite goal-extension witnesses without replacing the solver.

Uses bounded_backtracked_goal.BacktrackResult and explicit finite laws. Results
are scoped to these laws; no remote provenance or physical A/B claims.
"""
from collections import deque
from dataclasses import dataclass
from itertools import combinations

ROOT = (0, 0, 0)

@dataclass(frozen=True)
class Collision:
    first: int
    second: int
    cause: str
    left_word: str
    right_word: str
    old_equal: bool
    new_equal: bool

@dataclass(frozen=True)
class Selection:
    status: str
    indices: tuple
    carried: tuple
    paired_states: tuple
    admitted_edges: tuple
    compatible_subsets: int
    conflicts: tuple
    possible_goal_images: tuple

def _check(old, new, record):
    if record.status != "GOAL_CARRIED_FINITE_WITNESS":
        raise ValueError("candidate has not completed a finite goal witness")
    fwd = dict(record.paired_states)
    if (not fwd or fwd.get(ROOT) != ROOT or
            len(fwd) != len(record.paired_states) or
            len(set(fwd.values())) != len(fwd)):
        raise ValueError("invalid paired states")
    edges = {}
    for s, a, t, ns, nt in record.admitted_edges:
        e = (s, a, t, ns, nt)
        if (fwd.get(s) != ns or fwd.get(t) != nt or
                old.step(s, a) != t or new.step(ns, a) != nt or
                ((s, a) in edges and edges[(s, a)] != e)):
            raise ValueError("admitted transition fails independent finite replay")
        edges[(s, a)] = e
    if (record.goal not in fwd or fwd[record.goal] != record.mapped_goal or
            old.follow(record.goal_word) != record.goal or
            new.follow(record.goal_word) != record.mapped_goal):
        raise ValueError("goal witness fails replay")
    words = {ROOT: ""}
    queue = deque([ROOT])
    while queue:
        s = queue.popleft()
        for a in "AB":
            edge = edges.get((s, a))
            if edge and edge[2] not in words:
                words[edge[2]] = words[s] + a
                queue.append(edge[2])
    if set(words) != set(fwd):
        raise ValueError("paired state has no admitted rooted path")
    for s, w in words.items():
        if old.follow(w) != s or new.follow(w) != fwd[s]:
            raise ValueError("retained rooted witness failed")
    return fwd, edges, words

def compare_completed(old, new, candidates, goals):
    """Exact compatible-subset search over 1..8 already completed candidates."""
    if not (type(candidates) is tuple and 1 <= len(candidates) <= 8 and
            type(goals) is tuple and goals and len(set(goals)) == len(goals)):
        raise ValueError("1..8 completed candidates and distinct goals required")
    checked = [_check(old, new, r) for r in candidates]
    conflicts = []
    for i, j in combinations(range(len(checked)), 2):
        fi, _, wi = checked[i]
        fj, _, wj = checked[j]
        collision = next(((wi[s], wj[s], "SOURCE_COLLISION")
                          for s in sorted(set(fi) & set(fj)) if fi[s] != fj[s]), None)
        if collision is None:
            reverse = {n: s for s, n in fi.items()}
            collision = next(((wi[reverse[n]], wj[s], "TARGET_COLLISION")
                              for s, n in sorted(fj.items())
                              if n in reverse and reverse[n] != s), None)
        if collision:
            left, right, cause = collision
            equal_old = old.follow(left) == old.follow(right)
            equal_new = new.follow(left) == new.follow(right)
            if equal_old == equal_new:
                raise ValueError("collision lacks separating equality witness")
            conflicts.append(Collision(i, j, cause, left, right, equal_old, equal_new))
    options = []
    for count in range(1, len(checked) + 1):
        for subset in combinations(range(len(checked)), count):
            fwd, rev, edges = {}, {}, {}
            compatible = True
            for i in subset:
                for s, n in checked[i][0].items():
                    if ((s in fwd and fwd[s] != n) or
                            (n in rev and rev[n] != s)):
                        compatible = False
                        break
                    fwd[s], rev[n] = n, s
                if not compatible:
                    break
                for key, edge in checked[i][1].items():
                    if key in edges and edges[key] != edge:
                        compatible = False
                        break
                    edges[key] = edge
                if not compatible:
                    break
            if not compatible or any(fwd.get(s) != ns or fwd.get(t) != nt
                                     for s, a, t, ns, nt in edges.values()):
                continue
            carried = []
            for goal in goals:
                if goal in fwd:
                    word = min((checked[i][2][goal] for i in subset
                                if goal in checked[i][2]), key=lambda w: (len(w), w))
                    carried.append((goal, fwd[goal], word))
            score = (len(carried), len(edges), len(fwd), -len(subset))
            options.append((score, subset, tuple(carried),
                            tuple(sorted(fwd.items())), tuple(sorted(edges.values()))))
    if not options:
        raise ValueError("no compatible nonempty candidate subset")
    best = max(o[0] for o in options)
    chosen = next(o for o in options if o[0] == best)
    peak = max(o[0][0] for o in options)
    images = tuple((goal, tuple(sorted({image for score, subset, carried, _, _ in options
                                         if score[0] == peak
                                         for g, image, word in carried if g == goal})))
                   for goal in goals)
    return Selection("GOALS_CARRIED" if len(chosen[2]) == len(goals) else
                     "PARTIAL_GOALS", chosen[1], chosen[2], chosen[3], chosen[4],
                     len(options), tuple(conflicts), images)

if __name__ == "__main__":
    from finite_goal_priority import Law
    from bounded_backtracked_goal import discover_and_extend
    old, new = Law((0, 0, 1)), Law((0, 0, 0))
    goals = ((0, 1, 0), (0, 1, 1))
    records = tuple(discover_and_extend(old, new, goal) for goal in goals)
    report = compare_completed(old, new, records, goals)
    print(report.status, "selected", report.indices,
          "carried", report.carried, "conflicts", len(report.conflicts))
