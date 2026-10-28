# NIH Phase 1 — Tracework oscillation harness

*The filename retains the former spelling for existing references.*

**Purpose:** Refine Tracework layer separation by repeatedly comparing NIH Phase 1 native evidence against independently produced Tracework representations. This is a harness specification, not a claim of completed execution.

## Fixed referent and preserved baseline
- Preserve the original twelve-job NIH Phase 1 W13/NIH source-owned native execution and its immutable source/run/artifact identities.
- Keep `research/nih_audit/PHASE1_OUTPUT_LANE.md` and `systems/workspace/nih_phase1_output_compare.py` as existing comparison inputs. Do not replace their original referent with the latest commit or a presentation layer.
- Each iteration pins a checkout SHA, exact source snapshots, workflow ID, run ID, artifact hashes, and candidate configuration. Missing identity is UNKNOWN.

## Layer contract
For every assertion, retain distinct records for:
1. **Input**: exact bytes, schema, and supplied boundaries.
2. **Source**: origin, retrieval/publication time, validity time, version, and hash.
3. **Observation**: directly recorded events, receipts, and source excerpts.
4. **Interpretation**: derived relationships, transformation rule, assumptions, and competing interpretations.
5. **Execution**: actual command, code SHA, environment, workflow/run/job IDs, exit status, logs.
6. **Verification**: independent replay or check, comparator version, shared cases, discrepancies, limitations.
7. **Presentation**: projection and display state, with links back to the above; never an independent proof.

A projection must not promote interpretation to observation, documentation to execution, workflow success to research verification, or an unknown to a pass. Every cross-layer edge must name its origin, target, rule, and evidence. A missing edge remains explicitly unresolved.

## Oscillation cycle
1. **Pin** the original baseline and candidate snapshot without rewriting either.
2. **Run** one bounded Phase 1 candidate through its native entrypoint; capture success *and* failure receipts.
3. **Project** results through Tracework, preserving every layer's original identity.
4. **Compare** the original native records, candidate receipts, Tracework projection, and rendered claims on the *same shared cases*; separately record feature coverage.
5. **Challenge** with one boundary perturbation: future evidence arriving late, source conflict, stale retrieval, contradictory observations, forged relationship, missing artifact, nonzero exit, or presentation-only claim.
6. **Trace** each discrepancy to the first layer/edge where provenance, time, referent, or status changed. Do not silently repair or discard mistakes.
7. **Correct** only the implicated transformation or guard; preserve before/after artifacts and regression cases.
8. **Repeat** the original case and prior failures, then run the next perturbation. Do not claim convergence from one clean pass.

## Per-iteration evidence record
```json
{
  "iteration": "NIH-P1-TW-0001",
  "baseline": {"commit": null, "run_id": null, "artifact_sha256": null},
  "candidate": {"name": null, "commit": null, "workflow": null, "run_id": null},
  "inputs": [], "sources": [], "observations": [], "interpretations": [],
  "executions": [], "verifications": [], "presentations": [],
  "edges": [], "boundary_challenge": null,
  "discrepancies": [], "corrections": [], "regressions": [],
  "status": "NOT_RUN"
}
```

## Required negative tests
- Future-dated source is unavailable to an earlier decision, even when later published.
- Retrieval time and valid time remain distinct.
- Conflicting sources stay conflicting until an evidenced rule resolves them.
- A forged source-to-result edge is rejected; path overlap is not native execution proof.
- Absent receipts and failed jobs cannot become PASS or winning candidates.
- An outdated projection cannot claim live state.
- Presentation text cannot increase verification level.
- Re-running identical pinned inputs yields comparable receipts; any nondeterminism is recorded, not hidden.

## Decision and reporting
- Report each iteration as NOT_RUN, BLOCKED, RUNNING (only with verified run ID), FAIL, or PASS_WITH_EVIDENCE.
- For every check record EXPECTED, OBSERVED, SOURCE, RUN, and FIRST_BROKEN_BOUNDARY.
- **Zero observed cross-layer promotions** is a test target, not a universal guarantee. Retain failures as regression cases.
- The existing output comparator's REPORTED_PASS is not an independently verified PASS; its `selection: UNDETERMINED` remains authoritative until source-backed shared-case replay.
- Do not label this harness complete or Tracework universally safe without actual native runs and retained evidence.

## Next execution step
Wire an executable boundary-test runner to the existing `.github/workflows/nih-phase1-output-comparison.yml` or a separate explicitly named workflow; have it emit per-iteration machine-readable records and a failing exit code for violated invariants. Verify the Actions run and uploaded artifacts independently before advancing status.
