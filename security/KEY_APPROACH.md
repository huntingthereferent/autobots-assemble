# A/B bipolar approach at key use — bounded evidence

The request is **not** to rotate, rewrite, freeze or derive a novel cipher
from the key material. The existing A/B bipolar `BipolarBoundary` is placed
at the actual `AuthenticatedHandoffIngress` observation seam. A single
trusted native ingress owns its established signing/verifying and recipient
keys as before.

## Observed relationship

An incoming signed-envelope attempt is an **approach** and advances only
the bounded probe trajectory. Existing independent cryptographic
authentication, operator pin and native evidence checks determine whether
it is authorized. Only a *successfully persisted native SUBMISSION or
RESULT* advances the protected trajectory. Unauthorized/invalid/replayed
approaches do not move that trajectory.

```text
external approach
    ↳ bipolar probe movement recorded (no key bytes involved)
    ↳ operator pin, signature, bounded ancestry, native witness validation
         refused → no protected movement
         admitted + durable native commit → protected movement recorded
```

The observer is a small privileged in-process object holding only motion
orientation and counts. It never stores a key, passphrase, decrypted input,
signing secret, event body, or claimed user identity. It is not exposed by
any HTTP route. Existing X25519/Ed25519 key material and envelope algorithms
are left untouched. This is **not** a replacement for their authentication.

## What was actually tested

- Thousands of external approach movements cannot themselves advance
  the independently modeled protected trajectory.
- Interleaving external approaches with authorized movements does not
  change the model's protected orientation for the same authorized sequence.
- Hundreds of invalid signed-envelope attempts at the **real native
  ingress** preserve the protected trajectory; subsequent valid native work
  continues it.
- An invalid signature does not reach the existing HKDF/private-key
  derivation function.
- Unauthorized native actors and replayed envelopes are refused; no
  protected native commit is counted.
- Disposable test signing/recipient private keys are unchanged across
  attempted and admitted movements.
- Native encrypted journal records still reject plaintext recovery from
  raw database bytes in the tested examples.

These tests use the existing trusted handoff runtime, encrypted journal,
replay checks and genuine standard cryptographic keys. They do not
demonstrate a perpetual, autonomous native movement when no event is
occurring. The current observation is *event-driven*; any future tie to an
independent world-motion driver must be evidenced by real native movement.

## Bounds that cannot be skipped

This bipolar instrument does **not** prevent a passive observer from
watching a connection, measuring timing, or seeing unencrypted envelope
metadata. The current `seal_record` format exposes lane, event ID,
sender/recipient public-key fingerprints and ciphertext size. It
authenticates these fields, not encrypts them. Motion does not remove that
observation.

It also cannot protect against arbitrary direct Python access to
`recipient_private_key`, malware with process memory access, a compromised
trusted sender, stolen signing/decryption keys, a malicious callback, or
host-level rollback. Those are separate measurable boundaries.

**No conclusion of universal safety, no-leak security, or guaranteed
deterrence is drawn.** The demonstrated claim is narrower and checkable:
approaches submitted through the actual signed ingress cannot themselves
change the protected modeled movement, and bad signatures are denied
before private-key derivation. Existing cryptographic safeguards remain the
source of real access-control decisions.

No production key is touched; this work is on draft PR #262 only.
