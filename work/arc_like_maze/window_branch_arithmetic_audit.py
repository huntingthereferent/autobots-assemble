"""Independent arithmetic audit of the 24-world window construction.

This module intentionally does NOT import WindowProcess, window_branch,
or any other repository implementation. Its transition formula is written
separately so that reproducing the claimed finite evidence is not just
asking the implementation to compare its own outputs to itself.

Execute from repository root:
    python -m work.arc_like_maze.window_branch_arithmetic_audit

A finite exhaustive audit is not a proof of an unbounded theorem.
"""
from itertools import product


def step(state, support, chart, pulse, action):
    result = list(state)
    if action == "A":
        result[0] = (state[0] + 1) % 3
    elif action == "B":
        u, v = state[:2]
        result[1] = (v + u + 1) % 3
        support_term = int(u == 2 and v < support)
        independent_term = pulse * int((u, v) == (0, 0))
        shear_term = chart * ((v + u + 1) ** 2 - v ** 2)
        result[2] = (state[2] + support_term + independent_term + shear_term) % 3
        # All higher coupling increments are zero in this declared family.
    else:
        raise ValueError("action must be A or B")
    return tuple(result)


def shear(state, coefficient):
    result = list(state)
    result[2] = (state[2] + coefficient * state[1] ** 2) % 3
    return tuple(result)


def preimage(state, support, chart, pulse, action):
    result = list(state)
    if action == "A":
        result[0] = (state[0] - 1) % 3
    elif action == "B":
        u = state[0]
        result[1] = (state[1] - u - 1) % 3
        v = result[1]
        result[2] = (
            state[2] - int(u == 2 and v < support)
            - pulse * int((u, v) == (0, 0))
            - chart * ((v + u + 1) ** 2 - v ** 2)
        ) % 3
    else:
        raise ValueError("action must be A or B")
    return tuple(result)


def audit():
    counts = dict(conjugacy_edges=0, reverse_checks=0,
                  projection_edges=0, word_fixed_checks=0)
    distinct = set()
    for support, pulse, chart in product(range(4), range(2), range(3)):
        distinct.add(tuple(
            step(x, support, chart, pulse, "B")
            for x in product(range(3), repeat=3)
        ))
        for depth in range(3, 8):
            B_fixed = BBB_fixed = 0
            for state in product(range(3), repeat=depth):
                if step(state, support, chart, pulse, "B") == state:
                    B_fixed += 1
                triple = state
                for _ in range(3):
                    triple = step(triple, support, chart, pulse, "B")
                if triple == state:
                    BBB_fixed += 1
                counts["word_fixed_checks"] += 2
                for label in "AB":
                    advanced = step(state, support, chart, pulse, label)
                    if preimage(advanced, support, chart, pulse, label) != state:
                        raise AssertionError("inverse failed")
                    counts["reverse_checks"] += 1
                    if depth > 3:
                        expected = step(state[:-1], support, chart, pulse, label)
                        if expected != advanced[:-1]:
                            raise AssertionError("projection failed")
                        counts["projection_edges"] += 1
                    for target_chart in range(3):
                        c = (target_chart - chart) % 3
                        lhs = shear(advanced, c)
                        rhs = step(shear(state, c), support, target_chart,
                                   pulse, label)
                        if lhs != rhs:
                            raise AssertionError("state-level conjugacy failed")
                        counts["conjugacy_edges"] += 1
            if B_fixed != (3 - support) * 3 ** (depth - 2):
                raise AssertionError("Fix(B) formula failed")
            expected_BBB = (3 if pulse == 0 else 2) * 3 ** (depth - 1)
            if BBB_fixed != expected_BBB:
                raise AssertionError("Fix(BBB) formula failed")
    if len(distinct) != 24:
        raise AssertionError("world laws collided as concrete tables")
    reference = dict(conjugacy_edges=470448, reverse_checks=156816,
                     projection_edges=155520, word_fixed_checks=156816)
    if counts != reference:
        raise AssertionError(f"audit count drifted: {counts}")
    return dict(counts, concrete_laws=len(distinct),
                statuses="ALL_BOUNDED_CHECKS_PASSED")


if __name__ == "__main__":
    print(audit())
