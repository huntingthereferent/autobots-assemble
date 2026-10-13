# 30 — Independent-process identity verification

Three pre-trusted synthetic source keys sign challenge-bound source evidence. A separate process verifies all signatures before the existing owner-backed receiver replays its selected route and independently checks its tasks. This is not external identity enrollment.

[Scoped record](record.md) · [Research overview](../../README.md) · [Checkpoint index](../README.md)

| Material | File |
| --- | --- |
| Integrated adapter | [`ab_chatbot_independent_process_identity.py`](ab_chatbot_independent_process_identity.py) |
| Owner-backed tests | [`test_ab_chatbot_independent_process_identity.py`](test_ab_chatbot_independent_process_identity.py) |
| Independent signed-scope verifier | [`finite_process_attestation.py`](finite_process_attestation.py) |
| Independent tests | [`test_finite_process_attestation.py`](test_finite_process_attestation.py) |
| Demo | [`run_independent_process_identity_demo.py`](run_independent_process_identity_demo.py) |
| Results | [`INDEPENDENT_PROCESS_IDENTITY_RESULTS.json`](INDEPENDENT_PROCESS_IDENTITY_RESULTS.json) |
| Test accounting | [`INDEPENDENT_PROCESS_IDENTITY_REGRESSION.json`](INDEPENDENT_PROCESS_IDENTITY_REGRESSION.json) |

The GitHub finite-reference tests require `cryptography>=45,<47`. The owner-backed integrated tests still require the CP-20 baseline preserved in the separately archived complete ZIP.
