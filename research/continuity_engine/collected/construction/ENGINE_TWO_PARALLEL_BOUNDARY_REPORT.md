# Engine 2 — parallel constructed-space Boundary Math

**Date:** 9 October 2026. **Status:** completed local bounded experiment; no GitHub repository edits. **Current referent:** follow an inconclusive invariant WATCH into a justified, constructed candidate-map space, and distinguish equivalence of underlying laws from the transport of particular selected centralizer symmetries. This work is complementary to the repo's newly committed `MIXED_CENTRALIZER_COMPOSITION.md`; it does **not** supersede or validate that repository's pending CI checks.

## Starting comparison and native mathematical constraints

Consider the two established nonconstant lower-coupling systems' gain-one example only. Fix the lower nine-entry coupling

`q0 = (0,1,2, 0,2,1, 1,1,1)`, gain `g=1`, normalized offsets `k=(0,0,0)`, the nine-entry fifth coupling `q2=0`, and an entirely zero higher-coordinate tail. Vary **only** the quotient table `Q=(Q(0),Q(1),Q(2))`, with each entry in F3. There are exactly 27 such quotient tables.

For a state `(u,v,z,y,tail)`, the A and B operations act as

```
A(u,v,z,y,tail) = (u+1, v, z, y, tail)
B(u,v,z,y,tail) = (u, v+u+1, z+q0(u,v), y+Q(z+alpha(v)), tail)
alpha=(0,1,1)                 [all arithmetic mod 3]
```

The existing comparison `Q=(0,0,0)` against `Q=(0,1,2)` had equal B/B³/B⁹ fixed-state counts and exact origin-reachable graph alignment. Those **do not by themselves prove** full-state conjugacy. The next WATCH is justified by the goal (explicit full-state labeled conjugacy), not by a mandate that some WATCH must eventually differ.

## Engine 2 constructs a new bounded mathematical space

Instead of requesting that Engine 1 remake itself or searching for an arbitrary new agent, construct a finite-dimensional space of candidate maps

```
H_(lambda,f)(u,v,z,y,tail) = (u,v,z,lambda*y + f(v,z),tail)
lambda in F3^× = {1,2}
f:F3² -> F3, normalized by f(0,0)=0.
```

This is **two possible scales plus nine potential values**, subject to exactly 27 compatibility equations:

```
f(E_u(v,z)) - f(v,z) = Q_target(w) - lambda*Q_source(w)
E_u(v,z) = (v+u+1, z+q0(u,v))
w = z + alpha(v)
```

Because `f` is independent of `u`, it also automatically respects generator A. The solver constructs a potential with full signed-path witnesses or returns two incompatible paths, a replayable obstruction **to this candidate-map grammar**. It never converts that local construction wall into global nonconjugacy.

Let `tau(Q)=Q(0)+Q(1)+Q(2) mod 3` be the trace. Applying B three times leaves all coordinates fixed except `y`, which is translated by `tau(Q)`. Hence 0 versus nonzero trace gives a complete-state conjugacy obstruction (`Fix(B³)` differs).

For equal zero/nonzero type, choose an invertible `lambda` so `tau(Q_target-lambda*Q_source)=0`. The space of zero-trace differences is the 2D kernel of the linear functional `sum Q`. It is spanned by the two differences `(1,2,0)` and `(1,0,2)`; each has a directly verified potential satisfying all 27 equations. By linearity, every zero-trace difference does, so the affine-gauge construction is **sufficient**, not merely successful on selected examples. Each constructed conjugacy is bijective, fixes the distinguished zero point, and commutes with A and B for every state.

Because the fifth coupling and higher tail are fixed at zero, the same explicit four-coordinate formula works at every higher finite dimension `d>=4`; this all-depth statement does not rely on extrapolating 81 observed points without a formula.

## Result — closed classification for this narrowly declared family

| Result | Count |
| --- | ---: |
| Quotient tables Q | 27 |
| Ordered comparisons | 729 |
| Exact ROOT-PRESERVING full-state conjugacies constructed | **405** |
| Full-state inequivalence proved by Fix(B³) | **324** |
| Unresolved comparisons in the declared family | **0** |
| Rooted full-state classes | **2** (sizes **9**, **18**) |

