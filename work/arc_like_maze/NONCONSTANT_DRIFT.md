# Cohomological criterion for a corrected translation with nonconstant coupling

[Mathematical terminology](TERMINOLOGY.md) · [Exact construction and signed-cycle certificates](nonconstant_drift.py) · [16 focused tests](../../network/tests/test_arc_like_nonconstant_drift.py) · [Independent full table audit](nonconstant_drift_arithmetic_audit.py)

## Current referent

The preceding [corrected-translation theorem](CORRECTED_TRANSLATION.md) gives an explicit centralizer action when the lower coordinate has constant nonzero drift, and an obstruction when that drift vanishes and a higher coefficient reads the coordinate. The new question is whether the same construction survives **nonconstant** lower-coordinate increments.

We consider the entire nine-entry grammar for the first lower coupling and distinguish an explicitly prescribed *additive triangular lift* from arbitrary unknown conjugacies.

## Transformation system and proposed symmetry

Work over the prime field `F3`. On every complete state space `F3^d` for `d>=3`, define two invertible transformations:

```text
A: x0 -> x0+1, others unchanged

B: x0 -> x0
   x1 -> x1+g*(x0+1)             g in {1,2}
   x2 -> x2+q0(x0,x1)            arbitrary q0:F3² -> F3
   x3 -> x3+b*x2                when x3 exists
   x4 -> x4+c*x2                when x4 exists
   xi -> xi                     for i>=5
```

The increments depend only on **old coordinates**. This is an exact finite-stem instance of the existing two-predecessor triangular transformation grammar, with complete dimensional projections and inverses.

Seek a *particular class* of centralizer symmetries that fixes x0 and x1, translates x2 by r, and corrects the next coordinates using a function of the lower state `(x1,x2)`:

```text
F_r(x0,x1,x2,x3,x4,...) =
    (x0,x1,x2+r,
     x3+b*K_r(x1,x2),
     x4+c*K_r(x1,x2),...)
```

If b=c=0, every q0 permits the uncorrected translation and imposes no cohomology equation. Assume henceforth that at least one higher coefficient is nonzero, so a correction is necessary.

## The finite cohomological equation

Set `u=x0`, `v=x1`, `z=x2`. The lower-coordinate permutation induced by B at fixed u is:

```text
E_u(v,z)=(v+g*(u+1), z+q0(u,v)).
```

An additive correction for the translation r=1 exists exactly if there is a potential `phi:F3² -> F3` satisfying **all 27 directed compatibility equations**

```text
phi(E_u(v,z)) - phi(v,z) = 1 mod 3,
for every u,v,z in F3.
```

The first generator A forces a correction independent of u. The second generator B gives the displayed equation; a b- or c-coordinate correction divided by its nonzero coefficient must obey it.

Equivalently, assign voltage +1 to each directed edge E_u and -1 to its inverse. A potential exists precisely when **every signed closed walk has total voltage zero**. Inconsistent walks are concrete mathematical obstruction certificates—not an inference from a limited search depth.

## Exact closed-form admission condition

Let `q0(u,v)` be indexed by u (row) and v (column). For any fixed gain g, the nonzero translation admits such a correction **if and only if** the following three conditions hold:

```text
1. q0(2,v) = a in {1,2}, constant for every v
2. q0(0,0)+q0(0,1)+q0(0,2) = 0 mod 3
3. q0(1,v)+q0(0,v-g) = 2*a mod 3 for every v.
```

Here all subscripts use addition modulo three. This is not just a sufficient construction.

**Proof of necessity.** Since `E_2(v,z)=(v,z+q0(2,v))`, an equation requiring phi to increase by one forces all three values `q0(2,v)` to be nonzero. For each v, it also forces phi to be affine in z with slope `q0(2,v)^{-1}`. The E0 equation changes v by the nonzero gain g; therefore all three slopes must agree. Thus the entire last row is a single nonzero value a.

Normalize the potential as `phi(v,z)=a^{-1}z+alpha(v)`. Its E0 equation requires

```text
alpha(v+g)-alpha(v) = 1-a^-1*q0(0,v).
```

Summing around the three-cycle of v gives condition 2. Comparing the E0 equation with the reverse v step in E1 gives condition 3. These conditions are also sufficient, since they make all E0, E1 and E2 equations hold.

