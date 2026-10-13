# Cross-pin comparison of two finite owner revisions — 2026-10-13

**Current referent:** Extend the existing A/B finite mathematical chatbot to compare **explicitly requested word relations** under two *independently owner-pinned revision snapshots*. Replaying a relation at a new revision is a **new witness**; copying historical labels, metadata, or cached transitions into the new snapshot is not evidence. The language-level A/B referent is not defined by these two finite mathematical generators.

## Witness and exact boundary

One locally held owner issued two immutable, separately pinned local snapshots: historical revision **0**, phi=(0,0,0), and new revision **1**, phi=(0,1,2), both identity state labeling, rooted at (0,0,0).

- Explicit words empty string and AAA: both end at (0,0,0) under both revisions; that *declared endpoint equality* is preserved.
- Explicit words BA and ABB: both end at (1,1,0) under revision 0. Under revision 1, BA ends at (1,1,0) and ABB ends at (1,1,2); that *declared equality* changes.
- Separate owner-observed transition caches: **7 old and 7 new unique labeled edges**. The new cache starts empty. Both sources' retained used edges are re-audited on zero-read revisits against their respective owner-held historical views.
- One initial zero-new-edge step is SEARCHING, never claimed completion. An exhausted source budget is UNKNOWN_BUDGET, corrupted cached edge WALL_OBSERVATION, withdrawn/substituted pin OWNER_PIN_UNPROVED, and replaced snapshot/version UNKNOWN_VERSION.

The integrated local `CrossPinComparison` adds a strict structured input:

    {"required_owner_pins":{"old":"<registry-issued-token>","new":"<registry-issued-token>"},
     "compare_words":[["","AAA"],["BA","ABB"]]}

A pair consists of distinct explicit A/B words of length <=12; 1..8 pairs; both exact owner pins are required. This is a narrow word-endpoint equality comparison, **NOT** a demonstration that all A/B-labeled transitions agree, a whole-system conjugacy, continuity of owner identity outside the process, or a universal physical result. Pin predecessor linkage is historical attribution, not a mathematical matching relation.

## Integration verification

The full 153-file local source package `ab_chatbot_cross_pin_comparison_2026-10-13.zip` (SHA-256 `ca428238c2e4cfd90da874cfafc67fe334a2590201cb84001034147a42ffe728`) preserves **all 145 predecessor files byte-for-byte**. It adds `ab_chatbot_cross_pin_comparison.py` with live local pin validation and zero-read replay; 10 new tests; an independent finite word-relation implementation and 5 tests; runnable demo; README and machine-readable test/evidence records.

Completed local modules: 10 new integration + 5 standalone finite + 10 owner pin + 14 provenance + 14 rule-change + 12 mixed obligation + 35 language bridge = **100 passing tests**. Full historical suite not rerun; GitHub CI not verified. This record does not claim that the full integrated chatbot has been committed to GitHub.

## GitHub standalone finite reference

The executable finite checker uses the previously committed `finite_goal_priority.Law`, and reproduces both positive and negative word equalities without depending on the chatbot's observation bookkeeping:

    cd work/arc_like_maze/chatbot
    python finite_cross_pin_relation.py
    python -m unittest -q test_finite_cross_pin_relation.py

This reference knows its complete finite laws; it does **not** model HTTP origin verification, snapshots, owner revocation, or authenticated source identity. The complete package is a separate local artifact.

**Next:** Explore whether multiple individually witnessed word relationships can be joined into a jointly consistent partial state correspondence **without** assuming off-path identity or transporting unobserved edges. Leave the separate Continuity referent and `state/current.json` unchanged.
