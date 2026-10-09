# Zero-trace fourth-coordinate systems: fifth-coordinate correction and cyclic order

[Finite-field terminology](TERMINOLOGY.md) · [Exact classifier and pointed maps](zero_trace_lift.py) · [Independent full-matrix audit](zero_trace_arithmetic_audit.py) · [13 focused tests](../../network/tests/test_arc_like_zero_trace_lift.py)

## Current referent and question

The [preceding variable fourth-coordinate theorem](VARIABLE_FOURTH_LIFT.md) classified the fifth-coordinate extension for all **nonzero-trace** fourth-coordinate quotients. There the corrected lower map already had order nine, and every admitted extension retained that order.

Now admit the complementary **zero-trace** fourth-coordinate quotient family, still over the two fixed, proven nonconstant lower systems. The lower corrected map has order **three**. The central question is whether a newly admitted fifth-coordinate correction also has order three, raises the order to nine, or is obstructed by the cohomological equation.

A difference between correction choices on disconnected graphs is not a difference between the underlying world laws; the chosen correction itself must remain part of the witness.

## The precise finite-field system

Use the two previously admitted nonconstant couplings `q0` with gains g=1 or g=2:

```text
g=1: q0 rows (0,1,2), (0,2,1), (1,1,1); alpha=(0,1,1)
g=2: q0 rows (0,1,2), (1,0,2), (1,1,1); alpha=(0,0,1)

w=phi(v,z)=z+alpha(v), where v=x1 and z=x2
q1(v,z)=Q(w)+k(v), with k(0)=0
sum_(w in F3) Q(w)=0.
```

Of 27 functions Q, exactly nine have zero trace. For each Q there are nine normalized row offsets k. That gives **81 fourth-coordinate systems per gain, 162 across both gains**.

On `F3^d` the generating transformations A and B remain triangular and invertible:

```text
A: x0 -> x0+1, other coordinates unchanged

B: x1 -> x1+g*(x0+1)
   x2 -> x2+q0(x0,x1)
   x3 -> x3+q1(x1,x2)
   x4 -> x4+q2(x2,x3)
   xi -> xi                  for i>=5.
```

All increments depend on old coordinates. The arbitrary new fifth-coordinate coupling `q2:F3² -> F3` has nine entries.

The previously proved commuting lower transformation fixes x0,x1 and sends

```text
C_lower(v,z,y)=(v,z+1,y+h(w)),  y=x3
h(w)=Q(w)-Q(0).
```

Since `sum Q=0`, `C_lower^3=id`: the fourth-coordinate projection now has **order three**, not nine.

## The 27-state compatibility equation

A proposed fifth-coordinate extension changes x4 by `L(v,z,y)`, with L independent of x0. Let `E_u` be the lower part of B for each u=x0:

```text
E_u(v,z,y)=
  (v+g*(u+1), z+q0(u,v), y+Q(w)+k(v)).
```

The exact commutation condition is:

```text
L(E_u(s))-L(s)=q2(C_lower(s))-q2(s),
for each u in F3 and s=(v,z,y) in F3³.
```

This is a system of **81 linear equations** in the 27 values of L and the nine entries of q2, or **36 finite-field unknowns**.

The induced graph on the 27 states is not always connected. Of the 162 fourth-coordinate systems, **144 have one connected component and 18 have three**. Every connected component contributes an independent constant to a solution L. Thus a solution is not always unique up to a *single* global constant.

For any fixed q2, a signed-cycle voltage contradiction obstructs the specified correction. A successful graph solution supplies L and all component labels. Its component constants can be varied without changing q2 or breaking commutation.

## Exact admissibility rank classification

The independent 81-by-36 finite-field matrix reduction and a separate spanning-forest voltage calculation agree on the full rank distribution.

| Connected components | Constraint rank on q2 | Fourth-coordinate systems (both gains) | Admitted q2 tables per system |
|---|---:|---:|---:|
| 1 | 3 | 12 | 729 |
| 1 | 4 | 24 | 243 |
| 1 | 5 | 36 | 81 |
| 1 | 6 | 72 | 27 |
| 3 | 3 | 2 | 729 |
| 3 | 4 | 4 | 243 |
| 3 | 5 | 4 | 81 |
| 3 | 6 | 8 | 27 |
| **Total** | | **162** | |

The number of admitted q2 tables for any individual configuration is `3^(9−rank)`. Across the 162 configurations, there are **22,410 admissible (fourth-coordinate system, fifth-coordinate table) combinations**.

This result is about the **specified additive triangular lift**, not a classification of every conceivable centralizer transformation. Rejected q2 tables carry literal two-path signed-cycle obstructions.

## The order-three versus order-nine distinction

