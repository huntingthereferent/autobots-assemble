# Cyclic Action Engine — Fifth-coupling classification

**Date:** October 9, 2026  
**Research status:** Closed for the declared five-coordinate two-input family; generalizations remain open.  
**Repository modifications:** None. Experiments run in an isolated checkout, with a separate reproducible local census.

## Current mathematical referent

The previously identified Cyclic Action Engine had three 27-cycles on one declared 81-state invariant fiber, with 4,374 automorphisms preserving the full A/B action **and the x₀ fiber labels**. The next mathematical question is whether this structure survives when the **fifth-coordinate coupling** changes rather than introducing another unrelated comparison.

Work over \(\mathbb F_3\), with five-coordinate states \((u,v,z,y,t)\). The original invertible generating actions are

\[
A(u,v,z,y,t)=(u+1,v,z,y,t),
\]

\[
B_q(u,v,z,y,t)=(u,\ v+u+1,\ z+q_0(u,v),\ y+q_1(v,z),\ t+q(z,y)),
\]

with all arithmetic modulo three and fixed lower coupling tables

\[
q_0(u,v)=\mathbf1_{v=2},\qquad q_1(v,z)=\mathbf1_{v=2,\ z=2}.
\]

The variable fifth-coordinate coupling is any \(q:\mathbb F_3^2\to\mathbb F_3\), i.e. nine table entries; there are exactly \(3^9=19,683\) alternatives. The all-depth zero tail is unchanged. The complete state space has 243 states; each \(u\)-fiber has 81.

## Result I: the observed cyclic structure cannot detect any fifth coupling

On \(u=0\), the lower \((v,z,y)\)-action has **one 27-cycle**. Each of the nine \((z,y)\) pairs appears exactly three times along that orbit. After one full lower cycle, the fifth coordinate changes by

\[
\Delta t=3\sum_{z,y\in\mathbb F_3}q(z,y)=0\pmod3.
\]

Consequently, for **every** fifth-coordinate table, the 81-state \(u=0\) fiber retains **three 27-cycles**. The same holds for \(u=1\). All 19,683 tables admit an abstract \(B\)-only conjugacy to the zero fifth coupling on each of those fibers.

This is a theorem from the exact finite orbit structure, not a failure to search far enough. Continuing the same fixed-point watch to \(B^{27}\) will not reveal a fifth-coupling distinction on those fibers.

## Result II: every nonzero fifth coupling changes the complete B-action

On \(u=2\), the lower action has 18 fixed triples and one 9-cycle. The 18 fixed triples have \(v=0\) or \(v=1\), with every \((z,y)\) pair occurring twice. A full state above one of those triples is fixed by \(B\) precisely when the corresponding \(q(z,y)=0\). Three fifth-coordinate states lie above each triple, so

