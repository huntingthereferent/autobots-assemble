# Native workstation receipts — local evidence boundary

The existing [Process Workstation](WORKSTATION.md) has a private
\`RuntimeJournal\` and a source-native \`reverify_job\` operation. This
**read-only local probe** joins their exact identifiers for an explicitly
selected job. It does not read a public GitHub Actions workflow as native
execution proof.

The receipt contains only the handoff/job ID, worker/edition identity, pinned
SHA-256 source fingerprint, declared verifier ID, recorded state, exact event
IDs/types and explicit parent-event references. No arbitrary user inputs,
result payloads, evidence references, actors, journal paths or timestamps are
copied into the response.

A completed recorded job is **RECORDED_NOT_REVERIFIED** by default. Calling
\`--reverify\` invokes the existing worker-specific, read-only
\`controls.reverify_job\` boundary. A successful response labels only that
exact job/edition as locally and freshly reverified, and refuses the claim if
the journal changes while it is checked.

\`\`\`sh
python -m systems.workspace.native_receipt_projection \
  --data-dir /path/to/private-runtime --job-id EXACT_JOB_ID

python -m systems.workspace.native_receipt_projection \
  --data-dir /path/to/private-runtime --job-id EXACT_JOB_ID --reverify

python -m unittest -v network.tests.test_native_receipt_projection
\`\`\`

The probe runs only when invoked. No work is admitted/executed, no endpoint is
opened, and no file is written or uploaded. Output remains private to the
operator's local shell. The unit tests mock the dispatch to the native verifier
and therefore establish only the routing/negative conditions, **not real
source-native verification**. A real receipt needs a real original native
worker and its actual verifier and source edition available in the same
authorized local runtime.

**Still open:** Public publication, exact binding to a repository SHA, and
causal joining to a structured research movement. Those are distinct edges:
neither a matching filename nor a result label proves them. A separate
operator-approved, sanitized publication protocol and independently verified
source relationship are prerequisites. Do not publish private runtime journals
or infer edges from heading text, nearby dates, or convenient names.
