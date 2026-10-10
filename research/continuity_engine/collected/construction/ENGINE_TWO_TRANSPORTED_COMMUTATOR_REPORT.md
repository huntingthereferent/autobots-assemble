# Engine 2 — boundary research: transport of ordered commutators across proved law conjugacies

**Date:** 2026-10-09. **Status:** local, bounded experiment; no GitHub modifications. **Research referent:** carry the two selected noncommuting centralizer symmetries from the fixed zero-trace quotient law Q through an independently constructed law conjugacy H to a different quotient law P; preserve the actual selected maps, their order, component gauges, and transported points. This is separate from the original repository's mixed-composition theorem and group-presentation work.

## Declared mathematical family

Let all arithmetic be in F3. Use gain g=1, fixed nonconstant nine-entry lower coupling `q0=(0,1,2,0,2,1,1,1,1)`, zero normalized fourth-coordinate offsets, zero fifth-coordinate coupling, and zero higher tail. The quotient Q : F3 -> F3 determines the fourth-coordinate update. In dimension five write a state `(u,v,z,y,t)`.

- `A` increments `u` by 1.
- `B` maps `v -> v+u+1`, `z -> z+q0(u,v)`, `y -> y+Q(z+alpha(v))`, `t -> t` with `alpha=(0,1,1)`.
- The canonical lower centralizer C_Q maps `(u,v,z,y,t)` to `(u,v,z+1,y+Q(z+alpha(v))-Q(0),t)`.
- The induced B-compatibility graph on lower triples `(v,z,y)` determines connected-component labels `component_Q(s)`.
- A selected fifth-coordinate component gauge T_c maps `t -> t+c[component_Q(s)]`. The corresponding selected symmetry is `F_c=C_Q ◦ T_c` (apply the component gauge first).

The source quotient is `Q=(1,0,2)`, with gauge constants `a=(0,0,0)` and `b=(0,0,1)`. They produce respectively an order-three and order-nine selected symmetry. Both individually commute with A and B. Their ordered compositions do not commute.

## Constructed cross-law transport

Choose target `P=(0,2,1)`. The previously constructed, origin-preserving law conjugacy H has scale 1 and the explicit potential f(v,z), ordered lexicographically:

```
rows (v=0,1,2; z=0,1,2):
  (0,2,1)
  (2,1,0)
  (2,1,0)
H(u,v,z,y,t)=(u,v,z,y+f(v,z),t)
```

The 27 compatibility equations certify that `H A_Q=A_P H`, `H B_Q=B_P H`. Direct inverse and full-state checks were also performed on all 243 states.

The selected canonical symmetry does **not** transport to the unadjusted target canonical symmetry. There is a witnessed fourth-coordinate correction:

```
delta = P(0) - lambda*Q(0) = 0 - 1 = 2  (mod 3)
H C_Q H^-1 = D_delta C_P,
```

where `D_delta` adds delta to `y` (the fourth coordinate). Each fifth-coordinate component gauge does transport with its component labels:

```
H T_c H^-1 = T_(sigma_H(c)),
```

where `sigma_H(c)` is the explicitly constructed target-component assignment obtained from `H^-1` on the target lower graph. Thus the complete factorization is:

```
H F_c H^-1 = (D_delta C_P) T_(sigma_H(c)).
```

**This equation keeps the fourth-coordinate correction and the fifth-coordinate gauge separate.** No arbitrary identification of the two different selected centralizer maps is made.

## Result — a false negative if the correction is dropped

| WATCH | Source Q | Target P after exact transport | Target P using only its *uncorrected* canonical symmetry |
|---|---|---|---|
| B-compatibility graph components | 3 | 3 | 3 |
| Component permutation of shared lower action | `(2,0,1)` | `(2,0,1)` | `(0,1,2)` |
| Two selected transformations commute? | No | No | Yes (a *different* selected pair) |
| States exposing noncommutation | 162 / 243 | 162 / 243 | 0 / 243 |

For the distinguished origin x=(0,0,0,0,0), the original selected maps F and G yield

```
F(G(x)) = (0,0,2,2,0)
G(F(x)) = (0,0,2,2,1).
```

After H, the **same ordered compositions** yield

```
(H F H^-1)(H G H^-1)(H(x)) = (0,0,2,0,0)
(H G H^-1)(H F H^-1)(H(x)) = (0,0,2,0,1).
```

The fifth-coordinate distinction survives transport. For the convention `[F,G]=F G F^-1 G^-1`, the pointwise certificate at the origin is `(0,0,0,0,1)` on both sides of

```
H [F,G] H^-1 = [H F H^-1, H G H^-1].
```

This identity follows algebraically for bijective H; the local computation checks that the **specific candidate maps**, gauge adjustments and pointed trajectories realize it without a hidden map mismatch.

## Scope sweep over all zero-trace targets

With source Q fixed, all nine zero-trace target quotients P admit a constructed normalized H. For **each** of the nine targets, exhaustive checks over all 243 states establish:

- Source and target both have three graph components.
- The corrected transported lower symmetry acts as the component cycle `(2,0,1)`.
- Both ordered compositions disagree on 162 states.
- The transported commutator equals the conjugated source commutator on every state.
- Each transported factor still commutes with both target generators A and B.
- The explicit factorization via D_delta and transported fifth-coordinate component gauges holds on every state.

The target **uncorrected canonical** component actions split into three patterns (three target quotient laws each): identity `(0,1,2)`, cycle `(2,0,1)`, and reverse cycle `(1,2,0)`. The correction restores the transported source component action in all nine cases. This variation demonstrates why a canonical-representative-only comparison would be unreliable.

An 81-chain check (nine possible middle and nine possible final zero-trace quotients, with source Q fixed) also verified the native law-conjugacy correction composition rule `delta_QR = delta_PR + lambda_PR delta_QP` and the explicit H compositions on representative states.

## Verification

Reproduce from this file's directory:

```
python -m unittest test_engine_two_commutator_transport test_engine_two_quotient_conjugacy -v
python engine_two_commutator_transport.py
```

**29/29 local tests passed**, including **12 new tests**. The 12 tests cover law-conjugacy inversion and A/B squares, component transport, orders three and nine, full-state commutator transport, factorization, a canonical-only false-negative control, all nine target quotients, the 81 cross-law correction chains, cross-trace obstruction and provenance separation. This is not a claim about GitHub CI or the original repository's new regression tests.

The all-dimensional statement in this *zero-tail* declared family follows from the explicit triangular formulas acting only on the first five coordinates. No arbitrary higher couplings, all possible centralizer maps, arbitrary inter-law conjugacies, universal inverse A/B closure or native ARC solve are established.

## Engine 2 shape/function result

The research function reached a legitimate representation boundary: selecting the canonical symmetry of a conjugate target law did not preserve the previously observed ordered commutator. Engine 2 therefore constructed and retained the exact transported target symmetry instead, with a fourth-coordinate correction and fifth-coordinate component-gauge adjustment. The underlying law conjugacy was never discarded and never promoted into an unjustified equality of selected maps.

**Next native question:** determine when two differently factored transported symmetry words denote the same actual target map, using the existing component-permutation action and witness-preserving composition. That is a specific candidate for a normal-form WATCH, not permission to assert a general group presentation before its proof.