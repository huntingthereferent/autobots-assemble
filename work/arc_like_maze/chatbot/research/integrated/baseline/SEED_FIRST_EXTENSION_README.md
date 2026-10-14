# A/B chatbot — Seed-first multi-goal coupling (2026-10-12)

## Referent

In this finite chatbot experiment, compare compatible witnessed A/B-labeled paths **before** greedily extending a pairing, rather than trying to merge two already-completed, incompatible pairings. A/B remains the language-level research referent; finite `A` and `B` are two specified mathematical transformations, not a universal definition.

## New module

`ab_chatbot_seed_first_extension.py` reuses the existing `BranchDiscoverer` (one shared bounded prefix exploration), `PathUnionAgent` (multiple goals; exact subset selection over a capped path candidate pool), and `UnionEdgeExtender` (replayable greedy extension). It does not replace their underlying mathematics. The API `SeedFirstGoalExtender(old,new,goals).advance(max_new_edges=...)` preserves pinning, incomplete searches, observation budgets, owner/remote scope, replay and counterexamples.

Run:

    python -m unittest -q test_ab_chatbot_seed_first_extension
    python run_seed_first_demo.py

## Comparative witness

Source law `phi=(0,0,1)`, changed law `phi=(0,0,0)`, root `(0,0,0)`, requested source goals `(0,1,1)` and `(0,2,0)`.

- **Complete each goal, then attempt union:** each goal has an individually verified extension, but their full pairings conflict. `CompletedExtensionPortfolio` carries only **1/2** goals under any one of those candidates; exposes a target collision.
- **Join goal paths before extension:** selected witnessed seed words `ABAA` and `ABBABA` coexist. The resulting checked partial relation carries **2/2 goals**, with **9 paired states**, **13 admitted edges**, and **5 excluded edges**. Destination images `(0,2,0)` and `(0,1,0)` are not presumed equal to corresponding source coordinates.
- **Negative:** with changed law `phi=(0,0,0)` and goals `(0,1,0)` and `(0,1,1)`, it still carries only **1/2** goals, not an invented joint solution. Another changed law `(1,0,1)` carries 2/2 with 27 pairs/41 admitted/13 excluded. Identical laws close 27 pairs/54 edges/0 exclusions.

## Local verification

- 12 focused new integration tests passed, including old-vs-new improvement, independent `FiniteSystem` action replay, stale version, forged cached edge, remote evidence, budgeted resumption, and no-global-solution claim on depth limit.
- 5 separate deterministic finite witness tests passed using a local copy of the already-committed GitHub `Law` definition (same 27-state step formulas). GitHub contains the standalone finite version and tests in the same research directory.
- Relevant historical modules `test_ab_chatbot_alternative_extension` (9), `test_ab_chatbot_backtracked_extension` (9), `test_ab_chatbot_branch_discovery` (13), and `test_ab_chatbot_extension_portfolio` (10) finished and passed separately.
- A wider historical suite did **not** complete: one module stalled and the command was interrupted. Its result is **UNKNOWN**. The previous 330/330 total is a historical result for the preceding version and is not claimed for this one.
- No GitHub Actions or physical observation claimed.

## Limits / next

Finite depth and capped candidate search may omit admissible paths; selected union and greedy extension need not be globally maximal. Even joint completion does not imply full-state conjugacy. 5 excluded edges are genuine obstacles *under the selected pairing*, not global impossibility.

Next: compare *multiple compatible seed unions* by downstream completion, not only score paths by immediately available goal coverage and edges. Preserve alternate goal images and provenance.
