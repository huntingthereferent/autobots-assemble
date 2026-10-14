# Integrated Finite Correspondence Process — recovered source edition

The historical CP20–CP30 source is now available on `main` at
[`work/arc_like_maze/chatbot/research/integrated/`](../../work/arc_like_maze/chatbot/research/integrated/README.md).
It is preserved as a 201-file CP20 baseline and ten eight-file deltas. Nothing in
this page modifies a historical file or assumes all owner-backed regressions pass.

## Copy an integrated edition into the Process Workstation

From the repository root, using a trusted clone of this repository:

```bash
python -m systems.workspace.integrated_source \
  --data-dir runtime/data --stage 30 --version recovered-cp30-001 --copy
```

The command checks all **281 source-file digests and lengths against the
GitHub-published manifest**, reconstructs the selected CP into a temporary
private directory, and copies the source into a new workstation edition:

`runtime/data/workstation/finite-correspondence-integrated/recovered-cp30-001/`

CP20–CP29 can be selected with `--stage`, using a fresh version name.
Existing editions are never overwritten. The source copies can be inspected,
compared, and independently branched through the existing workstation
facilities. The original integrated source on `main` is not edited.

The command is **source-only** and does not import or execute historical
worker code. No job is submitted, no worker is launched, and no archived CP
witness is attributed to a changed source branch. `source_verified=true`
means only the recovered byte content matched the historical manifest.
`capability_verified=false`, `job_admitted=false`, and `executed=false`
remain explicit.

## View the preserved source edition

```bash
python -m systems.workspace.view_server --data-dir runtime/data --port 8051
```

Open `http://127.0.0.1:8051/workstation.html`. The integrated edition appears
alongside other worker versions, but **has no registered executor**. It must not
be admitted through the existing narrow finite prefilter adapter merely because
its source is available. A later source-specific job adapter must define native
operation, bounded inputs, verification and scope before actual execution.

## Evidence boundaries

- Historical source matches a manifest, not a live external owner identity.
- CP30's signed example scopes are synthetic. Their tests do not authenticate
  independent real-world owners.
- Reconstructing CP30 does not prove an integrated application is production-ready.
- Local execution of copied code is not OS-sandboxed by the workstation.
- Original checkpoint manifests, archive hashes, source and user research records
  remain preserved; no CP record or research `ABOUT_ME.md` is rewritten.

Reproduce the workstation source-isolation checks with:

```bash
python -m unittest -v network.tests.test_integrated_source_workstation
```
