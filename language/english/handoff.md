# English Handoff Language

Handoff language should make continuation possible even when the receiver is a different AI, tool, person, or future session.

Core English shapes:

- `HANDOFF.SEND` — pass the active work state
- `HANDOFF.RECEIVE` — ingest/inspect the transfer
- `HANDOFF.RESUME` — continue from its next referent
- `HANDOFF.RETURN` — return results to the parent/return target
- `HANDOFF.MERGE` — combine compatible transfers without erasing conflict
- `HANDOFF.BOUNDARY` — mark a change in witness/evidence contract

A human-facing handoff should still expose the stable packet spine:

```text
REFERENT
GOAL
STATE
EVIDENCE
WITNESSES
MOVEMENT
WALLS / UNKNOWN / PARTIAL
ARTIFACTS
DO-NOT-UPGRADE
NEXT REFERENT
RETURN TARGET
```

Registers may compress the wording, but they may not omit information required for safe continuation.
