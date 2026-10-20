# Cross-host observation — signed, bounded remote witnesses

**Status:** Draft research implementation, not remote worker admission and
not a distributed consensus service. No public listener or deployment.

## The actual relationship

Host A retains ownership of its own encrypted native journal. Host B does
not copy A's private journal key or silently join A's runtime. The operator
on B already has a **separately verified source public key and a signed,
independently retained checkpoint** for A.

A exports a read-only **witness span** containing its next signed checkpoint
and at most 64 consecutive encrypted journal rows (sequence, predecessor
digest, nonce, ciphertext, record digest). Nothing decrypts or schedules
remote work. This is an offline data artifact—not an HTTP ingestion route.

B verifies the signed checkpoint with the **previously pinned source key**,
requires the exact same journal identity, and independently recalculates
each ciphertext record hash from its last trusted checkpoint through to the
signed new head. B then atomically advances only its own small observation
ledger, preserving the source-specific last observed signed checkpoint.

```text
Host A — source-owned sealed journal
  encrypted records 1..N
    → operator-signed source checkpoint N
    → bounded export of ciphertext frames since B's known checkpoint
    → transfer by separately authorized means (not implemented here)

Host B — observer-owned private ledger
  existing operator-pinned source public key + signed checkpoint K
    → verify signed source checkpoint N
    → replay *hash relationships*, not remote plaintext
    → require every frame K+1 .. N with no gap or wrong parent
    → commit observed checkpoint N or commit nothing
    → continue observing; DO NOT execute or import source work
```

## Verified boundaries

- Source identities must be **locally enrolled**, not created by an
  incoming message. One observer can follow multiple distinct sources
  with separate signing keys, journal identities and checkpoints.
- The receiver has **no need for the source AES encryption key**. Its
  recorded witness proves a particular signed ciphertext hash-chain
  continuation relative to its prior source checkpoint.
- Bounded size: maximum 64 records per span; missing, reordered,
  modified or incorrectly encoded frames are refused.
- Repetition, old snapshots, wrong keys, wrong journals, and an
  observer-ledger race are refused. A source that signs **two different
  histories from one base** can issue two individually valid proofs, but
  the observer accepts at most the first observed continuation; it
  cannot pretend they were one chain.
- The *actual source* can be replayed and audited by an authorized
  holder of that source journal key. The observer **cannot decrypt**
  ciphertext, validate the underlying native witness semantics, or
  attest that the remote actor truly performed the described science.

## What is intentionally absent

- No local or remote server endpoints, worker dispatch, execution or
  callbacks are added. No automatic trust enrollment or key transport.
- No distributed lock, leader election, quorum, lease, global consensus,
  or exactly-once remote delivery guarantee.
- No proof that an operator's signed ciphertext is a truthful account of
  the underlying real world or that the source owner is honest.
- The receiver's SQLite observations can be rolled back if the receiving
  host is compromised; high-value observers need their own independent
  checkpoints and retention policy. Remote source honesty cannot be
  inferred from a locally passing test.
- The CI cases simulate **independent source and observer ownership with
  different journals and keys on one test machine**. They do not
  demonstrate reliability of actual network transport, multi-host clock
  coordination or operation across untrusted remote hardware.

## Reproduction

```sh
python -m pip install 'cryptography>=45,<47' 'rdflib>=7,<8'
python -W error::ResourceWarning -m unittest \
  discover -s network/tests -p 'test_security_remote_witness.py' -v
```

The [native test suite](../network/tests/test_security_remote_witness.py)
creates independent encrypted source journals and a separate local
observer ledger. It tests successful movement across each source, bounded
hash verification, forged or missing evidence, repeated observation,
wrong signers and origin, simultaneous observer updates, and same-signer
fork exclusion.

A passing test verifies these relationships in the stated scope only.

## Authenticated local transfer laboratory

The [mTLS witness-only receiver and independent observer anchors](WITNESS_TRANSPORT.md)
offer an explicit transport seam for this **observation-only** protocol.
Trusted operators separately pin TLS client certificates, source Ed25519
signing keys, and observer-owned signed checkpoints. The loopback-only
receiver accepts no worker commands, no automatic key enrollment, and
no remote source journal decryption. The localhost TLS integration
tests exercise this seam; actual physically separated hosts and
production certificate custody remain outside current evidence.
