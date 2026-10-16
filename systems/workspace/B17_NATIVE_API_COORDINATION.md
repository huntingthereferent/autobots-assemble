# B17 — Direct operator API coordination and fresh native journal state

## Current referent

B16 serialized **cooperating command processes** at the operator boundary.
But Python callers could instantiate `B13OfflineOwnerDelivery` or
`B14OperatorTrustedDelivery`, keep that instance across other processes'
commits, and deliver using its **stale in-memory ObservedEventJournal**.
Similarly, a direct `OperatorPinLedger.revoke()` or `rotate()` did not
participate in the B16 operator-policy lease.

B17 moves the same local advisory coordination into these **direct, source-
owning operator API entry points**, while preserving B16's command behavior.

## Specific contract

1. B13's constructor acquires the B16 **trust-policy + observed-journal locks**
   *before* constructing B10/B11 journal objects, because journal recovery
   itself may re-observe a persisted native result.
2. Every B13 `prepare`, `signing_request`, and `deliver` call takes the
   same locks and **reconstructs the B12/B11 observed journal from durable
   records while locked**. A B13 object constructed before another process
   registered a B10 request or admitted a signed result therefore cannot
   reuse its stale journal snapshot.
3. Direct B14 native host construction also acquires both locks, and its
   methods delegate to those coordinated B13 operations. Direct B14
   `OperatorPinLedger.enroll/rotate/revoke` mutations take the policy lock,
   so a key change cannot race with signed native delivery through the
   cooperating APIs.
4. B16 lock leases are **reentrant for a single thread only when the
   requested paths are already held**. This preserves existing B13/B14 CLI
   commands which take the outer lease, yet ensures a second thread must
   acquire a real OS lock. An inner call cannot *expand* the lock set,
   avoiding lock-order inversions and deadlocks.
5. B10/B11's original write-ahead START, signature validation and
   independently observed B3 result remain unchanged. An uncertain
   external effect is not automatically retried. No B3 subprocess is
   re-executed to satisfy a B17 read-only native re-observation.

## Verification

`workstation-b17-native-api-coordination` requires **15 direct API cases**,
including stale Python host objects created before request registration,
cross-object signing and delivery, concurrent threads attempting the same
source-owned native result, B14 policy mutation blocked by a held native
session, thread-local reentrancy vs real inter-thread lock contention,\nPOSIX forked-child rejection of inherited thread-local lock authority,
recovery of signed LOCAL_PASS only after acquiring the journal locks,
and immediate revocation enforcement.

Existing B16 CLI/subprocess concurrency cases, B15–B10 native/regression
cases, 73 original B9 construction tests and the full repository protocol
suite must remain green on the exact PR head before merging.

## Preserved walls

This is **not** a universal event-store transaction or remote distributed
lock. The guarantee applies to the B13 and B14 high-level native operator
classes and B14's policy mutations when they use the shared B16 lock files.
The direct low-level `RuntimeJournal`, `ObservedEventJournal`,
`SourceOwnedLocalDelivery`, B12 native integration, B9 construction and
B3 source-journal writers remain separate boundaries, and a caller that
bypasses these interfaces can still race them.

This does not establish a production key owner, a daemon, multi-host/NFS
locking, cross-journal atomic commits, reconciliation of uncertain native
effects, or independent verification of an entire B9 route.
