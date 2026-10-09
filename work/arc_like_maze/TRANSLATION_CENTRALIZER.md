# Centralizer of a two-generator finite-field transformation system

[Notation and terminology](TERMINOLOGY.md) · [Exact criterion](translation_centralizer.py) · [13 focused tests](../../network/tests/test_arc_like_translation_centralizer.py)

## Current mathematical question

Given two invertible transformations `A_d,B_d` on `X_d=F_3^d` and the coordinate translation `T_r(x)_2=x_2+r`, under which two-predecessor coupling rules does `T_r` belong to the **centralizer** of the generated action?

The preceding [central-translation construction](WINDOW_ROOT_TRANSLATION.md) proved commutation only when higher couplings were zero. This extension characterizes **all** permitted higher couplings for the same specific coordinate translation, rather than assuming that every nonzero higher coupling is an obstruction.

## Mathematical definition

Use the triangular two-predecessor transformation system:

```text
A(x)_0 = x0+1,   A(x)_i = xi   (i>=1)
B(x)_0 = x0
B(x)_1 = x1 + g*(x0+1),      g in {1,2}
B(x)_(i+2) = x_(i+2) + q_i(x_i,x_(i+1))   (i>=0)
```

Every `q_i` is a nine-entry function `F_3² -> F_3`. Stems and nonempty repeating tails specify the infinite rule stream exactly. The B update reads **old-state coordinates** throughout.

Define the coordinate translation `T_r` by `T_r(x)_2=x_2+r`, leaving all other coordinates unchanged.

- `T_r` always commutes with `A`.
- It always commutes with the B updates of coordinates 0, 1 and 2.
- It can affect the B update of coordinate 3 through `q_1(x_1,x_2)`.
- It can affect the B update of coordinate 4 through `q_2(x_2,x_3)`.
- It cannot affect any other B increment because of the two-predecessor dependence bound.

## Exact if-and-only-if centralizer criterion

For any nonzero `r ∈ F_3`, the translation commutes with **both generating transformations at every finite dimension** precisely when

```text
q_1(u,v+r) = q_1(u,v)  for every u,v in F3
q_2(u+r,v) = q_2(u,v)  for every u,v in F3
```

Because `F_3` has prime order, translation by either nonzero `r` cycles through every value in the affected argument. Equivalently:

- `q_1` must be independent of its **second** argument.
- `q_2` must be independent of its **first** argument.

There is no restriction on `q_0` or `q_i` for `i>=3` arising from this translation, because they do not read coordinate `x_2`.

**Theorem:** the subgroup of admitted coordinate translations within `{T_0,T_1,T_2}` is either the full cyclic group of order three or its trivial subgroup `{T_0}`. The obstruction criterion is exact at the rule-table level, not a test of arbitrarily many finite prefixes.

## Minimal concrete obstructions

Start with the zero-coupling system and add exactly one higher rule.

**Dimension 4:** `q_1(u,v)=v`, all other `q_i=0`. For state `x=(0,0,0,0)`:

```text
B(T_1(x)) = (0,1,1,1)
T_1(B(x)) = (0,1,1,0)
```

The two compositions first disagree in **coordinate 3 at dimension 4**. Translation was still a symmetry at dimension 3.

**Dimension 5:** `q_1=0` and `q_2(u,v)=u`, all remaining `q_i=0`. For `x=(0,0,0,0,0)`:

```text
B(T_1(x)) = (0,1,1,0,1)
T_1(B(x)) = (0,1,1,0,0)
```

The compositions agree in dimensions 3 and 4, and first disagree in **coordinate 4 at dimension 5**.

**Nonzero higher couplings that preserve the symmetry:** `q_1(u,v)=u` and `q_2(u,v)=v` are both nonzero but satisfy the exact criterion. Later couplings `q_i` for `i>=3` can also be nonzero without affecting this specific centralizer calculation.

These examples show that **dependency, not merely nonzero coupling, determines the obstruction**.

## Pointed systems and checked conjugacy

An action symmetry does not mean the original distinguished point remains fixed. `PointedSystem` stores the system law and an explicit three-coordinate finite-support mark. If the criterion holds, `translate_point` constructs a new pointed target with the translated mark, returning a `PointPreservingConjugacy` arrow between the two *explicitly pointed* systems.

If the criterion fails, attempting to construct a nonidentity translation arrow raises an error. Explicit factors are retained by inversion and composition; two pointed arrows compose only when the entire intermediate pointed system matches.

The centralizer theorem concerns the **specified translations**. An obstruction to `T_1` does not rule out other, more elaborate conjugacies or point-moving symmetries.

## Verification and evidence

The locally executed 13-test suite uses the exact newly committed `translation_centralizer.py` and test-file contents, plus a **local reproduction** of the existing `WindowProcess` dependency; the new Git blob hashes match the tested files.

Those tests check the first-dimension obstruction, reversible order-three translations, pointed-mark guards, 49 table-pair samples checked against full state-space equations through dimension 5, and invertibility and projection compatibility through dimension 6. **Do not represent the local reproduced-dependency pass as full GitHub integration or CI success.**

Run from repository root:

```bash
python -m unittest network.tests.test_arc_like_translation_centralizer -v
```

## State and next referent

**Proved for this declared grammar:** the complete centralizer criterion, first-failure dimension 4 or 5 for any nonzero shift, and explicit counterexample states whenever the criterion fails.

**Preserved:** the previous central-translation theorem for the zero-tail family; invertibility and dimensionally coherent actions remain true even in the two counterexamples.

**Not proved:** universal conjugacy classification, existence or nonexistence of other centralizer elements, an unrestricted stopping theorem or native ARC puzzle completion.

**Next:** determine whether an x2-translation that ceases to commute can be repaired by a simultaneous, explicitly constructed translation of x3 or x4. Search for a cohomological consistency obstruction using the periods of the generating transformations, retaining the pointed mark and exact intertwining map rather than assuming repair is always possible.
