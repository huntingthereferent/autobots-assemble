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
