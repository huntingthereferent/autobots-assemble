# CP30 — source-origin authorization publication (staged)

**Status:** locally staged; tested against synthetic native CP30 owners and mocked public GitHub responses. The original CP20–CP30 research source and workstation runtime are untouched. No genuine source operator or outside witness has been enrolled or contacted.

## Precise question

The earlier [independent witness publication](INDEPENDENT_AUTHORITY_SOURCE.md) asks whether a *separately enrolled witness key* published a matching statement. That does not establish whether the **source** authorized the review.

This module asks a narrower additional question: **did all three presently enrolled source keys countersign the exact grant and witness publication, and did the specified source GitHub repositories publish those signed statements while preserving the observed source files?**

This is checkable technical corroboration of a signed source-side statement and a public repository publication. It is not evidence of legal ownership, control of a human account, proof that the signer is the repository administrator, or proof that the parties are genuinely independent. Real-world authority still requires an externally confirmed source-owner relationship.

## Receiver-enrolled repository identity

Before any network read, the receiver pins each scope's exact existing source enrollment plus the public GitHub repository's immutable numeric repository ID and owner account ID, backed by a separately obtained human verification reference. Example (placeholder values, **not** live enrollment):

```python
from systems.workspace.source_origin_authority import SourceOriginPolicy

policy = SourceOriginPolicy(PRIVATE_DATA_DIR)
policy.pin(
    scope="donor",
    source_id=EXACT_ALREADY_ENROLLED_DONOR_ID,
    locator=EXACT_ALREADY_ENROLLED_GITHUB_FILE_URL,
    repo_id=OUT_OF_BAND_CONFIRMED_REPOSITORY_ID,
    owner_account_id=OUT_OF_BAND_CONFIRMED_OWNER_ACCOUNT_ID,
    key_sha256=EXACT_ALREADY_ENROLLED_SOURCE_KEY_SHA256,
    operator="receiver",
    verification_reference="independent operator review record",
)
```

Repeat for `middle` and `final`. The signed evidence ledger, authority-anchor ledger, witness ledger, and source-origin ledger have separate roles. All journals are local single-writer files with hash chains; they cannot protect against a fully malicious local filesystem writer. Revoking a source-origin pin blocks checks until separately reenrolled.

## Source-origin signed publication

Each source repository publishes one file at the **fixed path**:

- `.well-known/cp30/source-review-donor.json`
- `.well-known/cp30/source-review-middle.json`
- `.well-known/cp30/source-review-final.json`

Each file is a JSON object with exactly `statement` and `signature`. The source's already-enrolled Ed25519 key signs the canonical JSON statement. Its exact fields are:

```text
kind = cp30-source-origin-review-authorization/v1
scope, source_id, source_locator, source_key_sha256
source_repo_id, source_owner_account_id
source_observed_commit, source_observed_sha256
authority_grant_sha256, witness_id
witness_publication_commit, witness_publication_sha256
observation_event, native_evidence_sha256
authorization_scope = external-evidence-corroboration-only
issued_at, expires_at
```

The 30–300-second publication lifetime cannot exceed the original signed grant. The receiver verifies all three signature bytes against the **currently enrolled keys**, not arbitrary keys in the fetched documents. The fixed paths prevent a caller from substituting an unrelated authorization file.

## Explicit verification

```python
from systems.workspace.source_origin_authority import verify_source_origin_authorizations

result = verify_source_origin_authorizations(
    data_dir=PRIVATE_DATA_DIR,
    signed_grant=EXACT_CURRENT_SIGNED_AUTHORITY_GRANT,
    native_binding=EXACT_LIVE_NATIVE_CP30_BINDING_ARGS,
    witness_id=ALREADY_ENROLLED_INDEPENDENT_WITNESS_ID,
    confirm_grant_sha256=OUT_OF_BAND_REVIEWED_GRANT_SHA256,
    confirm_observation_event=EXACT_ACCEPTED_OBSERVATION_EVENT,
    allow_network=True,  # explicit, bounded GitHub public reads
)
```

The verifier first reruns the **existing** independent witness and live-native authority checks. It then checks each source repository's numeric IDs, current branch commit, GitHub-reported ancestry from the original observed commit, unchanged declared file bytes, fixed-path source authorization file and Git blob hash, and enrolled-source-key countersignature. It rechecks the branch heads, identities, and all relevant local journals before returning.

Successful status: `SOURCE_REPOSITORY_AUTHORIZATION_CORROBORATED`. The response includes public immutable-commit URLs for each authorization, file SHA-256, repository IDs, source key fingerprints, and a deterministic review-receipt SHA-256. The review receipt can be saved or independently inspected; it is **not** an externally anchored proof, nor does the verifier persist a new ledger event.

## Explicit nonclaims

The response **does not** assert real-world or legal owner identity, source controller independence, authority over an unrelated physical system, full equivalence of finite transition tables, CP30 native route-audit success, task eligibility, task completion, or native runtime handoff admission. It never acquires new native transitions or changes historical research. Public GitHub comparisons are trusted provider reports, not independent cryptographic Merkle proofs of ancestry. A separate operational deployment would need authentication of the actual source principals, durable policy anchoring, and a new source-owned contract before any wider use.

## Reproduce the checks

```sh
CP30_NATIVE_SOURCE_DIR=/tmp/cp30-native python -m unittest -v \
  network.tests.test_external_evidence \
  network.tests.test_github_observation \
  network.tests.test_external_route_mapping \
  network.tests.test_external_source_continuity \
  network.tests.test_native_owner_observation \
  network.tests.test_external_native_binding \
  network.tests.test_external_authority_binding \
  network.tests.test_independent_authority_source \
  network.tests.test_source_origin_authority
```

All network provider data used in unit tests is mocked and every key is synthetic. Run GitHub CI only after the staged files are intentionally committed; passing local tests alone is not GitHub CI verification.
