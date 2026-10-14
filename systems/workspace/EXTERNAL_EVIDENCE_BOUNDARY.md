# External evidence — explicit enrollment and receiver challenges

**Status:** local opt-in trust boundary, not an external-owner implementation of CP30.
This stage is intentionally separate from the recovered `IntegratedRouteBridge`, which
still runs **synthetic owner/pin fixtures**. It does not alter any historical
CP20–CP30 byte or grant a new mathematical witness.

`external_evidence.py` accepts a three-scope **signed source-claim bundle** only
when an authorized local operator previously enrolled each scope's Ed25519
public key and a receiver-issued, short-lived random challenge binds all three
claims. Keys are supplied from outside the repository. No signing secrets are
stored in the ledger. External HTTPS locators are descriptive pinned metadata,
**not fetched** by this module.

## Admission sequence

1. An operator obtains and verifies each provider's **public key and ownership
   authority out of band**. Enroll an explicit key/locator for each `donor`,
   `middle`, `final` scope, confirming the full SHA-256 of its **raw 32-byte key**.
   Enrollment alone does not prove that the out-of-band check was valid.
2. Submit a declared route name (`left`/`right`), route fingerprint, witness
   fingerprint, and three source content digests. These are declarations;
   nothing here calculates them from a live owner registry.
3. The receiver issues and logs a fresh random **48-hex-character challenge**,
   pinning the currently enrolled key for each scope. It expires in 30–600
   seconds (default 300).
4. Each source key signs a canonical UTF-8 JSON claim covering its `scope`,
   `source_id`, challenge, route, route fingerprint, witness digest, source
   digest and claimed `observed_at` UTC timestamp. The receiver checks every
   signature against the previously pinned key and checks claim equality,
   challenge lifetime and timestamp window.
5. Explicitly accept the exact challenge once. A receipt records only the
   signed-bundle SHA-256, pinned keys, challenge and event hash. A replay,
   missing scope, wrong key, altered claim, revoked/rotated key or expired
   challenge fails before a receipt is appended.

Use from the repository root (Python 3.12+, `cryptography>=45,<47`):

```bash
python -m pip install 'cryptography>=45,<47'
python -m systems.workspace.external_evidence --data-dir runtime/data status
python -m systems.workspace.external_evidence --data-dir runtime/data enroll \
  --scope donor --source-id provider-donor --locator https://provider.example/donor \
  --public-key-file /private/donor-public-key.b64 \
  --confirm-key-sha256 <SHA256_OF_DECODED_RAW_PUBLIC_KEY> --operator local-operator
# Repeat deliberately for middle and final with their own public keys.
python -m systems.workspace.external_evidence --data-dir runtime/data challenge \
  --request-json /private/route-declaration.json
python -m systems.workspace.external_evidence --data-dir runtime/data accept \
  --challenge <ISSUED_CHALLENGE> --confirm-challenge <ISSUED_CHALLENGE> \
  --bundle-json /private/three-signed-claims.json
```

The route declaration JSON has **only** `route`, `route_fingerprint`,
`witness_sha256`, and `source_digests` (exactly `donor`, `middle`, `final`).
Digests are lowercase 64-character hex SHA-256. The three signed claims are
ordered donor/middle/final and have a `signature` containing canonical Base64
Ed25519 signature bytes. `claim.kind` is `external-source-observation/v1`;
`bundle.kind` is `external-source-bundle/v1`. See
`network/tests/test_external_evidence.py` for a synthetic **protocol-test**
example of the wire shape (test-generated keys are not external owners).

## What a receipt establishes

- A set of declarations was signed by possession of private keys corresponding
  to **locally enrolled** public keys, with the receiver's unpredictable
  challenge and claimed observation timestamp.
- A receipt was accepted once under those local trust settings.
- **It does not establish** that the claims are true, the provider names denote
  real-world owners, the signed content was independently observed, the remote
  source is currently reachable, or CP30's fresh route audit or exact tasks
  passed. A sender can sign a false timestamp or source digest.
- This package performs **no network requests**, owner enrollment ceremony,
  source digest retrieval, route audit, handoff admission, automatic execution,
  or filesystem modification on `status`.
- The hash-chained journal is not independently anchored and does not resist a
  malicious local administrator rewriting all records. It assumes an authorized
  **single writer**; concurrent writes require a separate lock/transaction
  facility. Store it privately and back it up securely.

Future work needs a **source-specific observation adapter**, pinned transport
and owner verification policy, measured source-state transitions, and a mapping
from the accepted evidence to CP30's native route/edge preconditions **before**
any `proof_for_use` or `COMPLETE` claim beyond the signed-claim check.

## Reproduce

```bash
python -m unittest -v network.tests.test_external_evidence
```

These tests use generated local keys solely as adversarial protocol fixtures.

## Subsequent public GitHub content observer

The [GitHub observation adapter](GITHUB_OBSERVATION.md) can deliberately fetch
public source bytes **after** the three-scope signed claim has been accepted.
It verifies exact Git blob content and SHA-256 against the signed claims, with
branch-head checks before and after retrieval. The result is a separate
`SOURCE_OBSERVED` receipt, not real-world ownership authentication, native
CP30 route proof, or task execution.

## Next read-only mapping boundary

[CP30 external-source declaration mapping](EXTERNAL_ROUTE_MAPPING.md) adds a
strict, hash-bound finite source-document schema with tests against the recovered
native CP29 owner/pin guards. Matching GitHub bytes and internally consistent
finite law declarations do **not** satisfy native owner bindings or authorize a
route task.