\[
\boxed{\left|\operatorname{Fix}(B_q)\right|
 =6\#\{(z,y):q(z,y)=0\}.}
\]

For \(q=0\), there are 54 complete-state fixed points. For any \(q\ne0\), there are **strictly fewer than 54**. Therefore none of the 19,682 nonzero couplings can be conjugate to the zero-coupling complete \(B\)-action, regardless of what full-state bijection is proposed. This is also an obstruction to full simultaneous A/B conjugacy.

The exhaustive scan recovered **18 different complete-state B-cycle signatures** across the 19,683 laws. The zero coupling is the only law in its signature class.

A concrete one-entry pulse is \(q(2,2)=1\), zero elsewhere:

| B-invariant region | Zero coupling | Single pulse |
| --- | --- | --- |
| \(u=0\) | Three 27-cycles | Three 27-cycles |
| \(u=1\) | Three 27-cycles | Three 27-cycles |
| \(u=2\) | 54 fixed points, three 9-cycles | 48 fixed points, two 3-cycles, one 27-cycle |

Thus a complete-state nonconjugacy witness survives even though the original watched fiber remains abstractly unchanged.

## Result III: the surviving full-action automorphisms have four exact forms

Fix the \(u\)-fiber labels. Every simultaneous A/B automorphism is then determined by one permutation \(f\) of the 81-state \(u=0\) fiber. It must intertwine the **three transported B actions**

\[
D_u=A^{-u} B A^u\big|_{u=0},\qquad u=0,1,2.
\]

The simultaneous action of \(D_0,D_1,D_2\) has three separate orbits of length 27 for zero coupling, but is **transitive on all 81 states for every nonzero coupling**. For nonzero \(q\), a point where \(q(z,y)\ne0\) allows \(D_2\) to move vertically among all three \(t\)-values above a fixed lower triple. \(D_0\) reaches all 27 lower triples, proving the transitivity.

For a transitive action, an equivariant automorphism is uniquely determined by the image of one marked state. Exhaustively checking the 81 possible marked images per nonzero coupling, replaying every generating edge, gives this complete classification:

| Fifth coupling \(q(z,y)\) | Number of laws | Full A/B automorphisms preserving \(u\) | Abstract group |
| --- | ---: | ---: | --- |
| \(q=0\) | 1 | **4,374** | \(C_9^3\rtimes S_3\) |
| Nonzero constant | 2 | **27** | \(C_9\times C_3\) |
| \(q(z,y)=f(z)\), nonconstant | 24 | **9** | \(C_3\times C_3\) |
| Genuine dependence on \(y\), including \(q=f(y)\) | 19,656 | **3** | \(C_3\) |
| **Total** | **19,683** | | |

**Variable precision:** The 24-law class consists of couplings that depend only on \(z=x_2\), the **earlier** of the two inputs to the fifth-coordinate rule. The final class contains all tables that depend on \(y=x_3\), whether or not they also depend on \(z\). It must not be described as requiring dependence on both variables.

The exact group-order census returned 19,656 nonzero laws of order 3, 24 of order 9, and 2 of order 27. For the 24 nonconstant \(z\)-only laws, all eight nonidentity automorphisms have order three. The two constant nonzero laws have eight elements of order three and 18 of order nine, establishing the stated abelian group types. The zero-law normal form was independently established by the earlier three-cycle phase enumeration.

The vertical global translation \(t\mapsto t+c\) survives for **every** fifth coupling, giving the guaranteed \(C_3\) subgroup. Most of the original cycle-phase freedoms and cycle permutations do **not** survive compatibility with the transported actions.

**Pointed distinction:** For \(q\ne0\), the joint action on the watched fiber is transitive. Any self-automorphism that fixes one designated point is the identity, so there is exactly **one** origin-preserving fiber-preserving self-automorphism. For \(q=0\), the previously computed origin stabilizer has order **162**.

## Result IV: identical complete B-cycles can still conceal different A/B actions

The family scan supplies a sharper question than a zero-vs-nonzero comparison. Select the two **nonzero** couplings

\[
q_z(z,y)=z,\qquad q_y(z,y)=y.
\]

Their complete B-cycle structures are **identical on every one of the three x₀ fibers**:

| x₀ fiber | Both couplings: full B-cycle signature |
| --- | --- |
| 0 | Three 27-cycles |
| 1 | Three 27-cycles |
| 2 | 18 fixed states, twelve 3-cycles, three 9-cycles |

Thus no observation depending only on the fixed points of powers of B can distinguish these two full B-permutations; they are abstractly conjugate as individual permutations. The fiber-preserving A/B automorphism groups have distinct orders (9 versus 3), but an **unrestricted** obstruction is stronger and does not require assuming a conjugacy preserves x₀.

Continuing the same two generating transformations and their inverses yields the action word

\[
\boxed{W=B^{-3}A^{-1}B^3A.}
\]

In the implementation, the letters `ABBBabbb` are applied **left to right**: first A, then B three times, then A⁻¹, then B⁻¹ three times. The exact full 243-state fixed-point counts differ:

\[
|\operatorname{Fix}(W_{q_z})|=27,\qquad
|\operatorname{Fix}(W_{q_y})|=63.
\]

At the distinguished origin, the actual images are

\[
W_{q_z}(0,0,0,0,0)=(0,0,0,0,1),\qquad
W_{q_y}(0,0,0,0,0)=(0,0,0,0,0).
\]

A simultaneous A/B conjugacy would necessarily intertwine W and preserve its fixed-point count. **Therefore these two systems are not simultaneously A/B conjugate on the complete state space**, even though their B-cycle structures match exactly. This conclusion has no fiber-preservation restriction.

The independent reduced-word search checked every freely reduced word over `A`, `A⁻¹`, `B`, and `B⁻¹` through length seven without finding a fixed-count difference. The displayed length-eight word is the first found by the documented deterministic search order. This is a shortest distinguishing word under that exact freely reduced word grammar, not a claim about every conceivable mathematical test.

### Research movement preserved

The B-only observation remains **valid but insufficient** for simultaneous A/B conjugacy. The additional witness is built from the original admitted generators, specifically by comparing their mixed continuation and reverse continuation. It is not evidence that the B-only experiment was erroneous, nor does matching complete B-cycles permit declaring full A/B equivalence.

## Evidence and replication

- The full 19,683-table cycle-signature scan was independently run on the GitHub repository's real `WindowProcess.step` implementation in an isolated worktree, not a hand-written replacement.
- An independent formula-matched local enumerator verified all 19,683 cycle signatures and their frequencies, including the invariant 27-cycles and complete-state obstructions.
- An exhaustive compiled search calculated the common centralizer of the three transported action permutations for every nonzero coupling. The search checked all 81 potential images of an origin, propagating and validating all three generator equations.
- An independent Python directed action-graph algorithm reproduced the group orders for representative couplings. Separate group-element enumeration verified the abstract types of the 3-, 9-, and 27-element groups; all 24 nonconstant \(z\)-only cases were checked individually.
- **11/11** focused local regression tests passed, including the equal-B-cycle action-word negative control.

Reproduce from the provided files with:

```bash
python cyclic_action_coupling_study.py
python cyclic_action_coupling_census.py
python cyclic_action_group_types.py
python cyclic_action_same_B_mixed_words.py
python -m unittest test_cyclic_action_coupling_study -v
```

The census uses Python, NumPy, and Numba. The study's direct enumeration is pure Python.

## What is proved, and what remains unknown

**Closed within the stated family:** All fifth-coordinate couplings preserve the originally watched three 27-cycles; all nonzero couplings are obstructed from zero-coupling full B-conjugacy by the fixed-point invariant; the fiber-preserving full A/B self-automorphism group types and their census are enumerated exactly. The selected nonzero pair with matching complete B-cycle signatures has an unrestricted full A/B obstruction witnessed by a length-eight mixed action word.

**Not established:** The unrestricted full-state automorphism groups allowing maps that change or mix the \(x_0\) fiber labels; a classification of conjugacies among **different nonzero** coupling laws; action equivalence in dimensions other than the declared five coordinates; an automatic rule for constructing new mathematical grammars; or native ARC execution.

**Next mathematical referent:** Compare **different nonzero fifth couplings with the same complete-state B-cycle signature and the same mixed-word fixed-point invariants through the current depth**. Construct and check explicit full A/B correspondences where possible, preserving UNKNOWN wherever the available action-word observations agree without a witness. This keeps the distinction between an individual B-permutation and the complete generated A/B action.