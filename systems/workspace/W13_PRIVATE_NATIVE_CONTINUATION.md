# Original W13: private encrypted native continuation

The original owner verifier succeeded in GitHub run 39135756852, and its source RESULT was rechecked by the historical audit in run 39145620225. The child journal from 39135756852 was ephemeral and NOT retained; its exact event cannot be reproduced from a GitHub log. The earlier source artifact contains only the original W13 parent.

This change adds a future-run capability, not a recovery claim. The module owner_native_evidence_vault.py requires the ACTUAL game-w13-github-001 parent and game-native-verifier-github-001 child, their exact dependency, the original parent RESULT event and worker fingerprint. Before sealing, existing source-native controls independently reverify both COMPLETE jobs and their copied worker editions. The parent-only archive fails closed.

It writes a bounded private runtime (runtime.jsonl, coordinator-windows.jsonl, native worker editions) to an explicit new 0600 encrypted ciphertext file using ephemeral X25519, HKDF-SHA256 and AES-256-GCM. It needs an owner-supplied raw-X25519 public key (base64) and the exact execution commit. Restoration needs the exact child event, matching owner-execution commit, private raw X25519 key and an empty target directory. Both native jobs are independently reverified AGAIN after decryption and before restoration completes. Neither action executes a worker or prints journal contents.

Usage, only INSIDE a separately authorized FUTURE execution with the actual journal:

    python -m systems.workspace.owner_native_evidence_vault seal --data-dir /private/native --public-key-file /private/public.b64 --owner-execution-commit EXACT40SHA --output /private/continuation.enc

In the trusted receiving environment (recipient private key is raw 32 bytes, mode 0600, outside the repo):

    python -m systems.workspace.owner_native_evidence_vault restore --sealed-file /private/continuation.enc --private-key-file /private/recipient-private.raw --owner-execution-commit EXACT40SHA --child-event EXACT_NEW_CHILD_EVENT --output-dir /private/reverified-native

The commit value is a source identity label, NOT proof of owner approval by itself; a separately owner-authenticated invoking workflow is required. This PR provides no owner execution request, key, upload workflow or storage destination. No artifacts are uploaded, no third job is admitted, and no historic child journal is fabricated. Any later encrypted transfer needs independent owner review of artifact permissions and retention.

GAME-WORKER-READY is still distinct. Its existing adapter belongs to the older synthetic nine-job history and also requires a separately source-owned LIVE-GAME-TEMPORAL parent. Encryption does not establish that parent or readiness.

The encryption tests use disposable fixture keys and explicitly mocked sample receipts for codec testing; these are not historic W13 observations. Production uses the unmocked existing native verifiers. Run focused tests with:

    python -m unittest -v network.tests.test_owner_native_evidence_vault


## Future execution hook (local capsule only)

`execute_exact_authorized_child` accepts optional `recipient_public_key_b64`
and `encrypted_output` arguments together. With neither argument, the historical
one-shot behavior and authorization remain unchanged. With both, a NEW exact
`systems/workspace/native_retention_requests/w13/verified-child-local-capsule.json`
request must be introduced by the owner merge. It embeds `EXPECTED_REQUEST`, pins
the SHA-256 of the decoded raw recipient public key, permits local encrypted
retention, and explicitly denies artifact upload and raw export. The calling
workflow still has to authenticate owner, push, protected main and exact commit.
Existing execution consent cannot activate retention.

The destination must be new and outside the repository. Sealing happens only
after native child verification and CP-frontier checks, while the temporary
journal still exists. A seal failure fails the invocation; no successful retained
result is returned. The codec checks both actual native results again. Temporary
plaintext is cleaned up on success or failure. This adds no CLI retention flags,
workflow activation, request, key, artifact upload or cross-run witness.

Next movement: prepare the owner-authenticated future invoking workflow with an
explicit recipient and separately reviewed encrypted storage/retention contract;
then run and independently restore its actual capsule. The historical lost child
journal remains lost, and GAME-WORKER-READY remains separate.


## GitHub capsule configuration (prepared, inactive)

The producer `w13-encrypted-capsule-producer.yml` authenticates a NEW owner merge
and the original archive, executes one exact native verifier child, seals before
cleanup, and uploads only `continuation.enc` plus the redacted `receipt.json` as
`w13-encrypted-RUN_ID` with **one day** retention. The separate
`w13-encrypted-capsule-restore.yml` workflow accepts only a successful first-attempt
owner push on main in this repository. It checks out the exact producer commit,
rechecks the recipient/request, downloads that run's capsule, checks its receipt
hash and event/commit binding, then decrypts and independently re-verifies both
native jobs. Restored plaintext is deleted even if verification fails. Its logs
contain only the redacted verification result. It admits no further worker.

Before activation, install these repository Actions settings:

- Variable `W13_CAPSULE_PUBLIC_KEY_B64`: base64 of the raw 32-byte X25519 public key.
- Secret `W13_CAPSULE_PRIVATE_KEY_B64`: base64 of the corresponding raw private key.

Keep an owner-controlled backup of the private key outside Git. Never commit it
or put it in an artifact. GitHub secret installation is an administration action;
the connected repository content tools cannot perform it.

After key installation, a separate owner merge must add the retention request at
`RETENTION_REQUEST`. Its exact value embeds `EXPECTED_REQUEST` and contains:
`contract=owner-w13-future-child-encrypted-github-retention/v1`,
`recipient_public_key_sha256=SHA256(decoded public key)`,
`authorizes_local_encrypted_retention=true`, `authorizes_artifact_upload=true`,
`authorizes_raw_journal_export=false`,
`storage=github-actions-encrypted-capsule-only`, `retention_days=1`, and
`authorizes_separate_run_restore=true`. Local-only requests cannot authorize
GitHub storage; passing `artifact_retention_days=1` explicitly selects this scope.
No request or key is included in the configuration PR, so merging the workflows
alone does not execute a worker. Both workflow files must already be on main
before the activating request merge, so the cross-run receiver is registered.

Prepared configuration is not a witnessed cross-run result. Activation, successful
artifact retention, and successful separate-run restoration each need actual run
evidence. No GAME-WORKER-READY claim is added.
