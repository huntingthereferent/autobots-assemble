# Cyclic Action Engine — native B-action continuation

**Current referent.** Resume a bounded mathematical research relation without changing its source, transformation, watched carrier, or earlier witnesses. The inverse constructor is not invoked during continuation. This is a concrete research entry/exit surface, not a universal autonomous research engine.

## Current mathematical shape

The implemented mathematical object is a **cyclic B-action** on a finite,
declared B-invariant carrier. The action's powers, orbit cycles,
fixed-point observations, explicit B-intertwiners, and replayed
witnesses are the supported capabilities. The term "Cyclic Action Engine"
names that shape, not the eventual research function of the embryo.

Two existing integration surfaces remain deliberately separate:
- CyclicActionEngine accepts a pair of WindowProcess laws and a
  caller-declared carrier.
- CyclicActionContinuation is the narrower ConstructedEngine.watch_B_against
  handoff for the declared 81-state x0=2 fiber.
Both continue the same B relation; neither establishes full A/B conjugacy.

## Native mathematical entry and exit

- `CyclicActionEngine.start(source, target, carrier, max_power)` validates the actual `WindowProcess` laws and their common B-invariant carrier, then follows successive applications of that same transformation.
- `CyclicActionEngine.resume(saved_json, max_power, expected_question_id=...)` reconstructs the original laws and WATCH, replays every previous observation, rejects forged claims, and continues from the previous power.
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

Run `python -m unittest network.tests.test_arc_like_cyclic_action_engine -v` from the repository root.

Example:

```python
from itertools import product
from work.arc_like_maze.window_two import WindowProcess
from work.arc_like_maze.cyclic_action_engine import CyclicActionEngine

zero = (0,) * 9
q0 = tuple(int(v == 2) for u, v in product(range(3), repeat=2))
q1 = tuple(int(u == 2 and v == 2) for u, v in product(range(3), repeat=2))
source = WindowProcess(1, (q0, zero), (zero,))
target = WindowProcess(1, (q0, q1), (zero,))
kernel = CyclicActionEngine()
carrier = kernel.fiber(5)
early = kernel.start(source, target, carrier, 8)
assert early.status == 'UNKNOWN_BUDGET'
later = kernel.resume(early.serialize(), 9, expected_question_id=early.record['question_id'])
assert later.status == 'DISTINGUISHED_B_ACTIONS'
```

## Existing inverse-construction handoff boundary

The existing `engine_one.py` still exposes the older `ConstructedEngine.evolve(engine_one, ...)` path that calls Engine 1 again for subsequent law changes. This kernel does **not** call it and does not claim that the legacy handoff architecture has been corrected. The independent research entry/exit path is verified here; a full one-shot construction-and-handoff contract remains separate work.

## Boundary and next referent

The tested example has nine B-cycles of length 9 versus three B-cycles of length 27 on the declared **81-state B-invariant carrier**; the whole 243-state space has different earliest distinguishing behavior. This bounded kernel is not a proof of general A/B closure, automatic research-question selection, arbitrary new space grammars, or native ARC execution.

**Next:** integrate a witness-preserving interface for other already-earned native WATCHes while keeping their distinct mathematical contracts. Do not introduce a generic scheduler to replace continuation of the current relation.
