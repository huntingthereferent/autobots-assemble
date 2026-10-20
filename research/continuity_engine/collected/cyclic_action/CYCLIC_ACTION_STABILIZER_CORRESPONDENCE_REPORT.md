# Cyclic Action Engine — finite path-collision correspondence

**Research date:** October 9, 2026  
**Status:** Mathematically closed for the declared pair; standalone local experiment. **No GitHub modification.**

## Current referent

The earlier 702-law investigation found two nonconjugate five-coordinate systems with matching global fixed-point counts for all **3,188,644** nonempty freely reduced A/B words through length 13. Agreement of periodic-word observations did not establish simultaneous conjugacy. The next question is whether **the existing labeled A/B action graph supplies a finite positive-or-negative correspondence witness**, without replacing the relation.

The system on \((u,v,z,y,t)\in\mathbb F_3^5\) is

\[
A(u,v,z,y,t)=(u+1,v,z,y,t),
\]
\[
B_q(u,v,z,y,t)=(u,v+u+1,z+[v=2],y+[v=2\land z=2],t+q(z,y)).
\]

Increments use pre-move coordinates; addition is modulo 3. Here the two fifth-coordinate tables are

\[
q(z,y)=(y,\,0,\,y)_z,
\quad
r(z,y)=(0,\,2y,\,1+2y)_z.
\]

Equivalently, the coefficient pairs are \(a=(0,0,0), b=(1,0,1)\) and \(a'=(0,0,1), b'=(0,2,2)\). The two actions are transitive on all 243 states. These are the same hard negative control as in the prior report.

## The complete finite correspondence criterion

Choose the source origin \(o\), and choose one A/B word \(p_x\) carrying \(o\) to each source state \(x\). A breadth-first spanning tree supplies all 243 such paths, with longest path length 11.

For each source edge \(x\xrightarrow{g}gx\) with \(g\in\{A,B\}\), construct the path-collision word

\[
\ell_{x,g}=p_x\,g\,p_{gx}^{-1}.
\]

It fixes the source origin. Each non-tree edge supplies a generator of the source root stabilizer. The connected two-generator action graph has **243 vertices and 486 labeled positive-generator edges**; removing the 242 spanning-tree edges leaves

\[
\boxed{486-242=244\text{ Schreier generators}.}
\]

The 244 words generate the entire source-point stabilizer (as a subgroup of the free group on A and B). For an origin image \(y\) in the target action, **a labeled A/B-equivariant map sending \(o\mapsto y\) exists precisely when every one of these generators fixes \(y\)**.

Reason: if the source stabilizer fixes \(y\), the assignment \(p_xo\mapsto p_xy\) is well-defined; it intertwines A and B by construction. Since both actions are transitive of the same finite size (243), it is necessarily a bijection. This is an exact *complete* test for these finite transitive actions, unlike truncated fixed-point observations.

## Complete result for the hard pair

| Source stabilizer WATCH | Eligible target images for the origin |
|---|---:|
| Starting candidate space | 243 |
| All basis loops of length at most 13 | 3 |
| All basis loops of length at most 14 | **0** |
| All 244 basis loops | **0** |

After the length-13 source-root loops, the three unresolved candidate origins are precisely

\[
(0,0,2,1,0),\ (0,0,2,1,1),\ (0,0,2,1,2).
\]

A breadth-first search of the synchronized (source-root, target-candidate) action gives a shortest root-fixing loop of **length 14** that moves each remaining candidate. One such word is `ABABABABAbbAbb` (capital letters are forward actions; lowercase their inverses; apply letters left to right). It fixes the source root but not those three target points. Its *individual* global fixed-point counts also differ (57 source, 39 target), so this length-14 example is not claimed to improve the shortest single-word obstruction.

Thus, in the source-stabilizer correspondence space, there is a decisive finite obstruction. A separate exhaustive 243-origin-image transport search independently reached the same nonconjugacy conclusion.

## More informative witness: two individually inconclusive observations

The same native action supplies another obstruction that retains **two source-root relations at once**:

| Word (left-to-right actions) | Length | Source fixed | Target fixed |
|---|---:|---:|---:|
| `BBBAbbba` | 8 | 39 | 39 |
| `ABABABBBabbaba` | 14 | 15 | 15 |
| **Fixed by both words** | — | **3** | **0** |

The three jointly fixed source states are exactly \((0,0,0,0,t)\) for \(t=0,1,2\). The target has **no** common fixed state.

A hypothetical simultaneous conjugacy \(H\) must preserve intersections of fixed sets:

\[
H(\operatorname{Fix}(w_1)\cap\operatorname{Fix}(w_2))
=
\operatorname{Fix}(w_1)\cap\operatorname{Fix}(w_2)
\]

(with the actions on each side taken in the corresponding system). The sizes 3 and 0 contradict that identity. **This is a direct unrooted full-state nonconjugacy certificate**, even though the fixed-point counts of each selected word match separately. It illustrates why relationships *among witnesses* may carry more information than each observation in isolation. It does not imply that a length-14 single-word obstruction was unavailable; one was also found.

## Positive control: construct rather than infer equivalence

The already proved lower-coordinate symmetry

\[
R(u,v,z,y,t)=(u,v,z+1,y+[z=2],t)
\]

transports the source law to the distinct law \(q_R\). The same 244-generator source-stabilizer check finds **exactly three** possible target images of the origin:

\[
(0,0,1,0,0),\ (0,0,1,0,1),\ (0,0,1,0,2).
\]

For each one, the spanning-tree words explicitly construct a 243-state bijection. **All 486 full-state A/B generator squares pass for each map**, and the first image agrees with \(R(o)\). None of these maps is origin-preserving. The source compared with itself likewise has three eligible origin images, including its original mark.

This control distinguishes three outcomes: **verified full A/B conjugacy**, **a full-state obstruction**, and **UNKNOWN when only a prefix of the witness equations is examined**.

## Verification and limits

- Generated all 243 canonical shortest source paths and all 244 nontrivial Schreier loops.
- Checked the remaining candidate-image sets at basis-loop depths 13 and 14.
- Confirmed the two-word fixed sets using both the action-array implementation and an independent direct triangular evaluator with explicit inverse formulas.
- Verified three positive full A/B conjugacies against every state and both actions; independently rejected all 243 origin images for the hard negative pair.
- **10/10 focused regression tests passed**.

**Closed for this pair:** a finite action-graph correspondence criterion, a positive-control bijection construction, and a compact joint fixed-set nonconjugacy certificate.

**Not established:** that two words suffice for arbitrary systems; that single-word observations at every depth determine conjugacy; that every possible higher-dimensional A/B system is transitive; or that the Cyclic Action Engine already has this routine integrated into its runtime.

**Next mathematical referent:** re-enter the witness basis as a native Cyclic Action Engine WATCH only where transitivity and equal finite cardinality have been explicitly verified. Preserve the distinction between a periodic-word reading, a joint fixed-set obstruction, and a constructed full-action bijection; maintain the existing UNKNOWN boundary where the complete basis has not been checked.