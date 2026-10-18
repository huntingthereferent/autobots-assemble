# Original owner-authorized native W13 evidence

The original [GitHub W13 owner run](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39025574748) executed and independently reverified a real finite job. Its artifact 12098716155 is pinned to SHA-256 543c08f9f9f5cb1eee47b0ab21535e759495c6e7318dc5e06f3519f27f4dfcfa. The downloaded ZIP was verified against this digest and its nested native runtime journal contains exact CREATED, STARTED and RESULT COMPLETE events for game-w13-github-001.

The [structured W13 original record](../../research/dives/W13-NATIVE-RECEIPT-001/dive.json) retains only the source identity, job/result event identity, and pinned worker edition fingerprint. No private journal or raw output is copied into this record.

The existing original-source validator, bounded safe extractor, native re-verifier, and exact Git-source-to-RESULT join are composed in systems.workspace.w13_original_research_witness. It restores the archived native source only in a temporary runtime and rechecks its original RESULT, without admitting or executing another job.

The protected-main workflow original-w13-native-research-source runs only when an owner merge newly adds this record. It authenticates the source run and exact artifact digest using GitHub data before downloading. The private runtime exists only in the ephemeral runner and is not uploaded or published by this workflow. No original archive is downloaded in PR checks; the artifact's 30-day expiry is a genuine source wall.

The strongest supported claim is an exact native computation result and source-record identity. This does not prove scientific causality, general benchmark performance, or the downstream GAME-NATIVE-VERIFIER checkpoint.

Structural negative controls: python -m unittest -v network.tests.test_w13_original_research_witness.
The actual fresh native replay is performed by the owner-only on-main workflow after merge.
