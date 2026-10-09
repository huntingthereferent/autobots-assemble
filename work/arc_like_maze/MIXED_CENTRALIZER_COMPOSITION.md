# Composition of distinct selected centralizer symmetries

[Standard mathematical terminology](TERMINOLOGY.md) · [Exact selected-map and mixed-arrow implementation](mixed_centralizer_composition.py) · [14 focused tests](../../network/tests/test_arc_like_mixed_centralizer_composition.py) · [independent composition audit](mixed_centralizer_independent_audit.py)

## Current referent

The [pointed fifth-coordinate classifier](POINTED_COUPLING_CLASSIFICATION.md) establishes that one underlying finite-field coupling law can admit several commuting transformations, sometimes with different exact cyclic orders. The present question is whether two separately **selected centralizer symmetries** commute with *each other*, and whether their composition can be represented without identifying unlike maps or losing distinguished-point witnesses.

**Answer:** even though each selected symmetry commutes with the two generating transformations A and B, two different selected symmetries do **not** necessarily commute with each other. Their ordered composition is nevertheless an invertible transformation centralizing A and B, provided the factors act on the same underlying coupling law.

## Exact commutator formula

Let s=(v,z,y) be one of the 27 lower-coordinate states and t=x4 the fifth state coordinate. The same-law selected transformations have a shared lower action C and possibly different corrections L_a and L_b:

F_a(s,t) = (C(s),t+L_a(s))

F_b(s,t) = (C(s),t+L_b(s)).

Both obey the same 81 cohomological compatibility equations. Therefore their difference delta(s)=L_b(s)-L_a(s) is invariant under every induced lower-coordinate B transformation E_u. The difference is **constant on each connected component** of the 27-state B-orbit graph.

Let component(s) be the graph component of s, and let c_i be delta on component i. The lower action C commutes with each E_u, hence C induces a permutation pi of those components.

Direct composition gives the full criterion, modulo three:

F_a(F_b(s,t)) minus F_b(F_a(s,t))
  = delta(s)-delta(C(s))
  = c[component(s)]-c[pi(component(s))]

in the fifth coordinate. The first four coordinates agree.

**Necessary and sufficient condition:** the two selected symmetries commute if and only if c_i=c_pi(i) for every component i.

An associated B-invariant vertical gauge T_c changes t by c[component(s)], leaving other coordinates fixed. It is an order-three gauge when nonidentity and satisfies the explicit conjugation relation

F_a composed with T_c composed with F_a inverse
  = T_(c composed with pi inverse).

These are ordinary finite-field group-theoretic statements. The centralizer of the generating action need not be abelian.

## Component-action classification

Across the previously verified 486 fourth-coordinate configurations, the lower centralizer action has three possibilities:

| Graph components and action | Configurations |
|---|---:|
| One connected component | 468 |
| Three components, each individually fixed | 6 |
| Three components, cyclically permuted | 12 |
| **Total** | **486** |

In a connected graph the relative gauge is globally constant, so every pair of selected corrections commutes. With three individually fixed components, every pair also commutes. When the three components are cyclically permuted, two selections commute **only if their relative correction is the same constant on all three components**.

To count carefully, fix **one admitted fifth-coordinate law (the zero coupling)** for each fourth-coordinate configuration and take all ordered pairs of admissible component constants. There are three choices per component.

| Component action | Configurations | Commuting ordered pairs | Noncommuting ordered pairs |
|---|---:|---:|---:|
| Connected | 468 | 4,212 | 0 |
| Three fixed components | 6 | 4,374 | 0 |
| Three cyclic components | 12 | 972 | 7,776 |
| **Total** | **486** | **9,558** | **7,776** |

The total is **17,334 ordered pairs**. The pair classification depends only on the component action, so it holds for other admissible fifth-coordinate tables with the same fourth-coordinate configuration; the displayed pair totals follow the explicit one-table-per-configuration counting convention. They are not counts of all automorphisms, conjugacy classes or possible fifth-coordinate laws.

