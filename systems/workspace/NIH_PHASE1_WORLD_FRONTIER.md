# Phase 1 temporal-evidence frontier in the original playable world

**Status: native-world experiment; no new CP, no NIH submission, synthetic data only.**

## What moves in the world

This experiment is an *addition to the existing original* [12-job browser-backed W13/NIH complete stack](nih_benchmark_temporal_join.py). It does **not** replace any game-worker source, prototype source, Phase 1 packet, or original recorded native job. It first executes and independently re-verifies the actual twelve-job parent in its workstation RuntimeJournal. Then it launches **a new Chromium session in an isolated temporary directory** serving the original game HTML, original generated `temporal_query.py`, original dataset and original local Python HTTP bridge. The only new presentation code is a read-only `phase1-frontier` panel injected into the copied playable HTML.

Every real button action in the native game moves time through the **existing original** source cutover configuration. The original temporal view and the new panel independently request the same real Python endpoint. The panel displays:
- `T(K,V)`: observations valid at V and known by K;
- `S(V)`: valid-at-V static-union observations, ignoring known time;
- `L(K,V)`: valid records that the static union would leak before K.

The host obtains original Phase 1 `NIH-P1-SCOPE` inputs from the pre-existing handoff, and independently calculates expected sets via the separate [prototype host oracle](nih_prototype_native.py). It checks the exact current game turn, source program SHA-256, knowledge and validity cutoffs, evidence IDs, the source partition, and every captured actual Python request. It also submits **nine additional knowledge/validity boundary queries** directly to the **unchanged original** generated Python program. It verifies monotonicity of evidence availability **only for fixed source, fixed validity target, append-only observations, and increasing knowledge cutoffs**. This is not a theorem about corrections overwriting history or evidence with unknown first-publication times.

## Bounded claims

A live PASS means an interactive game actually moved, the original temporal executable was called on those movements, native Phase 1 inputs independently reproduced the answers, later-known synthetic evidence was withheld before the cutover and admitted after, and the original 12-job runtime journal and Chromium evidence log were byte-for-byte preserved.

A PASS does **not** establish:
- authentic public ClinicalTrials.gov historical-version contents or publication times (see [issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106));
- clinical accuracy, patient outcomes, real-world biomedical transfer, original OWL entailment, embeddings, or a general temporal-KG benchmark;
- official NIH Phase 1 application/submission/award or Phase 2 eligibility;
- the proposed three-way indeterminate publication-time extension in [Phase 1 draft PR #125](https://github.com/huntingthereferent/autobots-assemble/pull/125); that proposal remains separate and **unimplemented in this original executable**;
- a newly witnessed source-owned checkpoint or a thirteenth worker.

The playable HTML file in the artifact requires the original *loopback Python bridge* and generated source dataset to provide live results. It is not represented as an independently deployed website or auto-running hosted workstation. The artifact includes the actual Chromium screenshot, original browser evidence, bounded additional queries, and the initial twelve source-owned job receipts. It is a real new observation layer **inside the world**, not a paper-only phase report.

## Reproduce

```sh
python -m pip install 'cryptography>=45,<47' 'rdflib>=7,<8' 'playwright>=1.54,<2'
python -m playwright install chromium

python -m unittest -v network.tests.test_nih_phase1_world_frontier
python -m systems.workspace.nih_phase1_world_frontier \
  --data-dir /tmp/nih-phase1-original-world-native \
  --output-dir /tmp/nih-phase1-original-world-receipts
```

The first command is an offline set of deliberate negative-control cases; those are **not** live evidence. The second executes real Chromium, original W13/NIH parent and emitted source; its dedicated GitHub CI must finish successfully before describing the new world experiment as verified. All original source directories remain unchanged.
