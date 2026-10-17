# W13 continuation across GitHub-hosted runner shutdowns

The game W13 source-owned native worker was **already executed and independently verified** in [Actions run 39025574748](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39025574748), artifact **12098716155**, SHA-256 **543c08f9f9f5cb1eee47b0ab21535e759495c6e7318dc5e06f3519f27f4dfcfa**. The W12 verifier, W13 multi-world replay, game adapter and CI evidence already exist. **Do not rebuild them.**

## New boundary: carry the actual journal to another runner

`.github/workflows/workstation-w13-cross-run-continuation.yml` starts from one explicit owner-merged bootstrap request (and listens to future successful `workflow_run` events from the same owner-merged W13 source workflow). It checks the GitHub source run's identity, event, branch, actor, conclusion, exact artifact and digest **before downloading**. The original witnessed run is individually pinned to its SHA, archive ID and digest; future source jobs must meet the same source-owned provenance rules.

The runner downloads the historical W13 evidence archive using `actions/download-artifact@v4` with GitHub's internal artifact digest validation. `github_w13_continuation.py` then checks the original authorization JSON, source and fixture Git blobs, job execution and verifier receipts, journal archive SHA-256, and a safe bounded tar extraction. It uses the **original** `RuntimeJournal`, copied `ProcessWorkstation` edition, `CoordinatorIndex`, `controls.reverify_job` and `cp_motion` to independently reverify native W13 in a *new Python process on a new GitHub machine*.

Only when native W13 is again `WITNESSED` and `GAME-NATIVE-VERIFIER` is `ADMISSIBLE` does it call the **existing** `branch_help.open_help` to append a bounded help opening at the next CP slot. This opening has capability `game-native-archive-consumer` and remains `OPEN_UNSTAFFED` until there is a separately source-owned admitted native job. It is not a duplicate W13 verifier, invented worker, proof of `GAME-NATIVE-VERIFIER`, or automatic arbitrary process execution.

The run archives `source-binding.json`, `continuation.json`, and `continued-runtime.tar.gz` containing the inherited W13 workstation journals **plus** the new help opening. This verifies state preservation across separate runners and a real evidence-driven branch. A future worker can consume that archived state only after re-authenticating its provenance and independently verifying it. Artifacts have a 30-day retention limit; the archive is not a permanent database or always-running agent.

## Safety and negative evidence

- An expired, mismatched, incomplete, forged or unsafe source archive fails closed.
- The next CP never advances from previous CI green status alone or from an unverified parent journal.
- Only an exact protected-main owner bootstrap or an actual successful owner W13 source workflow can trigger; no PR content runs on the trusted evidence consumer.
- The continuation consumes an existing proof, **not** a new authorization to execute source-owned child code.
- No claim of multi-agent autonomous self-expansion is made: the genuine next step is to staff the exposed branch with a registered, separately witnessed source-owned worker, using the existing engine.

Run local regression tests with `python -m unittest -v network.tests.test_github_w13_continuation`. The workflow also tests against the actual pinned historical source on GitHub after the bootstrap merge.
