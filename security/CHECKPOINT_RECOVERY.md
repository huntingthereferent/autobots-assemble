# Journal continuity: signed checkpoints and offline recovery

This is an **optional, source-observable security lane**, not a deployed
backup daemon, remote key service, or new worker. It runs on the existing
encrypted `SealedRuntimeJournal` and `HandoffRuntime`.

## Checkpoint movement

1. An authorized operator opens the encrypted journal with its established
   32-byte key and independently verifies the current native history.
2. The operator issues a signed checkpoint with
   `security.journal_checkpoint.issue_checkpoint(journal, signer_private_key)`.
   The checkpoint records the *specific* journal identity, sequence and the
   authenticated digest of the last record.
3. The checkpoint is copied to a trusted independent storage domain; only the
   **public** checkpoint verification key is needed to verify it.
4. On restart, a trusted host supplies `trusted_runtime_checkpoint` and
   `trusted_checkpoint_public_key` to `EcosystemService`, alongside the
   original `protected_runtime_key`. The service refuses a missing journal,
   an invalid signature, a different journal, a shorter history or a different
   digest at the checkpointed sequence.

The journal can **continue beyond** an older valid checkpoint. Operators
must issue and independently preserve a new one when ready to advance the
anchored prefix. The code does not silently create or publish checkpoints.

**Source ownership matters:** keeping a signed checkpoint beside the same
database gives a host attacker the opportunity to roll back both. The signing
key, checkpoint and retained independent reference must be secured beyond
the same failure/rollback domain. Even with an independent anchor, history
*after the latest checkpoint* can still be rolled back without detection.

## Offline journal key envelope

`security.key_recovery.issue_recovery_envelope` accepts the already-opened
verified journal, its *actual* key, a separately signed journal checkpoint,
the verified checkpoint signer, an operator's Ed25519 signing key, and an
**offline** X25519 recovery recipient public key. It first checks that the
provided journal key opens the existing records, then encrypts it to the
designated recovery recipient using the established A/B envelope.

The resulting envelope contains signed context and ciphertext; it does not
contain the raw journal key in readable form. The operator exports that
envelope to independently protected storage. No key, recovery private key,
or envelope is automatically saved by the implementation.

`recover_journal_key` requires:

- The independently confirmed original journal identity and signed checkpoint.
- A **separately pinned checkpoint signer public key**, checked against
  the checkpoint Ed25519 signature before any envelope decryption. A
  recovery-envelope signature never substitutes for checkpoint authority.
- The operator's independently enrolled **public** signing key.
- The recovery recipient's X25519 **private** key, held outside the original
  workstation.
- A writable local replay ledger for this controlled recovery attempt.

A successful decryption yields 32 bytes *in the caller's memory*. The operator
still needs to open the original encrypted history, verify the independently
anchored checkpoint, inspect source ancestry, and approve resuming workers.
The function does **not** restore files, rotate credentials, install a key,
change a service or automatically restart work.

A replay ledger is local to an individual recovery environment. Reusing the
same package in a fresh environment can still decrypt it: this protocol does
not claim remote cancellation or revocation of already distributed packages.

## Failure boundaries

- A checkpoint authenticates a known prefix, not unseen future movements.
- A signature proves which signing key endorsed bytes, not whether human
  authorization or scientific evidence is correct.
- A valid old checkpoint alone does not prove the latest state is present.
- If the recovery **private key**, operator signing trust, signed checkpoint,
  or encrypted data are all lost, this code cannot recreate them.
- A compromised host holding a live journal key can still read or misuse
  data. This does not provide secure enclave isolation or guarantee future
  secrecy if that key has been exposed.
- No automated key rotation/re-encryption, distributed consensus,
  multi-host locking, trusted timestamping, off-host checkpoint publication,
  backup retention, or incident-response review has been implemented.

## Reproduction

```sh
python -m pip install 'cryptography>=45,<47' 'rdflib>=7,<8'
python -W error::ResourceWarning -m unittest discover \
  -s network/tests -p 'test_security_*.py' -v
```

Tests cover a legitimate continued chain, rollback below an independently
signed sequence, a forked valid encrypted database, a different journal,
tampered anchors, wrong signer, unverified concurrent movement, wrong escrow
recipient, package replay, wrong journal key, and a recovered key opening the
original native runtime records.

## Adversarial review correction

The initial recovery implementation accepted signed checkpoint bytes as
parent context without independently validating their Ed25519 signature
during offline recovery. This has been corrected: the recovery call now
requires `trusted_checkpoint_public_key` and verifies it before opening
the operator-signed recovery envelope. A regression constructs a
*cryptographically valid* operator recovery envelope referencing a forged
checkpoint and confirms refusal. See [security review and local
staging](REVIEW_AND_STAGING.md).
