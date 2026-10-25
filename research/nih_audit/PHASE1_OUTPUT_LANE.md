# NIH Phase 1 — output selection execution lane

**Lane:** NIH-P1-OUTPUT-COMPARE-2026-10-25
**Original referent:** compare completed NIH Phase 1 output versions on the same original W13/NIH native baseline, and identify the best *verified* output for the specified domain.
**State:** DISPATCH REQUESTED; do not mark RUNNING without a GitHub run ID.
**Execution entry:** `.github/workflows/nih-phase1-output-comparison.yml`
**Comparator:** `systems/workspace/nih_phase1_output_compare.py`

## Bounded children

| Child | Candidate | Output |
|---|---|---|
| NIH-P1-01 | Original-world frontier | `frontier/nih-phase1-original-world-frontier.json` |
| NIH-P1-02 | Independent two-clock | `two_clock/nih-phase1-two-clock-world-report.json` |
| NIH-P1-03 | Synthetic source motion | `source_motion/nih-phase1-world-source-motion.json` |
| NIH-P1-04 | Publication uncertainty | `publication_uncertainty/nih-phase1-world-publication-uncertainty.json` |
| NIH-P1-05 | A/B comparison | `comparison.json` and per-candidate logs |
| NIH-P1-06 | Source verification and selection | exact Actions run ID, commit, artifacts, shared-case evidence, limitations and best-version decision |

The original twelve-job source-owned Phase 1 execution remains the baseline and is not replaced by these follow-on experiments. No new NIH CP or official submission is implied.

## Acceptance

1. The four native candidates execute from a known checkout SHA and preserve receipts, including failures.
2. The same shared synthetic source, knowledge/validity boundaries and original program are compared wherever outputs overlap.
3. Missing or failed receipts remain UNKNOWN/FAIL, never a win. Separate feature coverage from correctness on common cases.
4. A winning version requires source-backed replay, common-case agreement, and an explicit selection rule. If the candidates are incomparable, retain a Pareto set and next discriminating test.
5. Only after independent GitHub run verification and evidence-backed selection may this lane close. The initial audit referent must not be replaced by the latest commit.

## Starting this lane

The workflow has a `push` trigger scoped to changes to its own YAML. Updating the workflow starts a **request for execution** on GitHub Actions, subject to repository Actions settings. A commit is not itself a runner receipt. Check the Actions run and its artifacts before reporting RUNNING or PASS.
