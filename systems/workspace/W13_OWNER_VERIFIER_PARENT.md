# Exact owner W13 parent for the existing GAME-NATIVE-VERIFIER

The [original W13 native result](../../research/dives/W13-NATIVE-RECEIPT-001/dive.json) was independently reverified against its exact owner-run archive in [GitHub Actions 39095851290](https://github.com/huntingthereferent/autobots-assemble/actions/runs/39095851290).

The **existing** native GAME-NATIVE-VERIFIER was originally tied only to `game-w13-cp-joined-001`, the parent of an independent synthetic nine-job Complete Stack. That receipt **cannot** be substituted for the owner job `game-w13-github-001`.

The existing `game_native_verifier_bridge.py` now recognizes two **distinct, exact** source-owned W13 parent identities. The owner source may request a witness only with:

- Parent job: `game-w13-github-001`
- Worker: `game-native-independent-verifier`
- Owner-only edition: `witness-owner-v1`
- Owner-only child job: `game-native-verifier-github-001`
- Required checkpoint: `GAME-NATIVE-VERIFIER`

The same separately copied bounded W13 witness algorithm tests exact two-room states and negative early advance; the host separately checks the original W12 oracle. A wrong parent, incomplete or changed parent, wrong edition/job pairing, source tamper, or missing execution confirmation **fails closed**. Legacy `game-w13-cp-joined-001` and `witness-v1` still use their previous admission identity; no existing journal is rewritten.

This prepares the genuine owner-source *admission contract* but deliberately **does not** admit or execute that child job in the owner-protected original W13 archive. The actual descendant requires a separately authenticated and explicitly authorized owner request to restore the real original journal, pin and copy the witness worker source, admit the exact child, and execute and independently reverify it. Only then may the coordinator consider the native `GAME-NATIVE-VERIFIER` checkpoint witnessed. The current original W13 result alone does not staff it.

The focused tests reproduce the two-job workflow in a fresh temporary native Workstation, including actual subprocess execution, source-native independent re-verification and negative failures. This is a finite synthetic fixture experiment **not a claim of original archived owner-child execution**.

Reproduce: `python -m unittest -v network.tests.test_w13_owner_verifier_parent network.tests.test_game_native_verifier_temporal_join`.
