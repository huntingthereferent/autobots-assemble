# Nonlinear higher-coordinate couplings: centralizer extensions of order three and nine

[Standard mathematical terminology](TERMINOLOGY.md) · [Construction and obstruction certificates](higher_coupling_lift.py) · [16 regression tests](../../network/tests/test_arc_like_higher_coupling_lift.py) · [Independent arithmetic audit](higher_coupling_arithmetic_audit.py)

## Current referent

The earlier [nonconstant lower-coupling theorem](NONCONSTANT_DRIFT.md) identified exactly 36 admitted pairs consisting of a nine-entry lower coupling table and a nonzero gain. Their potentials make the lower-coordinate transformations cohomologically compatible with a translation of the third state coordinate.

The new task is to admit an **independently chosen, potentially nonlinear coupling in the fourth state coordinate** and distinguish three mathematical outcomes: no additive commuting lift, an order-three centralizer symmetry, and a commuting symmetry whose actual order is **nine**.

This is a scoped finite-field dynamical-system problem; it is not a universal centralizer classification or ARC execution.

## Generators and proposed lift

Work over `F3` with `X_d=F3^d`, `d>=3`. All additions are modulo three. Fix one of the previously admitted lower couplings `q0(u,v)` and its normalized potential `phi(v,z)`, satisfying

```text
E_u(v,z)=(v+g*(u+1), z+q0(u,v))
phi(E_u(v,z)) = phi(v,z)+1.
```

Extend the triangular transformations:

```text
A: x0 -> x0+1, other coordinates unchanged
B: x1 -> x1+g*(x0+1)
   x2 -> x2+q0(x0,x1)
   x3 -> x3+q1(x1,x2)
   xi -> xi                     i>=4.
```

Here `q1:F3² -> F3` is **any** nine-entry table, not assumed linear.

We seek the specific triangular additive lift

```text
C(x0,x1,x2,x3,...) =
  (x0,x1,x2+1,x3+K(x1,x2),...)
```

where K is independent of x0, so C commutes with A. The complete compatibility equation with B is

```text
K(E_u(v,z))-K(v,z)
    = q1(v,z+1)-q1(v,z)
for every u,v,z in F3.
```

It is a finite cohomological equation on the nine lower-coordinate states. A valid K defines a bijective, projectively coherent **commuting transformation**, but commutation alone does not specify its order.

## Exact characterization of commuting lifts

Write the earlier normalized potential as

```text
phi(v,z)=a^-1*z+alpha(v),
where a=q0(2,v) is the common nonzero last-row increment.
```

Every induced lower transformation E_u advances phi by exactly one. At a fixed lower state (v,z), the three choices u=0,1,2 lead to all three possible values of the new first coordinate v, but have the **same new potential coordinate** phi+1. Their right-hand cocycle voltage is also the same.

Consequently, any solution K must have the form

```text
K(v,z)=h(phi(v,z)).
```

The voltage must be independent of v when expressed in phi-coordinates. Equivalently, an exact solution exists **if and only if**

```text
q1(v,z)=Q(phi(v,z))+k(v)
```

for some functions `Q,k:F3 -> F3`.

Necessity follows from the three distinct E_u targets and the x2-translation derivative; sufficiency follows because Q's cyclic discrete derivative has sum zero. Fix `k(0)=0` to make this representation unique, so Q is determined by the first row of q1, and k by its row offsets.

Writing `h(0)=0` gives an exact primitive:

```text
h(w+1)-h(w)=Q(w+a^-1)-Q(w).
```

Summing the right side around the three-element field gives zero, so such h exists for every Q.

The [implementation](higher_coupling_lift.py) constructs Q, k and h directly. For a rejected table it independently constructs an explicit **nonzero-voltage signed cycle**: two paths in the nine-state graph reaching the same endpoint but requiring incompatible K-values. This is a mathematical obstruction to the **specified additive lift**, not to arbitrary state conjugacies.

## Second threshold: the order of the commuting map

The third iterate of C returns x2 to its original value. Its higher-coordinate change is

```text
C^3(x)_3 = x3 + tau,
tau = h(0)+h(1)+h(2) = a^-1 * sum_w Q(w)   (mod 3).
```

The trace is independent of the initial (v,z), and adding a constant to h cannot change it: three copies of that constant vanish in F3.

Therefore:

- If `tau=0`, the corrected generator C has **order three**.
- If `tau!=0`, C commutes with A and B but has **order nine**. Its third iterate is a nonidentity translation of x3; its ninth iterate is the identity.
- If q1 does not factor as Q(phi)+k(v), no commuting lift exists **in the specified additive form**.

