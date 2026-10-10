# Continuity Engine · research-board integration package

**Status:** Tested in a disposable worktree against repository `huntingthereferent/language-network` (current `main` checked out at `47c2d8e` during integration test); **not committed or merged**.

This is an additive integration of the Continuity Engine prototype with the current read-only, immutable-checkpoint research question board.

## Package files

- `research/continuity_engine.py`: existing Cyclic Action continuation adapter. Stores SHA-256-linked replayable checkpoints and question identity. External anchor is recommended; hashes do not provide cryptographic authorship/authentication.
- `research/continuity_board_bridge.py`: stages a separate copy of the board with a new candidate checkpoint, preserving original freezes and refusing publication without an explicit witness locator.
- `research/CONTINUITY_ENGINE.md`: mathematical scope of the prototype.
- `research/CONTINUITY_BOARD_BRIDGE.md`: staging and status semantics, including use of `load_research_board`.
- `network/tests/test_research_continuity_engine.py`: continuity and replay regression tests.
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

**74 tests passed.** Current mathematical scope is `cyclic_action/B`; full simultaneous A/B equivalence and native ARC solving are not claimed.

## Applying later

Review and place these files at the listed relative paths in the repository. Do **not** overwrite original `research/questions` freeze files. Stage evidence to an external directory for human review; the existing public board still points at its registered immutable checkpoints unless someone explicitly publishes a new one.

External packages such as GAP/ORB, SageMath, nauty, NetworkX and CADP/mCRL2 are *references*, not newly integrated dependencies. Swallowing their techniques remains separate work requiring correct mathematical witness contracts, independent comparison tests, and licensing review for source reuse.