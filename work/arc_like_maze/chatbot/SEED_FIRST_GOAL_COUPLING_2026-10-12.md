# Seed-first goal coupling — 2026-10-12

**Referent.** Compare witnessed compatible goal paths before completing a greedy finite correspondence. Formal A and B here name two defined finite generators, not the language-level A/B research referent.

## Comparative witness

Old law phi=(0,0,1); changed law phi=(0,0,0); root (0,0,0). Requested goals (0,1,1) and (0,2,0).

- Completing each goal independently then trying to combine the full results yields PARTIAL_GOALS: 1/2, with a verified collision.
- The bounded seed-first search discovers the compatible words ABAA and ABBABA, joins them, then extends their shared pairing.
- Result GOALS_CARRIED: 2/2; goal (0,1,1) maps to (0,1,0), and (0,2,0) maps to (0,2,0). The selected pairing has 9 paired states, 13 admitted edges, and 5 excluded edges.
- Negative control: goals (0,1,0) and (0,1,1) under the same changed law still yield only 1/2. Identical laws close a 27-state rooted component with 54 admitted edges and 0 exclusions.

## Run the standalone GitHub witness

    cd work/arc_like_maze/chatbot
    python finite_seed_first.py
    python -m unittest -q test_finite_seed_first.py

This deterministic standalone witness uses the existing checked-in finite_goal_priority Law and bounded_backtracked_goal, finite_extension_portfolio helpers. Five finite tests passed locally using an equivalent copy of the defined Law formula. GitHub CI has not been verified.

## Integrated local chatbot

The separate 73-file local archive ab_chatbot_seed_first_extension_2026-10-12.zip (SHA-256 b256d673ffd56dbc65d5e7caf73934ffee7080909158255106bd8d0e025e84c8) preserves all 68 predecessor files byte-for-byte and adds the integrated SeedFirstGoalExtender, tests, demo, and result records. It composes the existing BranchDiscoverer, PathUnionAgent, and UnionEdgeExtender with pinned evidence and replay.

The integrated new module passed 12/12 focused tests, including source revision, cache forgery, remote labeling, observation limits, old-vs-new improvement, and independent finite action replay. Completed separate legacy runs: alternative extension 9, backtracking 9, branch discovery 13, extension portfolio 10. The attempted wider suite stalled; no new full-suite count is asserted. Historical 330/330 belongs to the prior version only.

**Boundary.** Candidate pool and depth are bounded; greedy extension is selection-dependent; excluded edges are local obstructions, not universal no-go claims. The result does not prove whole-system equivalence, general agency, or physical A/B.

**Next.** Compare more than one compatible seed union by downstream completion, preserving alternative images and observation cost. Leave state/current.json untouched because it belongs to the Continuity frontpage referent.
