# Cyclic Action Engine — Full A/B Conjugacy and Rooted Transport

**Date:** October 9, 2026  
**Status:** Closed for the 26 nonzero fifth-coordinate couplings depending only on the preceding coordinate; wider 19,683-law family remains open.  
**Repository:** No GitHub changes. This is a local, reproducible finite experiment.

## 1. Current relation and fixed mathematical grammar

Work over \(\mathbb F_3\) on 243 states \((u,v,z,y,t)\), with original generators

\[
A(u,v,z,y,t)=(u+1,v,z,y,t),
\]

\[
B_f(u,v,z,y,t)=(u,v+u+1,z+q_0(u,v),y+q_1(v,z),t+f(z)),
\]

where \(q_0(u,v)=[v=2]\) and \(q_1(v,z)=[v=2,z=2]\). Each value of a nonzero function \(f:\mathbb F_3\to\mathbb F_3\) defines a fifth-coordinate table \(q_f(z,y)=f(z)\). There are \(3^3-1=26\) such functions.

This research studies full-state, **simultaneous** conjugacy of the two labeled generators A and B, not only a B-invariant fiber. The distinguished origin is separately tested.

## 2. Why the test is complete for these 26 laws

For each nonzero \(f\), exhaustive reachability from the origin through the forward A/B edges covers all 243 states: the generated action is transitive. Therefore a simultaneous A/B intertwiner \(H\), if it exists, is uniquely determined by the chosen image of the origin. For any selected image \(p\), the equations

\[
H(Ax)=A H(x),\qquad H(B_f x)=B_g H(x)
\]

force H along every reachable edge. A breadth-first propagation either yields a globally verified bijection on all 243 states or detects a contradiction. Testing all 243 possible origin images exhausts all unrestricted conjugacies; testing only the origin as image exhausts origin-preserving conjugacies.

A source/destination map is admitted only after all 486 generator squares hold and all 243 images are distinct. The procedure does not infer equivalence from matching counts.

## 3. Five exact full-action conjugacy classes

| Representative \(f(0),f(1),f(2)\) | Class size | \(|\mathrm{Fix}(B)|\) | \(|\mathrm{Fix}(W)|\) |
| --- | ---: | ---: | ---: |
| (0,0,1) | 6 | 36 | 45 |
| (0,1,1) | 6 | 18 | 45 |
| (0,1,2) | 6 | 18 | 27 |
| (1,1,1) | 2 | 0 | 81 |
| (1,1,2) | 6 | 0 | 45 |
| **Total** | **26** | | |

Here \(W=B^{-3}A^{-1}B^3A\) in function-composition notation, i.e. the letters `ABBBabbb` are applied **left to right** in the executable test.

The ordered-pair census is exact:

- 148 ordered pairs lie in the same class. **Every one** has an explicitly constructed and exhaustively checked full-state A/B conjugacy.
- 528 ordered pairs lie in distinct classes. The ordered pair \((|\mathrm{Fix}(B)|,|\mathrm{Fix}(W)|)\) differs, giving an exact conjugacy-invariant obstruction.
- Thus all \(26^2=676\) ordered pairs are decided for this declared mathematical family.

## 4. Positive witness where the earlier observations agree

Choose \(f(z)=z\) and \(g(z)=2z\). These are different nonzero fifth-coordinate couplings with the same full B-cycle structure and the same fixed-point counts for every A/B action word, **because** they are genuinely conjugate.

The origin-preserving full-state witness is:

\[
H(u,v,z,y,t)=(u,v,z,y,2t).
\]

Over \(\mathbb F_3\), the inverse is H itself. This map is bijective and satisfies both H A = A H and H B_f = B_g H on all 243 states. The same scaling construction works for every nonzero \(f\) paired with \(2f\), and has been checked for every such pair.

## 5. A full conjugacy can still fail the rooted question

For the same unrooted class, consider \(f=(0,1,2)\) and \(g=(1,0,2)\).

A verified full A/B conjugacy exists, but it takes the source origin \((0,0,0,0,0)\) to \((0,0,1,0,0)\), not the target origin. Testing the origin as the unique allowed target mark produces a contradiction. A short concrete **rooted obstruction** is the existing generator word `aBA` (apply A inverse, then B, then A):

\[
(A B_g A^{-1})(0,0,0,0,0)=(0,0,0,0,1),
\]

whereas

\[
(A B_f A^{-1})(0,0,0,0,0)=(0,0,0,0,0).
\]

If a conjugacy preserved both generators **and** the origin, it would preserve the property of this word fixing the origin. Therefore rooted conjugacy is impossible for this pair. This does **not** contradict their unrooted conjugacy.

Of the 148 full-conjugate ordered pairs:

- **52** admit an origin-preserving conjugacy; these are exactly \(g=f\) and \(g=2f\) within the stated 26-law family.
- **96** are conjugate only after moving the distinguished point.

Each rooted test was run by fixing the image of the origin to the origin and replaying the same forced-edge equations.

## 6. What survived as Cyclic Action Engine mathematics

This experiment supports a three-way mathematical distinction beyond the initial B-action:

1. Matching periodic/mixed-word invariants: **not automatically equivalence**.
2. A verified full-state A/B intertwiner: **full labeled-action conjugacy**, with its actual origin image retained.
3. A rooted word obstruction: **no origin-preserving conjugacy**, without erasing an existing unrooted map.

The engine follows the same admitted A and B operations and constructs candidate correspondences forced by their equations. It does not need a new unrelated comparison to decide this finite family.

## 7. Verification and limits

- 7/7 regression tests passed.
- All 26 actions were independently verified transitive over 243 states.
- Every one of the 148 positive ordered comparisons has a complete 243-state bijection satisfying both generator squares.
- All 528 negative ordered comparisons have distinct fixed-point invariants for B or the single existing mixed action word W.
- Every one of the 148 positive comparisons has an independently checked rooted outcome.

**Limits:** The five classes concern only the 26 nonzero couplings of the form \(q(z,y)=f(z)\), at dimension five, with the fixed lower tables above. They do not classify arbitrary \(q(z,y)\) with dependence on \(y\), arbitrary dimensions, unrestricted inverse-construction closure, or native ARC execution.

**Next mathematical referent:** move to couplings with genuine dependence on the second input \(y\), preserving the distinction among B-action agreement, mixed-word agreement, full A/B conjugacy, and pointed correspondence. Stop with UNKNOWN when no verified positive map or proved invariant obstruction is yet available.