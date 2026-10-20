# Cyclic Action Engine — linear-in-\(y\) coupling classification

**Research date:** October 9, 2026  
**Scope:** five-coordinate two-input \(\mathbb F_3\) windows with fixed lower couplings and variable fifth rule. Local mathematics, **not** native ARC execution or a repository commit.

## Current referent

Continue the fifth-coordinate coupling \(q(z,y)\) beyond the previous 18 affine \(y\)-dependent examples. Investigate **every** fifth law of the form

\[
q(z,y)=a_z+b_z y \pmod 3,
\qquad a_z,b_z\in\mathbb F_3,\quad (b_0,b_1,b_2)\ne(0,0,0).
\]

There are \(3^3(3^3-1)=702\) distinct laws in this family. The lower two tables remain

\[
q_0(u,v)=[v=2],\qquad q_1(v,z)=[v=2\land z=2],
\]

and all rules after the fifth-coordinate coupling are zero. The actions on \((u,v,z,y,t)\in\mathbb F_3^5\) are

\[
A(u,v,z,y,t)=(u+1,v,z,y,t),
\]

\[
B_q(u,v,z,y,t)=\bigl(u,\;v+u+1,\;z+[v=2],\;y+[v=2\land z=2],\;t+q(z,y)\bigr).
\]

All arithmetic is modulo three; all fifth-coordinate increments use **pre-move** values.

## The new mathematical operation, not a guessed change of test

A genuine intertwiner between *different fifth-coordinate laws* arises from the same underlying A/B equations:

\[
R(u,v,z,y,t)=(u,v,z+1,y+[z=2],t),\qquad
S(u,v,z,y,t)=(u,v,z,y,2t).
\]

They are invertible and satisfy \(R^9=S^2=1\) and \(RS=SR\). Define their action on coupling rules by exact transport:

\[
q_R(z+1,y+[z=2])=q(z,y),\qquad q_S(z,y)=2q(z,y).
\]

Then **every** transformation equation is preserved:

\[
R\circ A=A\circ R,\qquad R\circ B_q=B_{q_R}\circ R,
\]

\[
S\circ A=A\circ S,\qquad S\circ B_q=B_{q_S}\circ S.
\]

For the 702-law family, the \(C_9\times C_2\) action on coupling laws has no nonidentity stabilizers, hence **every orbit contains 18 laws**. This explains the complete positive construction: each member of an orbit is related by an explicit product \(R^k S^e\).

Earlier shifts of \(y\) were only the \(R^3\) subgroup. That smaller grammar generated 117 six-law orbits; the native lower-coordinate movement \(R\) joins these in triples.

## Complete classification for this family

| Exact finding | Count |
|---|---:|
| Laws studied | **702** |
| Complete \(A/B\) conjugacy classes (unrooted) | **39** |
| Laws per unrooted class | **18** |
| Origin-preserving conjugacy classes | **351** |
| Laws per rooted class | **2** |
| Positive ordered law-pair comparisons | **12,636** |
| Of these, origin-preserving positive comparisons | **1,404** |
| Proven nonconjugate ordered law pairs | **480,168** |
| Total ordered comparisons | **492,804** |

**Completeness of negative results:** All 702 labeled \(A/B\) actions are origin-transitive on 243 states, verified by explicit graph reachability. Any complete intertwining bijection between transitive labeled actions is determined by the image of one point. Trying all 243 possible destination images is therefore exhaustive.

The independent 117-orbit census required 585 representative-pair searches within identical coarse invariant signatures: 117 positive comparisons merge the orbits into 39 eighteen-law classes; the remaining representative comparisons are negative. Invariant differences settle representatives outside the matching-signature groups. All rooted representatives were subsequently checked, and all 1,404 rooted ordered positives were independently confirmed.

The distinction between **number of conjugate ordered law pairs** and **number of individual conjugating maps** matters: the 12,636 count is for ordered law pairs.

## Nontrivial positive witness, outside the first six-law grammar

The fifth laws

\[
q(z,y)=[z=2]y,\qquad q'(z,y)=[z=1]y
\]

are conjugate by the explicit \(R^8\) action. At the distinguished origin,

\[
R^8(0,0,0,0,0)=(0,0,2,2,0).
\]

So the unrooted result is positive, but the origin-preserving result is negative. This is an actual lower-coordinate transport witness, not a failed/unknown correspondence treated as equivalence.

## First obstruction when existing action words agree

Consider the two laws with coefficient triples

\[
(a_0,a_1,a_2)=(0,0,0),\quad (b_0,b_1,b_2)=(1,2,1),
\]

and

\[
(a_0',a_1',a_2')=(0,0,1),\quad (b_0',b_1',b_2')=(1,2,2).
\]

The previously used observations agree:

| Fixed-state count | Law 1 | Law 2 |
|---|---:|---:|
| \(B\) | 18 | 18 |
| \(B^3\) | 54 | 54 |
| \(B^9\) | 81 | 81 |
| Word `ABBBabbb` | 39 | 39 |

Lowercase letters denote inverses; **the listed letters are applied left to right**.

But for the existing eight-step action word **`ABBabbbb`**:

\[
|\operatorname{Fix}(W_1)|=21,\quad
|\operatorname{Fix}(W_2)|=12.
\]

This is an exact obstruction to simultaneous full-state conjugacy. A direct exhaustive search independently rejects all 243 possible images of the origin. The previous eight-letter word was insufficient; another word of the **same length** supplies the distinction. All freely reduced words of length at most 7 were examined without a fixed-point difference for this pair.

## A deeper UNKNOWN boundary for short-word observations

A different pair,

- \(a=(0,0,0), b=(1,0,1)\), and
- \(a'=(0,0,1), b'=(0,2,2)\),

has matching fixed-point counts for **all 3,188,644 nonempty freely reduced words of lengths 1–13** in \(A,A^{-1},B,B^{-1}\). Nevertheless, complete origin-image enumeration proves these two 243-state labeled actions **not conjugate**.

Thus the word-observation result remains **UNKNOWN at the tested depth**, while the separate complete search provides a valid nonconjugacy result. No claim is made that longer words must distinguish these actions—or that their fixed-word counts agree at all lengths.

Among the 39 actual unrooted classes, the checked fixed-word observations through length 9 distinguish only 20 fingerprints; the mathematical objects are **not** thereby merged.

## Verification and remaining boundaries

- Explicitly enumerated all 702 laws and their full 243-state transition graphs.
- Verified 702 origin-transitive generator actions.
- Constructed \(C_9\times C_2\) transport; checked 682,344 full-state generator squares for \(R\) and \(S\).
- Exhaustively classified all 39 unrooted classes and rooted relationships.
- Independently recomputed the mixed-word obstruction using an explicit forward/inverse triangular transition implementation.
- Verified the 3,188,644 freely reduced short-word negative-control comparisons.
- Nine focused regression tests passed.

**Closed:** simultaneous full-state and rooted \(A/B\) conjugacy classification for the declared 702-law linear-in-\(y\) family.

**Open:** arbitrary nine-entry \(q(z,y)\), coupling-dependent symmetries outside the tested family, other lower window laws, and any automatic method for deciding what mathematical witness space to construct when observations remain inconclusive.

**Next referent:** compare complete transitive action-graph correspondence with long-range action-word observations. Preserve their different evidence types: fixed-word agreement is not a conjugacy certificate, while a verified complete intertwiner or a proved exhaustive obstruction is decisive for the stated finite action.

No GitHub changes were made.