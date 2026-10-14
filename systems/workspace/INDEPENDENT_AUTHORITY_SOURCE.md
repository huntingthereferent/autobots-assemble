# CP30 independent public authority witness — separate publication, bounded verification

**Status: locally staged; no external authority or real-world source is enrolled.**
This extends the staged source-signature, GitHub observation, source lineage,
native-owner capture, cached-edge binding and operator-anchored delegation
contracts. No historical CP20–CP30 file is modified.

## What it tests

A receiver has already checked an exact, time-limited operator-pinned
**authority delegation** over previously observed external file digests and six
native CP30 snapshot sides. This module asks one more narrow question:

> Does a **separately enrolled witness signing key**, associated by operator
> policy with a *different public GitHub account and repository*, publish a
> currently valid signature over that **exact original authority grant**?

The answer uses the public repository's identity and file contents as observed
through GitHub's HTTPS API. The checks include the repository's immutable
numeric ID, owner account's numeric ID, branch commit, file's Git blob hash,
Ed25519 signature, signed claim content, issuance and expiry, current
source-owner key enrollment, and a **new in-process native authority recheck**.

The witness's `review_method` and `review_reference` are **signed statements
by the witness**, not independently audited evidence that such a review
occurred. Separate GitHub account IDs do **not** prove different humans or
organizations control the accounts. GitHub is the publication provider, not
a government or legal authority for source ownership.

## Trust bootstrap remains external

A human/operator must first verify and pin the witness source's public-key
fingerprint, GitHub repository ID, and GitHub owner account ID independently:

```python
from systems.workspace.independent_authority_source import IndependentWitnessLedger

IndependentWitnessLedger(PRIVATE_DATA_DIR).pin(
    witness_id="review-witness-001",
    owner="EXTERNAL-REVIEW-ACCOUNT",
    repo="published-attestations",
    branch="main",
    path="statements/cp30-authority.json",
    repo_id=CONFIRMED_IMMUTABLE_REPO_ID,
    owner_account_id=CONFIRMED_GITHUB_ACCOUNT_ID,
    public_key=WITNESS_PUBLIC_ED25519_B64,
    confirm_fingerprint=OUT_OF_BAND_VERIFIED_SHA256,
    operator="receiver-operator",
    verification_reference="independent external verification record or case ID",
)
```

The pin is recorded in a local append-only, hash-chained **policy journal**.
It is not tamper-resistant against an attacker who can rewrite all local
files. The witness private signing key remains outside the receiver system.
The authority delegation key, witness key, and all three source keys must be
distinct. A revoked witness must be explicitly re-enrolled before use.

## Published signed statement

The separate witness publishes a UTF-8 JSON file in its own public repository:

```json
{
  "statement": {
    "kind": "cp30-independent-authority-publication/v1",
    "witness_id": "review-witness-001",
    "authority_id": "pinned-authority",
    "authority_key_sha256": "<64 lowercase hex>",
    "grant_sha256": "<SHA-256 of the canonical complete signed authority grant>",
    "observation_event": "<64 lowercase hex>",
    "native_evidence_sha256": "<64 lowercase hex>",
    "native_process_identity_sha256": "<64 lowercase hex>",
    "review_method": "independent-document-review",
    "review_reference": "external case ID or independently inspectable proof pointer",
    "issued_at": "<timezone-aware ISO 8601>",
    "expires_at": "<timezone-aware ISO 8601>"
  },
  "signature": "<base64 Ed25519 signature over canonical statement JSON>"
}
```

The statement must match the previous signed grant **byte-for-byte at its
canonical digest**, and every individually listed identity and native-evidence
field must match too. `review_method` is one of
`independent-document-review` or `out-of-band-owner-contact`; accepting either
verifies the witness *claimed* this method, not that it was performed.
The published witness statement is valid for 30–300 seconds and cannot
outlive the existing authority grant.

## Explicit live verification

Only call this in the trusted source-owning CP30 process, with real local
source-capture objects. The module's `native_binding` values are passed to
the existing **native verifier**, not an arbitrary callback returning a
caller-controlled verdict:

```python
from hashlib import sha256
from systems.workspace.external_evidence import _canonical
from systems.workspace.independent_authority_source import verify_published_authority

native_binding = {
    "challenge": ACCEPTED_RECEIVER_CHALLENGE,
    "observation_event": OBSERVATION_EVENT_HASH,
    "source_files": {"donor": DONOR_FILE, "middle": MIDDLE_FILE, "final": FINAL_FILE},
    "native_source_root": CP30_SOURCE_DIR,
    "source_capture": SOURCE_OWNED_LIVE_TASK_CAPTURE,
    "authority_id": PINNED_AUTHORITY_ID,
    "authority_public_key": AUTHORITY_PUBLIC_ED25519_B64,
    "anchor_fingerprint": AUTHORITY_OUT_OF_BAND_SHA256,
}

result = verify_published_authority(
    data_dir=PRIVATE_DATA_DIR,
    witness_id="review-witness-001",
    signed_grant=EXACT_AUTHORITY_SIGNED_GRANT,
    native_binding=native_binding,
    confirm_grant_sha256=sha256(_canonical(EXACT_AUTHORITY_SIGNED_GRANT)).hexdigest(),
    allow_network=True,  # deliberate public GitHub API read
)
```

After the fetched witness statement's signature is validated, the adapter
calls `verify_authority_binding()` again with the original signed authority
grant and live CP30 objects. It rereads repository identities, branch head,
and source, authority and witness journals, refusing changes. This is a
single-writer design, **not** an atomic distributed transaction.

## Exact verdict and limitations

`SEPARATE_GITHUB_WITNESS_PUBLICATION_VERIFIED` means that an operator-pinned
second signing key published matching, unexpired claims at an observed GitHub
commit while the native authority check still succeeded. The result includes
its repo/account numeric IDs, commit SHA, public file SHA-256, and exact grant
SHA-256. It also explicitly reports:

- `independent_organization_authenticated: false`
- `legal_ownership_proved: false`
- `real_world_identity_proved: false`
- `cp30_fresh_route_audit: false`
- `exact_cp30_task_authorized: false`
- `native_handoff_admitted: false`
- `journal_modified: false`

No CP30 native transitions are acquired; no job is admitted or executed.
No new cryptographic trust root authenticates itself. **Actual authority
requires an independently established relationship to the claimed controller**,
not merely another account or signed document. No live external GitHub API
call or external source authority check was performed during tests.

## Reproduce locally (mock GitHub provider, synthetic native owners)

Reconstruct the historical CP30 source and, from the repository root with
this staged implementation on the Python path, run:

```sh
python work/arc_like_maze/chatbot/research/integrated/assemble.py --stage 30 --out /tmp/cp30-native
CP30_NATIVE_SOURCE_DIR=/tmp/cp30-native python -m unittest -v \
  network.tests.test_external_evidence \
  network.tests.test_github_observation \
  network.tests.test_external_route_mapping \
  network.tests.test_external_source_continuity \
  network.tests.test_native_owner_observation \
  network.tests.test_external_native_binding \
  network.tests.test_external_authority_binding \
  network.tests.test_independent_authority_source
```

Tests use synthetic Ed25519 private keys, synthetic CP30 owner objects, mocked
GitHub HTTP responses, and temporary private journals. They validate the
**contract**, not the legal authority of any outside organization.
