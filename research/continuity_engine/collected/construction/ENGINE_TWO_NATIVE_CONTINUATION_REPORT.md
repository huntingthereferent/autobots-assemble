# Engine 2 — Bounded native continuation A/B experiment

**Date:** 9 October 2026  
**Mode:** local standalone experiment; the GitHub repository is unchanged.  
**Question:** can the same *admitted* generator WATCH remain inconclusive for several steps, continue natively, then find a valid distinction without switching comparison types—and can it stop with UNKNOWN instead of manufacturing equivalence?

## Declared mathematical space

Construct two invertible triangular A/B systems over `F3^5` using the established two-input window rule format. State is `(u,v,z,y,t)`. A adds 1 to u. The B generator fixes u and has the following increments, based on the **old state**:

- `v += u+1`
- `z += q0(u,v)`, with `q0(u,v) = [v=2]` in *both* worlds
- `y += q1(v,z)`, with **World 9** `q1=0`, **World 27** `q1(v,z)=[v=2 and z=2]`
- `t += 0`

All values are in `F3`. The permitted WATCH carrier is the **B-invariant** fiber `u=0`, containing 81 states. This is not A-invariant, so claims about the fiber are **B-only**, not simultaneous A/B conjugacy claims.

Both systems' forward/inverse A and B transformations were checked on every state of the entire 243-state space.

## Witnessed progression

| Native power | Fix(B9^n) on u=0 | Fix(B27^n) on u=0 | Interpretation |
|:--|--:|--:|:--|
| 1…8 | 0 each | 0 each | no distinction from this WATCH; not equivalence |
| 9 | 81 | 0 | first distinguishing B-power invariant |
| 27 | 81 | 81 | both return; earlier obstruction still survives |

At the origin `(0,0,0,0,0)`:

- World 9: `B^9(origin) = (0,0,0,0,0)`.
- World 27: `B^9(origin) = (0,0,0,1,0)`.
- World 27: `B^27(origin) = origin`.

Independent enumeration of actual cycles on the fiber gives **nine 9-cycles** for World 9 and **three 27-cycles** for World 27. Their B-actions are therefore not conjugate as permutations of this invariant 81-state fiber. No new comparison operator was introduced between powers: each observation was obtained by applying the same `B` once more to the previous saved states.

### WATCH scope is essential

On the **whole** `F3^5` carrier (243 states), the earliest fixed-point count separation is already **n=3**, not n=9. The statement “first eight counts agree” holds **only** for the declared `u=0` fiber. Engine 2 must retain that scope in each witness and must not silently upgrade the fiber conclusion to a whole-space first-divergence claim. The whole-space difference independently proves these particular full-state B actions are nonconjugate, but the n=9 claim is fiber-scoped.

## Distinct stopping states

1. **Bounded UNKNOWN:** with observation budget 8, the ledger ends `UNKNOWN_BUDGET`, retaining eight unchanged comparisons and the original systems. Matching counts do not certify conjugacy.
2. **Decisive obstruction:** with budget 9, the ledger ends `DISTINGUISHED_B_ACTIONS` with actual `B^9` fixed sets and the origin trajectories retained. More observations cannot erase that distinction.
3. **Positive B-only control:** replace `q1=[v=2,z=2]` by `q1=2*[v=2,z=2]`. Both fiber actions have three 27-cycles. At `n=27`, closure is earned and an **explicit 81-state B-intertwining bijection** is constructed and checked on all B edges. Status `B_ONLY_CONJUGACY_WITNESSED`, with no claim about A/B simultaneous equivalence.
4. **Nonpremature stop:** the positive control at budget 26 returns UNKNOWN, not equivalence.

## Engine 2 function ↔ shape

The embryo needs a space constructor for a declared invariant subspace, an executable native continuation, a retained WATCH condition and actual states, and a source-bearing ledger. Its next research operation is not an arbitrarily selected new WATCH: the lawful continuation is the current generator B applied again. The comparison may end with a certified obstruction, a constructive B-only equivalence upon full closure, or explicit UNKNOWN at the allowed budget.

This is **an executable bounded instance** of Boundary Math-style witnessed continuation, not proof that an autonomous engine can discover arbitrary grammars, WATCH directions, or suitable computational budgets.

## Verification and next referent

**13/13 focused new local tests passed.** Tests cover A/B inverses, B-invariant fiber, 8-step UNKNOWN, 9-step distinction, two independent cycle decompositions, B-only positive map, no premature positive conclusion, full-space scope limitation, source-witness preservation, and invalid state/budget rejection.

Next: feed this witnessed native-continuation object into Engine 2's existing multi-WATCH ledger and verify that re-entry preserves the carrier constraint `u=0`, the original two-input rules, and the distinction between B-only and A/B claims. Do not reuse an unproven cross-grammar equivalence to bridge spaces.