# Continuity Engine — mathematical cross-scope handoff

**Date:** 2026-10-09  
**Status:** Local tested integration candidate; no GitHub repository changes.  
**Current referent:** Transport an existing restricted `B`-action investigation into a new full `A/B` mathematical question **without rewriting or promoting the old conclusion**.

## Mathematical result

The two laws are defined over `F3^5` and have the exact triangular generator semantics from the prior `WindowProcess` research. Let

```
A(u,v,z,y,t)=(u+1,v,z,y,t)
B_q(u,v,z,y,t)=(u,v+u+1,z+[v=2],y+[v=2 and z=2],t+q(z,y))
```

with old-state values throughout and all additions mod 3. Take

```
q_source(z,y) = a_z + b_z*y, a=(0,0,0), b=(1,0,1)
q_target(z,y) = a_z + b_z*y, a=(0,0,1), b=(0,2,2)
```

On the **81-state B-invariant fiber** `u=0`, each restricted B permutation has exactly **three disjoint 27-cycles**. The two restricted B-actions are conjugate. An explicit full 81-state interwiner can be constructed and checked on each B edge.

On the **complete 243-state full A/B action**, they are **not conjugate**. Independent exhaustive propagation of 243 candidate images of the origin rejects them all. The new Schreier-loop engine's breadth-first order rejects all 243 candidates after the first **17** nontrivial path-collision equations of a 244-generator family.

**This is not a contradiction.** The 81-state carrier is preserved under B, but **A moves every point of that fiber outside it**. The restricted conjugacy therefore does not furnish a full-space bijection intertwining both A and B. Nor does a negative result about full conjugacy imply negative restricted-B conjugacy.

## What the new handoff actually proves

Parent area: `cyclic_action/B` on the explicitly frozen invariant carrier.

Child area: `finite_action/AB` on the full `F3^d` state space, with its own question ID.

The link verifies the **identity inclusion of the restricted B-transition relation** into the full action. For each of the 81 carrier states and both frozen laws:

```
B_full(s) == B_restricted(s) in carrier
```

There are **162 generator transition checks**. The link also checks exact source and target law identity, dimension compatibility, and full finite-domain membership. **These 162 checks do not demonstrate an extension of the restricted-B conjugating map**; they only establish that the child examines the same underlying laws in a different domain and mathematical scope.

The parent's entire nested serialized witness, immutable question ID, SHA-256 digest, and exact scope remain in the cross-scope record. Child checkpoints form an independent verified ancestry of 0, 17, or more recorded collision observations; the previous parent bytes remain unchanged. Parent and child each replay against their exact mathematical laws. Hashes are local integrity checks, not externally authenticated signatures.

The handoff refuses unrelated law pairs, mismatched domains, reordered child ancestry, forged collision observations (even after a recomputed outer digest), changed question anchors, and collision-budget regression.

## Controls

| Parent restricted B result | Child full AB result | What it establishes |
|---|---|---|
| `B_ONLY_CONJUGACY_WITNESSED` | `UNKNOWN_COLLISION_BUDGET` | No promotion merely because the parent succeeded |
| `B_ONLY_CONJUGACY_WITNESSED` | `DISTINGUISHED_FULL_AB` | Verified finite counterexample to promotion |
| `B_ONLY_CONJUGACY_WITNESSED` | `CONJUGATE_FULL_AB` | Two **independently** witnessed positive relations, on different domains |
| `UNKNOWN_BUDGET` | `DISTINGUISHED_FULL_AB` | A new scope can establish a result while the parent remains UNKNOWN |

The last row does **not** imply the parent is distinguished. The broader result has not been shown to transfer in that direction either.

## Independent mathematical checks

1. The B-only cycle decomposition on the declared `u=0` fiber was calculated directly from the `WindowProcess` finite-field arithmetic and confirmed as `{27: 3}` for both laws.
2. The prior independent `cyclic_action_simultaneous_conjugacy.find_conjugacy` rejected all 243 origin images for the hard pair; a rotated positive control returned an explicitly valid 243-state bijection after testing 10 candidate origin images.
3. The new link's full child observation reconstructs the same complete negative via 17 nontrivial Schreier relations, with `244` total basis words for `2*243` labeled generator edges.
4. The local compatibility environment ran **47/47 tests** across the existing Cyclic integration, full AB integration, research-board bridge, and new cross-scope handoff. That compatibility environment uses explicit **test-only stand-ins** for unavailable repository modules and should not be claimed to be a test of the repository's exact imports.
5. No automatic publication: staging a candidate board checkpoint preserves the previous freeze, gives the new AB question a separate ID, records the parent origin relation, and leaves result status `REVIEW` if no public proof URL was supplied. A supplied URL is syntactically checked only, not verified for proof content.

## Why this changes the engine

Previously, the records admitted two independent scopes. They can now be *connected by an explicit verified mathematical relation*, and the record shows what that connection proves and **does not** prove.

```
existing B-only question + witness
     -> verify frozen original history
     -> prove source/target law identity
     -> prove B-action restriction into full space
     -> start NEW full AB question, status UNKNOWN
     -> continue Schreier evidence in child only
     -> negative or positive child result
     -> preserve the B-only result byte-for-byte
```

The engine still has no general autonomous research-area selector, general dimension inference, universal A/B mathematics, nontransitive full-action equivalence test, or automatically running research worker.

## Reproduction

When the actual GitHub repository is available, install/copy the package's `research/` modules into the corresponding repository paths, then run tests from repository root:

```
python -m unittest network.tests.test_research_cross_scope_handoff network.tests.test_research_full_action_correspondence network.tests.test_research_continuity_engine network.tests.test_research_continuity_board_bridge -v
```

**No source was automatically changed in the user repository.** Only this local distributable was created.

For self-contained review without repository checkout, the ZIP contains `test_support/` with explicitly labeled stub arithmetic and an isolated test runner; results of those tests verify the integration protocol under matching test arithmetic, not the exact repository implementation.

**Next boundary:** A/B conjugacy witnessed on a full invariant action graph need not preserve an arbitrary named B-fiber; a useful extension is to classify **which invariant subsets are transported by a given full-action intertwiner**, and which are not. That is a new transport question, not promotion of the old one.