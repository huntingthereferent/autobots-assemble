# CP30 external/native authority delegation — operator-anchored and local

**Status: locally staged.** This is a new cryptographic **authority-delegation check** layered on the previously staged CP30 source-signature, GitHub observation, continuity, native-local owner, and cached-edge matching adapters. It is not a change to the historical CP20–CP30 source, and does not deploy or authenticate any real-world owner.

## The exact question

Previously, externally signed and observed GitHub declarations could be shown to match *some already cached* old/new transitions of a live, locally pinned CP30 route. That supported **content matching**, not a claim that the signer had authority over the native objects. This layer makes one more relation independently **checkable relative to a separately pinned public key**:

> Did the operator-pinned authority key explicitly delegate the *same six native snapshot identities and digests*, with the same externally observed files, source-signer keys, receiver challenge, route fingerprint, and native evidence fingerprint, during a bounded freshness window?

A positive answer means a signature from that configured authority key passed verification. It is **not** proof that the initial key enrollment was rightful, that the signer is legally authorized, or that external signers are the native object's real-world owners. Someone must separately establish and protect that trust anchor **out of band**.

## Distinct trust and evidence layers

1. The receiver explicitly pins a *separate* Ed25519 authority public key using `AuthorityAnchorLedger.pin()`, with an operator, a independently checked full SHA-256 fingerprint, and a human-readable external verification reference. It is an append-only local, hash-chained **policy record**. Do not enroll the source's own signer key as the authority key.
2. The three source signers' public keys have already been enrolled separately, a receiver-issued challenge has been signed, and the signed GitHub file declarations have been byte-verified and recorded in the existing `SourceEvidenceLedger`.
3. The **source-owning process** supplies live `RouteBoundTask` objects to `source_capture()` and the originally imported native CP30 owner/pin modules. The already staged binder matches the six claimed old/new transition sets against **cached** native observations; it does not call a transition oracle.
4. `prepare_authority_binding()` produces an **unsigned** statement naming the exact challenge, observation event, source signer fingerprints, source-file SHA-256s, native route/evidence fingerprint, six native snapshot content digests and labels/revisions, and a deliberately **process-local identity digest**. This last digest only binds handles in the current Python process; it is *not* a portable snapshot owner identity.
5. An external holder of the **authority private key** signs the exact statement as canonical JSON (`systems.workspace.external_evidence._canonical`), without sending private key bytes into this workstation. This module does not create or hold authority private keys.
6. `verify_authority_binding()` independently rechecks the pinned root, signature, freshness (30–300 second validity), signed GitHub content, registered source keys, cached native-edge matches, exact source-owned object identity, and any journal changes. Source or authority key rotation/revocation, a replaced task object, modified evidence, or a restarted process rejects the old grant.

### Minimal Python interface

Run this code only **inside the already trusted source-owning process** after it has imported reviewed CP30 native modules from `CP30_DIR`:

```python
from systems.workspace.external_authority_binding import (
    AuthorityAnchorLedger, prepare_authority_binding, verify_authority_binding
)

anchor = AuthorityAnchorLedger(PRIVATE_DATA_DIR)
anchor.pin(
    authority_id="authority-name",
    public_key=AUTHORITY_PUBLIC_KEY_BASE64,
    confirm_fingerprint=OUT_OF_BAND_CHECKED_SHA256,
    operator="receiver-operator",
    verification_reference="independently checked authority statement/reference",
)

common = dict(
    data_dir=PRIVATE_DATA_DIR,
    challenge=ACCEPTED_RECEIVER_CHALLENGE,
    observation_event=EXACT_GITHUB_OBSERVATION_HASH,
    source_files={"donor": DONOR_COPY, "middle": MIDDLE_COPY, "final": FINAL_COPY},
    native_source_root=CP30_DIR,
    source_capture=SOURCE_OWNED_LIVE_TASK_CALLBACK,
    authority_id="authority-name",
    authority_public_key=AUTHORITY_PUBLIC_KEY_BASE64,
    anchor_fingerprint=OUT_OF_BAND_CHECKED_SHA256,
)

unsigned = prepare_authority_binding(**common)
# Have the independently authorized key holder review and sign the EXACT
# canonical JSON bytes of `unsigned` outside this process. Never transfer a
# private key to this adapter.
verified = verify_authority_binding(
    **common,
    signed_grant={"statement": unsigned, "signature": AUTHORITY_SIGNATURE_BASE64},
)
```

Do not call `pin()` again on every run. Existing active anchors cannot be overwritten; revoke with the original exact fingerprint and intentionally pin a new key. Old signed grants are not silently upgraded to the new key. `verification_reference` is *operator-recorded context*, not machine-proven authority.

## Bounded positive statement

The only positive status is `OPERATOR_ANCHORED_SNAPSHOT_DELEGATION_VERIFIED` and it remains scoped to the **same already cached six snapshot sides in the current process**, checked against previously accepted file bytes and a live local pin set. The result deliberately includes:

- `out_of_band_trust_anchor_authenticated_by_module: false`
- `real_world_external_owner_authenticated: false`, `legal_ownership_proved: false`
- `cp30_independent_process_attestation_verified: false`
- `fresh_native_route_audit: false`, `cp29_receipt_revalidated: false`
- `exact_task_authorized: false`, `native_handoff_admitted: false`
- `new_transitions_observed: false`, `journal_modified: false`

Neither this policy ledger nor the earlier source evidence log is independently anchored against a malicious local filesystem writer; each is *single-writer*. The authority's legal/organizational standing, external owner control, GitHub account ownership, and actual out-of-band approval cannot be established by signatures alone. If a process restarts, generate a new native-local signed statement after re-observation; a prior process's Python object identity cannot transfer.

## Reproduce with fixtures

The tests use generated fixture Ed25519 keys, a source-owning CP30 **synthetic** route fixture, and mocked GitHub responses; no real external owner, offline authority, or external API was verified:

```sh
python work/arc_like_maze/chatbot/research/integrated/assemble.py --stage 30 --out /tmp/cp30-native
CP30_NATIVE_SOURCE_DIR=/tmp/cp30-native python -m unittest -v \
  network.tests.test_external_evidence \
  network.tests.test_github_observation \
  network.tests.test_external_route_mapping \
  network.tests.test_external_source_continuity \
  network.tests.test_native_owner_observation \
  network.tests.test_external_native_binding \
  network.tests.test_external_authority_binding
```

Tests include forged signatures, wrong authority, mismatched native digests, stale/future grants, source and authority key revocation/rotation, wrong observation, changed live task objects, process restarts, journal tampering, and no new transition acquisition. Do not promote fixture results to live owner authority or production CP30 capability.

## Separate public witness publication (staged next layer)

The new [independent publication contract](INDEPENDENT_AUTHORITY_SOURCE.md)
observes a separately enrolled and signed GitHub witness statement covering
the exact short-lived authority grant. The additional signature and public
repository/account checks do **not** establish organizational independence,
legal authority, CP30 native route proof, or real-world owner authentication.
