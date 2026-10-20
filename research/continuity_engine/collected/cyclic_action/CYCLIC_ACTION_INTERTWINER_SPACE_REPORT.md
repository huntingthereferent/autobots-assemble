# Cyclic Action Engine — complete selected-intertwiner space

**Date:** 2026-10-09  
**Scope:** Actual `WindowProcess` actions on five coordinates over F3, with the zero higher tail, and explicitly fixed `x0` coordinate. Read-only local mathematical experiment; no GitHub changes.

## Mathematical question

Given two full-state actions (A_L,B_L) and (A_R,B_R), and a common B-invariant 81-state carrier S_0={x in F3^5 : x0=0}, classify all bijections f:S_0→S_0 satisfying f B_L = B_R f on S_0, then determine which extend by A-equivariance to simultaneous conjugacies on all F3^5.

The source has gain=1, first coupling q0(u,v)=[v=2], second coupling q1(u,v)=[u=2 and v=2], and zero higher coupling. The target has the same parameters except its second coupling is twice the source q1, modulo 3. `WindowProcess.step` is the native action implementation.

For u in F3, define the transported restricted action

    D^L_u = A_L^{-u} o B_L o A_L^u  on S_0
    D^R_u = A_R^{-u} o B_R o A_R^u  on S_0.

Every map f:S_0→S_0 has a unique A-equivariant extension that preserves x0:

    H(A_L^u x) = A_R^u f(x),  x in S_0, u in {0,1,2}.

It is a simultaneous A/B conjugacy precisely if f D^L_u = D^R_u f for every u. The u=0 equation is the original B-intertwiner equation. No additional comparison type is introduced: these are the existing B-relations transported along the admitted A orbit.

## Complete classification

Both D_0 actions have three cycles of length 27 on S_0. Every B-intertwiner is uniquely specified by (i) a permutation of the three cycles and (ii) one arbitrary 27-phase rotation per cycle. There are

    3! * 27^3 = 118,098

such bijections. They were exhaustively enumerated. The D_1 equation admits exactly rotations that are multiples of three in the chosen cycle coordinates. There are nine rotations per cycle. In this specific law pair the D_2 equation eliminates no additional candidate:

    3! * 9^3 = 4,374.

All 4,374 were promoted to five-coordinate maps. Each is bijective on 243 states, and for each state the A and B intertwining equations passed: 4,374*243*2 = **2,125,764 verified equations**.

The original distinguished origin has 162 admissible origin-preserving correspondences:

    2! * 9^2 = 162.

These counts are exact for the declared pair and the x0-preserving A-equivariant extension grammar, not an unqualified count of every conceivable conjugacy in arbitrary systems.

## Automorphism group and composition

For automorphisms of the source action that preserve the x0-fiber, a map has unique form (pi,r), where pi in S3 permutes the three cycles and r=(r0,r1,r2), ri in 3Z/27Z ≅ C9. With map composition (q,s) after (p,r),

    (q,s) o (p,r) = (q o p, (r_i + s_{p(i)}) mod 27)_i.

This gives the nonabelian wreath product

    C9 wr S3 = (C9)^3 ⋊ S3

of order 4,374. Five generators (three independent 3-phase rotations and two cycle swaps) were verified against all 243 states and both A/B equations (2,430 generator-state-action checks). All 25 ordered pairs of these generators matched the stated composition law. The complete normal-form set has 4,374 distinct maps.

The cross-law solutions form a torsor for this source automorphism group after choosing any one valid reference conjugacy; they are **not** themselves a group under ordinary same-domain composition. The origin stabilizer has order 162 and is isomorphic to C9 wr S2 under the adopted cycle labeling.

This noncommutativity is mathematically separate from the earlier same-law fifth-coordinate centralizer construction. The groups must not be identified merely because both contain noncommuting symmetries.

## Explicit correction of a failed selected map

Let H0 be the existing 81-state cyclic-engine B-intertwiner, which extends successfully and fixes the origin. Define h_bad=B_R o H0 on S_0. This remains a valid B-intertwiner, but its A-equivariant extension fails 108 B equations: 54 on S_1 and 54 on S_2.

Apply two more B_R steps to the selected map:

    h_repaired = B_R^2 o h_bad = B_R^3 o H0.

Its phase is now divisible by three, and the A-equivariant extension passes both A and B on all 243 states. Origin images in the source's five-coordinate ordering are:

    H0(0,0,0,0,0)         = (0,0,0,0,0)
    h_bad(0,0,0,0,0)      = (0,1,0,0,0)
    h_repaired(0,0,0,0,0) = (0,0,1,0,0)

The repaired map is valid as an **unrooted** full A/B conjugacy; moving the origin is not silently treated as origin-preserving. A separate rooted alternative was constructed by applying a B^3-phase shift only to the source's t=1 cycle before the original H0. That changes 27 restricted images, fixes the origin and passes 486 full-state generator equations.

A genuine obstruction from the earlier pulse-law negative control remains distinct: on the original S_0 fiber its B transitions agree, but on the A^2-transported fiber the complete B-fixed counts are 81 versus 54, proving full-state B-nonconjugacy. That cannot be repaired by choosing a different selected map.

## Research boundary

**Closed for the declared pair:** complete 118,098-element B-intertwiner search, exact 4,374-element extension space, rooted count, candidate correction, composition normal form and concrete checks.

**Open:** what happens for nonzero fifth couplings, other cycle lengths, state spaces lacking a single A-transversal, or all possible automorphisms allowed to move the x0 coordinate; and whether a research engine can construct this classification grammar from fresh relations without being supplied it.

No GitHub code or runtime integration was changed during this experiment.