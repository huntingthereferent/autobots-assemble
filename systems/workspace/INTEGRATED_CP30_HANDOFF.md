# Integrated CP30 — bounded signed-scope verification worker

The Process Workstation can now **execute the recovered 281-file CP30 edition** for precisely one historical operation: running its own `finite_process_attestation.py verify` command in a local child process. The result enters the existing `HandoffRuntime` only if a **separate host-owned Ed25519 verifier** computes the same verdict for all signed route-source scopes.

This is not CP30's complete owner-backed route audit. Public keys are supplied with the explicitly declared job; there is no real-world owner enrollment, external identity verification, or route witness refresh. A positive signature verdict only says that the supplied claims were signed by keys corresponding to the supplied public keys, under the supplied challenge and expectations.

## Execute a self-contained synthetic demonstration

From the repository root, with Python 3.12+ and `cryptography>=45,<47`:

```sh
python -m runtime.examples.integrated_cp30_attestation --data-dir runtime/data --execute
python -m systems.workspace.view_server --data-dir runtime/data --port 8051
```

Open `http://127.0.0.1:8051/workstation.html`. The demo reconstructs and copies the exact archived CP30 source under `finite-correspondence-integrated/recovered-cp30-001`, issues a **synthetic** challenge/signature fixture using ephemeral private keys, admits one job, executes the source in a child process, and requires independent native replay before persisting `COMPLETE`. The original research archive remains unchanged. Only public keys, signatures and declared expectations enter the handoff journal. Re-running the command re-verifies the existing result rather than re-signing or re-executing it.

`--execute` is an explicit opt-in to run selected local Python source; `-I` does **not** sandbox a compromised or malicious source copy.

## Use your own supplied signature bundle

First copy a reviewed CP30 edition with `python -m systems.workspace.integrated_source --data-dir runtime/data --stage 30 --version recovered-cp30-001 --copy` if not already copied. Save a JSON file at `runtime/data/cp30-attestation-input.json` with exactly three top-level keys: `bundle`, `trust`, `expect`. `bundle` contains the signed claims and Ed25519 signatures in the original CP30 format; `trust` contains the three **preselected** base64 Ed25519 public keys keyed by `donor`, `middle`, `final`; `expect` contains `challenge`, `route`, `fingerprint`, `witness`, `source_digests`. **Do not put private signing keys into the JSON.** This adapter has no signing command.

```sh
python -m systems.workspace.controls --data-dir runtime/data prepare --worker finite-correspondence-integrated --version recovered-cp30-001 --inputs-file runtime/data/cp30-attestation-input.json
python -m systems.workspace.controls --data-dir runtime/data admit-integrated --version recovered-cp30-001 --inputs-file runtime/data/cp30-attestation-input.json --job-id cp30-check-002 --confirm-admit cp30-check-002 --from-actor local-operator
python -m systems.workspace.controls --data-dir runtime/data execute --job-id cp30-check-002 --confirm-execute cp30-check-002
python -m systems.workspace.controls --data-dir runtime/data reverify --job-id cp30-check-002
```

Admission and execution are **separate**. The read-only GUI can prepare command text but cannot admit or run work. The original `Finite Correspondence Process` prefilter and Factory simulation are unchanged; this third worker has its own `worker_id` and native evidence verifier.

## Exact evidence boundaries

- CP30 source must be a source-pinned reconstructed edition with its 281-file baseline and `#CP-30` provenance. Missing files, an altered edition after admission or a false child verdict fail closed. Modified branches may be separately admitted and checked for **this** operation, not granted historical CP evidence automatically.
- The independently replayed result describes the bounded cryptographic computation. `ATTESTATIONS_VERIFIED` is **not** proof that any named human or independent organization owns the source. A negative signature verdict can also be a completed verification *job*.
- An actual CP30 owner-backed task would also need to audit fresh pinned route evidence and exact required edges for each declared task, with a separate native adapter and verifier. No such broader claim is made here.
- A child exception after a recorded `STARTED` may leave the handoff `ACTIVE`; automatic retries are deliberately absent.
- Full historical owner-backed tests are still not certified as one passing suite.

Reproduce the targeted integration tests:

```sh
python -m unittest -v network.tests.test_integrated_cp30_handoff
```
