# Phase 1 — uncertain source publication inside the original W13 world

This experiment follows the merged original twelve-job played-world experiments: source/known-time frontier (#130), independent validity/knowledge clocks (#132), and synthetic source changes/conflict (#135). The original **twelve native jobs, their runtime journal and their emitted Python program are unchanged**. This is a separate browser-replayed observation, not a new native worker or an NIH checkpoint.

## What is tested

A source-derived fact may be valid on January 4 even though its actual public posting time is not established. The existing generated native Python executable uses an **exact** `known_at` value. It cannot, by itself, tell the difference between **verified later publication** and **unresolved publication time**.

This experiment creates an explicitly fictional alternative provenance scenario for the original `delayed-result` record: its publication time is only known, in the constructed test, to fall between **January 4 and January 7, 2026**. This interval **is not real externally authenticated historical evidence**, and it does not override the original native fixture's synthetic `known_at=2026-01-05`. It models what happens if that exact timestamp is deliberately unavailable to a retrospective reviewer. The baseline `prior-note` remains available on January 1.

The browser can click four separate knowledge-cutoff controls while the original game independently advances through its real turns:

| Query cutoff | Delayed fictional result status, target date Jan 4 |
| --- | --- |
| January 3 | Definitely not yet available |
| January 4 | **Indeterminate** |
| January 6 | **Indeterminate** |
| January 7 | Definitely available by cutoff |

## Program and provenance distinction

The original source-owned program `temporal_query.py` is executed **unchanged**, in a bounded subprocess, against a separate **conservative synthetic dataset** where `delayed-result.known_at` is set to the upper-bound date (January 7). This yields a conservative *eligible* set: no fact with unverified availability is admitted before its upper bound.

Its raw `future_leakage_ids` means **not admitted under the conservative upper-bound coding**. That raw output **cannot be renamed “definitely withheld”**: before January 4 the source is definitely withheld, but between January 4 and 7 availability is uncertain. The separate, clearly attributed **source-policy observation layer** derives and labels those states, retaining all original source IDs.

The host separately checks every original subprocess result against the pre-existing Phase 1 native scope oracle, then checks the three-way bounds against the pinned declared hypothetical source interval. Every actual Chromium button click records the game turn, independent query cutoff, valid target, source-program and dataset SHA-256, and the exact result partitions. Synthetic mutations in independent tests reject collapsing indeterminate evidence into either a definite admission or a definite absence.

The original game and its earlier source panels continue operating on the **original native dataset**, not the conservative hypothetical one. Existing `runtime.jsonl`, coordinator ledger, and original browser query history must remain byte-identical. There is **no thirteenth native worker**.

## Evidence and limitations

A passing browser replay witnesses that the original world was played, its emitted Python was executed for every cutoff, and the additional provenance boundary did not make unsupported positive or negative claims within the constructed interval. It does **not** prove full unknown-time support in the native Python program, full OWL reasoning, authentic ClinicalTrials.gov historical-version first-publication dates, clinical accuracy, a new NIH checkpoint, or an official NIH application.

The [Phase 1 draft PR #125](https://github.com/huntingthereferent/autobots-assemble/pull/125) remains under owner review. The missing original historical-source evidence is still tracked separately in [issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106).

## Reproduction

```sh
python -m pip install 'cryptography>=45,<47' 'rdflib>=7,<8' 'playwright>=1.54,<2'
python -m playwright install --with-deps chromium
python -m unittest -v network.tests.test_nih_phase1_world_publication_uncertainty
python -m systems.workspace.nih_phase1_world_publication_uncertainty \
  --data-dir /tmp/nih-original-native --output-dir /tmp/nih-uncertain-publication-evidence
```

The first run tests falsification on bounded fixtures. Only the dedicated actual Chromium workflow can independently witness the live original game and generated-program execution.
