# Engine 2 — boundary-mathematics native-space continuation

**2026-10-09 · Local research experiment · no repository mutation**

## New referent

Read `work/arc_like_maze/ZERO_TRACE_LIFT.md` in `huntingthereferent/language-network` alongside the existing 48-law two-predecessor family. The zero-trace result is **not** just a larger catalog of transition laws: *one world law with the same fifth coupling can admit two different selected corrections with different cyclic orders*. Engine 2's research witness therefore cannot be keyed only by the world-law parameters.

A research object must separately retain:

- **Carrier/law**: the F3 world, its generators, and the declared construction grammar.
- **Selected correction**: the complete compatible 27-value function L, not merely `allowed=true`.
- **Correction order**: 3 or 9, earned via the full three-turn trace, not inferred from lower projection.
- **Pointed mark transport**: a five-coordinate mark and the actual selected centralizer action.
- **Admissibility/obstruction**: cohomological equations and, when unsolvable, replayable signed paths.
- **Unresolved cross-grammar relation**: the 48-law and zero-trace families have not been shown to share a general classification or mathematical bridge.

## Executed native experiments

**48 two-predecessor laws** — 2,304 ordered comparisons reproduced:

| Contract | Count |
|---|---:|
| Root-preserving full-state conjugacies | 144 |
| Full-state conjugacies moving the distinguished origin | 36 |
| `B` fixed-word obstructions | 1,728 |
| `BBB` fixed-word obstructions | 288 |
| `AABAB` fixed-word obstructions | 72 |
| `ABABAB` fixed-word obstructions | 36 |

**Zero-trace fifth-coordinate lifts** — an independently written signed-vector/matrix computation across 162 configurations reproduced:

| Property | Count |
|---|---:|
| Admissible world + fifth-coupling combinations | 22,410 |
| Permitting an order-3 selected correction | 11,106 |
| Permitting an order-9 selected correction | 12,492 |
| Permitting *both* distinct orders | 1,188 |
| Configurations with nontrivial component-gauge order effect | 12 |

The numbers of mutually exclusive combinations are 9,918 **only 3**, 11,304 **only 9**, and 1,188 **both**. The 1,188 intersection is why adding the two “permitting” totals double counts. These are not counts of distinct Engine 2 instances or distinct conjugacy classes.

The test reproduces the document's gain-one cases:
- `Q=(0,0,0), k=(0,0,1), q2=0`: order 3 only;
- `Q=(0,1,2), k=(0,0,1), q2=(2,1,0)*3`: order 9 only;
- `Q=(1,0,2), k=(0,0,0), q2=0`: both orders, via different compatible corrections;
- `q2=(1,0,0,0,0,0,0,0,0)` on the first case: signed-cycle obstruction with replayable contradictory paths.

The two selected order-3 and order-9 maps in the third example use **the same generator law** and the **same q2**. The experiment checks exact generator commutation on all 243 five-coordinate states for both A and B, and the selected mark's 3- versus 9-turn return. The nine-turn **symmetry of a mathematical world** must not be relabeled as an automatic nine-turn *runtime/research schedule* for Engine 2.

## Current architectural consequence

Engine 1 remains an on-demand one-shot **embryo constructor**, and turns off after handoff. It does not perform Engine 2's research. Engine 2 maintains multiple *native bounded mathematical spaces* through its Boundary Math research function. The 48-law, one-input coupling tower, and zero-trace higher-coupling work use different admissibility contracts; no generic comparison may silently identify their states or certificates.

When Engine 2 re-enters a result, it must keep `law`, selected `correction`, `order`, `mark`, and the signed-graph/fixed-word proof witness together. A matching status label alone is not a witness. Extra mathematical spaces are warranted by the watched relation, not by exceeding an arbitrary numerical quota such as 48.

**Remaining mathematical boundary:** no proved universal inter-family constructor; no unrestricted automatic generation of new operator grammars; no completed Boundary Math 0.5 implementation; no live ARC execution. The new code verifies *declared finite-field families*, not autonomous scientific discovery.

## Local files and verification

- `engine_two_window48_research.py`: independently implemented 48-law native full-state/rooted WATCH, all 2,304 pairs.
- `engine_two_zero_trace_extension.py`: independently implemented zero-trace fifth-coordinate cohomology, mark transport, order selection, full 162-case symbolic rank classification, and signed-voltage obstructions.
- `test_engine_two_new_shapes.py`: 15 focused new tests.
- Earlier `engine_two_research_kernel.py` and `test_engine_two_research_kernel.py`: separate one-input coupling-space native WATCHes.

Command from this directory:

```sh
python -m unittest test_engine_two_new_shapes test_engine_two_research_kernel test_engine_two_boundary_experiment -q
```

**Result: 39 tests passed.** Local execution only. No GitHub CI or commits asserted.