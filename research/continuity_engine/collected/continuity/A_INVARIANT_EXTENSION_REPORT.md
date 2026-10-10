# Continuity Engine — A-invariant action, cross-scope and transport verification

**Status:** Local integration package, not a repository edit or GitHub merge. The test harness uses a documented test-only reproduction of `WindowProcess`, the older cyclic continuation contract, and the read-only research board. Fresh execution against the repository's exact imports was not available in this session.

## Current mathematical laws and their invariant domains

On the five-coordinate state space `F3^5`, written `(u,v,z,y,t)`, the current `WindowProcess` uses two labeled generators. Under **every** admitted law,

\[ A(u,v,z,y,t)=(u+1,v,z,y,t)\pmod 3. \]

`B` preserves the first coordinate `u` and changes later coordinates according to its coupling tables. Consequently:

- A nonempty, minimal **A-invariant carrier** is a three-state first-coordinate orbit `C_A(v,z,y,t)={(0,v,z,y,t),(1,v,z,y,t),(2,v,z,y,t)}`.
- The earlier **B-invariant fiber** `C_B(u)={(u,v,z,y,t):v,z,y,t in F3}` consists of 81 states. Each is separately closed under `B` for the tested pair.
- The full space has 243 states. Its selected `A/B` action is transitive; therefore the only subsets invariant under **both** generators are the empty set and the entire 243-state space. This is a theorem for these particular action laws, not a universal dimension statement.

The smaller A carrier does **not** make its result a smaller B or full A/B proof. Different generator, distinct mathematical question.

## Implemented A-only research entry

`research/a_invariant_action.py` provides `AInvariantAction.start/replay/resume`, validates that both source and target are genuinely A-invariant permutations of the declared carrier, records periodic fixed-state subsets, anchors question identity, and constructs and checks an explicit A-intertwining bijection once closure is proved. The `ContinuityEngine` includes `start_a_invariant` and replays its saved ancestry through the same outer handoff contract used by cyclic B and full AB.

For a three-state first-coordinate orbit, the admitted A-action is a 3-cycle. Fixed-state counts are zero at powers 1 and 2, all three states at power 3. **The A-only conjugacy witness is pointwise identity** for every pair of these `WindowProcess` laws on the same selected carrier, because A does not depend on the B coupling. This means it is a useful certified invariant and handoff scope, **not** an independent discriminator among this law family. A broader A grammar would have to be explicitly justified, not inferred from this test.

Outcomes are `UNKNOWN_A_BUDGET`, `DISTINGUISHED_A_ACTIONS` (permitted contract outcome, not encountered for these WindowProcess laws on a shared invariant carrier), and `A_ONLY_CONJUGACY_WITNESSED`.

## A -> full A/B handoff (non-promotion)

`research/cross_scope_handoff.py` now accepts either frozen generator-specific parent, validates the exact same source and target laws, recomputes 2×carrier-size transition restrictions for the selected generator, then opens a distinct full A/B question. The old B envelope and proof fields are retained.

| Parent / child relation | Parent outcome | Full-space child outcome | Restricted equations |
|---|---|---|---:|
| A carrier (3 states) → full 243-state AB | A-only conjugate | Full AB nonconjugate | 6 |
| B fiber (81 states) → full 243-state AB | B-only conjugate | Full AB nonconjugate | 162 |
| A carrier (3 states) → known positive full AB control | A-only conjugate | Full AB conjugate | 6 |

For the negative pair, exhaustive full A/B path-collision checks reject every candidate origin even though **both narrower positive statements hold simultaneously**. Neither narrow witness is promoted into a full-space theorem. Parent snapshots are frozen; child proof and continuation are separate, with independent question IDs.

## Invariant transport under a *verified* full correspondence

If a full action conjugacy `H` is independently verified with `H A_1=A_2 H` and `H B_1=B_2 H`, then for any invariant source subset `C` under a chosen generator `g`, `H(C)` is invariant under target `g`. The new `research/invariant_transport.py` verifies the actual image `H(C)` and all intertwining equations on that carrier; it does **not** assume `H(C)` equals the preselected target carrier.

The chosen positive-control full map demonstrates the difference:

- The transported 3-state A carrier **does not** match the same named A carrier in the target (`named_target_matches_image=false`).
- The transported 81-state B fiber **does** match the same named B fiber (`named_target_matches_image=true`).

These are facts for the explicitly selected verified full map, **not** claims about all possible conjugacies between these laws. The transport record can be recomputed with `verify_invariant_transport` against the supplied full witness and named target; malformed or altered records are rejected.

A negative or still-UNKNOWN full correspondence is **not** permitted to certify transported invariance.

## Research board

`research/continuity_board_bridge.py` admits the A-only scope as a separate research area, requires independently locatable published witness URLs before marking a positive result ANSWERED, and leaves the existing frozen question board unchanged. `scope_board_bridge.py` now carries selected-generator checks for both A and B, while preserving legacy `b_transition_checks` metadata for B cases.

## Verification

`python test_support/run_local_compatibility.py` ran **65/65 local compatibility tests successfully**, comprising the prior 47-test B/AB regression baseline and 18 new A-invariant tests. It checks replay tampering, scope swaps, UNKNOWN retention, exact transport verification, board staging, backward compatibility with B-only handoffs, as well as the known negative/positive full AB controls.

The standalone harness supplies explicit test-only support modules for `WindowProcess`, `CyclicActionEngine` and `load_research_board`. It is **not** a fresh exact-import test of the GitHub repository. An earlier unrelated repository test pass cannot be presented as verification of these new files.

## Reproduction

From this package:

```bash
python test_support/run_local_compatibility.py
```

Within a compatible repository checkout containing the genuine modules, copy package `research/*.py` and `network/tests/*.py` to matching paths, then run:

```bash
python -m unittest \
  network.tests.test_research_continuity_engine \
  network.tests.test_research_continuity_board_bridge \
  network.tests.test_research_full_action_correspondence \
  network.tests.test_research_cross_scope_handoff \
  network.tests.test_research_a_invariant_action -v
```

No repository was modified. This is a mathematical and implementation extension, not a claim of physical dimensionality, autonomous cross-disciplinary research, or universal A/B closure.