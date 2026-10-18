# Phase 1 — two independently moving clocks in the original W13 game

**Status: bounded native game-world research experiment, not an NIH submission.**

## Question and source boundary

The first [witnessed game frontier](nih_phase1_world_frontier.py) already establishes the original native twelve-job game, emitted `temporal_query.py`, real Chromium turns, and the transition when a delayed fictional result becomes knowable. However, that original game demonstration holds its **validity target fixed** and moves only the **knowledge** cutoff.

This new experiment asks whether **both temporal dimensions can be varied independently while preserving source ownership**. It inherits the *already independently witnessed* original game-world execution, never replaces the twelve original native workers, then attaches a second inspection panel within an isolated copy of the same game. The user can click three explicitly synthetic validity target dates, while the original game advances the knowledge time:

- **January 2, 2026:** before the fictional delayed result's stated valid interval, so its target-validity test excludes that result regardless of whether it was later known.
- **January 4, 2026:** both facts are within their validity intervals, but the delayed one must remain withheld before it becomes knowable on January 5.
- **January 11, 2026:** after both half-open validity intervals have ended; both facts are outside validity for that target.

Each choice is an **actual browser button interaction** which invokes the **unchanged original emitted Python executable**, through Playwright's isolated host binding. The original game still uses the original `/api/query` HTTP bridge, its own generated room and its original Chromium interaction history. The added target picker uses a distinct Playwright instrumentation binding only for this bounded research experiment; the archived HTML is not represented as a self-deployed service. It requires the host runner for continued interaction.

## Independent evidence

For each actual game turn and each of the three clicked target choices:

1. The original emitted `temporal_query.py` is executed in a bounded independent child process on the original source-owned dataset; the exact returned JSON is recorded with source program SHA-256.
2. A **separate host oracle** reads the original Phase 1 scope handoff and independently recomputes the eligible facts, withheld future facts, and outside-validity facts. A mismatch rejects the run.
3. Chromium's actual selected panel is inspected. Its visible, withheld and static evidence sets must exactly match the independent oracle for the selected `(K,V)` pair.
4. The evaluator reconstructs every turn-target pair; it refuses missing frames, duplicate IDs, source digest drift, non-partitioned source evidence, mixed knowledge times on one turn, inverted knowledge monotonicity, or impossible expiry behavior.
5. The original twelve-job `runtime.jsonl`, coordinator index and **pre-existing native browser query evidence log** must remain byte-for-byte unchanged. All new evidence is in a separate report, screenshot and source receipts.

This tests the small deterministic two-clock rule on a fictional fixed dataset, not novelty against every existing temporal KG method.

## Important negative claims

- **No change to the original emitted prototype.** The original generated Python and original W13 room remain the independent computation source. A Playwright binding is an instrumentation channel, not an AI assistant or thirteenth source-owned workstation worker.
- **No new native CP or fake progress:** twelve original native jobs remain, with the pre-existing Phase 1 packet and Phase 2 benchmark still part of their original evidence ancestry.
- **Not an actual historical source trial.** Nothing authenticates original public ClinicalTrials.gov record-version content or the date an actual version first became public; see [issue #106](https://github.com/huntingthereferent/autobots-assemble/issues/106).
- **No production unknown-date algorithm or embedding:** the proposed three-way publication uncertainty and temporal-embedding gates in [draft #125](https://github.com/huntingthereferent/autobots-assemble/pull/125) remain proposed and unimplemented.
- **No clinical result and no official NIH submission.**

## Reproduction

```sh
python -m pip install 'cryptography>=45,<47' 'rdflib>=7,<8' 'playwright>=1.54,<2'
python -m playwright install chromium
python -m unittest -v network.tests.test_nih_phase1_world_two_clock
python -m systems.workspace.nih_phase1_world_two_clock \
  --data-dir /tmp/original-nih-native --output-dir /tmp/nih-two-clock-receipts
```

The standalone unit negatives only test failure boundaries. The source-connected assertion requires **successful actual Chromium execution** of the original twelve-job parent, this new two-axis world, and independent oracle reconstruction. The dedicated GitHub Actions workflow checks all those requirements before the experiment is admitted as evidence.
