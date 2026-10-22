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

## Focused regression

```sh
python -m unittest -v network.tests.test_game_w13_continuation_bridge
python -m unittest -v network.tests.test_game_w13_native_cp_worker
python -m unittest discover -s network/tests -p "test_*.py"
```

Tests use temporary local data directories and the existing bounded native W13
worker. They do not authorize or launch a private production job, and they do
not establish a universal or cross-domain relation.
