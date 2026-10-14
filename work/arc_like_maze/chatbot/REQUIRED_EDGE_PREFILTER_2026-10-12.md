# Evidence-preserving candidate prefilter — 2026-10-12

**Referent:** In a finite correspondence process, does a previously witnessed A/B-labeled transition provide a sound way to reject a candidate *before* full extension? Yes, but only relative to a **declared must-admit-edge task** and fixed, independently replayable seed state assignments. An exclusion from another pairing does not globally forbid an edge.

## Local integrated experiment

Original law phi=(0,0,1), changed law phi=(0,0,0), root (0,0,0), requested goals (0,1,1) and (0,2,0). **Additional requirement:** preserve root B transition. This extra requirement is important: it is a different task from merely completing the two goals.

- The prior fixed-order portfolio evaluates 11 completed seed extensions. When applying that same required edge to its finished results, the best eligible result carries **1/2 goals**.
- The optional prefilter identifies **two** seed unions whose existing target-state assignments collide with the already-observed root B image. These pairings cannot admit the required edge *while keeping their seeds*. The other nine are not ruled out.
- It evaluates **9 rather than 11** extensions and selects **exactly the same best eligible result**, with **1/2 goals**.
- Independently pinned local owner observations: baseline **28 old + 18 changed = 46**; prefiltered **26 old + 18 changed = 44**. This is a two-observation saving in one declared fixture, not a global performance guarantee.
- Each exclusion stores the old and changed source, action and observed targets, any already-assigned target image/preimage, and the type of collision. A cached-edge witness must replay on subsequent reads, or the current result becomes WALL_OBSERVATION. Source revision changes become UNKNOWN_VERSION. Incomplete or remote-reported provenance cannot become a local pruning certificate.
- Under a different required edge, the tested candidate portfolio may return REQUIRED_EDGE_UNPROVED. This is *not* proof that no other partial correspondence could satisfy it.

## GitHub standalone finite oracle

The repository's finite_required_edge_guard.py reconstructs eleven already-discovered candidate seed word tuples directly under the declared complete laws and checks which can satisfy the root B preservation requirement without changing their paired seeds. Four standalone finite tests reproduce **2 exclusions / 9 not contradicted**. This standalone program is a finite mathematical checker; it does not execute the source-pinned local integrated correspondence process.

Run in this directory:

    python finite_required_edge_guard.py
    python -m unittest -q test_finite_required_edge_guard.py

## full local integrated implementation

The separate artifact ab_chatbot_required_edge_prefilter_2026-10-12.zip (SHA256 65aaa31530d98eed3eaee8568d14c3a0186a3371896a5e261aa10b5c240bb73a) includes 108 files, leaving all previous 101 files byte-for-byte unchanged. Added integrated module, 8 tests, standalone finite oracle and 4 tests, demo, JSON record, and reproduction README. Default policy remains fixed-order; the required-edge prefilter is an *opt-in contract*.

Local completed verification: 8/8 new integration tests, 4/4 standalone finite tests, 10/10 previous conflict-guided, and 25/25 previous post-extension tests. **47 tests in separate runs**. Wider grouped regression invocations timed out and are not counted. No GitHub CI result is claimed.

**Next mathematical boundary:** Do not silently manufacture preservation requirements. Investigate how a task can explicitly supply such a requirement, then compare on held-out finite cases with query costs and failure witnesses. Keep A/B's language-level referent distinct from these specified finite generators. Leave the separate Continuity state/current.json unchanged.
