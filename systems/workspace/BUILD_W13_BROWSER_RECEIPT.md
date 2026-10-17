# BUILD W13 — playable two-room browser and explicit session receipts

**Status:** BUILD implementation candidate. Not independent WITNESS PASS, production deployment, proof of browser-origin identity, or automatic GAME CP admission.

## Current referent

Implement the already-merged [WORLD W13 Movement 01](WORLD_W13_MOVEMENT_01.md) for the **playable game**, using the existing October 15 \`w13_engine.py\` candidate. This is not an extension of the B9–B18 infrastructure roadmap and is not a definition of James's language referent.

W12 source, its strict native verifier, its original browser and all 32 tests/fixtures remain **unchanged**. The original \`systems/workspace/game_construction.py\` SHA-256 is \`dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1\`; BUILD's receipt verifier checks it before admitting a receipt.

## Implemented BUILD surfaces

- [Playable two-room browser](../../docs/game_w13_preview.html): first original W12 room (4×3, (0,1) to (2,1)), explicit **Advance** only after collection, then second candidate room (3×3, (0,0) to (1,1)). Each room retains separate local state, turns, actions and observations. No auto-advance, implicit third room or altered W12 movement rules.
- \`game_w13_engine.py\`: the **previously existing** October 15 two-to-four-world Python candidate moved into the repository with only its W12 import adapted to the restored canonical module. For this movement, the playable browser is scoped to exactly two named worlds; broad candidate capability does not authorize additional WORLD rooms.
- \`game_w13_receipt.py\`: a separate **BUILD native replay verifier** for the W13 session receipt and explicit cross-world join. It uses W12's \`run_actions\` and \`verify_trace\`, not \`game_w13_engine.py\`, to check two local world traces, action order, the one permitted \`advance\`, canonical state values and the completed-session claim.
- \`evidence/game_w13_build_reference.json\`: positive deterministic native fixture using the existing \`network/tests/fixtures/world_w13_movement_01.json\` actions. It is not represented as a live browser export.
- \`network/tests/test_game_w13_build_receipt.py\`: bounded native replay and hostile receipt cases.
- \`network/browser_w13_build_check.py\`: **actual headless Chromium** BUILD smoke checks using click and keyboard interaction and browser-downloaded JSON. The dedicated CI uploads fresh positive/altered browser exports and screenshot as an ephemeral job artifact. This is BUILD's own verification, **not independent WITNESS certification**.

## Exact versioned receipt schema — BUILD proposal for WITNESS to challenge

\`\`\`json
{
  "version": "game-w13-multiworld-v1",
  "worlds": [
    {
      "id": "first-room",
      "version": "game-construction-v0",
      "spec": {"width": 4, "height": 3, "start": [0, 1], "target": [2, 1]},
      "actions": ["right", "interact"],
      "observations": [{"action": "right", "before": {}, "after": {}, "verdict": "moved"}],
      "final": {"x": 1, "y": 1, "collected": true, "turns": 2}
    },
    {
      "id": "second-room",
      "version": "game-construction-v0",
      "spec": {"width": 3, "height": 3, "start": [0, 0], "target": [1, 1]},
      "actions": ["right", "interact"],
      "observations": [{"action": "right", "before": {}, "after": {}, "verdict": "moved"}],
      "final": {"x": 1, "y": 0, "collected": true, "turns": 2}
    }
  ],
  "actions": ["right", "interact", "advance", "right", "interact"],
  "boundaries": [
    {
      "action": "advance",
      "from_world": "first-room",
      "to_world": "second-room",
      "before": {"world_id": "first-room", "state": {"x": 1, "y": 1, "collected": true, "turns": 2}},
      "after": {"world_id": "second-room", "state": {"x": 0, "y": 0, "collected": false, "turns": 0}}
    }
  ],
  "final": {
    "world_id": "second-room",
    "state": {"x": 1, "y": 0, "collected": true, "turns": 2},
    "worlds_completed": 2,
    "solved": true
  }
}
\`\`\`

The abbreviated \`observations\` rows above illustrate **keys**, not valid complete records. For an actual *strict full-field sample*, use \`evidence/game_w13_build_reference.json\` or the browser's Export action. All observation objects must contain exactly \`action/before/after/verdict\`, with complete before/after state. The JSON field shapes are strict; unknown fields, duplicate world IDs and inconsistent types fail closed.

A receipt may be exported before completion: \`solved=false\` and a partial world's actions and current state are still replayable. When no \`advance\` occurred, second-room actions and boundaries must be empty. A session is solved only after its single accepted advance **and** second-room collection. A forged W13 receipt cannot be submitted to either original W12-only verifier.

## Build tests and negative controls

\`\`\`sh
python -m unittest -v \
  network.tests.test_game_construction \
  network.tests.test_game_receipt_compatibility \
  network.tests.test_game_w13_build_receipt

# Optional local actual-browser build tests:
python -m pip install playwright
python -m playwright install chromium
python -m network.browser_w13_build_check
\`\`\`

Negative cases include: advance before first-world collection, repeated advance, incomplete second-world collection, diagonal interaction, blocked-turn preservation, invented world spec, borrowed observation between rooms, changed source fingerprint, missing/extra schema fields, tampered before/after/verdict, altered boundary, false final counts, and global action order not matching local actions.

The exact two-room browser receipt is authenticated **neither as originating from a trustworthy website nor from a genuine owner**. The new native verifier is BUILD-authored and W12-source-based; it is not independent WITNESS, a signed source-owner proof, or a completed \`GAME-W13-WORLDS\` CP.

## Next single movement

**WITNESS** independently inspect BUILD's source and *actual downloaded Chromium receipt(s)*. Reconstruct the two-world session without importing BUILD's W13 verifier or engine as the sole oracle; compare original W12 source transitions, exact advance boundary and session state; modify source/receipts adversarially and verify failure. Preserve original W12 historical C1, BUILD 1–2, W12 PASS, the original W13 candidate and the new native/browser BUILD logs separately.

Only WITNESS may return its own bounded W13 verdict to COORDINATOR. Until that happens: **BUILD CANDIDATE / W13 CP NOT WITNESSED**.
