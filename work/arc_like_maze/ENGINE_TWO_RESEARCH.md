# Engine 2 — native B-continuation research kernel

**Current referent.** Resume a bounded mathematical research relation without changing its source, transformation, watched carrier, or earlier witnesses. Engine 1 is not called after Engine 2's construction. This is a concrete research entry/exit surface, not a universal autonomous research engine.

## Native mathematical entry and exit

- `Engine2ResearchKernel.start(source, target, carrier, max_power)` validates the actual `WindowProcess` laws and their common B-invariant carrier, then follows successive applications of that same transformation.
- `Engine2ResearchKernel.resume(saved_json, max_power, expected_question_id=...)` reconstructs the original laws and WATCH, replays every previous observation, rejects forged claims, and continues from the previous power.
- The record retains complete fixed-state sets, the anchor's trajectories, budgets, mathematical question identity, and any verified B-intertwining bijection.
- Retain `question_id` separately if an external caller needs to reject replacement of the entire research question. It identifies the mathematical WATCH; it is not an authenticity signature.

## Distinct stopping outcomes

| Outcome | Mathematical requirement |
| --- | --- |
| `UNKNOWN_BUDGET` | No distinguishing fixed-point invariant and no positive certificate before the cutoff |
| `DISTINGUISHED_B_ACTIONS` | Fixed-point cardinalities of the same `B^n` differ |
| `B_ONLY_CONJUGACY_WITNESSED` | Both restricted permutations close, earlier fixed-point counts match, and an explicit bijection passes every B-intertwining equation |

An earned distinction cannot be erased by a later return. Agreement without a verified bijection never becomes equivalence. The B-invariant `x0=0` fiber is not A-invariant, so no simultaneous A/B conjugacy is claimed.

## Reproduce on actual repository mathematics

Run `python -m unittest network.tests.test_arc_like_engine_two_research -v` from the repository root.

Example:

```python
from itertools import product
from work.arc_like_maze.window_two import WindowProcess
from work.arc_like_maze.engine_two_research import Engine2ResearchKernel

zero = (0,) * 9
q0 = tuple(int(v == 2) for u, v in product(range(3), repeat=2))
q1 = tuple(int(u == 2 and v == 2) for u, v in product(range(3), repeat=2))
source = WindowProcess(1, (q0, zero), (zero,))
target = WindowProcess(1, (q0, q1), (zero,))
kernel = Engine2ResearchKernel()
carrier = kernel.fiber(5)
early = kernel.start(source, target, carrier, 8)
assert early.status == 'UNKNOWN_BUDGET'
later = kernel.resume(early.serialize(), 9, expected_question_id=early.record['question_id'])
assert later.status == 'DISTINGUISHED_B_ACTIONS'
```

## Boundary and next referent

The tested example has nine B-cycles of length 9 versus three B-cycles of length 27 on the declared **81-state B-invariant carrier**; the whole 243-state space has different earliest distinguishing behavior. This bounded kernel is not a proof of general A/B closure, automatic research-question selection, arbitrary new space grammars, or native ARC execution.

**Next:** integrate a witness-preserving interface for other already-earned native WATCHes while keeping their distinct mathematical contracts. Do not introduce a generic scheduler to replace continuation of the current relation.
