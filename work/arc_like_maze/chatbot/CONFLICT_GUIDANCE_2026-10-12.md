# Conflict-guided finite chatbot continuation — 2026-10-12

**Referent.** Under two explicitly specified finite A/B-labeled transformation laws, can an excluded labeled edge in one witnessed rooted pairing be admitted under a *different*, independently verified partial pairing? A/B is the language-level relation under investigation; these letters are specific finite generators only.

## Verified finite observation

Original law phi=(0,0,1), changed law phi=(1,0,1), rooted at (0,0,0).

- First seed words AAAB, BBBB, BAABA, ABAABB: 27 paired states, 41 admitted A/B edges and 13 excluded edges.
- Alternative seed words AAAB, ABBAA, BAABA: 24 paired states, 40 admitted edges and 8 exclusions.
- The old-state edge (1,2,0) --B--> (1,1,1) is excluded under the first pairing: old target (1,1,1) is *already assigned* new image (1,1,0), while the witnessed B step from the paired source reaches (1,1,2).
- The alternative pairing assigns the old target (1,1,1) to (1,1,2) and admits the same old B edge.
- The original excluded-word witness retains the separating equality under the two laws; the alternative is rechecked from the finite laws. This is **not** a proof that the two full pairings can be combined.

Run from this directory:

    python finite_conflict_guidance.py
    python -m unittest -q test_finite_conflict_guidance.py

The four finite-law tests passed in the local package. This GitHub sidecar uses fully given transformation laws, not the integrated snapshot owner, remote provenance or language bridge.

## Full local chatbot implementation

The integrated source in ab_chatbot_conflict_guided_2026-10-12.zip (SHA-256 dd353e2e39025c1474b9712be3a2378a9f50babdf97d39979ad3ee0a98ed0072) preserves all 84 predecessor files unchanged. It adds the ConflictGuidedPortfolio with the existing BranchDiscoverer -> PathUnionAgent -> UnionEdgeExtender, 10 focused tests, demo, finite reference and verification notes; 91 files total. The ZIP is a conversation artifact and has NOT been copied wholesale to this repo.

The guidance policy prioritizes an alternative whose **already witnessed seed** contains the old labeled edge the first extension excluded, and only reports re-admission after completing/replaying the alternative. It preserves stale/UNKNOWN/remote-source conditions.

Local completed verification: 10/10 new integration tests, 4/4 standalone finite tests, 12/12 seed-first legacy tests, and 5/5 selected older union/extension/portfolio checks. Broad older regression runs timed out; full historical suite and GitHub CI are **not claimed**.

## Essential negative control

With equal 3-trial budgets, original fixed ordering and guided ordering both carry 2/2 goals and each selects a best 41-edge extension. With 4 trials, fixed ordering achieves 42 edges versus guided ordering's 41. Counterexample-driven ordering is a *new tested exploratory decision*, **not a proven improvement in completion rate, coverage, or observation cost**.

**Next warranted movement:** Compare whether exclusion-targeted continuation improves new-goal coverage and costs across a declared set of finite laws/goals with equal budgets. Retain negative cases and restrict conclusions to tested scopes. This research record does not change the separate Continuity project pointer.
