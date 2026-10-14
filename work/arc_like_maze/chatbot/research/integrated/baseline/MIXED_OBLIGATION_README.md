# Mixed explicit finite task obligations — 2026-10-12

**Referent:** The same snapshot-backed A/B chatbot, continuing from the 122-file multiple-required-edge version. Here A/B labels two scoped transformations of 27 finite states; it does not redefine the language-level A/B research.

## Scope of the addition

The opt-in `MixedTaskSession` accepts a strict **structured** contract with 1–8 distinct source goals and any combination of:

- `required_edges` (0–8): exact source state and action, requiring an admitted old/new labeled edge.
- `required_paths` (0–8): explicit rooted A/B word (length 1–8) and exact old/new endpoints, requiring **every step** of that complete word to survive in the same selected partial pairing. Replays both owner paths from the pinned snapshots when every edge is admitted.
- `required_destinations` (0–8): source state plus target-image identity, requiring that pairing with a retained rooted witness. An endpoint image alone does not prove a specified path history.

At least one path or destination obligation is needed to enter the new mixed-contract layer. **All obligations must be satisfied by one independently replay-audited candidate**. Incompatible destination/path assertions are rejected at intake (`INCONSISTENT_TASK`) without observations. Unrecognized prose is `UNKNOWN_TASK`. Existing exact text and structured goal-only, single-edge, and plural-edge tasks continue through the previous `MultiTaskSession` unchanged.

Example:

```json
{
  "goals": [[0,1,1],[0,2,0]],
  "required_edges": [{"state":[0,0,0],"action":"A"}],
  "required_paths": [
    {"word":"ABAA","old_destination":[0,2,0],"new_destination":[0,2,0]},
    {"word":"ABBABA","old_destination":[0,1,1],"new_destination":[0,1,0]}
  ],
  "required_destinations": [
    {"source":[0,1,1],"image":[0,1,0]},
    {"source":[0,2,0],"image":[0,2,0]}
  ]
}
```

The accepted contract retains the original input and a canonical SHA-256 **content fingerprint**, which is not a source-authentication guarantee. Optional edge prepruning only uses both cached owner transitions and explicit seed assignments; exclusions are individually replayed on subsequent calls. Path histories and destination pairings do **not** become global pre-pruning rules.

## Local witnessed outcomes

Original finite law phi=(0,0,1), changed law phi=(0,0,0), independent local owners, origin `(0,0,0)`, candidate pool unchanged. Reproduce with:

```
cd /path/to/extracted_chatbot
python run_mixed_obligations_demo.py
python -m unittest -q test_ab_chatbot_mixed_obligations test_finite_mixed_contract
```

1. **All three requirement types:** selected compatible paths `ABAA`, `ABBABA`; `GOALS_CARRIED_WITNESSED`, 2/2 goals; 9 paired states, 13 admitted edges, 5 excluded edges; observed 28 old-owner and 18 new-owner transitions.
2. **Same paths/destinations but required root B instead:** no completed candidate satisfies the conjunction; `REQUIREMENTS_UNPROVED`, no current selected result; 26+18 observed transitions. This is not a universal no-solution theorem.
3. **Directly inconsistent destination vs path declaration:** `INCONSISTENT_TASK`; 0 observations.
4. **Ambiguous prose:** `UNKNOWN_TASK`; 0 observations.

`MIXED_OBLIGATION_RESULTS.json` retains the per-candidate typed results and the selected case. A recorded task expression is a declaration, not a mathematical witness. Successful path/identity/edge claims are verified on pinned finite observations; source changes yield `UNKNOWN_VERSION`, tampered data `WALL_OBSERVATION`, and remote provenance stays remote-reported.

## Independent finite check

`finite_mixed_contract.py` is a smaller standalone checker over **complete declared laws** plus `finite_conflict_guidance.extend`. It independently replays admitted edges, exact path steps/endpoints and destination mappings. `test_finite_mixed_contract.py` supplies five negative/positive tests. It does **not** implement HTTP owner pinning, persistence, or unrestricted language understanding.

## Completed verification and limits

Focused integration 12/12, standalone finite 5/5. Completed unchanged regression modules: multi-required 13, explicit task 11, required-edge prefilter 8, post-extension 25, union edge-extension 15, and language bridge 35. **124/124 tests passed in individually completed module runs**. A grouped path-union regression run timed out and is explicitly **not counted**. The entire historical chatbot suite and GitHub CI were **not run to completion**.

This is a bounded candidate search; missing a satisfying candidate is `REQUIREMENTS_UNPROVED`, not an impossibility theorem. The new path and destination contracts do not imply finite whole-system conjugacy, universal A/B mathematics, general autonomous learning, or physical coupling.

**Next:** Distinguish a declared task's *required relationship* from its *witness provenance* at the input boundary; benchmark different mixtures and independent changes of observation order while preserving the original question and per-obligation evidence. Continue extending the current code rather than creating a replacement engine.
