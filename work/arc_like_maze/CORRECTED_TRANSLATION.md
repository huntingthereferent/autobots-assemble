# Corrected coordinate translations in a finite-field transformation system

[Mathematical notation](TERMINOLOGY.md) · [Exact construction and certificates](corrected_translation.py) · [13 regression tests](../../network/tests/test_arc_like_corrected_translation.py)

## Current referent and definition of solved

The preceding [centralizer theorem](TRANSLATION_CENTRALIZER.md) proves that translating the third coordinate alone fails when the fourth- or fifth-coordinate coupling reads that coordinate. The next question is whether an **additional, explicitly witnessed higher-coordinate correction** restores commutation with both generating transformations.

A solved result here needs either an actual bijective all-depth corrected symmetry or a precise invariant excluding the proposed lift, not merely a finite simulation.

## Declared transformation family

On `X_d = F_3^d` for `d>=3`, with all arithmetic modulo three, define two invertible generators:

```text
A(x) = (x0+1, x1, x2, x3, x4, ...)
B(x)_0 = x0
B(x)_1 = x1 + g*(x0+1)            g in {1,2}
B(x)_2 = x2 + a
B(x)_3 = x3 + b*x2                where coordinate 3 exists
B(x)_4 = x4 + c*x2                where coordinate 4 exists
B(x)_i = xi                       for i>=5
a,b,c in F3
```

These are a special case of the earlier two-predecessor coupling grammar: `q0(u,v)=a`, `q1(u,v)=b*v`, `q2(u,v)=c*u`, with a zero tail. They are independently valid reversible triangular maps at every finite depth and commute with dimensional projections.

The original translation `T_r` adds `r` to `x2` and changes nothing else. Its failure to commute with B occurs when `b` or `c` is nonzero.

## Constructive repair when a is nonzero

For `a in {1,2}`, let `a^{-1}` denote its multiplicative inverse in `F3`. Put

```text
K_r(x2) = a^-1 * (r*x2 + binom(r,2))
binom(r,2) = r*(r-1)/2           r in {0,1,2}, computed in F3

F_r(x)_0 = x0
F_r(x)_1 = x1
F_r(x)_2 = x2+r
F_r(x)_3 = x3 + b*K_r(x2)
F_r(x)_4 = x4 + c*K_r(x2)
F_r(x)_i = xi                    i>=5
```

Each coordinate formula applies only when that coordinate exists. The inverse is `F_{-r}`, not a guessed state lookup.

**Intertwining calculation:** B sends `x2` to `x2+a`. Thus

```text
K_r(x2+a)-K_r(x2) = r.
```

That difference exactly cancels the extra `b*r` and `c*r` introduced by translating `x2` in the higher-coordinate coupling increments. Consequently `F_r∘B=B∘F_r`. The formula is independent of x0, so `F_r∘A=A∘F_r` as well.

**Group law:** The binomial identity

```text
binom(r+s,2) = binom(r,2)+binom(s,2)+r*s  in F3
```

gives `F_r∘F_s=F_{r+s}`, `F_1^3=id`. Every map is invertible, triangular, and projectively coherent at all depths. This is an exact order-three subgroup of the centralizer of the generated transformation action.

If `a=0` and `b=c=0`, the original pure translation already commutes and needs no correction.

## A proved obstruction when a=0 and a higher coupling is nonzero

The failed translation is **not universally repairable**.

When `a=0`, take the invariant lower-coordinate fibers over `(x0,x1,x2)=(2,0,0)` and `(2,0,1)`. In both, B fixes the first three coordinates: `x0=2` makes the x1 increment vanish, and `a=0` freezes x2.

If `b!=0`, in dimension four B fixes **all three** states of the fiber with `x2=0`, but **none** in the translated fiber with `x2=1`: there B translates x3 nontrivially. An A/B-equivariant bijection that preserves x0 and x1 and sends x2 to x2+1 would have to identify these fibers and preserve B-fixed states, which is impossible.

If `b=0,c!=0`, the same obstruction first appears in dimension five: **9** B-fixed states in the source fiber versus **0** in the target fiber, since B nontrivially translates x4.

This obstruction applies to **any equivariant bijection respecting the specified x0,x1 and x2-translation coordinates**, including arbitrary higher-coordinate corrections. It does **not** rule out other centralizer symmetries that change lower coordinates or implement different actions.

| Drift a | Higher coefficients | Outcome |
|---|---|---|
| Nonzero | Any b,c | Explicit corrected order-three centralizer action |
| Zero | b=c=0 | Uncorrected translation is already central |
| Zero | b nonzero | Obstructed at dimension 4 (3 versus 0 fiber fixed states) |
| Zero | b=0,c nonzero | Obstructed at dimension 5 (9 versus 0 fiber fixed states) |

## Pointed systems and factor provenance

The corrected symmetry changes the distinguished point. It does not make the original point fixed. `PointedHigherSystem` stores an exact five-coordinate mark with zero tail, because the corrected map can change both x3 and x4; a three-coordinate mark would silently truncate the important witness.

For example, when `a=1,b=1,c=2`, applying `F_1` to the zero distinguished point gives `(0,0,1,0,0)`, and applying `F_1` again gives `(0,0,2,1,2)`. A third application returns to the original point.

`CorrectedConjugacy` admits an arrow only if the actual map transports the source distinguished point to the explicitly chosen target. Composition requires an identical pointed intermediate object; inversion reverses the literal stored correction factors. No algebraically obstructed translation may be silently admitted.

## Verification evidence

The 13 newly committed tests passed in the local execution environment using a reproduction of the existing `WindowProcess` dependency; the **exact new source and test Git blob hashes match** the tested files. The tests cover 54 parameter combinations `(a,b,c,g)`, complete finite state spaces through dimension six, both generator actions, order-three composition, exact triangular inverses, projection coherence, the two first-obstruction dimensions, and pointed-factor conservation.

This local run is not a GitHub CI result, and bounded enumeration by itself is not the proof of the all-depth theorem. The proof is the displayed algebra and fixed-fiber cardinality argument.

```bash
python -m unittest network.tests.test_arc_like_corrected_translation -v
```

## Boundary and next referent

**Closed within the declared linear coupling family:** an if-and-only-if existence criterion for a coordinate-prescribed translated lift, a constructive order-three correction in the positive case, and a fiber-fixed-point obstruction in the negative case.

**Not established:** a complete centralizer of either transformation system, arbitrary nonlinear higher couplings, arbitrary distinguished points with infinite nonzero tails, universal inverse construction or native ARC execution.

**Next mathematical referent:** lift this correction from the constant-drift linear family to a nonconstant lower coupling `q0(x0,x1)`. The resulting cohomological equation must be solved or obstructed along complete cycles of the lower-coordinate B action, preserving the exact distinguished point throughout.
