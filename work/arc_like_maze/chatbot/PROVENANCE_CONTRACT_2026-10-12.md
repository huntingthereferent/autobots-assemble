# Explicit provenance requirements — finite chatbot research record (2026-10-12)

**Active referent:** Preserve the distinction between a valid finite A/B-labeled mathematical correspondence and the separately declared requirement that its evidence originate from a currently verified local owner. A/B remains language for relationships through movement; the generators studied here are only a specified 27-state mathematical example.

## Explicit new task dimension

The integrated chatbot's new `ProvenanceTaskSession` accepts a strict structured key:

    {"goals":[[0,1,1],[0,2,0]],
     "required_provenance":{"old":"LOCAL_OWNER_VERIFIED","new":"LOCAL_OWNER_VERIFIED"}}

The prior edge, path, destination and goal declarations are unchanged. One-sided requests are allowed, and absent required_provenance preserves the previous task behavior. No prose inference, remote source-reported label, matching digest, or identity copied into the request can *create* local ownership proof. A normalized fingerprint distinguishes the explicit demand from the underlying task.

This is a fourth **witness requirement**, distinct from mathematical edge admission, step-by-step rooted history and destination identity.

## Executed local evidence

Original finite law phi=(0,0,1), changed phi=(0,0,0); independent HTTP-pinned local observer fixtures.

| Requirement and evidence | Result | Old/new observed edges |
|---|---|---:|
| Both sides required and verified local | GOALS_CARRIED_WITNESSED; 2/2 finite goals | 28+18 |
| Both sides required; changed side remote and not verified | PROVENANCE_UNPROVED | 0+0 |
| Only old source required, changed side remote | GOALS_CARRIED_REMOTE_REPORTED; 2/2 goals | 28+18 |
| Only old required, new initially local then loses bound owner | WITNESSED -> REMOTE_REPORTED on zero-read revisitation | 28+18 |
| Ambiguous instruction | UNKNOWN_TASK | 0+0 |

A pinned version change returns UNKNOWN_VERSION. A tampered retained edge still returns WALL_OBSERVATION under replay. Live owner binding is checked on each advance for both sides, including the unrequired side. An initially remote source is not retroactively made local solely from later owner metadata within this session. Missing requested proof stops before new A/B transition requests.

**Verified locally:** 14 new integration tests + 4 source-scope model tests + prior mixed 12, multi-required 13, task intake 11, language bridge 35, evidence prefilter 8, post-extension 25, union extension 15 = **137 tests passing**, each in separate completed module runs. Broad historical suite not completed; GitHub CI has not been verified.

## Deliverables and reproducibility

The **full snapshot-backed chatbot** is packaged as `ab_chatbot_explicit_provenance_2026-10-12.zip`, SHA-256 `9681985b3d6cf466f612dcc3d1a25c7d3b9d919544be5533f55d7a5a32db808f`. It has 137 files, preserving all 129 predecessor files byte-for-byte. It adds the integrated source, 14 tests, runnable demo, detailed JSON result, regression record and the source-scope checker.

The **GitHub** sidecar is only `finite_provenance_scope.py`, `test_finite_provenance_scope.py`, and this research record. To replay its 4 pure tests:

    cd work/arc_like_maze/chatbot
    python finite_provenance_scope.py
    python -m unittest -q test_finite_provenance_scope.py

Crucial boundary: the standalone Python verifier accepts trusted in-process handles as input. It cannot independently authenticate source objects or prove HTTP data origin. Actual local proof in the full chatbot depends on the existing `LanguageBridge._scope` with a live owner-bound loopback and independently replayed cached transition values. Neither finite replay nor a user-supplied source identifier authenticates a third-party system.

**Next:** Investigate requests for a *specific pinned local owner* and explicitly re-pinned evidence history. A new owner or revision should be a new evidence referent, not an automatic continuity or source-equivalence assertion. No universal physical A/B or unrestricted AI claim. `state/current.json` retains the separate Continuity project.