Because the old corrected lower map has order three, its third iterate returns (v,z,y) to the original lower state. The fifth-coordinate displacement after three iterations is

```text
T_L(s)=L(s)+L(C_lower(s))+L(C_lower²(s)), mod 3.
```

The full corrected map therefore has order **three** if `T_L(s)=0` for all 27 lower states, and order **nine** otherwise. It cannot have higher order in this construction: repeating the three-turn displacement three times returns x4.

The trace `T_L` depends linearly on L. The space of compatible L consists of one normalized solution for q2 plus one independent constant on each E-component.

This produces three genuinely distinct outcomes for an **admitted q2**:

| Admissible corrected orders | (System, q2) combinations |
|---|---:|
| Only order three | **9,918** |
| Only order nine | **11,304** |
| Both orders, with different compatible L | **1,188** |
| **Total** | **22,410** |

Equivalently, **11,106 combinations permit an order-three correction** and **12,492 permit an order-nine correction**, with 1,188 in their intersection. These are counts of coupling combinations, not counts of distinct maps or conjugacy classes.

The 1,188 ambiguous cases occur in **12 fourth-coordinate systems**, each having three graph components. Their independent constants produce a nonzero three-turn trace for some choices and zero trace for others. Thus the same generating transformations and the same q2 can possess different explicitly chosen commuting symmetries, one of order three and one of order nine.

This is why a connectedness hypothesis that was automatic in the earlier order-nine analysis must **not** be carried into this layer.

## Three concrete witnesses

All three examples below use gain g=1 and the previously fixed nonconstant q0.

**Order three only:**

```text
Q=(0,0,0), k=(0,0,1), q2=all zero.
Graph: 1 component, q2 rank 5.
Every compatible fifth-coordinate correction has order three.
```

**Order nine only:**

```text
Q=(0,1,2), k=(0,0,1)
q2 rows: (2,1,0), (2,1,0), (2,1,0).
Graph: 1 component, q2 rank 6.
The third iterate translates x4 nontrivially; no constant can cancel it.
```

**Both orders for the same fifth-coordinate table:**

```text
Q=(1,0,2), k=(0,0,0), q2=all zero.
Graph: 3 components, q2 rank 6.
One component-constant choice has order three;
another has order nine.
```

All admitted transformations commute with both generators at every dimension, have triangular inverses and preserve projections. The distinguished point is five-dimensional with zero tail, and is transported explicitly by the selected correction. A three-turn pointed cycle is not substituted for a nine-turn cycle or vice versa.

## Independent calculations and verification boundary

Two independent mathematical implementations agreed:

1. **Signed-voltage spanning forests:** solve path equations on the 27-state graph, preserve connected components, compute the complete q2 kernel, and evaluate third-iterate traces of all basis and gauge vectors.
2. **Direct 81-by-36 elimination:** independently row-reduce all 162 systems, project the kernel onto q2, distinguish the component-gauge kernel, and recompute all third-iterate traces.

The second calculation reproduces the exact rank/component histogram and totals, using **624 nontrivial coupling-basis vectors**, **198 correction-gauge vectors**, and **22,194 third-iterate trace evaluations**. The first method yields identical admissibility and order categories.

The [independent executable audit](zero_trace_arithmetic_audit.py) records the direct-matrix route without importing the production classifier or the earlier transition interpreter. The [13 focused regression tests](../../network/tests/test_arc_like_zero_trace_lift.py) specify rank counts, exact correction selection, positive third/ninth iterates, two-path obstructions, projected generators and inverses, and pointed-conjugacy composition.

**Verification limit:** independent finite-field calculations support the classification, but this report does **not** claim that the newly committed repository tests passed or that GitHub CI ran. Any CI result must be inspected separately.

## Preservation, limitations, and next referent

**CLOSED for the declared family:** complete cohomological admission and available cyclic-order classification for 162 zero-trace fourth-coordinate systems and arbitrary nine-entry fifth-coordinate couplings, with component gauge freedom and exact witnesses.

**PRESERVED:** the preceding order-nine fourth-coordinate theorem, both nonconstant q0 systems, literal signed-cycle obstructions, projectively coherent inverses, and explicit distinguished points.

**UNKNOWN:** zero-trace fourth-coordinate systems for all previously admitted q0 beyond the two fixed exemplars; general nonlinear higher-coordinate corrections; alternative centralizer maps outside this additive triangular form; universal inverse-construction stopping and native ARC execution.

**NEXT:** compare zero-trace and nonzero-trace families through a single witness-preserving classification interface. It must report four independent properties—coupling admission, component count, possible cyclic orders, and mark transport—rather than collapsing them into one status. Only then should additional higher-coordinate rules be admitted.