An **independent** canonical labeled A/B graph classifier (not importing the potential solver) exhaustively recovers the same 2 classes in dimension four. Its root orbit sizes are 27 for each of the 9 zero-trace systems and 81 for each of the 18 nonzero-trace systems. The explicit affine potential formulas provide the extension beyond dimension four.

### Positive concrete witness

For `Q_s=(0,0,0)` and `Q_t=(0,1,2)`, choose `lambda=1` and

```
f(v,z) rows for v=0,1,2 and z=0,1,2:
  (0,0,1)
  (0,1,0)
  (0,1,0)
```

The resulting `H` is a verified bijective, zero-point-preserving full-state conjugacy. The same experiment **does not** mean the two Q tables are identical or that arbitrary centralizer choices are identified.

### Why one local obstruction is not a universal obstruction

For `Q_s=(0,0,1)` and `Q_t=(0,0,2)`, fixing `lambda=1` yields a replayable incompatibility among the potential equations. Yet choosing `lambda=2` yields the exact map `H(u,v,z,y,tail)=(u,v,z,2*y,tail)`—an admitted rooted full-state conjugacy. The first obstruction belongs to the additive-only subgrammar, not to the system as a whole.

## Boundary Math one layer up: law maps versus selected symmetry transport

The new mixed-centralizer result from GitHub shows that the same law can admit distinct centralizer maps, and that these maps need not commute with one another. The parallel experiment asks a **different** question: if `H` is a proved law conjugacy, does it necessarily intertwine *specified* selected symmetries?

For the canonical zero-fifth-coupling selection in this family, define

```
C_Q(u,v,z,y,tail) =
    (u,v,z+1,y + Q(z+alpha(v))-Q(0),tail).
```

Each `C_Q` commutes with its own A and B. For each of the 405 explicitly constructed normalized `H` maps, directly check whether

```
H ○ C_source = C_target ○ H.
```

| Property of this particular constructed H | Ordered pairs |
| --- | ---: |
| Also intertwines the canonical selected symmetries | **135** |
| Conjugates laws, but does **not** intertwine these selected symmetries | **270** |

Concrete witness: `Q_s=(0,0,0)`, `Q_t=(1,0,2)`, root `x=(0,0,0,0,0)`:

```
H(C_source(x)) = (0,0,1,1,0)
C_target(H(x)) = (0,0,1,0,0).
```

Nevertheless, `H C_source H^-1` remains a valid centralizer of the *target* A/B generating system. This is **not** a counterexample to the law conjugacy; it shows that the particular preselected canonical centralizer is a separate research object. Nor does it prove there is no alternative law conjugacy which intertwines the two selected maps. The results are scoped to the normalized constructed H family and specified C choices.

## Engine 2 shape/function lesson

- **Shape:** an admitted mathematical family plus spaces of unknown witness parameters (here nine `f` values and a unit scaling), not merely a catalog of existing laws.
- **Function:** Boundary Math WATCHes on fixed words, explicit correspondence, and selected symmetry transport. Each WATCH retains its own native evidence.
- **Movement:** equality of a limited invariant leads to a *question-justified* witness construction, not equivalence by declaration; a local subgrammar obstruction leads to another already admitted candidate if it exists.
- **Next layer:** law-conjugacy witnesses can be used to transport centralizer maps. Testing whether transported maps lie in a chosen canonical selected family is separate from proving that they commute with A/B or with each other.

## Verification and limitations

All **62/62 local Engine 2 regression tests** passed when run together, including the 17 new tests, the earlier coupling/window/zero-trace local tests and six fixed-word boundary tests. The independent direct graph classifier agrees. These are **local** outcomes. No changes were made to GitHub; no CI status is inferred for the other window's commits. The 27-law theorem is for the fixed gain-one lower table, zero offsets, zero fifth rule, and zero higher tail only. It says nothing about arbitrary q0, arbitrary q2, cross-grammar equivalence, universal construction closure, or native ARC execution.

**Next referent:** witness-preserving transport of *selected* centralizer maps along newly proved cross-law conjugacies, without assuming their canonical selected representatives match. Preserve the failure/wall of a particular map choice and distinguish it from an obstruction to all possible intertwiners.