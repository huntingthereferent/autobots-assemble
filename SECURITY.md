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