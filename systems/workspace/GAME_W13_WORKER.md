# GAME W13 — bounded native multi-world builder candidate

**Current referent:** one existing Complete Stack workstation, one game CP lane. This is a **bounded native GAME BUILD helper**, not a general model-backed agent capable of automatically writing a complete game. The original W12 world, strict verifier, expanded receipt boundary, and earlier W1–W12 reports remain preserved.

## W12 source and preservation

The original `W12_receipt_compatibility_candidate.zip` from October 14 is pinned to SHA-256 `ec6b8b6e7371f7e3e30343af72fa090097e253768205a3aa93f5a064e7905582` (candidate's reported W12 WITNESS PASS remains historical). Its `systems/workspace/game_construction.py` is installed **byte-identically** as `game_w12_reference.py`, and a second byte-identical source resides in `game_w13_worker_source/` for the isolated workstation edition. Both must match SHA-256 `dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1` or this worker rejects execution.

## New worker capability

`game_w13_worker_source/w13_engine.py` implements a two-to-four-world game session over the **unchanged** W12 movement/interact rules. A declared `advance` action switches worlds **only after** the current world is solved. A session does not complete until its final world is also solved. Invalid transition, extra fields, invalid coordinates, identical/duplicate worlds, missing actions and unknown verbs are rejected.

`GameW13Bridge` uses the existing `ProcessWorkstation.copy_source`, `HandoffRuntime`, `RuntimeJournal`, `controls.run_job`, `controls.reverify_job`, `CoordinatorIndex` and `cp_motion` as is. Source copying, admission, execution, and native verification remain distinct; the isolated child source runs in a subprocess. The host verifier does not import the *new* W13 engine from the worker edition—it rebuilds expected world traces by reusing byte-pinned original W12 `run_actions` and `verify_trace`, and checks strict result equivalence, job metadata and edition fingerprint.

**Proof boundary:** A successful job is `COMPLETE` **for this multi-world build candidate only**. It intentionally returns `checkpoint_verdict=CANDIDATE` for `GAME-W13-WORLDS`, not `PASS`. This means the one-window CP planner MUST leave `GAME-W13-WORLDS` unwitnessed. WORLD W13's **proposed** contract also calls for an explicit versioned browser experience, receipt round-trips and independent WITNESS negative tests, none of which this worker claims to have completed.

## Trusted checkout commands

```bash
python -m unittest -v network.tests.test_game_w13_worker
python -m systems.workspace.cp_motion --data-dir runtime/data admit-research
python -m systems.workspace.game_w13_cli --data-dir runtime/data copy --version w13-v1 --confirm-copy
python -m systems.workspace.game_w13_cli --data-dir runtime/data prepare --version w13-v1 --inputs-file network/tests/fixtures/game_w13_example.json
python -m systems.workspace.game_w13_cli --data-dir runtime/data admit --version w13-v1 --inputs-file network/tests/fixtures/game_w13_example.json --job-id game-w13-001 --confirm-admit game-w13-001 --from-actor local-review
python -m systems.workspace.coordinator_window --data-dir runtime/data bind-job --lane game --slot cp-game-w13-worlds --job-id game-w13-001 --worker-id game-w13-world-builder --version w13-v1
python -m systems.workspace.coordinator_window --data-dir runtime/data run-linked --lane game --slot cp-game-w13-worlds --confirm-execute game-w13-001
python -m systems.workspace.cp_motion --data-dir runtime/data handoff --markdown --reverify
```

Tests execute on ephemeral CI-owned workstations, not Dessy's PC. Repository publication cannot silently transfer private source editions or journal state from her workstation. No AI model credential, autonomous coding-loop runner or browser-native witness is registered here.

## Next SINGLE movement

Admit WORLD W13's first exact versioned browser-world contract, implement matching playable browser world changes, then independently compare real browser observations to native W12/W13 semantics under WITNESS. Only a newly verified source-pinned `PASS` with exact W13 CP contract may advance GAME W13. A later dedicated GAME BUILD agent must separately demonstrate model-backed code generation, safe branch editing, tested patch return, and retry/termination policy before it can autonomously finish the engine.