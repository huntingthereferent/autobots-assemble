# NIH Phase 1 — source motion within the original twelve-job W13 world

**Bounded synthetic research.** This is a new independently observed world experiment, not a new native workstation job, an additional NIH checkpoint, a patient trial, or an NIH submission.

## Referent

The first real [world frontier](nih_phase1_world_frontier.py) proved that original game turns drive the original Python executable. The second [two-clock world](nih_phase1_world_two_clock.py) proved independent `known_at` and `target_at` selection. Both used a fixed synthetic source.

This continuation varies **source observations**, still through the same original W13 playable game and the same original emitted `temporal_query.py`. It reuses three exact scenarios from the [previous source-variation work](nih_dataset_sensitivity.py), rather than implementing duplicate source logic or inventing a new worker:

- `original`: the original Phase 1 synthetic observations and knowledge cutoff.
- `later-knowledge`: the fictional delayed result's source `known_at` is moved **three days later**. When the game's original cutoff moves from January 4 to January 6, the result remains withheld in this counterfactual source even though the baseline already reveals it.
- `additional-conflict`: a separately attributed fictional `has-status` observation is added with a different object. Because this predicate is **explicitly declared functional in the original bounded fixture**, the original program and independent oracle must expose the conflict, not quietly pick a preferred status.

The new panel is a **synthetic what-if source selector**, never a representation of original archived ClinicalTrials.gov versions. Changing a source dataset is **not** equivalent to merely advancing knowledge time. The original game and its earlier research panels continue using their unmodified native source.

## Verification path

The runner:

1. Executes the **already merged original twelve-job W13/NIH stack**, original Phase 1 frontier, and verified independent two-clock experiment. It refuses incomplete ancestry.
2. Preserves original native `runtime.jsonl`, coordinator index and prior Chromium query log byte-for-byte. It creates a **new temporary source-variation test directory**; no source-worker folder or admitted native job is changed.
3. Builds three **attributed synthetic counterfactual datasets** from the original native Phase 1 scope with the already existing source-variation generator. Each receives its own SHA-256 fingerprint. All versions execute the original **unchanged generated `temporal_query.py`**.
4. Uses an **actual Chromium game session** to click all three source-profile buttons at every original game turn (the game still advances the original knowledge clock). The new panel uses an isolated Playwright binding for bounded host invocations of the original executable.
5. For each actual source-profile/turn observation, the independent host oracle recomputes the answer directly from that synthetic source profile's original-scope-derived observations. All visible, withheld, static, outside-validity and explicitly declared conflicts must match both original program output and browser-rendered data.
6. Rejects missing source-profile clicks, false original cutover, incorrectly revealed later-published data, missing explicit conflicts, changed source SHA, reduced evidence partitions, regressive knowledge time, and damaged original journals.

Evidence is recorded as exact emitted program/source SHA-256s, actual original Python subprocess calls, browser observation frames, native lineage, and a **real game screenshot**. The resulting HTML requires the local game HTTP bridge and host-bound instrumentation to remain live; it is not represented as an independent hosted production service.

## Boundaries

Only **constructed synthetic source movements** are tested. The claims do **not** establish original historical study version bytes, their first-public-posting timestamps, medical efficacy, semantic OWL entailment, a production temporal embedding, an NIH award/submission, or a thirteenth native worker. The original source gap remains [issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106); the separate 9-page [Phase 1 proposal draft #125](https://github.com/huntingthereferent/autobots-assemble/pull/125) remains subject to human scientific and intellectual-property review.

A CI green result on this experiment is evidence for the **limited source-motion computation**—not the missing real-world historical-data claim.

## Replay

```sh
python -m pip install 'cryptography>=45,<47' 'rdflib>=7,<8' 'playwright>=1.54,<2'
python -m playwright install --with-deps chromium
python -m unittest -v network.tests.test_nih_phase1_world_source_motion
python -m systems.workspace.nih_phase1_world_source_motion \
  --data-dir /tmp/nih-source-motion-native \
  --output-dir /tmp/nih-source-motion-evidence
```
