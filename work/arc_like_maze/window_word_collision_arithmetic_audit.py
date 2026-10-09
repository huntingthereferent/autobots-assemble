"""Independent arithmetic verification of the 36-world fixed-word collision.

Intentionally imports NO work.arc_like_maze implementation. The transitions
are calculated directly, independently of WindowProcess / CollisionWorld.
Checks are exhaustive for the finite full state spaces at depths 3..7.
The all-depth claims still depend on the accompanying algebraic proof.

Run from repository root:
  python -m work.arc_like_maze.window_word_collision_arithmetic_audit
"""
from collections import Counter
from itertools import product


def step(state, support, pulse, balanced, coefficient, action):
    first, second, third, *rest = state
    if action == "A":
        return ((first + 1) % 3, second, third, *rest)
    if action != "B":
        raise ValueError("only A/B")
    added = (
        int(first == 2 and second < support)
        + pulse * int((first, second) == (0, 0))
        + balanced * (
            int((first, second) == (1, 0))
            - int((first, second) == (1, 1)))
        + coefficient * (
            (second + first + 1) ** 2 - second ** 2)
    ) % 3
    return (first, (second + first + 1) % 3,
            (third + added) % 3, *rest)


def predecessor(state, support, pulse, balanced, coefficient, action):
    first, second, third, *rest = state
    if action == "A":
        return ((first - 1) % 3, second, third, *rest)
    if action != "B":
        raise ValueError("only A/B")
    old_second = (second - first - 1) % 3
    added = (
        int(first == 2 and old_second < support)
        + pulse * int((first, old_second) == (0, 0))
        + balanced * (
            int((first, old_second) == (1, 0))
            - int((first, old_second) == (1, 1)))
        + coefficient * (
            (old_second + first + 1) ** 2 - old_second ** 2)
    ) % 3
    return (first, old_second, (third - added) % 3, *rest)


def chart(state, coefficient):
    result = list(state)
    result[2] = (result[2] + coefficient * result[1] ** 2) % 3
    return tuple(result)


def apply_word(state, parameters, word):
    for action in word:
        state = step(state, *parameters, action)
    return state


def worlds():
    return tuple((support, pulse, balanced, coefficient)
                 for support in range(4)
                 for pulse, balanced in ((0, 0), (0, 1), (1, 0))
                 for coefficient in range(3))


def first_count_break(a, b, depth=3, max_length=5):
    space = tuple(product(range(3), repeat=depth))
    for length in range(1, max_length + 1):
        for letters in product("AB", repeat=length):
            word = "".join(letters)
            counts = tuple(sum(apply_word(s, p, word) == s for s in space)
                           for p in (a, b))
            if counts[0] != counts[1]:
                return word, *counts
    return None


def audit():
    parameters = worlds()
    if len(parameters) != 36:
        raise AssertionError("expected 36 independently constructed worlds")
    patterns = {
        tuple(step(s, *p, "B") for s in product(range(3), repeat=3))
        for p in parameters
    }
    if len(patterns) != 36:
        raise AssertionError("two constructed concrete laws coincide")
    counts = Counter()
    for depth in range(3, 8):
        space = tuple(product(range(3), repeat=depth))
        for support, pulse, balanced, coefficient in parameters:
            parameters_ = (support, pulse, balanced, coefficient)
            for state in space:
                for action in "AB":
                    after = step(state, *parameters_, action)
                    if predecessor(after, *parameters_, action) != state:
                        raise AssertionError("triangular inverse failed")
                    counts["inverses"] += 1
                    if depth > 3:
                        if step(state[:-1], *parameters_, action) != after[:-1]:
                            raise AssertionError("projection commutation failed")
                        counts["projections"] += 1
                    for next_coefficient in range(3):
                        difference = (next_coefficient - coefficient) % 3
                        left = chart(after, difference)
                        right = step(chart(state, difference), support, pulse,
                                     balanced, next_coefficient, action)
                        if left != right:
                            raise AssertionError("shear conjugacy failed")
                        counts["conjugacies"] += 1
            expected_counts = {
                "B": (3 - support) * 3 ** (depth - 2),
                "BBB": (18 if pulse else 27) * 3 ** (depth - 3),
                "AABAB": (6 if pulse else (3 if balanced else 9))
                         * 3 ** (depth - 3),
            }
            for word, expected in expected_counts.items():
                actual = sum(apply_word(s, parameters_, word) == s
                             for s in space)
                if actual != expected:
                    raise AssertionError(
                        f"word {word} at {parameters_} depth {depth}:"
                        f" expected {expected}, observed {actual}")
                counts["word_formulas"] += 1
    for support in range(4):
        first = (support, 0, 0, 0)
        balanced = (support, 0, 1, 0)
        if first_count_break(first, balanced) != ("AABAB", 9, 3):
            raise AssertionError("first fixed-count break was not length five")
    expected = {
        "conjugacies": 705672,
        "inverses": 235224,
        "projections": 233280,
        "word_formulas": 540,
    }
    if dict(counts) != expected:
        raise AssertionError(f"arithmetic counts changed: {dict(counts)}")
    return {
        "status": "BOUNDED_ARITHMETIC_PASSED",
        "concrete_laws": len(patterns),
        "first_separating_word": "AABAB",
        **dict(counts),
    }


if __name__ == "__main__":
    print(audit())
