# B12 — Existing B3 native return -> source-owned B11 delivery

## Current referent

B9 carries proposed, route-scoped requirements. B10 prepares an inert
source-edition-bound native continuation and reacts to a trusted LOCAL_PASS.
B11 accepts local results only with an externally pinned source key and
independent native-result verification.

B12 uses **an existing, executed B3 finite worker's source-owned persisted
return** as that local result. Its adapter reads and independently rechecks
the original job, opening and lane, then B11 admits and appends a signed
LOCAL_PASS to the B10 journal.

There is no new engine, simulated return, worker registration, daemon or
unattended ChatGPT action in the B12 implementation.

## Native source boundary

`B3NativeLocalSource(data_dir, lane_handoff_id, opening_id, job_id)`
requires exact prior native assignments, a `WORKSTATION_NATIVE_RESULT_VERIFIED`
record on the original B2 lane, and the admitted finite worker edition.

Every `inspect()` uses native `branch_help.verify_return`, which delegates to
current workstation job view and `controls.reverify_job`. It then reopens
the source runtime and checks that the job is still COMPLETE, the exact
edition remains registered, the native B3 return has not changed, and the
output/evidence SHA-256 digests agree with persisted job state.

B12's source adapter's `execute` method is **read-only re-observation**.
It must not launch the finite worker a second time. Its independent observer
reopens native source state yet again. Source changes, invalid assignments,
contradictory or missing return events and stale native editions are rejected.

The B3 return concerns **one finite computation**. It does not establish
external owner identity, an independently witnessed parent CP or a complete
B9 route. The original B3 test harness uses a synthetic starting B2 branch
observation; B12's CI does not erase that provenance boundary.

## Trust and delivery boundary

`B12B3LocalDelivery` requires all of:

- The exact source-owned B3 job, an existing completed native return, and an
  explicit matching `confirm_source_job` on initialization.
- An **externally provisioned** pinned Ed25519 public key and source-owned
  `sign_native_proof(bytes)->bytes` callback. No private key is generated,
  read, or stored by this module.
- A B9 candidate whose requirement is
  `source-owned native finite return reverified`, and an explicit source
  suggestion for the actual job's source edition and locator.
- Explicit `allow_native_local_delivery=True` and a `confirm_request`
  matching the exact prepared B10 request.

`prepare()` only creates the inert B10 handoff. `deliver()` freshly rechecks
native B3 evidence, constructs the exact-handoff `NativeLocalProof`, asks the
source-owner callback to sign canonical B11 bytes, and then lets the original
B11 admission independently recheck the current native source before the
original event journal attempts its read-only native adapter.

Neither a B9 source suggestion nor a public key implies source-owner trust.
The host controls key pin enrollment, source-owner signing, and when an
already executed source result is eligible to be delivered. Without these,
the library cannot authenticate or emit a production event.

## Minimal invocation in a source-owning host

```python
source = B3NativeLocalSource(
    data_dir=existing_workstation_data_dir,
    lane_handoff_id=original_b2_lane,
    opening_id=actual_cp_help_opening,
    job_id=already_completed_native_b3_job,
)
service = B12B3LocalDelivery(
    construction=existing_b9_construction,
    observed_journal_path=separate_observed_journal,
    source=source,
    pinned_public_key=trusted_public_key_from_source_owner,
    sign_native_proof=trusted_source_owner_sign_callback,
    confirm_source_job=already_completed_native_b3_job,
)
request = service.prepare(
    goal_id, candidate_id, route=complete_B9_candidate_route,
)
service.deliver(request, confirm_request=request, allow_native_local_delivery=True)
```

The B3 job must already have been admitted, confirmed and executed by its
source-owning controls. B12 will never execute it itself.

## Verification and remaining walls

`workstation-b12-b3-native-delivery` GitHub CI requires 16 native B12 cases,
including actual B3 subprocess creation, live source re-verification, source
edition mutation and revocation, invalid jobs/openings, exact request gating,
wrong source-owner key, duplicate delivery, stale B9 routes and forged PASS.
It also runs the existing B11/B10 native integration suites and the complete
original 73-test B9 construction suite without skips.

The remaining external conditions are intentionally not fabricated: actual
trusted operator key provisioning, signer availability and source-owner
authorization; concurrent-writer safety; external event delivery/scheduling;
and independent cross-route/owner admission. B12 is a source-native callable
path—not an unattended deployed agent or cryptographic identity registry.
