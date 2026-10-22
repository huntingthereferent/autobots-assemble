# NIH Phase 2 — Full-candidate frozen benchmark and error audit

**Trace:** existing [parent PR #290](https://github.com/huntingthereferent/autobots-assemble/pull/290) → [tracking issue #401](https://github.com/huntingthereferent/autobots-assemble/issues/401) → this independent branch.

## Current referent
[#288](https://github.com/huntingthereferent/autobots-assemble/pull/288) and [#290](https://github.com/huntingthereferent/autobots-assemble/pull/290) produced nonstandard *nine-candidate* link rankings. The 8 alternative tails were **unlabeled**; published splits were random rather than temporal. These metrics are not a real temporal NIH score.

## Independent movement
Freeze the original #290 executable/configuration and inspect an **unseen nonoverlapping selection** under predeclared full eligible target-tail ranking (or a transparently fixed broad bounded pool if full is infeasible). Do not change inference or use untouched test labels to tune parameters. Implement independent filtered-rank oracle, tie policy, train/valid/test leakage check and entity/relation candidate count.

## Measured outcomes
Hits@1/3/10, filtered MRR, candidate universe, per-relation error/abstention, actual runtime/peak memory, and equal-graph equal-capability static + simple baselines. Preserve all losses; zero performance gain is a valid answer.

## Test gates
Original full-file hashes, no sample overlap with #288/#290, frozen rules, test isolation, candidate pool provenance, independently replayed rankings and strict bounded execution. Do not relabel unknown alternatives as true negatives.

## Lane boundaries
- **Status (2026-10-22): OPEN / SPECIFIED, NOT EXECUTED.** No new scientific finding, worker job, checkpoint, native CI PASS or NIH submission is asserted by opening this branch.
- Source-owned work stays in its parent code area; this file specifies an independently auditable branch without changing other NIH source, W13 native 12-job journal/executable, WORLD, ARC or license.
- A failure, empty result or unavailable upstream source is retained as evidence, not repaired with fictional examples.
- Before any merge: implement finite source-owned tests, run dedicated authentic-source GitHub Actions, record artifact hashes and negatives, then review whole-repo protocol CI against the same exact branch head.
- This is independent research connected to NIH-style requirements, not institutional affiliation, clinical validation, patient-level inference, official challenge scoring or a grant application.
