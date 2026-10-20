# Protected native research journals — operational boundary

The opt-in `SealedRuntimeJournal` encrypts native `HandoffRuntime` SUBMISSION and
EVENT records at rest. It implements the existing journal interface. This is not
a new executor, scheduler, scientific witness, or definition of A/B.

## Storage behavior

- AES-256-GCM encrypts each native record with a fresh 96-bit nonce.
- Authenticated associated data binds each record to its sequential position
  and preceding record digest. A keyed sentinel authenticates the supplied
  journal key even before the first research event.
- SQLite commits the ciphertext before the runtime publishes an event into
  its in-memory state. Native restart replays the decrypted records through
  the original `RuntimeJournal` validation.
- An unexpected gap, altered ciphertext, broken chain, incorrect key, or
  second writer advancing beyond the loaded state fails closed.
- The key never gets written to the SQLite tables; the trusted application
  must obtain, protect and provide it. The example creates **ephemeral test
  key material only**.

## Explicit service adoption

This mode is **not** automatically enabled by the default HTTP server.

A trusted host can construct the same service with:

```python
from os import urandom
from pathlib import Path
from runtime.service import EcosystemService

# Test fixture only; real host must recover the SAME independently
# protected 32-byte key after restart, not create a new one.
fixture_key = urandom(32)
service = EcosystemService(
    data_dir=Path("/secure/private/brand-new-data-directory"),
    protected_runtime_key=fixture_key,
)
```

The directory must already be owned and protected by the operator. The
service refuses protected mode if `runtime.jsonl` exists, and refuses
unprotected mode if `runtime.sealed.sqlite` exists. This prevents silently
creating a second history. An existing plaintext journal needs a separately
authorized, integrity-preserving migration. **Do not delete it or rename it
to bypass this check.**

New records, events, and native replay must continue using the exact same
authenticated key. Losing that key makes encrypted records unrecoverable.
Generate and back up production keys only through a reviewed key-management
system; no HTTP input may supply, rotate or retrieve them.

## Recovery boundaries

Backing up encrypted SQLite bytes **and** the exact corresponding key
through separately protected processes permits attempted restoration with
the original key. Recovery must check the complete journal, source
fingerprints, event ancestry, record count, and operator-authorized restore
point before doing work. There is no automatic recovery/rotation tool yet,
and restoring stale backups can reintroduce old state.

The chain detects record tampering, missing middle rows and many corruptions.
It **cannot** distinguish a valid old database snapshot from the most recent
one without an independent trusted checkpoint. It is not tamper-proof against
an attacker with host or key access.

**Only the native handoff runtime journal is encrypted.** This does not
encrypt other workstation files such as personal operations, agent sidecar
logs, calendar, notes, traces, browser logs, workflow artifacts or backups.
Those remain separate storage boundaries. Nor does encrypted storage control
which connected user or local process can call the runtime.

## Operator-controlled signed ingress

The native HTTP admission layer uses existing
`systems.workspace.b14_operator_pin_ledger.OperatorPinLedger`, not a new
self-issued trust database. Each signer is scoped to
`ab-ingress:{lane}:{sender}:{receiver}` and edition
`ab-security-ingress-v1`. The operator must independently confirm and
enroll the signer Ed25519 **public** key digest before installing the ingress.

On every incoming sealed handoff/result, the already registered handler
re-reads the current ledger. Operator rotation and revocation disable its
old signing key. A new key requires new authenticated operator enrollment
and reconfiguration; a network request never enrolls itself.

A B14 local hash chain is not a hardware trust anchor and cannot prevent a
malicious host from replacing the entire policy with forged historical
records. Race-free revocation coordinated with runtime admission and remote
identity enrollment still require review.

## Reproduction

```sh
python -m pip install 'cryptography>=45,<47' 'rdflib>=7,<8'
python -W error::ResourceWarning -m unittest discover \
  -s network/tests -p 'test_security_*.py' -v
```

This provides a working bounded research prototype; not a production
security certification.
