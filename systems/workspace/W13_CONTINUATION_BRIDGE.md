# W13 native evidence into workstation continuation

This adapter uses the existing source-owned `GAME-W13-WORLDS` CP as an
observation provider. It does not add a game runtime or replace the native
checkpoint verifier.

## Acceptance rule

A `BRANCH` observation is accepted only when its witness reference names an
existing W13 native job, the job is `COMPLETE`, the job metadata identifies the
source-owned W13 CP, its original provenance binds the exact workstation lane,
and `GameW13NativeBridge.reverify(job_id)` succeeds against the pinned copied
worker and original W12 replay. A READY job is not evidence.

The continuation harness may then create a READY coordination lane. That is
not a worker process, execution result, or checkpoint PASS. The adapter rejects
cross-lane connection claims: two runs of this same finite W13 CP are not by
themselves a join witness.

## Integration boundary

The verifier is a callback provider, not a global registration or automatic
hook. A caller must instantiate `GameW13ContinuationVerifier(data_dir)` and
pass its `verify_observation` and `verify_connection` methods to
`WorkstationContinuationHarness`. Merely setting a worker-edition label allows
a coordination proposal; it does not register or execute a worker.

The observed capability is the generic `game-engine-build`. The existing
helper router deliberately leaves that capability unregistered, so explicit
native-help intake remains `OPEN_UNSTAFFED` unless a separately source-owned
adapter is implemented. Do not silently alias it to the registered
`game-w13-native-two-room` helper: that helper is narrower and requires an
exact trusted parent edition and bounded native input. A W13 continuation
observation is therefore evidence for a coordination proposal, not permission
to launch a generic game-building worker.

## Focused regression

```sh
python -m unittest -v network.tests.test_game_w13_continuation_bridge
python -m unittest -v network.tests.test_game_w13_native_cp_worker
python -m unittest discover -s network/tests -p "test_*.py"
```

Tests use temporary local data directories and the existing bounded native W13
worker. They do not authorize or launch a private production job, and they do
not establish a universal or cross-domain relation.
