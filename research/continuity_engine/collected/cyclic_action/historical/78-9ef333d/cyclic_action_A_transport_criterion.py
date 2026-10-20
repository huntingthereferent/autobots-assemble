"""Read-only A-orbit bridge research for the Cyclic Action Engine.

Execute from huntingthereferent/language-network repository root with this
file on PYTHONPATH:
  python cyclic_action_A_transport_criterion.py

Uses actual existing WindowProcess and CyclicActionEngine implementations.
"""
from itertools import product
from work.arc_like_maze.window_two import WindowProcess
from work.arc_like_maze.cyclic_action_engine import CyclicActionEngine

F3 = (0, 1, 2)
Z = (0,) * 9
r0 = tuple(int(v == 2) for u, v in product(F3, repeat=2))
r1 = tuple(int(u == 2 and v == 2) for u, v in product(F3, repeat=2))
twice = tuple(2*a % 3 for a in r1)
pulse = tuple(int((u, v) == (2, 0)) for u, v in product(F3, repeat=2))
S0 = CyclicActionEngine.fiber(5, first=0)
left = WindowProcess(1, (r0, r1), (Z,))
right = WindowProcess(1, (r0, twice), (Z,))
baseline = WindowProcess(1, (Z, Z), (Z,))
altered = WindowProcess(1, (pulse, Z), (Z,))


def power_A(w, x, n):
    for _ in range(n):
        x = w.step(x, "A")
    return x


def count_failed_transports(w1, w2, f0):
    counts = []
    for u in F3:
        count = 0
        for x in S0:
            left_shifted = power_A(w1, x, u)
            left_back = power_A(w1, w1.step(left_shifted, "B"), (-u) % 3)
            right_shifted = power_A(w2, f0[x], u)
            right_back = power_A(w2, w2.step(right_shifted, "B"), (-u) % 3)
            count += f0[left_back] != right_back
        counts.append(count)
    return counts


if __name__ == "__main__":
    witness = CyclicActionEngine().start(left, right, S0, 27)
    assert witness.status == "B_ONLY_CONJUGACY_WITNESSED"
    f0 = {tuple(a): tuple(b) for a, b in witness.record["B_bijection"]}
    shifted = {x: right.step(f0[x], "B") for x in S0}
    identity = {x: x for x in S0}
    readings = {
        "canonical": count_failed_transports(left, right, f0),
        "shifted_B_witness": count_failed_transports(left, right, shifted),
        "dormant_pulse": count_failed_transports(baseline, altered, identity),
    }
    assert readings == {"canonical": [0, 0, 0],
                        "shifted_B_witness": [0, 54, 54],
                        "dormant_pulse": [0, 0, 27]}
    print(readings)