# Atomic native admission — sealed SQLite journal

**Status:** Bounded implementation on draft PR #262. This replaces the
separate replay-ledger/journal commit only for authenticated movements
accepted through `AuthenticatedHandoffIngress` when its actual native
runtime uses `SealedRuntimeJournal`. Other entrypoints retain their
established, separate trust contracts.

## One real movement, one durable decision

```text
operator-current public-key pin
    → signed scope and ciphertext verification [no write]
    → parse exact native Handoff or ExecutionResult [no write]
    → verify native actor/event relationship and witnesses [no write]
    → SQLite BEGIN IMMEDIATE in the sealed native journal
         → read exact previous native sequence
         → insert opaque replay token (lane + signed event ID)
         → insert encrypted native SUBMISSION or RESULT
       SQLite COMMIT
    → update runtime in-memory native history
    → minimal HTTP acknowledgement
```

The replay token is a SHA-256 digest of the bounded lane/event-ID
relationship; it is not the caller's plaintext handoff. SQLite's
`PRIMARY KEY` enforces first admission even after process restart.
A read-only early replay check is only an optimization; final authority
is the transaction that inserts **both** replay identity and native event.

This construction does **not** substitute a new task engine, invent
work results or prove that scientific evidence is independently true.
The original native witness verifier still decides admissible results.

## Recovery semantics tested

- **Fault before commit:** a crash after insertion of the replay token,
  or after insertion of the encrypted event, rolls back **both** changes.
  On restart the same signed envelope may be retried; it has not been
  admitted or counted as observed native movement.
- **Fault after commit but before acknowledgement:** the signed movement
  remains present in the reopened native journal. Retrying the same
  envelope, even after restart, fails as a replay.
- **Native validation failure:** the sealed path does not consume a replay
  event ID before it verifies the actor, native structure and witness
  requirement.
- **Concurrent stale writer:** a writer holding an out-of-date native
  sequence fails without recording a replay token. An operator must
  reload and check the latest independently anchored history.
- **Legacy sealed database:** if an earlier encrypted journal contains
  movements but no atomic admission table, opening it fails closed.
  It requires an explicit, audited migration of historical replay
  identities; creating an empty table over old movements would silently
  forget previous admissions.

These tests inject exceptions **inside** the SQLite transaction, rather
than claiming to simulate loss of power to the underlying hardware.
SQLite crash durability still depends on host filesystem and storage
configuration. There is no distributed consensus or cross-host recovery
claim.

## Remaining bounds

The legacy plaintext JSONL native journal and separate `ReplayLedger`
remain supported for existing local development. They are **not atomic**
and must not be advertised as safe external ingress. Offline key
recovery envelopes have their own replay ledger and are not native
runtime movements; they are unchanged.

This transaction does not authenticate the local Python caller,
protect other workstation data stores, prevent whole-database rollback
without independent checkpoints, or solve adversarial host control.
A successful commit does not mean a worker ran; an admitted submission
remains READY until the existing scheduler acts on it.

No existing history is migrated or touched by adding this code. It does
not execute a worker, enroll keys, deploy a service or authorize merging.
