# Integrated CP30 — fresh synthetic selected-route audit and exact tasks

The recovered 281-file CP30 edition has a second, separately admitted
workstation operation: the original CP30 owner/pin **synthetic fixture** can
issue a route receipt and three signed scope attestations, check them in its
independent signature-verifier subprocess, run a fresh two-pass selected-route
audit, and test each declared finite edge obligation **separately**. The
recorded result is checked against an additional execution of a newly
reconstructed, SHA-256-manifest-verified canonical CP30 source copy.

**Boundary:** this is same-algorithm canonical reference replay, not a distinct
mathematical proof implementation. Owners and public keys are generated
synthetic fixtures. No live owner was authenticated or remotely contacted; no
production trust bootstrap or real-world source observation is implied.
`COMPLETE` means the bounded computation was recorded, even when the receiver
rejects attestations or some tasks remain unproved.

## Explicit local demonstration

With `cryptography>=45,<47` installed in your authorized checkout:

```sh
python -m runtime.examples.integrated_cp30_route --data-dir runtime/data --execute
python -m systems.workspace.view_server --data-dir runtime/data --port 8051
```

This demo copies exact CP30 source to a private workstation edition if missing,
admits one named fixture job, executes once, and on subsequent invocation
re-verifies the persisted result without re-executing the worker or appending
new events. The read-only page remains at
`http://127.0.0.1:8051/workstation.html`.

## Prepare, admit and execute one selected job

An input JSON file can contain, for example:

```json
{"route":"left","scenario":"intact","tasks":[
  {"name":"a","state":[1,0,0],"action":"B"},
  {"name":"b","state":[1,1,2],"action":"A"},
  {"name":"unproved","state":[0,1,2],"action":"B"}
]}
```

Strict host admission checks the route (`left`/`right`), one to eight distinct
named exact finite edges, and scenario (`intact`, `revoke-selected`,
`revoke-neighbor`, `untrusted-key`). These scenario settings manipulate only
the local synthetic owner/pin fixture and cannot select real owner identities.

```sh
python -m systems.workspace.integrated_source --data-dir runtime/data --stage 30 --version cp30-route-v1 --copy
python -m systems.workspace.controls --data-dir runtime/data prepare-cp30-route --version cp30-route-v1 --inputs-file /path/to/route.json
python -m systems.workspace.controls --data-dir runtime/data admit-cp30-route --version cp30-route-v1 --inputs-file /path/to/route.json --job-id cp30-route-job-1 --confirm-admit cp30-route-job-1 --from-actor local-review
python -m systems.workspace.controls --data-dir runtime/data execute --job-id cp30-route-job-1 --confirm-execute cp30-route-job-1
python -m systems.workspace.controls --data-dir runtime/data inspect --job-id cp30-route-job-1
```

Selecting a version does not admit a job. Admission does not execute it. The
existing read-only HTTP viewer never gains a POST or executor route. The
version's **whole 281-file current fingerprint** is pinned at admission; source
modification blocks execution and replay. Editing a copy never edits the
original research.

## What an observed result establishes

- `INDEPENDENT_PROCESS_FRESHLY_VERIFIED` means the *fixture* passed the CP30
  receiver's signature checks and mandatory fresh selected-route re-audit.
- A `ROUTE_TASK_REQUIREMENTS_UNPROVED` task is not completed, even when another
  declared task on the same route is usable.
- Revoked selected source and untrusted key fixtures withhold route use.
  Revoking only the neighbor leaves an unaffected route auditable.
- The workstation's second canonical replay checks equality with the original
  historical implementation, not external owner authenticity or new proofs.
- Worker Python subprocesses are **not** operating-system security sandboxes.

The original CP20–CP30 archive, recovery hashes, checkpoint views, and the
narrower CP30 signature-only adapter remain unchanged.
