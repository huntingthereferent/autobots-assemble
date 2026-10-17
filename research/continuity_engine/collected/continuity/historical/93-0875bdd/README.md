# Continuity Engine · research-board integration package

**Status:** Local additive prototype of the previously tested board integration; this A/B extension has **not** been executed against the repository’s exact modules in this turn and is **not committed or merged**.

This adds separate full labeled A/B action correspondence witnesses alongside the existing B-only Continuity Engine and keeps the read-only, immutable-checkpoint research question board contract unchanged.

## Package files

- `research/simultaneous_action_correspondence.py`: full transitive A/B Schreier collision basis, correspondence witness, and native replay.
- `research/continuity_engine.py`: B-only continuation plus separately scoped full A/B adapter. Stores SHA-256-linked replayable checkpoints and question identity. External anchor is recommended; hashes do not provide cryptographic authorship/authentication.
- `research/continuity_board_bridge.py`: stages a separate copy of the board with a new candidate checkpoint, preserving original freezes and refusing publication without an explicit witness locator.
- `research/CONTINUITY_ENGINE.md`: mathematical scope of the prototype.
- `research/CONTINUITY_BOARD_BRIDGE.md`: staging and status semantics, including use of `load_research_board`.
- `network/tests/test_research_full_action_correspondence.py`: 10 new A/B positive, negative, tamper, resource, and board tests.
- `network/tests/test_research_continuity_engine.py`: existing B-only continuity and replay tests with expected supported-area listing updated.
- `network/tests/test_research_continuity_board_bridge.py`: staging, publication-scope, identity, and immutable-board regression tests.

## Tested

Executed against native repo modules in a disposable Windows Git worktree, without changing the active checkout:

```bash
python -m unittest \
    network.tests.test_research_continuity_engine \
    network.tests.test_research_continuity_board_bridge \
    network.tests.test_research_question_board \
    network.tests.test_arc_like_cyclic_action_engine \
    network.tests.test_arc_like_cyclic_action_continuation \
    network.tests.test_arc_like_engine_one -q
```

**Previous package:** 74 tests passed against actual repo `main` at `47c2d8e`. **New extension:** 10/10 focused tests passed using a local test harness reproducing the same WindowProcess step/inverse arithmetic; real-repository regression of the extension is still pending. No native ARC solving is claimed.

## Applying later

Review and place these files at the listed relative paths in the repository. Do **not** overwrite original `research/questions` freeze files. Stage evidence to an external directory for human review; the existing public board still points at its registered immutable checkpoints unless someone explicitly publishes a new one.

External packages such as GAP/ORB, SageMath, nauty, NetworkX and CADP/mCRL2 are *references*, not newly integrated dependencies. Swallowing their techniques remains separate work requiring correct mathematical witness contracts, independent comparison tests, and licensing review for source reuse.

## New full-action reproducer

```python
from research.continuity_engine import ContinuityEngine
engine = ContinuityEngine()
first = engine.start_full_action(source, target, dimension=5, max_loops=0)
assert first.status == "UNKNOWN_COLLISION_BUDGET"
continued = engine.resume(first.serialize(), 244,
                          expected_question_id=first.question_id)
assert continued.status in {"CONJUGATE_FULL_AB", "DISTINGUISHED_FULL_AB"}
```

Run from the repository root with this package overlaid (do not overlay any
`research/questions` data):

```bash
python -m unittest network.tests.test_research_full_action_correspondence \
  network.tests.test_research_continuity_engine \
  network.tests.test_research_continuity_board_bridge \
  network.tests.test_research_question_board \
  network.tests.test_arc_like_cyclic_action_engine \
  network.tests.test_arc_like_cyclic_action_continuation \
  network.tests.test_arc_like_engine_one -v
```

The source-board freeze is never in the delivery package. No GitHub changes.