# Cross-scope finite intertwining — October 13, 2026

**Current referent:** Continue the existing A/B mathematical chatbot by testing an explicitly selected, independently witnessed *single edge* across DIFFERENT pinned source-owner scopes. A/B is language for tracing movement; the finite A/B-labeled operations in this experiment are not that language's definition.

## What was verified

Four independent locally owner-bound historical snapshots form two pairs:

| Source pair | Old law phi | Changed law phi | Witnessed join words |
|---|---|---|---|
| Recipient | `(0,0,0)` | `(0,1,2)` | `A`, `BAA` |
| Donor | `(0,0,1)` | `(1,0,1)` | `AB`, `B` |

The recipient join initially has **5 paired states, 4 admitted edges**. The donor independently witnesses its edge `(1,0,0) B`: old endpoint `(1,2,0)` and changed endpoint `(1,2,1)`.

The user-declared transport maps **two endpoint states on each side**, not entire sources:

- donor old `(1,0,0) -> (1,2,0)` maps to recipient old `(1,0,0) -> (1,2,0)`;
- donor new `(1,0,0) -> (1,2,1)` maps to recipient new `(1,0,0) -> (1,2,0)`.

The nonidentity second endpoint in the changed-law map is intentional. Both **recipient** owner snapshots independently observe their corresponding labeled B transition; these are **2 new owner observations**, one per recipient side. They are not copied from the donor.

Both commuting squares replay, the recipient's rooted source pairing is retained, and adding the recipient-observed edge yields a **NEW 6-state, 5-edge** derived partial relation, leaving both base joins untouched. A task requiring recipient `(1,1,0) A` and derived `(1,0,0) B` completes **2/2** against the new fingerprinted witness.

### Boundaries and negative results

- A plausible but wrong state mapping returns `TRANSPORT_INTERTWINING_CONFLICT`, with expected versus independently observed endpoints.
- Donor lacks the selected witnessed edge -> `TRANSPORT_DONOR_EDGE_UNPROVED`.
- Missing, duplicate, or extra endpoint assignments are refused; no off-edge transport is treated as proved.
- A recipient source budget exhaustion returns `UNKNOWN_BUDGET`, rather than falsely transporting.
- Revoked source pins, version changes, forged cached edges, or witness fingerprint substitution withhold previously admitted task success.
- The **entire** old and changed transformation systems have NOT been shown equivalent, nor is a general transport across arbitrary owners, revisions or languages established. Four local owner bindings are not authenticated remote third-party identities.
- Only the single selected labeled edge has a fresh double-sided intertwining witness. No unseen source transition or entire graph is carried over automatically.

## Integrated interface

```
CrossScopeIntertwiningTransfer(recipient, donor, {
  "recipient_fingerprint": current_digest(recipient),
  "donor_fingerprint": current_digest(donor),
  "selected_donor_edge": {"state": [1,0,0], "action": "B"},
  "old_state_transport": [
    {"donor": [1,0,0], "recipient": [1,0,0]},
    {"donor": [1,2,0], "recipient": [1,2,0]}],
  "new_state_transport": [
    {"donor": [1,0,0], "recipient": [1,0,0]},
    {"donor": [1,2,1], "recipient": [1,2,0]}]
}).advance()
```

An explicit `CrossScopeTransportTask` binds goal/edge/path/destination obligations to the new derived fingerprint and re-audits the four pinned owner scopes on each read. No existing production module was changed.

## Reproduction

```
python run_cross_scope_transport_demo.py
python -m unittest -q test_ab_chatbot_cross_scope_transport.py
python finite_cross_scope_transport.py
python -m unittest -q test_finite_cross_scope_transport.py
```

**Completed current-turn verification:** 12 genuinely new integration tests + 10 inherited imported fixture tests = 22 test executions; 6 standalone finite reference tests; prior same-pin transfer 23, joint witness binding 22, cross-pin join 20, exact owner pin 10. **103 passing test executions** across separate completed module runs; counts overlap from imported fixtures. An attempted longer grouped regression timed out; the full historical suite and GitHub CI were not verified.

This full local artifact has **193 files**: all **185** previous files were preserved byte-for-byte; 8 new source/test/demo/readme/evidence files were added. GitHub carries a separate standalone finite oracle and recorded scope, not the complete integrated owner-bound source. Leave the unrelated Continuity project pointer `state/current.json` unchanged.

**Next:** Test compatibility and explicit selected-edge chains between *more than two* source scopes, while preserving each independent source's trace and measuring fresh owner observations. Do not infer global state correspondence from one commuting square.
