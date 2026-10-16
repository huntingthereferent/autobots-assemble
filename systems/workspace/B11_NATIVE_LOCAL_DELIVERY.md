# B11 — Native local-result admission and delivery

## Referent

B9 can construct a possible route. B10 can prepare an inert, route-scoped,
source-edition-bound handoff and react to a genuinely verified `LOCAL_PASS`.
B11 provides one explicit route by which a source-owned *local result* can be
delivered to that journal without turning B9 proposals into evidence.

It is not enough to copy a PASS label, claim an actor name, present a source
hint, or show an old signed result. Native evidence must still exist when the
journal admits the event.

## Boundary and implementation

`SourceOwnedLocalDelivery` constructs the existing
`ObservedEventJournal` with B10's construction-aware
`scoped_local_verifier` plus a new `SourceOwnedAdmission` gate.

The gate checks **all** of the following before a LOCAL_PASS can trigger
continuation:

1. An exact B10 handoff, including its candidate specification digest,
   required relation, and source locator. The full currently constructed
   B9 route must still be valid. Route completion remains false.
2. A source name and **edition** matching the authorized B10 adapter.
   The signed source-edition identity is bound to an externally configured
   Ed25519 public key, not a key supplied by the result.
3. A source signature over canonical `protocol + receipt` bytes including
   the **specific B10 handoff ID**, relation, exact candidate spec, source
   edition, source locator, native result reference and digest.
4. A mandatory independent callback `verify_native_current(proof)` which
   MUST inspect the native owner's currently available result/receipt and
   compare the exact reference, source edition, and content digest. A valid
   signature alone is not freshness or current source approval.

The signed proof and signature are stored with the local event so interrupted
events can be independently rechecked after restart. A duplicate identical
delivery has a deterministic identity; it does not replay completed native
execution. The existing journal writes ATTEMPT_STARTED before the external
adapter executes. An interrupted external effect remains RECOVERY_REQUIRED,
and B11 never retries it automatically.

B11 does not sign anything, mint a source identity, invent a receipt, choose
the operator's trust anchors, or run independently in the background. Private
keys remain with the native source owner. Source owners must provision public
key pins through a trusted channel and implement the native-current verifier.
The CI test key is an **ephemeral fixture**, not a production source owner.

## Invocation

```python
# Native source owner provisions the PUBLIC key and genuine native adapter.
delivery = SourceOwnedLocalDelivery(
    construction=graph,
    journal_path=observed_journal_path,
    adapters=(authorized_native_source_adapter,),
    pinned_public_keys={(source_name, source_edition): pinned_ed25519_public_bytes},
    verify_native_current=source_owner_recheck,
)
request = delivery.bridge.prepare(
    goal_id, candidate_id, route=exact_candidate_route,
    worker_id=source_name, edition_ref=source_edition,
    source_locator=source_locator,
)

# The native owner independently establishes a fresh local result and signs
# canonical_proof_bytes(proof) using its own, external private key.
# Only then:
delivery.deliver(proof, signature_hex=source_owner_signature_hex)
```

`deliver` validates before persistence; journal recovery validates again.
The B10 continuation adapter independently verifies the result of its own
subsequent native attempt. Local admission does **not** verify a complete route,
cross-lane join, source capability, job approval, external owner identity
beyond the configured key pin, or production deployment.

## Tested

`workstation-b11-native-local-delivery` GitHub CI requires 19 B11 cases,
including invalid signatures, revoked source state, stale B9 route,
source-edition mismatch, durable idempotence and crash recovery, plus an
actual existing B3 subprocess whose completed return is independently
rechecked before source-owned local delivery.

The suite also runs the B10 event journal and native B3 regression tests and
all 73 B9 construction tests. No skip is accepted. All green is a source
and integration verification boundary; it does not mean the system is
unattended, production authenticated, or live outside that controlled source.

## Remaining boundaries

- Source owner trust provisioning, revocation, and receipt storage are
  external operational responsibilities.
- There is no multi-writer lock or cross-journal transaction across the
  original B9 and observed journals.
- An externally authorized host must decide *when* a native source emits a
  signed local result and invokes `deliver`; B11 is not a scheduler.
- Current native source verification and B2/B3/B7/B8 admission remain
  source-owned, never inferred from construction or from a signature alone.
