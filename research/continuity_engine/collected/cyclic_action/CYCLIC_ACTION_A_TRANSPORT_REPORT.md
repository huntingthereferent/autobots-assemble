# Cyclic Action Engine — A-orbit transport of a restricted B witness

**Research date:** October 9, 2026  
**Repository revision used:** `6be75fcd7bccc0a2fe4029e00c1b231aac24939a` (isolated checkout of `huntingthereferent/language-network`).  
**Research status:** Local proof-of-concept and actual-repository verification; no GitHub changes.

## Current referent

The existing `CyclicActionEngine` certifies periodic-point obstructions and explicit B-intertwiners on a caller-declared B-invariant fiber. Such a fiber is not necessarily A-invariant. Ask whether the **selected** B-intertwiner can be extended over its A-orbit into a simultaneous A/B conjugacy. Do not conflate failure of that selected map with impossibility of *any* full-state conjugacy.

## Exact A-transport criterion

Let `S0 = {x in F3^5 : x0=0}`, and `Su=A^u(S0)` for `u=0,1,2`. Both systems' generator `A` increments the first coordinate, so the fibers are disjoint and exhaust `F3^5`. Let `f0:S0→S0` be a selected bijection intertwining the two B-actions restricted to `S0`. Its **unique A-equivariant extension** is:

`F(A_L^u x) = A_R^u f0(x)` for every `x in S0` and `u in {0,1,2}`.

Then `F` also intertwines B on the entire space **if and only if** all three exact equations hold on S0:

`f0( A_L^{-u} B_L A_L^u(x) ) = A_R^{-u} B_R A_R^u( f0(x) )`.

For `u=0` this is the already-proved B-fiber equation. The `u=1` and `u=2` equations examine B transported across the existing A-action. They are not an unrelated new WATCH. All equalities use the actual finite-field `WindowProcess.step` laws and are independently replayable on 81 states for each fiber.

## Positive control: a selected B-witness extends to full A/B

Two laws share the rule `q0(u,v)=1[v=2]` and zero higher tail. Their `q1(v,z)` tables are `1[v=2 and z=2]` and twice that table, modulo 3. The existing Cyclic Action Engine at budget 27 constructs a bijection on the x0=0 fiber. Its canonical B-map coincides with the following full-state transformation:

`H(x0,x1,x2,x3,x4)=(x0,x1,x2,2*x3,x4)`.

This H fixes the origin, is a bijection with its own inverse, and satisfies `H A_L=A_R H` and `H B_L=B_R H` on all 243 states. This correspondence is exact at every depth at least four under the stated zero-tail grammar (all higher coordinates unchanged).

## Selection counterexample: not every B-intertwiner extends

On the very same laws, take the valid B-fiber bijection `f0` above and construct another valid B-fiber bijection `f1 = B_R ∘ f0`. Its unique A-equivariant extension intertwines A but fails B on 108 of the 243 full states: 0 failures at x0=0, 54 at x0=1, and 54 at x0=2. One replayable failure occurs at `(1,0,0,0,0)`; the extended map of `B_L(x)` gives `(1,0,1,0,0)` but `B_R` of the extended map of `x` gives `(1,0,0,0,0)`.

This refutes the inference **'a selected B-only conjugacy must extend'**, but it does not refute full A/B conjugacy of these laws: H above is a constructive positive certificate. Hence selected-witness obstruction and law nonconjugacy are distinct mathematical outcomes.

## Negative control: the A-orbit exposes a previously dormant coupling

Compare two laws with both `q1=0` and zero tail. One has `q0=0` and the other has `q0(u,v)=1[(u,v)=(2,0)]`. The B-actions are *identical* on S0, so the kernel correctly certifies a restricted B-conjugacy at power 3.

But A² moves S0 to S2 where the extra q0 entry becomes active. At power B¹ on S2 the full fixed-point counts differ: **81 versus 54**. On the entire 243-state space, `Fix(B)` also differs **81 versus 54**, a complete-state conjugacy invariant. Thus these actual laws cannot be fully conjugate by a B-preserving bijection; in particular they cannot be simultaneously A/B-conjugate.

The discrepancy persists at depth d≥4 in the declared zero-tail family:

`|Fix(B_base)|=3^(d-1)` and `|Fix(B_pulse)|=2·3^(d-2)`.

## Reproduced evidence

- **8/8 focused local regression tests passed** against repository `WindowProcess` and `CyclicActionEngine` (not a copied transition interpreter).
- A separate native A-transport criterion program checked all three fiber conditions: canonical positive map `[0,0,0]` failures; selected shifted map `[0,54,54]`; dormant pulse identity map `[0,0,27]`.
- The existing B-only serialized record remains `UNKNOWN_NOT_WATCHED` for simultaneous A/B, even for cases where an independent full conjugacy is subsequently constructed.
- No repository changes, commits, or CI claims were made in this research pass.

## Preserved boundary and next mathematical referent

**Closed for these examples:** the exact A-transport criterion; extension of one chosen B-witness to an A/B conjugacy; a nonextending chosen B-witness for conjugate laws; and a full-state obstruction invisible to the original B-invariant fiber.

**Open:** an admission rule and witness type for *searching* alternative B-fiber intertwiners satisfying all three transported B equations, without claiming this is already implemented in the Cyclic Action Engine. If a particular candidate fails, preserve that obstruction but continue the mathematically permitted correspondence search; if all admitted candidates are exhausted, return a scope-correct result rather than inventing a universal nonconjugacy theorem.