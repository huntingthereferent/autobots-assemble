# B16 — Coordinated operator delivery and recovery

## Current referent

B9 constructs possible candidate routes. B10 can react to verified local
results. B11 independently checks signed local proof, B12 rereads the actual
B3 native return, B13 provides the offline signing interface, B14 records
operator trust, and B15 makes that trust mandatory in B13.

The next failure boundary is **two operating-system processes using stale
in-memory snapshots of one append-only observation journal**. A journal append
is durable, but without coordination two independently constructed runtimes
could both believe a native attempt had not started.

B16 coordinates the **operator-facing B13 and B14 commands** with two
cooperative, local OS file locks:

- The operator **trust-policy lock** is shared by B14 pin
  status/enrollment/rotation/revocation and both B13/B14 native commands.
  Key rotation or revocation cannot occur concurrently with one of these
  cooperating delivery commands.
- The **observed-journal lock** is shared by B13/B14 native commands, even
  if separately provisioned operator policies point to the same observation
  journal. This prevents simultaneous startup recovery and delivery from
  different cooperating command processes.

Locks are acquired in a deterministic order and held **before constructing**
B11's `ObservedEventJournal` until the command returns. This matters because
construction itself may recover a persisted LOCAL_PASS and invoke a native
adapter. The native B3 adapter still reads and independently verifies the
existing persisted finite-worker return; it does not run that worker again.

Contended locks **fail immediately**, reporting that the journal is busy.
Successful sequential commands see the latest committed journal and avoid
restarting an already-started native attempt. Durable signed results retain
B10's distinction between safe pre-START recovery and uncertain external
START effects that require reconciliation.

## Lock-file behavior

`coordinated_operator_entry` uses local native OS locks (POSIX `flock`
or Windows `msvcrt.locking`). Each lock is a persistent sidecar next to its
canonical journal path with suffix `.b16.lock`. It rejects symlinked
journals, symlinked sidecars, sidecar hard links, non-regular sidecars, and
colliding trust/observed paths.

**Do not delete the lock files**, including when no process owns them:
deleting the inode can allow independent processes to lock different files.
The lock is held across validation, native-result recheck, journal replay,
any explicit operator approval, and the complete B11/B10 delivery.

B13 and B14 retain the same command syntax. No private signing key enters
either process. No `LOCKED` entry is placed into the evidence journal.

## Verified behavior

The dedicated `workstation-b16-delivery-coordination` workflow requires
16 B16 cases, including two simultaneous signed B13 delivery subprocesses,
the absence of duplicate LOCAL_PASS / START records, lock contention
across different policy paths for a shared observed journal, lock refusal
before journal startup, operator revocation between commands, and recovery
of an already persisted signed result only after the lock is released.

The original B15–B10 native verification suites and all 73 B9 construction
cases also run in GitHub CI. Green PR checks are the gate for merging.

## Remaining walls

- This is a **cooperative, local-process CLI guarantee**, not a universal
  transaction layer. Direct `RuntimeJournal`, `B11`, `B12`, `B13`, or
  `B14` Python API callers that bypass the coordinated operator entry
  are not automatically serialized. The B3 and B9 journals are also not
  generally protected against independent writers here.
- These OS locks are not distributed coordination for multiple machines,
  NFS/cloud object storage, forked workers that ignore the contract, or
  compromised processes. Operator policies and lock files require appropriate
  filesystem permissions and trustworthy storage.
- An interrupted native START remains recovery-required; B16 does not
  reconcile unknown external side effects or claim exactly-once delivery to
  an external system.
- Neither a signed result nor a local operator label establishes a real-world
  source-owner identity or completes an entire route.