The normalized alpha is uniquely obtained by setting `alpha(0)=0` and following the E0 cycle. That is why a potential can be constructed algebraically rather than guessed by trial and error.

## Exact corrected group action

When the conditions hold, set

```text
phi(v,z) = a^-1*z + alpha(v)

K_r(v,z) = r*phi(v,z) + a^-1*binom(r,2),
where binom(0,2)=0, binom(1,2)=0, binom(2,2)=1.
```

The equation for phi implies `K_r(E_u(v,z))-K_r(v,z)=r`, which proves `F_r` commutes with B. It commutes with A by independence of u.

Because translating z by s changes the potential by `a^{-1}s`, the binomial identity yields `F_r∘F_s=F_{r+s}`, the inverse is `F_{-r}`, and `F_1^3=` identity. The transformations are bijective, triangular, and projectively coherent at every dimension of the specified system.

### A genuinely nonconstant admitted example

For `g=1`, choose rows:

```text
q0(0,*) = (0,1,2)
q0(1,*) = (0,2,1)
q0(2,*) = (1,1,1)
```

This gives `a=1`, `alpha=(0,1,1)`, and `phi(v,z)=z+alpha(v)`. The correction depends on x1 as well as x2. It is not the earlier constant-drift formula in disguise.

## Two distinct ways the admission can fail

A zero last-row entry yields a B-fixed-fiber obstruction of the kind already identified in the constant-drift layer. But this is **not the only obstruction**.

For gain `g=1`, take these rows:

```text
q0(0,*) = (0,0,0)
q0(1,*) = (0,0,0)
q0(2,*) = (1,1,1)
```

The last row is nonzero and the first row has zero sum. Nevertheless E0 shifts v by +1 and E1 shifts v by -1 while **both leave z unchanged**. Their two-step composition returns `(v,z)` to itself. The potential equation would require

```text
phi(E1(E0(v,z))) - phi(v,z) = 1+1 = 2 mod 3,
```

contradicting the fact that the start and end points are identical.

This is a *nonzero signed-cycle-voltage obstruction*. Its existence rejects the specified additive correction regardless of the values of the higher coordinates. The implementation records two literal paths with equal endpoints but different accumulated voltages and checks each edge.

## Exhaustive completeness within the admitted grammar

For each fixed gain, q0 has nine F3 entries, hence `3^9=19,683` possible tables. The criterion permits two choices for a and nine row-zero triples satisfying the zero-sum condition; the remaining row is uniquely determined. Therefore:

| Admitted system family | Per gain | Both gains |
|---|---:|---:|
| All q0 tables | 19,683 | 39,366 |
| Corrected additive lifts when b or c is nonzero | 18 | 36 |
| No such additive lift | 19,665 | 39,330 |

An **independent** signed-graph potential solver checked all 39,366 table-and-gain cases against the closed-form condition, with **zero disagreements**. Independent arithmetic also checked 699,840 actual generator-commutation equations and 1,049,760 group-law equations for a representative nonzero higher-coefficient set across every admitted table, depths 3–6. These checks are independent mathematical verification, not GitHub CI results.

The [independent audit](nonconstant_drift_arithmetic_audit.py) retains an exhaustive repro with all eight nonzero pairs (b,c) and finite dimensions 3–6. The [16 Python regression tests](../../network/tests/test_arc_like_nonconstant_drift.py) further verify signed path certificates, strict input validation, correspondence with the previous constant-drift theorem, and explicit pointed-system factor transport. The repository workflow is configured to run both. A successful CI run must be separately confirmed before it is claimed.

## Distinguished points, preservation, unknown

A new `DistinguishedSystem` stores a five-coordinate distinguished point with zero higher tail. `PointedConjugacy` requires the corrected transformation to map its chosen source point **exactly** to its chosen target point; inversion and composition retain every literal correction factor.

**Closed:** the complete nine-entry lower-coupling classification for the stated class of fiber-additive triangular translations, together with explicit algebraic corrections or voltage-cycle obstructions. All admitted corrected transformations are valid at every depth.

**Not closed:** arbitrary nonlinear corrections using other state coordinates; general centralizer classification; unboundedly many higher-coordinate couplings; universal inverse-construction stopping; native ARC execution.

**Next referent:** admit a second nonconstant higher-coordinate rule and determine when the potential must be lifted another coordinate upward. Preserve the signed-cycle obstruction and pointed conjugacy factors; do not replace the current scope by an unproved universal criterion.