## Explicit noncommuting witness

Choose one previously admitted coupling law with

- gain = 1
- quotient Q=(1,0,2)
- normalized row offsets k=(0,0,0)
- fifth-coordinate coupling q2=zero.

Its three graph components are cyclically permuted by pi=(2,0,1). The normalized correction for the zero fifth coupling is zero.

Select the correction constants a=(0,0,0), giving one **order-three** centralizer symmetry F_a. Select b=(0,0,1), giving one **order-nine** centralizer symmetry F_b. Both are genuine selected centralizer symmetries of **the same coupling law**.

The five-coordinate original distinguished point x=(0,0,0,0,0) lies in component 0. Its image under the common lower action lies in component 2. Hence delta(x)=0 but delta(C(x))=1.

It follows that F_a(F_b(x)) and F_b(F_a(x)) have the same first four coordinates but fifth coordinates differing by 2 modulo three. This is a literal noncommuting witness.

It does **not** show that either F_a or F_b fails to commute with A or B; both commute with those generators. It shows only that these two **centralizer elements** do not commute with one another.

## Mixed pointed-arrow contract

[The implementation](mixed_centralizer_composition.py) retains:

| Object | Mathematical meaning |
|---|---|
| PointedLaw | The underlying complete coupling law and one explicit distinguished five-coordinate point |
| SymmetryFactor | A particular certified selected centralizer symmetry, plus its exact cyclic exponent |
| GaugeFactor | An explicit B-invariant component-gauge translation |
| MixedPointedArrow | A nonempty ordered word of actual symmetry/gauge factors, with exact source and target distinguished points |
| CommutatorCertificate | Full 27-state commutator differences and, when noncommuting, a literal state and both resulting states |

A mixed arrow may contain factors using **different selected symmetries** but requires all factors to use the **identical coupling law**. It composes only when the entire intermediate pointed law matches. Its inverse reverses the literal factor sequence and replaces each factor by its exact inverse.

A noncommuting composition is kept in its given order. The construction never silently reorders factors, collapses them into one selected cyclic subgroup, or treats an unproved map between different coupling laws as a valid conjugacy.

## Independent verification

The mathematical enumeration was executed independently: it constructed the 27-state connected components for all 486 fourth-coordinate configurations and checked every one of 17,334 ordered gauge pairs by comparing the actual composed maps over lower states. It returned **9,558 commuting** and **7,776 noncommuting** ordered pairs.

An [independent executable audit](mixed_centralizer_independent_audit.py) records that finite enumeration without importing the production classifiers. [Fourteen focused tests](../../network/tests/test_arc_like_mixed_centralizer_composition.py) cover actual selected order-three/order-nine commutators, both original generator commutations, vertical-gauge conjugation, explicit ordered mixed-arrow factors, inverses and mark transport, and refusal to compose different underlying laws.

**Verification limit:** the independent mathematical enumeration ran and passed. The new regression tests and independent audit are committed; a successful GitHub Actions run is **not yet confirmed**. The all-depth statement is proved by the displayed triangular formulas and component invariance, not solely by a sample of finite states.

## Preservation and next referent

**Closed for the declared family:** exact commutator criterion, classification of the component action for all 486 configured fourth-coordinate laws, and mixed pointed-arrow composition retaining both factor order and distinguished-point provenance.

**Preserved:** earlier zero- and nonzero-trace admission theorems, actual 27-state corrections, cyclic orders, component gauges, literal signed-cycle obstructions, and generator action inverses.

**Unknown:** conjugacies across different coupling laws, any unrestricted centralizer classification, arbitrary higher-coordinate coupling rules, universal inverse-construction closure, and native ARC execution.

**Next:** derive a normal form and group presentation for the group generated by one selected lower symmetry and the finite component-gauge translations. Prove its size and factorization—including the noncommutative three-cycle cases—before making any canonical-composition claim.
