# Fifth-coordinate centralizer extension

[Exact construction](fifth_coordinate_lift.py) · [15 regression tests](../../network/tests/test_arc_like_fifth_coordinate_lift.py) · [independent arithmetic audit](fifth_coordinate_arithmetic_audit.py) · [mathematical terminology](TERMINOLOGY.md)

## Current mathematical referent

The preceding [fourth-coordinate theorem](HIGHER_COUPLING_LIFT.md) built a transformation of order nine commuting with both generating transformations. Introduce a new, independently chosen nine-entry fifth-coordinate coupling and determine whether the previous symmetry extends, whether its order changes, or whether a cohomological obstruction prevents the chosen triangular extension.

On the full finite-field state space, define the same generating transformations A and B. The previously admitted lower couplings are:

```
g=1: q0 rows (0,1,2), (0,2,1), (1,1,1); alpha=(0,1,1)
g=2: q0 rows (0,1,2), (1,0,2), (1,1,1); alpha=(0,0,1)

w=phi(x1,x2)=x2+alpha(x1)
q1(x1,x2)=w^2
B(x4)=x4+q2(x2,x3)
```

Every other higher coordinate remains unchanged. B uses old-state coordinates and A increments only x0.

## Exact cohomological condition

The preceding order-nine centralizer generator has lower-coordinate action

```
C(x1,x2,x3)=(x1,x2+1,x3+w^2).
```

Seek a higher correction `L(x1,x2,x3)` in the fifth coordinate. Commutation with B is equivalent to

```
L(B_lower(v,z,y))-L(v,z,y)
 = q2(z+1,y+w^2)-q2(z,y)
```

for all 81 combinations of the three possible x0 parameters and the 27 lower-coordinate states, where `B_lower` is induced by B on (v,z,y).

**Theorem for these two fixed lower systems:** this additive lift exists if and only if

```
q2(z,y)=a*z+f(y),  a in F3 and f:F3 -> F3.
```

The explicit correction is

```
L(v,z,y)=a*phi(v,z)+f(y).
```

Every lower transformation B advances phi by one and x3 by w². Substituting L into the equation verifies the commutation exactly, at every finite dimension.

For necessity, the signed 27-vertex voltage graph converts compatibility into homogeneous linear constraints on the nine q2 table entries. A spanning-forest reduction and Gaussian elimination over F3 yield **rank five** for both gains. Thus the allowable q2 space has dimension four. The displayed family is an admissible four-dimensional subspace, hence it is the entire solution space. Any rejected q2 has a concrete nonzero-voltage cycle certificate, consisting of two paths to one endpoint that require inconsistent corrections.

## Order is exactly nine, not 27

The lower centralizer acts on (w,y) by

```
(w,y) -> (w+1,y+w^2).
```

Three turns translate y by 0²+1²+2²=2 (mod 3). Thus the lower action has order nine and traverses all nine (w,y) pairs. Over nine turns the extra fifth-coordinate displacement is

```
sum_(w,y in F3²)(a*w+f(y))=0.
```

Therefore C^9 is the identity for each admitted fifth-coordinate rule. The fourth-coordinate projection already has order nine, so the full lifted transformation has **exact order nine**. At dimension three the projection still has order three; order nine first appears at dimension four.

## Complete table counts

| Outcome | Per gain | Both gains |
|---|---:|---:|
| Commuting lift of order nine | 81 | 162 |
| Admitted and genuinely x3-dependent | 72 | 144 |
| Admitted and independent of x3 | 9 | 18 |
| Cycle obstruction to this lift | 19,602 | 39,204 |
| All q2 tables | 19,683 | 39,366 |

A genuine fifth-coordinate dependence is `q2(z,y)=z+y²`, with rows (0,1,1), (1,2,2), (2,0,0). Its correction is `L(v,z,y)=phi(v,z)+y²`. The function `q2(z,y)=z*y` fails the criterion and has a signed-cycle obstruction.

## Reproducibility and scope

An independent Python calculation solved the full 27-state voltage graph for every q2 table at both gains and checked every admitted map on all 243 five-coordinate states. Its executed counts were **39,366** table decisions, **78,732** generator-commutation equations, **39,366** exact nine-turn returns, and **39,366** nonidentity third-iterate witnesses. Its output was `INDEPENDENT_27_VERTEX_LIFT_AUDIT_PASSED`.

The committed [15 tests](../../network/tests/test_arc_like_fifth_coordinate_lift.py) specify rank five, full q2 enumeration, literal obstruction replay, triangular inverses, dimensional projections, exact cyclic order, and pointed-map composition. **A GitHub CI pass has not yet been observed**.

```bash
python -m unittest network.tests.test_arc_like_fifth_coordinate_lift -v
python -m work.arc_like_maze.fifth_coordinate_arithmetic_audit
```

**Closed:** the specified triangular fifth-coordinate extension over these two lower systems, with exact maps or cycle obstructions.

**Not proved:** all higher-coupling centralizers, all choices of previous nonlinear q1, any unrestricted order-27 lifting theorem, universal inverse-construction closure, or native ARC gameplay.

**Next referent:** vary the previous fourth-coordinate function Q, preserving its actual order and lower potential, and check whether the fifth-coordinate admission rank changes. Retain the complete voltage-graph witness and the explicitly transported distinguished point.
