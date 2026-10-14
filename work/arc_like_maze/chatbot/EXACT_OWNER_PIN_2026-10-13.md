# Exact pinned owner referents — October 13, 2026

**Current referent:** Continue the existing finite A/B correspondence process with an *explicitly chosen exact owner* provenance requirement, not a source-reported identity or a claim of uninterrupted continuity. A/B is the language of relational movement; the finite A/B-labeled operators here are separate scoped mathematics.

## Integrated in-process result

A new opt-in layer, `ab_chatbot_owner_pin_contract.py`, composes the already-tested `ProvenanceTaskSession` without altering prior solvers or task grammars. `OwnerPinRegistry.issue(bridge)` requires a live in-process locally verified owner binding. It issues an opaque 48-character local referent, recording the **same owner object**, **same snapshot object**, source claim, revision, digest, and optional previous pin ID.

Example structured request:

    {"goals":[[0,1,1],[0,2,0]],
     "required_owner_pins":{"old":"<locally-issued-token>","new":"<locally-issued-token>"}}

The registry checks exact owner/snapshot object identity, the source-reported version triple, and the existing live local owner binding **before and after task continuation**. It latches a pin invalid when those conditions fail. Unknown or bad handles return UNKNOWN_OWNER_PIN or INVALID_TASK with zero transition observations; withdrawn or changed pins return OWNER_PIN_UNPROVED, without supplying a formerly cached completion.

A new snapshot (even with identical label, digest and revision) cannot use an older pin. An explicit re-pin creates a distinct token and distinct task session, with an optional historical predecessor ID—not a continuity theorem. The previously pinned source retains its already observed edges in *historical* evidence; a fresh source snapshot begins with zero edges and must replay its own proof.

## Local witnessed controls

Using separate live pinned local finite owners (original phi=(0,0,1), changed phi=(0,0,0)) and a two-goal task, the first task returns **GOALS_CARRIED_WITNESSED** with **28 + 18** observed old/new edges. Reusing its old pin on a newly opened observer over the same owner returns OWNER_PIN_UNPROVED before new observations. Issuing a new pin and new task returns SEARCHING with zero new old-side observations. Owner-object substitution, pinned revision mutation and registry revocation invalidate the old task; recovering a prior object or copied metadata cannot automatically restore its invalidated pin.

**Tests:** 10 exact-owner integration tests + 5 standalone object-identity tests + 97 unchanged targeted regressions from seven modules = **112 passed across separately completed runs**. The full historical suite and GitHub CI have not been verified.

## Local full archive

`ab_chatbot_exact_owner_pin_2026-10-13.zip` SHA-256 `73265683ab53f7c8175ac15e66d49acc127b0aace97ece6cab534325244b6216`, **145 files**, all previous **137 files preserved byte-for-byte**. New files include integrated owner-pin module, test module, standalone finite model and five tests, runnable demo, JSON example and regression evidence, and README. This full HTTP-pinned correspondence process is in the local archive; **it is not being asserted to exist entirely in GitHub**.

## Executable GitHub standalone model

`finite_owner_pin_identity.py` models exact in-process object/snapshot identity and re-issuance, with `test_finite_owner_pin_identity.py` containing five pure tests:

    cd work/arc_like_maze/chatbot
    python finite_owner_pin_identity.py
    python -m unittest -q test_finite_owner_pin_identity.py

**Crucial limitation:** This standalone model cannot authenticate a remote system or prove its caller was authorized to issue a pin; the integrated layer's real proof depends on the existing `LanguageBridge._scope` owner-bound loopback, and that mechanism itself only certifies a local in-process source relation. Tokens are referent handles, **not external identity credentials**. Version or owner changes do not imply any globally valid source-transport relation.

**Next:** Test *explicitly authorized evidence comparison across re-pins* while keeping old and new witnesses disjoint until a fresh verifier replays the necessary relations. Leave the unrelated active Continuity project in `state/current.json` unchanged.
