# Security policy

This repository contains research prototypes and scoped security experiments.
A passing test is evidence about the tested implementation, not a claim that
all repository systems are secure or production-ready.

## Report a vulnerability privately

Please do **not** publish vulnerability details, credentials, personal data,
private keys, or exploit transcripts in a public issue or pull request.

If GitHub private vulnerability reporting is enabled for this repository,
use **Security → Report a vulnerability** on the repository page. Otherwise,
contact the repository owner through an established private channel before
sharing sensitive details. No response-time commitment is represented here.

Include the affected component and commit, minimal reproducing conditions,
security impact and any relevant logs **with secrets removed**. Testing should
be confined to systems you own or are authorized to assess.

## Scope

Security components under `security/` are opt-in until a caller explicitly
integrates their trust and admission boundaries. Legacy experimental code is
not automatically covered. See [the security lane's model and limits](security/README.md).
## HTTP entrance

This server is intentionally loopback-only, including the legacy routes.
A cross-origin browser request is not an authenticated worker. The optional
authenticated handoff endpoints remain disabled without independently
enrolled actor keys; see [the HTTP ingress boundary](security/HTTP_INGRESS.md).
Legacy local APIs and plaintext native journals are **not** protected merely
because the signed endpoint exists. Do not publish the service by changing
the bind address or adding an unaudited reverse proxy.

## Protected native journal (opt-in)

The optional [encrypted runtime journal](security/SEALED_JOURNAL.md) encrypts only the native handoff history. It is not a whole-workstation encryption guarantee. Existing plaintext journals cannot be silently migrated or replaced; key custody, backup and recovery remain operator responsibilities. Signed HTTP admission requires a current operator-enrolled signer key, and revoked keys are checked again on subsequent requests.

## Independent continuity checkpoint

The optional [signed journal checkpoint and offline recovery contract](security/CHECKPOINT_RECOVERY.md) covers observed native encrypted history and a separate recipient-encrypted key envelope. It does not implement unattended key backup or off-host publication. A checkpoint stored only beside a rollback-able database does **not** defend against whole-history rollback. See also the signed-worker-only HTTP policy in [HTTP ingress](security/HTTP_INGRESS.md).
