# NIH Phase 2 — Typed biomedical path semantics

**Trace:** existing [parent PR #290](https://github.com/huntingthereferent/autobots-assemble/pull/290) → [tracking issue #399](https://github.com/huntingthereferent/autobots-assemble/issues/399) → this independent branch.

## Current referent
Observed original PharmKG-8K edge witnesses from [#290](https://github.com/huntingthereferent/autobots-assemble/pull/290). Mixed paths raised Hits@3 but first-choice accuracy was weak; equivalent static reasoning matched A/B exactly.

## Independent movement
Authenticate the original source-owner vocabulary, relation direction and entity types before declaring any biomedical relation composition. On the exact pinned training graph, freeze type-safe path rules using training data and published external definitions only. Then challenge them on disjoint untouched gold without exposing labels to rule discovery.

## Measured outcomes
Record original source path and rejection rationale for each candidate, Hits@1/3, MRR, abstention rate, coverage, same sample vs fixed untyped baseline, and *equally expressive typed static reasoner* with identical information. Report whether semantics improved selectivity; a loss or no documented semantics is an admissible result.

## Test gates
Source identity and checksums, zero test/validation leakage, relation/type direction negatives, heldout overlap rejection, independent per-edge oracle, reproducible frozen sample and complete failing examples.

## Lane boundaries
- **Status (2026-10-22): OPEN / SPECIFIED, NOT EXECUTED.** No new scientific finding, worker job, checkpoint, native CI PASS or NIH submission is asserted by opening this branch.
- Source-owned work stays in its parent code area; this file specifies an independently auditable branch without changing other NIH source, W13 native 12-job journal/executable, WORLD, ARC or license.
- A failure, empty result or unavailable upstream source is retained as evidence, not repaired with fictional examples.
- Before any merge: implement finite source-owned tests, run dedicated authentic-source GitHub Actions, record artifact hashes and negatives, then review whole-repo protocol CI against the same exact branch head.
- This is independent research connected to NIH-style requirements, not institutional affiliation, clinical validation, patient-level inference, official challenge scoring or a grant application.
