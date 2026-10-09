# Inverse A/B — gauge and root-transport interchange

**Current referent:** the operations that change entire eventually periodic A/B construction processes. Previous work established separately (1) projectively compatible coordinate gauges, and (2) coinductive root transport for marked A/B processes. This experiment tests their **composition**, including the alignment witness itself.

## The marked mathematical object

A process `P` is a finite rule stem followed by a repeating tail of coupling tables `p_i:F₃→F₃`, with `p_i(0)=0`. Its **marked root gain** `g∈{1,2}` changes only the incoming B transition:

```text
A(x)_0 = x_0 + 1
B_g(x)_1 = x_1 + g*(x_0+1)
B_g(x)_(i+2) = x_(i+2) + p_i(x_(i+1))
```

An aligned **arrow**, not merely a pair of process descriptions, contains:

- source marked object `(P,g)`;
- target marked object `(Q,h)`;
- exact coinductive alignment witness `w=(b,s₀,s₁,...)`, with `b=h/g`.

The witness equation is `q_i(s_(i-1)u)=s_i p_i(u)` for all `i≥0` and `u∈F₃`, taking `s₋₁=b`. A witness is a finite head plus periodic lasso, verified for the complete infinite rule stream. An arbitrary finite prefix alone is not admitted.

## Two operations, one commuting square

A boundary-aware gauge `U=(u₋₁,u₀,u₁,...)` changes the source process according to `P'_i(u_(i-1)v)=u_i P_i(v)` and changes its marked gain to `u₋₁g`. The target may independently use a gauge `V`.

The **same original arrow** is transformed using the exact scalar relation

```text
w'_-1 = v_-1 * w_-1 * u_-1^-1
w'_i  = v_i  * w_i  * u_i^-1                 (all in F₃)
```

Root transport by `k` rules keeps the **literal tail of this witness**, rather than invoking the solver again and possibly choosing a different valid alignment:

```text
S_k(w).incoming = w_(k-1)             k > 0
S_k(w).scale_i  = w_(k+i)
```

When the source gain on the transported result is chosen as `u_(k-1)`, the following square commutes exactly:

```text
      marked arrow (P → Q)
         |             |
    apply U,V         shift k
         |             |
         v             v
      gauged arrow    shifted arrow
         |             |
    shift k with     apply shifted
    source mark      gauges U,V
    u_(k-1)              |
         |             |
         +------=------+
```

Equality here includes both infinite rule streams, both actual marked gains, and the entire ultimately periodic alignment scalar sequence. This is stronger than checking a quotient label or a numerical return period.

## Results and proof boundaries

| Finite audit | Observed |
|---|---:|
| Boundary-aware period-two gauge schedules | 8 |
| Two-rule process templates | 81 |
| Gauge compositions checked against direct application | 5,184 |
| Gauge/shift interchange squares on a nonidentity morphism | 256 |
| Focused integration regression tests | 11 |

The eight gauges form `C₂ × C₂ × C₂` under coordinatewise multiplication. More generally, permitted periodic `F₃` unit scales and incoming marks are closed under multiplication and inverse, and combining them with a witness-aware shift obeys the displayed interchange equation **algebraically for all admitted dimensions**.

Focused tests also verify:

- all marked A/B transitions in finite full state spaces at depths 3–7;
- composed and reversed witness morphisms, with compatible middle objects;
- compatibility of shifting a composed arrow with composing shifted arrows;
- stemmed, not only strictly periodic, process streams;
- ambiguity of zero-rule alignments: a shift keeps the original witness, not a newly selected one;
- a hard rejection if an incoming gain is silently reset to one;
- the existing counterexample showing rule addition can still break diagonal equivalence.

**CLOSED (declared operator layer):** periodic coordinate-gauge transformations compose into a closed group, and verified, witness-carrying simultaneous shifts commute with gauge changes when incoming marks are transported.

**NOT a general group action of shift on unmarked process objects:** the source gain after moving the root must be chosen and an actual witness must be carried. In processes with arbitrary finite stems, discarding a prefix is not generally invertible. A shift of a raw process description alone cannot establish a valid transported A/B morphism.

**UNKNOWN / OPEN:** unrestricted addition of coupling tables still breaks previously valid equivalence. Arbitrary nonperiodic rule oracles, non-diagonal conjugacies, a maximal family of possible process operators, universal A/B closure, and native ARC game execution are not established.

## Artifacts and reproducibility

- [Implementation](marked_operator_system.py)
- [Regression tests](../../network/tests/test_arc_like_marked_operator_system.py)
- [Previous root-transport certificate](ROOT_TRANSPORT.md)
- [Existing process operator contract](process_operators.py)

Run from repository root:

```bash
python -m unittest network.tests.test_arc_like_marked_operator_system -v
```

**Next referent:** determine whether the witness-carrying marked-arrow system admits a nontrivial *operator-level* quotient that is complete for a justified family of transformations. Do not erase boundary or witness provenance merely to force a smaller class count.
