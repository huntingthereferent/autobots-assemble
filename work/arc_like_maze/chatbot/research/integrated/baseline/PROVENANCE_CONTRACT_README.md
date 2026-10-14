# A/B chatbot — explicit owner provenance requirements

**Research date:** 2026-10-12  
**Layer:** `ab_chatbot_provenance_contract.py` above the existing 129-file mixed-task chatbot. No old solver, path, union, task-intake, or HTTP owner code has been modified.

## Referent and strict task contract

Language-level A/B continues to mean recognition and continuation of witnessed relations. The finite A/B generators in this experiment are explicitly declared 27-state mathematical operations, not universal physical A/B.

The new **source-provenance** obligation is independent of mathematical goal, admitted-edge, rooted-path, and destination-identity obligations. Caller-provided metadata cannot authorize a local-owner claim. Accepted input is strict structured JSON-like data; for example:

```json
{
  "goals": [[0,1,1],[0,2,0]],
  "required_edges": [{"state":[0,0,0],"action":"A"}],
  "required_paths": [
    {"word":"ABAA","old_destination":[0,2,0],"new_destination":[0,2,0]},
    {"word":"ABBABA","old_destination":[0,1,1],"new_destination":[0,1,0]}
  ],
  "required_destinations": [{"source":[0,1,1],"image":[0,1,0]}],
  "required_provenance": {
    "old":"LOCAL_OWNER_VERIFIED",
    "new":"LOCAL_OWNER_VERIFIED"
  }
}
```

A caller may explicitly require only `old` or only `new`. An evidence-only requirement works with ordinary `goals`. Omit `required_provenance` to follow the previous task solver completely unchanged. Other origin levels and extra fields are rejected rather than guessed from ambiguous language. A task fingerprint includes its normalized prior task fingerprint plus the precise per-side provenance demands. It is **not** authentication.

## Distinct proof rules

1. The old and new `LanguageBridge` observations remain pinned to the same snapshot objects and reported source revisions. A version change returns `UNKNOWN_VERSION`.
2. A demanded side must have originally been locally verified and still pass the existing live loopback-to-actual-owner identity check, owner view, and version/digest check. An identical source-reported label or matching copied finite output alone does not pass.
3. A missing source proof returns `PROVENANCE_UNPROVED` **before any transition observation** and without exposing an earlier selected completion. Remote evidence is not reclassified as local evidence, even if user text requests it.
4. Both sides' live scopes are re-evaluated on every read. If a side that is *not* demanded loses local verification, a previously witnessed mathematical result is downgraded to `REMOTE_REPORTED`. Re-attaching metadata to a side that started remote does not retrospectively upgrade it within the session.
5. The preexisting mixed task engine independently zero-read replays admitted edges, paths and destination pairings on each completed read. A forged cached edge still yields `WALL_OBSERVATION`. The source-proof checker alone cannot guarantee these mathematical witness conditions.

## Completed local experiments

Original finite law `(0,0,1)` and changed law `(0,0,0)` on independently pinned source observers:

| Case | Result | Old/new observed owner edges |
|---|---|---|
| Both sides explicitly require verified local owners, both available | `GOALS_CARRIED_WITNESSED`, 2/2 goals | 28 + 18 |
| Both required, new side remote | `PROVENANCE_UNPROVED`, no solver execution | 0 + 0 |
| Old required only, new side remote | `GOALS_CARRIED_REMOTE_REPORTED`, 2/2 finite goals | 28 + 18 |
| Old required only, new side initially local but binding withdrawn after completion | `GOALS_CARRIED_WITNESSED` then `GOALS_CARRIED_REMOTE_REPORTED` on zero-read revisit | 28 + 18 |
| Ambiguous source instruction | `UNKNOWN_TASK`, no solver execution | 0 + 0 |

Results: `PROVENANCE_CONTRACT_RESULTS.json`.

**Verification:** 14 new integrated tests, four standalone source-scope model tests, 12 unchanged mixed-obligation tests, 13 multi-required-edge, 11 task-intake, 35 language-bridge, eight evidence-prefilter, 25 post-extension portfolio, and 15 union-extension tests — **137 passing tests across nine completed, separate test runs**. Full historical suite was **not** run; GitHub CI not verified. `PROVENANCE_REGRESSION_RESULTS.json` records individual modules.

## Reproduce

From an extracted local archive directory:

```bash
python -m unittest -q test_ab_chatbot_provenance_contract.py
python -m unittest -q test_finite_provenance_scope.py
python run_provenance_demo.py
```

The pure `finite_provenance_scope.py` model accepts a verifier-controlled in-process owner handle and checks identity and pinned metadata. It **does not independently authenticate a remote source**. The real local check is in the existing `LanguageBridge._scope` with source-owned loopback binding. Any GitHub standalone reproduction must preserve this boundary.

## Next bounded movement

Evidence requirements with a strict *named* local owner and evidence re-pinning history, as separate declarations; independently test what survives explicit owner replacement and sourced migration. Never convert source-reported identifiers into an attestation, and never make a global physical or general-agent claim from finite mathematical models. The unrelated Continuity project pointer in `state/current.json` is unchanged.
