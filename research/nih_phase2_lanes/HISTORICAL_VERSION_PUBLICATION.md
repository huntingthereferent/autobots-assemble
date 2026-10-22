# NIH Phase 2 — Historical version and publication-time authentication

**Trace:** existing [parent PR #268](https://github.com/huntingthereferent/autobots-assemble/pull/268) → [tracking issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106) → this independent branch.

## Current referent
The [#268](https://github.com/huntingthereferent/autobots-assemble/pull/268) source-clock result established a real record-status contrast and conditional source-reported posting clocks, **not** an independently witnessed first-public timestamp for an exact historical version. Original clinical `valid_at` is unknown. The upstream evidence gap stays tracked in [issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106).

## Independent movement
Select an original version-specific record with immutable version identifier and **an independent source-backed publication/availability witness**; verify all identities, original full/field hashes and actual observation time separately. Preserve distinct `submitted_at`, `source_reported_posted_at`, `first_public_at` (only if genuinely authenticated), `observed_at` and `valid_at` (unknown unless supported).

## Measured outcomes
If availability cannot be verified independently, emit `UNAVAILABLE` with exact source refusal, never invent an as-known-at cutoff. If authenticated, create separate query receipts and independent temporal/static oracle without mutating W13's original synthetic executable or 12-job native journal. No inference about clinical event time.

## Test gates
Exact source version and status consistency, content hash and timestamp negative controls, retracted/revised record handling, source availability rejection, date-order separation and zero unsupported clinical-validity claims. Keep original public source bodies out of artifacts.

## Lane boundaries
- **Status (2026-10-22): OPEN / SPECIFIED, NOT EXECUTED.** No new scientific finding, worker job, checkpoint, native CI PASS or NIH submission is asserted by opening this branch.
- Source-owned work stays in its parent code area; this file specifies an independently auditable branch without changing other NIH source, W13 native 12-job journal/executable, WORLD, ARC or license.
- A failure, empty result or unavailable upstream source is retained as evidence, not repaired with fictional examples.
- Before any merge: implement finite source-owned tests, run dedicated authentic-source GitHub Actions, record artifact hashes and negatives, then review whole-repo protocol CI against the same exact branch head.
- This is independent research connected to NIH-style requirements, not institutional affiliation, clinical validation, patient-level inference, official challenge scoring or a grant application.
