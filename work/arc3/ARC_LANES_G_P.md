# ARC expansion — research lanes G–P

Status: registered research questions only. No native experiment or successful result is implied by this file.

Scope: original ARC-AGI-3 SDK observations in `work/arc3/`. Keep the separate `work/arc_like_maze/` mathematical construction distinct. Existing A–F lanes remain active and independent.

## Shared evidence contract
Each lane must state: source SDK/version and source commit; native reset/action history; actual returned frames and status; artifact IDs and hashes; hypothesis frozen before a holdout; predicted versus observed outcomes; counterexamples; stop/compute budget; and an explicit next test. A successful workflow run is not evidence of a solved ARC level. No repeated green runs solely to inflate activity.

## G — Evidence inventory
Question: Which native observations are actually comparable?
Input: source-owned ARC A–F run artifacts, JSON/NPZ, provenance.
Output: deduplicated inventory keyed by reset, action history, SDK version, source SHA, artifact hash; unresolved missing artifacts clearly flagged.
Gate: independent artifact/hash reconciliation, no invented observations.

## H — Minimal counterexamples
Question: What is the shortest native history that breaks each frozen transition rule?
Input: C long-history counterexamples, B controls.
Output: candidate minimized histories with exact expected/actual pixel transitions.
Gate: rerun the minimal history in fresh native resets; report nondeterminism.

## I — Action-order dependence
Question: Which ordering and spacing of actions alters the next native response?
Input: B temporal factorial observations.
Output: pre-registered matched action-order interventions.
Gate: hold initial observed state and total action counts comparable; distinguish association from causal isolation.

## J — Observable-state sufficiency
Question: Can identical visible frames yield different next responses?
Input: C histories and native frame stacks.
Output: matched visible-state pairs with divergent continuation, or a documented failure to find any.
Gate: verify exact frame equality and source actions; no claims about hidden state absent discrimination.

## K — Policy comparisons
Question: Which action-selection policy reliably changes progress rather than merely frame counts?
Input: source-verified action affordances and native observations.
Output: deterministic baseline versus alternative policy under equal budgets.
Gate: native levels/status, actions, resets, and failures reported for each policy.

## L — Level-boundary interventions
Question: What observed conditions distinguish stage transitions, especially level four?
Input: D stage-four controls and genuine native checkpoints.
Output: bounded intervention matrix around documented transitions.
Gate: report all NOT_FINISHED outcomes and zero-WIN evidence without inferring hidden target semantics.

## M — Reset variability
Question: How stable are observations across independent native resets?
Input: original SDK reset batches across A–D.
Output: per-reset outcome distribution, source state fingerprints, reproducibility intervals.
Gate: do not pool incompatible starting states.

## N — Held-out generalization
Question: Do frozen hypotheses predict unseen action histories?
Input: models frozen from A–M and held-out native trajectories.
Output: exact prediction coverage, false positives/negatives, error categories.
Gate: prevent train/holdout leakage; report failed predictions.

## O — Independent verification
Question: Can a separate implementation reconstruct claimed results from source artifacts?
Input: immutable JSON/NPZ, source SHA, native action transcripts.
Output: independently computed checksums, transition comparisons and discrepancy report.
Gate: do not reuse the same analysis function as the claimed result.

## P — Cross-lane integration
Question: Which claims survive independent tests and which conflict?
Input: A–O evidence receipts and counterexamples.
Output: source-pinned claim/evidence/contradiction matrix and prioritized next tests.
Gate: no synthetic aggregate 'success' metric; unresolved conflicts remain visible.

## Execution policy
G may begin with available artifacts. H–O may proceed independently as source evidence permits; P updates only on new evidence. Native execution requires a separate reviewed workflow or existing worker dispatch with explicit budget and cooldown. Do not auto-dispatch from this registry.

## ARC-native CP entry / output boundary (bounded source-owner test)

The original finite-correspondence CP20–CP30 history is not transferable as
ARC task authority. For the **existing** SP80 stage3 and Window48 smoke
workflows, `work/arc3/cp_gate.py` now checks an explicit A/entry receipt
before SDK execution and a B/output receipt after the native source report.
The entry binds a named lane to current checkout source-file digests,
`AGENTS.md`/this lane register, preserved prior observations, and an exact
output destination. Output refuses a changed source, missing raw-frame archive,
incomplete 16×2 controls, cross-lane substitution, or a promoted win unsupported
by the original SDK report. Negative trials and walls survive as observations.

**Boundary:** These are source-integrity and report-accounting checks, not an
independent original SDK replay, a proof of ARC completion, or universal
worker admission. CI must execute the entry step to enforce the gate.
Tests: `python -m unittest -v network.tests.test_arc3_cp_gate`.
