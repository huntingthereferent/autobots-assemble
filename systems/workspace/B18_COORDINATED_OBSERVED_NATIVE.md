# B18 — Coordinated lower-level observed native delivery

## Current referent

B17 coordinates the high-level B13/B14 Python operator APIs and their
native continuation. But the underlying B11 `SourceOwnedLocalDelivery` and
B9 `B9ContinuationBridge` could be instantiated directly and hold stale
`ObservedEventJournal` snapshots while another writer already registered a
handoff or started a native attempt.

B18 adds a **coordinated lower-level observed journal** to the original
B11 signed admission and B9 continuation paths.

## Source and admission

`B18CoordinatedObservedJournal` subclasses the original
`ObservedEventJournal` and takes the same observed-journal sidecar lock
as B16 and B17:

- Before its constructor loads and recovers durable LOCAL_PASS.
- Before append/submission, while it refreshes the persisted event stream.
- Through reactor verification, write-ahead START, independent native
  observation, and OBSERVED or unresolved-effect recording.
- Before explicit journal recovery after a crash.

`B18CoordinatedBridge` refreshes that journal under its lock before
preparing or projecting a B9 source-edition-bound request.

The existing B11 `SourceOwnedLocalDelivery` now instantiates both coordinated
components. Its direct `deliver` method encloses exact-handoff Ed25519
admission, duplicate detection and event append in one journal lease and
reconstructs the journal from durable records first.

These locks are the same physical B16 observed-journal sidecar locks. B13/B14
already hold the operator trust and observed locks during their entry and
reenter the same observed lease within that owning thread. A different
thread or process remains blocked or fails fast. No new signer, authority,
identity enrollment or background worker is introduced.

## Native and recovery boundaries

B11 still requires an independently supplied Ed25519 public key for a
source edition and a currently verified source-native receipt; B12 rereads
the real original B3 finite worker return. A proposed B9 source hint cannot
authorize either the signed result or a new native subprocess.

An interrupted LOCAL_PASS before START may be safely recovered after fresh
verification. Once START is durable, an unobserved effect remains
RECOVERY_REQUIRED rather than being reexecuted. A successful B11 event
only closes its candidate-local relation, not the entire B9 route.

## Required verification

The B18 workflow runs 12 tests for stale direct B11 objects, concurrent
threads using identical signed evidence, B9 submission/projection freshness,
lock contention before native recovery, and independently rechecked real
B3 returns with exactly one native attempt. It preserves every B17–B10
native/journal regression suite and the original 73 B9 construction cases.

All acceptance claims must come from GitHub CI on the exact PR head, followed
by the independent merge-commit Actions run.

## Preserved walls

The generic `RuntimeJournal` and opt-in original
`ObservedEventJournal` remain unchanged. Low-level callers that deliberately
use those classes or call `RuntimeJournal.append` directly can bypass this
cooperative observed lock. The B9 construction source, B3 native source
journal, independent external owner, distributed hosts and any unknown
external-effect reconciliation remain separate. This is a local cooperating
observed-native delivery guarantee, not a universal transactional ledger.
