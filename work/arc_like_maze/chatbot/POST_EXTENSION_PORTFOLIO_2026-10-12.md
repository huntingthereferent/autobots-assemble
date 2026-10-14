# finite correspondence process: compare goal-seed unions after extension (2026-10-12)

**Current referent:** Within fully specified finite A/B-labeled generators, compare several *compatible root-path unions* by the relation that survives after admitted-edge exploration. This is a mathematical experiment, not a claim that A/B language is a finite state machine or that a physical couplesense mechanism has been realized.

## Verified comparison

Original law phi=(0,0,1); changed law phi=(1,0,1); root=(0,0,0). Two source goals: (0,1,0) and (0,1,1). Both selections carry 2/2 goals.

- **Earlier seed-first:** selected AAAB, BAAA, ABBAA; 40 admitted transitions.
- **New post-extension portfolio:** evaluated six candidate seed unions; selected BAAA, BBBB; 42 admitted transitions, 12 excluded under that pairing.
- The candidate pool is selected by compatible witnessed paths. Each candidate is extended under the stated two finite laws, and the final score prioritizes completed goal coverage, then admitted edges. The additional admitted edges are verified within these rules only.
- Controls include an incompatible changed-law case that stays PARTIAL, and an identical-law case reaching the closed 27-state component of 54 edges.

## Runnable GitHub witness

From work/arc_like_maze/chatbot:

    python finite_post_extension_portfolio.py
    python -m unittest -q test_finite_post_extension_portfolio.py

The standalone witness uses checked-in finite_goal_priority.py and finite_seed_first.py. Four finite tests passed in a separate local run using a law-equivalent mirror of those dependencies. GitHub CI has not been checked.

## integrated local correspondence process

Separate downloadable package ab_chatbot_post_extension_portfolio_2026-10-12.zip (SHA-256 f7323f2093ffae27e6988cbfbb4676ce9d949f463176d0c8d5a7a72c12f49ff1), containing 84 files with all prior 73 files byte-for-byte unchanged. Its new PostExtensionPortfolio reuses the pinned BranchDiscoverer, PathUnionAgent and UnionEdgeExtender. It audits each complete candidate on every final read and retains remote-source status rather than upgrading it.

Local verification: 10/10 integrated post-extension tests, 4/4 standalone finite tests; adjacent prior modules separately passed seed-first 12/12, completed-extension portfolio 10/10 and union extension 15/15. A grouped regression timed out before completing; no overall historical pass is claimed.

**Wall:** Candidate paths, subset enumeration, and trial budget remain bounded. Different seed unions may admit different partial correspondences; this result does not prove maximality, unrestricted learning, whole-system equivalence or a physical A/B witness.

**Next:** Use admissible-edge exclusions as evidence to prioritize new candidate path choices, while tracking the observation cost of each exploration. The current Continuity project pointer is not changed.
