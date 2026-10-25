# NIH Phase 1 — Tracework independent comparison handoff

Status: ADMITTED FOR COMPARISON / NOT EXECUTED. Date: 2026-10-25.
Parent referent: original NIH-P1-SCOPE and its completed 12-job W13/NIH native evidence.
Method: [Universal harness](../../UNIVERSAL_HARNESS.md). Preserve original receipts append-only.

## Same-input comparison
A: replay original NIH Phase 1 native scope, generated temporal_query.py and existing 12-job evidence without mutation.
B: Tracework A/B observation of the identical native operations, with source revisions, hashes, input IDs, valid-at and known-at cutoffs, outputs and transitions.
C: independently implemented Tracework-native computation on the same pinned fixture; do not merely wrap or relabel the original Python executable. If C is not executable, record BLOCKED, not PASS.

## Required evidence
- Exact commit, fixture hashes, dependencies, command, runtime, exit status, stdout/stderr and receipt paths for each executable run.
- Original baseline scope, temporal frontier, two-clock, source-motion and uncertain-publication test cases; distinguish hypothetical source intervals from authenticated source history.
- Compare evidence ID partitions T(K,V), S(V), L(K,V), fixed-valid-time monotonicity under append-only evidence, source changes/conflicts, and uncertain publication states.
- Negative controls and counterexamples; no silently corrected failures.
- Side-by-side correctness, boundary coverage, source provenance, execution cost and drift.
- Report winner only for criteria with independent witnesses; otherwise INDETERMINATE.

## Boundaries
No NIH submission or new checkpoint is implied. Do not change original Phase 1 source, original journal, 12 native jobs or historical results. No thirteenth source-owned worker. Existing Phase 1 documentation is prior evidence, not proof that this comparison executed.

## Next executable handoff
Run the existing repository-native tests and Phase 1 reproductions in an isolated GitHub execution environment; record the receipts. Then implement and execute an independent Tracework-native comparator using the same fixture and universal harness retention record. Publish results in this branch before proposing merge.
