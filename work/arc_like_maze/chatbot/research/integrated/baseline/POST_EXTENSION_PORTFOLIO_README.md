# A/B finite chatbot — downstream seed-union selection (2026-10-12)

**Referent:** Can the existing finite goal agent compare several witnessed compatible seed unions **after** extending each one, rather than taking the union with the strongest initial seed score? Formal `A` and `B` are scoped generators; this implementation does not define language-level A/B or physical coupling.

## Executed comparison

Old law `phi=(0,0,1)`, changed law `phi=(1,0,1)`, root `(0,0,0)`, source goals `(0,1,0)` and `(0,1,1)`. With identical depth, candidate-pool, and goal conditions:

| Construction | Chosen seed words | Goals carried | Admitted A/B edges |
|---|---|---:|---:|
| Seed-first (prior) | `AAAB`, `BAAA`, `ABBAA` | 2/2 | 40 |
| Post-extension portfolio | `BAAA`, `BBBB` | 2/2 | **42** |

The post-extension layer evaluated six candidate seed unions, checked the retained edges on both pinned sources, preserved rejected transitions, and chose based on goal coverage first and admitted transitions second. The finite-law mirror independently reproduces the 40→42 comparison. Three law-pair controls, source-revision invalidation, corrupt-cache invalidation, remote-source labeling and low-budget resumption were tested.

## Files added (existing 73 files unchanged)

- `ab_chatbot_post_extension_portfolio.py`: integrated bounded portfolio; reuses BranchDiscoverer, PathUnionAgent and UnionEdgeExtender.
- `test_ab_chatbot_post_extension_portfolio.py`: 10 integrated tests.
- `run_post_extension_portfolio_demo.py`: runnable integrated demo.
- `finite_post_extension_portfolio.py` and `test_finite_post_extension_portfolio.py`: independent full-law finite comparator and four tests.
- `finite_goal_priority.py`: self-contained mirror of the earlier public finite Law model needed by the standalone tests; not a replacement of the main chatbot.
- This README.

Run:

    python run_post_extension_portfolio_demo.py
    python -m unittest -q test_ab_chatbot_post_extension_portfolio.PostExtensionPortfolioTests
    python finite_post_extension_portfolio.py
    python -m unittest -q test_finite_post_extension_portfolio.PostExtensionFiniteTests

**Verification completed this turn:** 10 integrated tests and 4 standalone finite-law tests passed. The seed-first legacy module passed 12, completed-extension portfolio 10, and union extension 15 in independent completed runs. A larger grouped run timed out; do not claim a complete historical regression pass. No GitHub CI execution was witnessed.

**Boundary:** Exact ranking only over at most 24 selected candidate seed unions, themselves sampled from a bounded prefix pool. A finite trial's verified partial pairing is not necessarily maximal, and its rejected edges are local to that pairing. Unobserved physical or remote source claims remain unverified. The portfolio preserves UNKNOWN/WALL and never labels a stale source result complete.

**Next warranted experiment:** Explore a backtracking candidate generator informed by the rejected-edge witnesses rather than relying only on a pool of the shortest goal-reaching words, while retaining explicit search cost and evidence boundaries.
