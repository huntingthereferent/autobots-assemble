# Continuous Handoff — read-only reference

This folder demonstrates **backward traversal of declared candidate automation paths**, with observational determination kept separate from construction.

Start with the [contract](../../../language/handoff/CONTINUOUS_HANDOFF.md). This demo is not a new scheduler, native verifier, or replacement for the [existing handoff runtime](../../README.md).

## Run

From this folder:

~~~sh
python reference.py example.json
python reference.py example.json --toy-fixture
python -m unittest -v test_reference.py
~~~

The default output leaves unverified claims UNKNOWN and alternative paths PROPOSED. The optional toy fixture trusts **only hard-coded synthetic receipts** so the example can show how observational verification changes the per-edge verdict. It does not validate real-world evidence. The code intentionally does not execute jobs, edit files, or certify composed routes.

Files: [reference.py](reference.py) (read-only traversal), [example.json](example.json) (two declared paths), [sidecar.schema.json](sidecar.schema.json) (separate sidecar wire shape), [test_reference.py](test_reference.py) (12 focused unit tests).

When wiring a real system, reuse existing native admission and evidence requirements. Implement domain-native verifiers, current source-edition checks, and separately authenticated joins before claiming supported operational results.
