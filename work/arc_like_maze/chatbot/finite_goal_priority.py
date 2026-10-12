"""Finite goal-priority witness. A/B here names TWO SCOPED GENERATORS only."""
from dataclasses import dataclass

ROOT = (0, 0, 0)

@dataclass(frozen=True)
class Law:
    phi: tuple[int, int, int]

    def step(self, state, action):
        x, y, z = state
        if action == "A":
            return ((x + 1) % 3, y, z)
        if action == "B":
            return (x, (y + x + 1) % 3, (z + self.phi[y]) % 3)
        raise ValueError("invalid action")

    def follow(self, word):
        state = ROOT
        for action in word:
            state = self.step(state, action)
        return state

@dataclass(frozen=True)
class Result:
    order: str
    pairing: tuple
    admitted: tuple
    excluded: tuple
    reached: tuple

def extend(old, new, order, goals):
    if order not in ("AB", "BA"):
        raise ValueError("order must be AB or BA")
    forward, reverse, words = {ROOT: ROOT}, {ROOT: ROOT}, {ROOT: ""}
    queue = [(ROOT, a) for a in order]
    admitted, excluded = [], []
    cursor = 0
    while cursor < len(queue):
        source, action = queue[cursor]
        cursor += 1
        image = forward[source]
        target, new_target = old.step(source, action), new.step(image, action)
        if target in forward and forward[target] != new_target:
            compare, cause = words[target], "SOURCE_COLLISION"
        elif new_target in reverse and reverse[new_target] != target:
            compare, cause = words[reverse[new_target]], "TARGET_COLLISION"
        else:
            compare, cause = None, None
        if compare is not None:
            attempted = words[source] + action
            old_equal = old.follow(compare) == old.follow(attempted)
            new_equal = new.follow(compare) == new.follow(attempted)
            assert old_equal != new_equal
            excluded.append((source, action, cause, compare, attempted,
                             old_equal, new_equal))
            continue
        if target not in forward:
            forward[target], reverse[new_target] = new_target, target
            words[target] = words[source] + action
            queue.extend((target, a) for a in order)
        admitted.append((source, action, target, image, new_target))
    for source, action, target, image, new_target in admitted:
        assert forward[source] == image and forward[target] == new_target
        assert old.step(source, action) == target
        assert new.step(image, action) == new_target
    return Result(order, tuple(sorted(forward.items())), tuple(admitted),
                  tuple(excluded),
                  tuple((g, forward[g], words[g]) for g in goals if g in forward))

def choose(old, new, goals):
    if not goals or len(set(goals)) != len(goals) or any(
        type(s) is not tuple or len(s) != 3 or any(
            type(x) is not int or x not in (0, 1, 2) for x in s
        ) for s in goals
    ):
        raise ValueError("distinct goals in F3^3 required")
    candidates = tuple(extend(old, new, order, goals) for order in ("AB", "BA"))
    def score(r):
        return (len(r.reached), len(r.admitted), len(r.pairing), -len(r.excluded))
    top = max(score(r) for r in candidates)
    chosen = next(r for r in candidates if score(r) == top)
    images = tuple((g, tuple(sorted({image for candidate in candidates
                    for goal, image, _ in candidate.reached if goal == g})))
                   for g in goals)
    return chosen, candidates, images

if __name__ == "__main__":
    selected, candidates, images = choose(
        Law((0, 0, 1)), Law((1, 0, 1)), ((0, 0, 2),))
    for candidate in candidates:
        print(candidate.order, "states", len(candidate.pairing),
              "edges", len(candidate.admitted), "goals", candidate.reached)
    print("selected", selected.order, "possible images", images)
