# Original W13 native verifier — explicit source-owner execution boundary

The real W13 owner result was independently reverified in [run 39095851290](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39095851290). The read-only next-checkpoint preflight passed in [run 39099802771](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39099802771): the parent is WITNESSED and `GAME-NATIVE-VERIFIER` remains ADMISSIBLE but **not admitted**.

This capability uses the **existing** `NativeGameVerifierBridge`, `ProcessWorkstation`, `RuntimeJournal`, `CoordinatorIndex`, and `controls.run_job`. It does not invent bots or create a new scheduler.

The new workflow `w13-owner-native-verifier-one-shot.yml` cannot consume or run a child from its own PR. A source owner must deliberately **add one NEW JSON request** at:

`systems/workspace/native_job_requests/w13/game-native-verifier-github-001.json`

That request must exactly equal the Python `EXPECTED_REQUEST` in `systems/workspace/w13_owner_verifier_execution.py`. It names the original GitHub run, artifact ID and digest, original W13 RESULT event and source fingerprint, independent verifier source/bridge Git blobs, one exact `game-native-verifier-github-001` job, the fixed `witness-owner-v1` edition, and **explicit separate permission** to copy, admit and execute one bounded native child. There is no request committed in this PR.

**Activation:** only an owner-authored protected-main **two-parent merge introducing that exact new request** triggers the trusted child workflow. The workflow authenticates the merged source and owner *before* downloading the existing archived original journal. It independently validates the original GitHub run and digest, restores the private journal to a temporary runner, freshly re-verifies its exact research-source link and CP frontier, then uses the existing Workstation to copy the separate child edition, admit the exact job, bind it to the original planned slot, execute once via `controls.run_job`, and independently reverify source and event chain.

A real successful run would report `GAME-NATIVE-VERIFIER=WITNESSED` and `GAME-WORKER-READY=ADMISSIBLE`, but no future checkpoint is executed. It outputs only a redacted JSON result in job logs and uploads **no raw journal**. The ephemeral journal expires on runner teardown; downstream cross-run persistence is a separate unanswered boundary.

If the original artifact expires, the original RESULT is forged, the worker bytes drift, any authorization differs or the exact parent changes, the workflow refuses execution. Local PR tests demonstrate source pins and negative controls; they do **not** execute the genuine historical native child. No external game achievement or scientific causality is asserted.

Reproduce the nonexecuting contract tests: `python -m unittest -v network.tests.test_w13_owner_verifier_execution`.
