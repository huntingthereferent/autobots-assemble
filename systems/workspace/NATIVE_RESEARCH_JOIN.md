# Exact native result ↔ research MOVE source boundary

The native [private receipt probe](NATIVE_RECEIPT_PROJECTION.md) records one job and its RESULT event. The public [research index](research_observatory.py) indexes source-owned `MOVE` and `MOVE_WITH_WALL` records. These were **separate** sources; a coincidence of names, files, workflow jobs, or dates never justifies joining them.

`native_research_join.py` performs a strictly bounded **read-only local comparison**. A supported structured MOVE source in `state/pins/<name>.json` or `research/dives/<id>/dive.json` must be unchanged from an explicitly named Git commit, and it must itself contain the following declaration:

```json
{
  "native_workstation_receipt": {
    "schema": "research-native-receipt-relation/v1",
    "job_id": "EXACT_EXISTING_JOB_ID",
    "result_event_id": "EXACT_EXISTING_RESULT_EVENT_ID",
    "worker_id": "EXACT_WORKER_ID",
    "worker_version": "EXACT_EDITION_ID",
    "native_verifier_id": "EXACT_NATIVE_VERIFIER_ID",
    "source_fingerprint": "EXACT_64_CHARACTER_NATIVE_SOURCE_SHA256"
  }
}
```

Do **not** insert hypothetical values into actual research records to make the display advance. Those identifiers must come from a real operator-admitted, completed, independently reverified local job, then be intentionally placed in the original structured MOVE source and committed. Editing such a record has disclosure implications; **nothing is published automatically**.

When the committed source has no declaration, the result is `OPEN_NO_EXACT_SOURCE_DECLARATION`, and **no native re-verifier is invoked**. With a declaration, every identity field must match a freshly reverified `COMPLETE` native job and its exact completed `RESULT` event. A file edit after its pinned Git revision, missing/broken job, modified edition, forged event, incorrect worker/verifier, or native-verifier failure stops the join.

The strongest successful status is `EXACT_COMMITTED_SOURCE_TO_NATIVE_RESULT_MATCH`. It proves the **source record explicitly names the independently reverified native result**. It does **not** prove external researcher identity, scientific truth, temporal causality, or that the native computation was the actual cause of the research discovery. Those remain separately open and are never promoted based on a checked identifier.

```sh
python -m systems.workspace.native_research_join \
  --data-dir /path/to/private-runtime \
  --job-id EXACT_EXISTING_JOB_ID \
  --repo-root /path/to/repository-checkout \
  --research-commit EXACT_40_CHAR_GIT_COMMIT \
  --research-path state/pins/EXACT_RECORD.json

python -m unittest -v network.tests.test_native_research_join
```

The focused suite creates a *temporary Git repo* with synthetic source declarations and performs one **actual finite child-process execution and fresh source-native replay** using the existing Process Workstation. It does not claim a new externally witnessed research movement. Existing undeclared original records remain separate, and no private journal is uploaded, no server started, and no source or job mutated by the join command.
