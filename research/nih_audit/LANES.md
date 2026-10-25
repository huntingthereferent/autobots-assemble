# NIH audit — lane register (2026-10-24)

Status: initialized; no new NIH execution claimed.

This register is an audit plan, not a substitute for source evidence. The NIH source location must be resolved before comparison results are accepted.

| Lane | Input | Output | Initial state |
|---|---|---|---|
| NIH-01 inventory | NIH-related repository sources and prior run records | manifest with paths, hashes, timestamps | OPEN / source discovery |
| NIH-02 replay | frozen inputs, environment and comparator | reproducibility log | BLOCKED on inventory |
| NIH-03 differences | matched pairs and previous discrepancy records | categorized differences with examples | BLOCKED on replay |
| NIH-04 invariants | declared mathematical operators and domains | tested invariants with witness or failure | BLOCKED on specification |
| NIH-05 counterexamples | discrepancy classes and bounded search space | minimized counterexamples | BLOCKED on NIH-03 |
| NIH-06 provenance | run IDs, source versions, logs and cancellation records | evidence-quality audit | OPEN / inspection |
| NIH-07 reconciliation | reviewed outputs from other lanes | reconciled report and next bounded experiment | BLOCKED on review |

## Audit contract
1. Never treat a reported difference count as a validated result without its source, comparator, and matching rules.
2. Preserve raw records and hashes; keep interpretation separate.
3. Mark missing inputs UNKNOWN, not FAIL.
4. A canceled or interrupted run is not a negative scientific result.
5. A correction must specify what changed, why, and a replay test.
6. Workers only become RUNNING when an actual executor/run ID is recorded.
7. Keep NIH independent from ARC and WORLD evidence; cross-lane comparisons require explicit mappings.

## Next movement
Resolve canonical NIH paths; inventory source and previous comparison witnesses; replay one smallest deterministic comparison; classify the first discrepancy before scaling.
## Source discovery — 2026-10-24
Canonical NIH source is under `systems/workspace/`, not `research/nih/`.

- [Cross-source status comparison](../../systems/workspace/NIH_P2_STATUS_DIFFERENCE_SEARCH.md) and [implementation](../../systems/workspace/nih_p2_historical_status_difference_search.py)
- [Two original archive authentication](../../systems/workspace/NIH_P2_TWO_AACT_SNAPSHOT_BOUNDARY.md) and [implementation](../../systems/workspace/nih_p2_two_aact_snapshot_comparison.py)
- [Cross-source temporal boundary](../../systems/workspace/NIH_P2_CROSS_SOURCE_BOUNDARY.md)
- [Source owner/date relation](../../systems/workspace/NIH_P2_AACT_OWNER_DATE_LINK.md)
- [Synthetic source variations](../../systems/workspace/NIH_P2_SOURCE_VARIATIONS.md)
- [Existing research viewer](../../docs/research/nih.html)

### Preliminary neutral audit
The original comparison records 432,597 shared NCT IDs, 1,345 differing normalized status values, and 386 IDs found only in the 2022-labeled source. These are historical documented results, not results from a new execution. Publication date of the other Zenodo deposit does not establish the underlying AACT collection date; source chronology remains unresolved. Earlier selected NCT IDs NCT03280849 and NCT04153409 were Completed in both archives, so they are negative controls rather than status-change witnesses.

NIH-01: source paths RESOLVED, full artifact/hash inventory still pending.
NIH-02: ready for test-only replay, but large original downloads require an executor.
NIH-03: source comparison exists; discrepancy classification remains to audit.
NIH-04/05: do not invent new mathematical claims; derive bounded test specifications from existing implementations.
NIH-06: preserve native CI receipts separately from GitHub Pages presentation.
NIH-07: no new reconciliation verdict until fresh execution.

### Execution requirements
A worker lane is active only after a real runner/job ID and persisted receipt are attached. Do not claim the markdown register creates workers. Existing documented replay: `python -m unittest -v network.tests.test_nih_p2_two_aact_snapshot_comparison`; then `python -m systems.workspace.nih_p2_two_aact_snapshot_comparison --output-dir /tmp/nih-p2-two-original-archives`. The original archive replay downloads approximately 525 MB. Do not launch it implicitly.

## Referent correction — Phase 1 output selection (2026-10-25)

**Original audit objective:** compare completed NIH Phase 1 output variants under a common, bounded evaluation and select the strongest *verified* version. This supersedes treating Phase 2 archival source discovery as the audit objective. Phase 2 provenance remains a separate research boundary and may supply a constraint, not the selection target.

### Candidate outputs to compare
- Original NIH Phase 1 packet and native twelve-job W13/NIH execution (baseline; do not overwrite).
- Original-world Phase 1 frontier (`NIH_PHASE1_WORLD_FRONTIER.md`).
- Two-clock world (`NIH_PHASE1_WORLD_TWO_CLOCK.md`).
- Source-motion world (`NIH_PHASE1_WORLD_SOURCE_MOTION.md`).
- Publication-uncertainty world (`NIH_PHASE1_WORLD_PUBLICATION_UNCERTAINTY.md`).

These are **different scoped extensions**, not yet demonstrated interchangeable versions. First normalize the comparable outputs and label non-comparable features instead of inventing a ranking.

### Finite comparison motion
1. **Inventory outputs**: collect exact artifact paths, hashes, producing run/commit, source scope, inputs and output schema for every candidate. Missing receipts remain UNKNOWN.
2. **Define common fixture**: the same original synthetic Phase 1 scope, knowledge and validity queries, expected evidence partitions and fixed execution constraints. Preserve source-owning original program and original journal.
3. **Replay each candidate**: run existing dedicated tests and actual browser/native experiment as applicable. Record run IDs, source SHA, observations, runtime and failures; unit tests alone are not live execution evidence.
4. **Compare A/B**: evaluate correctness, withheld-future safety, conflict handling, provenance, reproducibility and capability coverage. Distinguish a new capability from improvement on a shared metric; do not award points for a feature absent from the common test.
5. **Select and reconcile**: name the strongest verified version **for each common domain** and an overall choice only if one candidate dominates under declared priorities. If no defensible single winner, return a Pareto set and the smallest discriminating experiment.
6. **Close** only when the decision, supporting receipts and remaining boundaries are retained. A newer commit or more features alone cannot win.

### Execution boundary
This register is a source-backed plan, not a new runner. The original audit referent is output comparison. Do not silently substitute NIH P2 archival comparisons, synthetic unit tests, or a Phase 1 proposal for executed Phase 1 output candidates.
