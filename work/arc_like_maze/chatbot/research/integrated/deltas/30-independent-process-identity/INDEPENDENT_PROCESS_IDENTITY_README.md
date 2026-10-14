# Stage 30 — Independent-process source attestation (October 13, 2026)

**Question.** Can a receiver check signed owner-scope identity evidence in an entirely separate process, with its own pinned verification keys, **before** using a CP-29 historical route receipt? Can it still withhold any task proof that is stale, forged, source-substituted or absent from the selected route?

## Observed bounded result

Yes, with **pre-enrolled ephemeral Ed25519 fixture keys** for the donor, middle, and final source scopes. The sender first issues the CP-29 route receipt after its two-pass owner-backed route audit, then a distinct signer process creates three challenge-bound signatures on exact scoped source digests, the selected route fingerprint, and the route witness digest. The receiver passes the signed bundle and its **previously pinned** public-key trust map to a separate verifier process. A valid signature alone is not enough: after verification, the original CP-29 receiver independently performs another complete two-pass owner-backed audit, checks the historic receipt's source/witness digest, and evaluates each task separately.

A valid two-task left-route handoff completes both tasks after just **two receiver route replay calls**. A third independent task requiring a right-only edge remains `ROUTE_TASK_REQUIREMENTS_UNPROVED`. This adds **zero** source observations. The signer process, verifier process, and parent caller have distinct process IDs in the executed tests. The independently executed verification is an actual subprocess call, not a simulated Python function call.

| Case | Observed outcome |
| --- | --- |
| Pre-trusted signer keys, exact source, fresh challenge | Three verified scope attestations; CP-29 fresh two-pass revalidation; two separately satisfied tasks |
| Third task asks for a right-only edge | Third task unproved; other tasks not promoted or merged |
| Wrong key for any scope or edited signature | `ATTESTATION_SIGNATURE_UNPROVED`; no route replay |
| Wrong challenge, route, witness or source digest | Claim mismatch or invalid request; no task proof |
| Selected source pin revoked or source revision changed | Historical bundle cannot authorize task |
| Source changes during receiver's own audit | `INDEPENDENT_PROCESS_SOURCE_MOVED` |
| Reuse of old signed bundle with unchanged challenge | Still requires two *new* CP-29 route replay calls; does not cache proof |
| Use old bundle with a *new* receiver challenge | Rejected; caller must request fresh attestation for the new challenge |
| Unrelated route pin revoked | Does not invalidate unchanged selected-left route |

## Trust and security boundary

- This is a **controlled synthetic in-process owner fixture** with cryptographic signing and signature verification performed across operating-system process boundaries. **It is not proof of externally governed identity**. Public-key enrollment, delegation, independent authority checks, private-key custody, revocation lists, remote network transport, clock-based expiry and deployed-process isolation are unimplemented.
- The trusted public keys enter the verifier from the receiver's separately supplied trust map, **never from the signed bundle**. The test harness provisions ephemeral private keys to the signer subprocess over its input pipe. That synthetic provisioning is deliberately **not** claimed as secure production key management.
- Signatures prove control of a pinned private key and bind the three source claims, witness, route and receiver-issued 192-bit nonce. They do **not** establish that a signer was authorized to represent a real-world owner. A malicious provisioner controlling both signing keys and the trust map can manufacture passing test attestations.
- The receiver must generate a **new challenge for each new assurance request**. The code checks a supplied expected challenge but does not maintain a persistent challenge-use ledger. An unchanged challenge and old bundle will still require a new owner-backed audit; no historical signature becomes automatic current proof.
- A receipt, source hash, ZIP checksum, or signed attestation **alone** never authorizes an edge or goal. CP-29's fresh selected-route audit and independent task-obligation checks are mandatory. No automatic polling or universal result about language is claimed.
- The complete Stage-20 owner-backed dependency baseline still lives in the integrated ZIP and is not fully runnable from a clean GitHub checkout. The GitHub finite verifier/tests are independent of that runtime, with an explicit dependency on the standard `cryptography` package (`>=45,<47`, tested locally with 46.0.4).

## Reproduction and evidence

From the extracted complete Stage-30 archive, with Python 3.11+ and `cryptography` installed:

```sh
python run_independent_process_identity_demo.py
python -m unittest -q test_ab_chatbot_independent_process_identity.IndependentProcessIdentityTests
python -m unittest -q test_finite_process_attestation.ProcessAttestationTests
python -m unittest -q test_ab_chatbot_certificate_handoff.HandoffOwnerTests
python -m unittest -q test_finite_certificate_handoff.FiniteHandoffTests
python -m unittest -q test_ab_chatbot_shared_route_certificates.SharedRouteTaskTests
python -m unittest -q test_finite_shared_route_certificate.SharedFiniteTests
python -m unittest -q test_finite_multi_task_dependency.FiniteMultiTaskDependencyTests
```

**100/100 completed targeted tests**, accounted across independently completed test suites: 16 new owner-backed + 17 new independent-process finite + 16 CP-29 owner-backed + 16 CP-29 finite + 13 CP-28 owner-backed + 14 CP-28 finite + 8 CP-27 finite. The broader all-in-one historical run stalled and was **excluded**. The full historical suite was not completed and is not claimed. See `INDEPENDENT_PROCESS_IDENTITY_REGRESSION.json` for command-level evidence.

## Eight new files and preservation

- `ab_chatbot_independent_process_identity.py` — new owner-backed, process-separated verification adaptor.
- `test_ab_chatbot_independent_process_identity.py` — live source and negative controls.
- `finite_process_attestation.py` — separately executable cryptographic signer/verifier protocol.
- `test_finite_process_attestation.py` — 17 independent finite cryptographic and subprocess tests.
- `run_independent_process_identity_demo.py` — reproducible owner-backed scenario.
- `INDEPENDENT_PROCESS_IDENTITY_RESULTS.json` — exact demonstration outputs.
- `INDEPENDENT_PROCESS_IDENTITY_REGRESSION.json` — suite accounting and boundaries.
- `INDEPENDENT_PROCESS_IDENTITY_README.md` — this scoped report.

The integrated CP-30 ZIP contains **281 entries**. The 273 CP-29 entries are preserved **byte-for-byte**. The checksum identifies the complete archive but does not authenticate a person or external source.

**Next supported movement:** an explicit, independently governed key-enrollment and rotation record, with challenge-use accounting across processes. Withhold authority where the trust anchor or key-rotation history is not established.
