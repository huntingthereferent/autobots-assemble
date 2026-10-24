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