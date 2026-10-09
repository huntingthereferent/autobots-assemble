# Inverse A/B — root transport on construction processes

**Status:** Integrated root-transport research witness in `huntingthereferent/language-network`. No native ARC gameplay, game solve, or universal A/B construction theorem is implied.

## Referent

The existing [process solver](process_alignment.py) compares eventually periodic streams of F₃ coupling rules under a **root-normalized**, full-state diagonal A/B alignment. It requires the incoming scalar at the first coupling to be exactly `s[-1] = 1`.

That equivalence **does not descend through a plain shift** of the rule stream. Resetting `s[-1]` to one after removing a rule loses the incoming alignment at the boundary. This is a mathematical obstruction, not a failed test to ignore.

## Construction: move the boundary datum

For process rule streams `P=(p₀,p₁,...)` and `Q=(q₀,q₁,...)`, an alignment carries an incoming scalar `b ∈ {1,2}` and scalars `s₀,s₁,... ∈ {1,2}`, such that

```text
q_i(s_(i-1)·u) = s_i·p_i(u)    for every i >= 0 and u in F₃
s_(-1) = b
```

The earlier *ordinary rooted* relation is the special case `b=1`. After shifting both processes by `k` rules, the proper transported boundary is **`b' = s_(k-1)`**, and the remaining scales are `s'_i = s_(k+i)`.

```text
Before:   P =====[s0]====[s1]====[s2]====...
          Q =====[s0]====[s1]====[s2]====...

Shift 1:  P' --[incoming s0]--[s1]====[s2]====...
          Q' --[incoming s0]--[s1]====[s2]====...
```

The indexed equality is preserved for **all** remaining couplings by substitution. The finite-state coinductive solver confirms whether the eventually periodic scale sequence exists and produces a repeatable lasso witness. Arbitrarily long finite agreement is not promoted to an all-depth proof.

## The necessary distinction: an interface is part of the world

An incoming `b ≠ 1` is **not by itself** a conjugacy of the old, normalized, shifted A/B systems. The implementation makes the boundary explicit with a **new marked-root A/B world**:

```text
A(x)_0 = x_0 + 1
B_g(x)_1 = x_1 + g·(x_0 + 1)
B_g(x)_(i+2) = x_(i+2) + p_i(x_(i+1))
```

For source boundary gain `gₚ`, target gain `gᵩ`, and incoming scalar `b = gᵩ/gₚ`, the map

```text
F(x_0,x_1,x_2,x_3,...) = (x_0,b·x_1,s₀·x_2,s₁·x_3,...)
```

is an exact bijective, projection-compatible conjugacy of the **marked** A/B worlds whenever the coupling equations hold. Marked-root transport constructs a **new rooted representation**, not literal restriction of the original actions to a shorter state tuple.

Marked morphisms compose by multiplying incoming and outgoing scalar sequences pointwise. Their inverses are pointwise reciprocals. Along with identities they form an alignment groupoid on the specified marked objects.

## Results on all 81 period-two rule templates

| Equivalence or operator test | Outcome |
|---|---:|
| Strict root-normalized diagonal equivalence classes | **34** |
| Boundary-transported diagonal equivalence classes | **23** |
| Boundary-transported class sizes | 1×1, 4×2, 18×4 |
| Classes fixed by simultaneous one-step shift | **5** |
| Paired classes interchanged by shift | **9 pairs** |
| Aligned marked pairs examined, with repeat marks included | **276** |
| Integration-specific regression tests | **14** |

On the finite **strict period-two** domain, the shift acts as an involution on the boundary-transported quotient. It is **not** a group action of invertible shifts on all eventually periodic streams with arbitrary stems, where dropping a finite prefix is generally not invertible.

A concrete example:

```text
P = [ZERO, (0,0,1)] repeated
Q = [ZERO, (0,1,0)] repeated
```

The original rooted systems align with `incoming=1`, and one compatible witness uses `s₀=2`. After shifting one rule, the **old** root-normalized comparison fails. Transporting `incoming=2` restores the coupling equation, and explicitly marking the target's new boundary gain gives a genuine A/B conjugacy of the augmented worlds.

Adding the same linear coupling rule to two previously aligned processes can still destroy the marked equivalence; the counterexample survives both incoming scales. Even 75 matching couplings can hide a later break. Therefore **not all process construction operators** have become admissible.

## Closure statement and limitation

**Closed at this layer:** the space of boundary-marked, coinductively diagonally aligned, eventually periodic rule streams is preserved by paired shifts **when the alignment witness is transported with the root**. For strict period-two streams, this yields the 23-class finite quotient and the shift cycles above.

**Not claimed:** shift preserves the old rooted quotient, full unmarked A/B world conjugacy after shift, all arbitrary/nonperiodic processes, non-diagonal alignments, closure under arbitrary rule addition, a universal terminal construction, or an ARC solve.

## Reproduction

From the repository root:

```bash
python -m unittest -v network.tests.test_arc_like_root_transport
```

Files: [`root_transport.py`](root_transport.py) (marked A/B worlds, finite-state coinductive certificates, transport, composition, inversion); [`network/tests/test_arc_like_root_transport.py`](../../network/tests/test_arc_like_root_transport.py) (14 checks, full-state and pairwise comparisons).

**Integration boundary:** `root_transport.py` imports the existing `PeriodicProcess` and `next_scales` from [`process_alignment.py`](process_alignment.py). It does not replace that module's existing root-normalized API, because the incoming boundary datum and marked-world distinction must remain explicit. The finite classifications do not prove arbitrary unmarked-world conjugacy.