This is an obstruction to a three-element cyclic **splitting**, not an obstruction to the existence of a commuting state transformation when the order-nine case applies. The trace is a distinct mathematical witness from the signed-cycle obstruction.

## Complete finite table counts

For each previously admitted q0 and gain, there are `3^9=19,683` fourth-coordinate q1 tables.

A factorized table is uniquely determined by three values of Q and the two free values k(1),k(2), since k(0)=0: `3^3 * 3^2 = 243` commuting lifts.

Among the `3^3=27` possible Q, exactly `3^2=9` satisfy `sum Q=0`. Thus:

| Outcome | q1 tables per admitted lower system |
|---|---:|
| Exact order-three symmetry | **81** |
| Exact order-nine commuting symmetry | **162** |
| No prescribed additive commuting symmetry | **19,440** |
| **Total** | **19,683** |

The previous layer admitted 36 lower-table/gain pairs. Applying this theorem to all of them gives **2,916 order-three**, **5,832 order-nine**, and **699,840 obstructed** combinations among **708,588** possible lower/upper-table pairs. These are combinatorial counts under the explicit finite grammar, not verified equivalence-class counts.

### Two concrete nonlinear examples

Take the admitted nonconstant lower table with gain one:

```text
q0 rows:
 (0,1,2)
 (0,2,1)
 (1,1,1)
phi(v,z)=z+alpha(v), alpha=(0,1,1)
```

**An exact order-three lift.** Choose `Q(w)=w`, `k=(0,0,2)`; then

```text
q1 rows:
 (0,1,2)
 (1,2,0)
 (0,1,2)
h(w)=w;  sum h=0.
```

The fourth-coordinate increment varies with both x1 and x2, and the corrected point is transported explicitly.

**An exact order-nine lift.** Choose `Q(w)=w²`, `k=(0,0,0)`; then

```text
q1 rows:
 (0,1,1)
 (1,1,0)
 (1,1,0)
h(w)=w²;  sum h=2.
```

The corrected generator satisfies the commutation equations at every dimension, but `C³` translates x3 by two. It cannot be described as an order-three lift by changing the arbitrary integration constant.

## Independent evidence and pointed provenance

[Independent checker](higher_coupling_arithmetic_audit.py) does not import the classifier or its helper functions. It separately solves the voltage equations for **all 19,683 upper tables at each of two distinct admitted lower systems**, representing gains 1 and 2. It then checks both generating transformations and complete cyclic returns for every admitted upper rule on the full 81-state fourth-dimensional space.

Its actual executed outcome was:

```text
Per gain:
  81 order-three lifts
  162 order-nine lifts
  19,440 voltage-obstructed cases
Both gains together:
  78,732 generator-commutation checks
  39,366 full cyclic-return checks
Status: INDEPENDENT_GRAPH_AND_ACTION_AUDIT_PASSED
```

[Sixteen focused repository regression tests](../../network/tests/test_arc_like_higher_coupling_lift.py) cover table enumeration, explicit order-nine third iterates, both generator commutations, signed-cycle certificate validation, comparison with the earlier linear higher coupling, reversibility and projection, and pointed factor composition. They have been committed but **have not yet been independently confirmed as passing against a complete GitHub checkout or CI**.

A pointed correction carries a four-digit distinguished point (with zero higher tail) because a nontrivial C shifts both x2 and x3. The pointed-conjugacy object preserves the literal exponent factors, rejects unsupported powers, and requires exact transport of the chosen point. An order-nine correction cannot be silently shortened to a three-turn marked cycle.

## Preserved boundary and next referent

**Proved for this family:** the complete nine-entry fourth-coordinate coupling classification for additive corrections of the displayed form, with explicit commuting maps, exact cyclic orders, or signed-cycle obstructions.

**Preserved:** the admitted nonconstant lower coupling, all-depth triangular inverse and projection identities, and separately named origin-preserving and origin-moving conjugacies.

**Unknown:** arbitrary nonlinear corrections depending on x3, further nonzero higher-coordinate rules, alternative centralizer actions on obstructed systems, general inverse-construction closure, and native ARC execution.

**Next mathematical referent:** admit a nonzero fifth-coordinate coupling depending on x3 and ask whether an existing order-nine generator requires an additional higher-coordinate correction. Compute the exact obstruction without assuming that the previously established order is preserved.
