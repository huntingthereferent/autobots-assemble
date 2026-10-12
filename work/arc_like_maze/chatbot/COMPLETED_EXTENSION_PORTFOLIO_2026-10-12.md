# Completed-extension portfolio — 2026-10-12

**Current referent.** Compare completed finite A/B-labeled rooted extension results before choosing a continuation, without conflating *individual* task success with a valid *combined* relation. Formal A and B are the specified finite operators, not a universal definition of A/B.

## Local integrated chatbot result

The full local chatbot (not yet wholly committed to GitHub) adds \`ab_chatbot_extension_portfolio.py\`, \`test_ab_chatbot_extension_portfolio.py\`, and \`run_extension_portfolio_demo.py\`. It uses existing pinned \`BacktrackedGoalExtender\` results; zero-read replays precede selection. In the source law phi=(0,0,1) and target law phi=(0,0,0), two independently completed candidates carry goals (0,1,0) and (0,1,1), respectively. Their full rooted pairings conflict, so a portfolio cannot legitimately claim both goals under a single chosen pairing.

- Candidate A: 9 paired states, 15 admitted edges.
- Candidate B: 9 paired states, 12 admitted edges.
- Joint selector: **PARTIAL_GOALS_WITNESSED**; selected candidate A, carrying **1/2 requested goals**, with 2 compatible nonempty subsets.
- Replayable collision: words \`B\` and \`ABBABA\` have different endpoints under the original law and identical endpoints under the changed law. This is a target-image collision.
- Identical-law control: 27 paired states, 54 admitted edges, 2/2 goals carried.

The local new module passed 10 focused tests, including an independent subset-score oracle on three pairs of finite laws. The prior backtracking module passed 9 and the path-union module passed 15 in separate reruns. A full regression attempt stalled: no new total such as 340/340 is claimed. Historical 330/330 belongs to the preceding unchanged version.

## Executable GitHub witness

\`finite_extension_portfolio.py\` and \`test_finite_extension_portfolio.py\` use the already committed standalone \`bounded_backtracked_goal.py\` and \`finite_goal_priority.py\`:

    cd work/arc_like_maze/chatbot
    python finite_extension_portfolio.py
    python -m unittest -q test_finite_goal_priority test_bounded_backtracked_goal test_finite_extension_portfolio

This is a **separate bounded finite witness**. It does not contain the integrated language bridge, snapshot cache, or remote identity checks; those remain in the local ZIP. Do not present these test files as independently executed on GitHub CI without CI evidence.

**Mathematical boundary.** Each finished greedy extension has already selected a mapping; separately valid maps need not be joinable. Future work may compare compatible *seed path unions before greedily completing them*, not retroactively assert that incompatible full results can be fused. No universal maximality or physically measured coupling is established.

No update to \`state/current.json\`: the current Continuity frontpage referent is separate.
