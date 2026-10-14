# Required-edge witness preflight — October 12, 2026

**Referent.** The prior conflict-guided heuristic did not win an equal-budget comparison. This continuation asks whether a *previously observed labeled edge*, when explicitly required by a task, can eliminate candidate **seed pairings** that are mathematically inconsistent with preserving that edge, before performing full candidate extensions.

The answer is **yes for a declared required-edge task**, with an important distinction: a conflict from one partial pairing does *not* disqualify a different pairing. We only reject a particular candidate when its **unchangeable seed assignments** contradict cached, owner-consistent old/new edge observations. A candidate with missing observations remains undecided, never guessed false.

## Executed experiment

Finite laws original phi=(0,0,1), changed phi=(0,0,0), root=(0,0,0); two requested source goals (0,1,1), (0,2,0), and an **additional requirement** to admit the old root `B` edge. The search configuration is `max_depth=6`, `variants_per_goal=4`, `candidate_limit=7`, `max_trials=12`; each run receives its own pinned owners with capacity 54 edges per side.

- The unconstrained fixed portfolio initially offers **11** compatible seed unions. Replaying all 11 and **only then** applying the exact same root-B requirement selects a candidate carrying **1/2 goals**.
- The required-edge prefilter rules out exactly **2** of the 11 seed unions from **existing** root-B observations. Each has a **target-image collision**: old root-B target `(0,1,0)` is not yet in the seed, but its new image `(0,1,0)` is already assigned to a *different original state* by the seed. Extending the seed can never repair that injectivity conflict without changing its original pairing.
- Nine remaining candidates are evaluated; the best eligible complete result is **exactly the same** as the unpruned eligible oracle, carrying **1/2** required goals. The prefilter performs **9 vs 11** full extension trials and **44 vs 46** total old+new owner observations (original 26 vs 28; changed 18 vs 18) in this *specific* fixture.
- **Do not compare the 1/2 result to the unrestricted portfolio's 2/2 as an algorithmic failure.** The filtered and baseline eligible oracles both solve the stricter task. No improvement in general search completeness or arbitrary-world performance has been demonstrated.
- A different required edge not admitted by any of these completed candidates returns `REQUIRED_EDGE_UNPROVED` rather than a global impossibility claim. Missing cached observations return `UNDECIDED`; stale versions and tampered owner caches revoke saved certificates. Remote-reported edges cannot be used to produce local exclusion certificates.

## Run

From this folder:

```bash
python run_evidence_prefilter_demo.py
python -m unittest -q test_ab_chatbot_evidence_prefilter
python -m unittest -q test_finite_required_edge_guard
```

**Verification actually executed:** new integrated preflight 8/8; independent finite guard 4/4; unchanged conflict-guided 10/10; unchanged post-extension portfolio 25/25. Total 47 tests in four separate completed runs. Grouped older regression attempts timed out. No claim is made that the entire historical suite passed, or GitHub CI ran.

The independent finite guard checks the two excluded candidate word sets and nine noncontradicted sets from complete finite-law arithmetic; it does not implement pinned source snapshots and is not the full chatbot.

## What changed

This version is strictly additive to the existing local Python implementation: `ab_chatbot_evidence_prefilter.py`, `test_ab_chatbot_evidence_prefilter.py`, `finite_required_edge_guard.py`, `test_finite_required_edge_guard.py`, `run_evidence_prefilter_demo.py`, this report, and `EVIDENCE_PREFILTER_RESULTS.json`. Earlier source remains untouched; the prefilter is an **opt-in task constraint** and leaves the previous fixed-order default and conflict exploration policy unchanged.

**Next grounded movement:** test whether an explicit higher-level preservation requirement can be generated from a task *without inventing one*, and compare the cost on held-out finite law/goal cases. Avoid universal edge bans; preserve the witness conditions, provenance, and task distinction.
