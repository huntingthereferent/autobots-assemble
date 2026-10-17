# Restored W12 playable game — exact archived source

**Scope:** source recovery and GitHub integration of the already-WITNESSed **W12 local candidate**. No new WORLD gameplay rule, no W13 certification, no browser-origin authentication.

## Recovery origin and evidence

On October 16, 2026, the original
`W12_receipt_compatibility_candidate.zip` was recovered **inside**
`game_nih_complete_stack_bridge_v1.zip`, at
`game_nih_complete_stack_bridge_v1/inputs/W12_receipt_compatibility_candidate.zip`.

- Recovered nested ZIP: **65,756 bytes**; SHA-256
  `ec6b8b6e7371f7e3e30343af72fa090097e253768205a3aa93f5a064e7905582`.
- This exactly matches the separately dated W12 WITNESS handoff and the
  Complete Stack bridge's pinned input manifest.
- Extracted ZIP was independently checked: **33/33 SHA256SUMS entries**
  matched and **32/32** original local W12 native Python tests passed.
- The extracted source and evidence were then committed under their **original
  relative paths**, without modifying gameplay, verifier, receipt schema, tests
  or browser HTML. The dedicated GitHub workflow rechecks their SHA-256 digests
  and reruns the original tests on GitHub's checked-out commit.

| Exact restored path | Original SHA-256 |
| --- | --- |
| `systems/workspace/game_construction.py` | `dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1` |
| `network/tests/test_game_construction.py` | `16fc2af47160b28b90cecc77e09a4e5c61766dee2b74e0aa4765c31bda186ce3` |
| `network/tests/test_game_receipt_compatibility.py` | `183f8ff5eb243cca260db10b206df36881e1fa69869791b4d5fa0a919c636da5` |
| `docs/game_preview.html` | `351aa430f23d5a08d3ec269288f19f2959cb372f81758660682aa5987e506eda` |
| `docs/first_trace.json` | `634b568ca85333c10ef86f4774b7b6cfbe4aa6565bcc775f4e841ddfdc93e5a1` |
| `evidence/export_success.json` | `925f94fcedf68c39b5ec10a39982e8a5638e8810f57a83d257e0734845121abb` |

The recovered ZIP also retains the separate C1, BUILD 1–2, WORLD and W12
WITNESS histories. The **ZIP itself is retained in the recovery source
library**, not committed in this change. A matched source hash is **not**
equivalent to re-checking every external artifact at a remote website.

## What is playable

Open `docs/game_preview.html` as a local HTML file in a browser. The W12
room is 4×3; the actor starts at (0,1) and the target at (2,1).
Arrow controls move, and `interact` collects only when adjacent.
A boundary-blocked movement still consumes one turn. Use the export
control to record expanded `before`/`spec`/`final` receipt evidence.
Use the CLI to check the saved receipt against the original strict W12
native replay.

```sh
python -m unittest -v network.tests.test_game_construction network.tests.test_game_receipt_compatibility
python -m systems.workspace.game_construction verify --trace docs/first_trace.json
python -m systems.workspace.game_construction verify-browser-expanded --receipt evidence/export_success.json
```

The original strict `verify-browser` command **still rejects** a raw
expanded receipt. Only the separate explicit `verify-browser-expanded`
compatibility path accepts it, after validating extension fields and
strict canonical native replay.

## Important distinctions

- W12 PASS remains scoped to the **previously verified local candidate**.
  The new GitHub suite verifies restored source bytes and runnable native
  tests, **not an externally deployed browser**.
- A locally exported browser receipt is not cryptographically authenticated
  as coming from a particular browser origin.
- An existing **W13 multi-world BUILD candidate** is preserved in the
  separate `_game_w13_publish_20261015` source library. Its new `advance`
  action after a solved world is candidate implementation evidence only.
  `game_nih_complete_stack_bridge_v1.zip` also contains a
  `WORLD_W13_PROPOSAL.md`, explicitly marked **not admitted**. Neither is
  an accepted WORLD W13 game contract or independent W13 WITNESS PASS.
- B9–B18's successful workstation native-delivery CI does not complete
  the game, the W13 browser experience, or its multi-world witness.

**Next bounded movement:** Have WORLD evaluate the existing W13 **proposal**
and the separately preserved BUILD candidate. WORLD must select an exact
versioned world/advance before-action-after contract and at least one
negative case. BUILD then connects the candidate to actual browser receipts,
and independent WITNESS verifies it. Do not invent another W13 design or
promote candidate work to CP `GAME-W13-WORLDS` PASS.
