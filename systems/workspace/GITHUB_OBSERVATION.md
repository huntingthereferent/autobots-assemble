# GitHub public-source observation after signed claim intake

**Status: staged bounded adapter, not deployed external CP30 owner evidence.**

The local external-evidence ledger supports a second, strictly downstream step:
read **three exact public GitHub files**, compare freshly downloaded bytes with
the three SHA-256 digests already declared and signed, and append a *separate*
`SOURCE_OBSERVED` event. The native CP30 route worker remains synthetic and is
**not invoked or authorized** by this step.

## Exact source contract

For `donor`, `middle`, and `final`, an operator explicitly enrolls a distinct
public Ed25519 verification key and a GitHub file locator of the form:

`https://github.com/OWNER/REPO/blob/BRANCH/PATH`

The branch is a single URL path segment (for example `main`); no slash-bearing
branch names, URL encoding, query strings, redirects, credentials or arbitrary
remote endpoints are accepted. The file must be **public** and at most 1 MiB.
The repository or GitHub account name is only a locator, **not an independently
verified owner's identity**. Three scope labels need not represent three
independent organizations.

Once an authorized receiver has issued and accepted a valid three-signature
challenge using `external_evidence.py`, request the observation *within ten
minutes of accepting the signed bundle*. This operation is **opt-in HTTPS GET**:

```sh
python -m systems.workspace.github_observation \
  --data-dir runtime/data \
  --challenge CHALLENGE_HEX_FROM_EARLIER_ACCEPTANCE \
  --confirm-challenge CHALLENGE_HEX_FROM_EARLIER_ACCEPTANCE \
  --observe
```

No network activity occurs from `external_evidence status`, merely starting the
read-only workstation dashboard, enrolling keys, or admitting signed claims.
The observation command itself never creates a CP30 job.

For each distinct `OWNER/REPO/BRANCH`, the observer obtains the public GitHub
branch head SHA, downloads each enrolled path **at that immutable commit**, and
checks GitHub's Git-blob SHA-1 plus independently computed byte SHA-256. It
requires exact equality with the corresponding signed source digest. Finally,
it re-fetches each branch head; any movement aborts without recording an
observation. Branch checks are **not** an atomic snapshot across different
repositories and do not prove that a branch never briefly changed and reverted.

The local append-only ledger records the challenge, resolved commits, Git blob
identifiers, SHA-256 values, timestamp and receipt hash. It does not persist
source file contents, remote owner credentials, signer secret keys or an
independent cryptographic journal anchor. The operator must retain the signed
bundle and public source snapshots separately if later independent audit is
required. The ledger assumes one authorized writer and is not a database
transaction service.

## Evidence ladder: do not skip levels

| Level | What is established | What is not established |
| --- | --- | --- |
| Key enrolled | Local operator pinned an exact public verification key | Authority, organization or source ownership |
| `SIGNED_SOURCE_CLAIMS_ACCEPTED` | Correct Ed25519 signatures for one receiver challenge, expected digests and claimed observation time | Truth of signed claims or contents of remote files |
| `PUBLIC_GITHUB_BYTES_MATCH_SIGNED_DIGESTS` | Public GitHub file bytes were fetched at checked branch heads and their SHA-256 digests matched previously accepted claims | Actual real-world owner's control, independent source identity, native CP30 route/edge evidence, task authorization |
| CP30 route/task proof | **Not implemented for external GitHub sources** | No `proof_for_use`, `COMPLETE` or external-owner authorization may be inferred |

The separate historical `IntegratedRouteBridge` checks owner-pin witnesses,
route fingerprint, two fresh source audits, and each requested edge. A GitHub
file digest supplies none of those native structures by itself. A future
adapter must translate **reviewed, explicit content schemas** into the actual
CP30 owner/pin contract and re-run its native checks before considering any
external task admissible. Do not create fictional owner objects merely to make
the historical tests pass.

## Tests

```sh
python -m unittest -v network.tests.test_external_evidence network.tests.test_github_observation
```

The GitHub network API is **mocked** in this test suite; assertions prove the
bounded fetch/verification contract and rejection paths, **not** successful
retrieval of any real user's sources. The CLI performs real public HTTPS reads
only if an operator has explicitly enrolled keys, accepted a signed claim, and
supplied `--observe`.

## Read-only finite-source declaration mapping

The [external CP30 declaration mapper](EXTERNAL_ROUTE_MAPPING.md) checks exact
operator-retained file bytes against this observer's signed-digest event,
validates a strict finite A/B transition-declaration schema, and reports why
live native CP30 owner/pin and route-proof requirements remain **unproved**.
It does not re-observe GitHub, create an owner pin or admit a CP30 task.

## Two-observation continuity boundary

A single `SOURCE_OBSERVED` event makes no temporal continuity claim. The [external source continuity checker](EXTERNAL_SOURCE_CONTINUITY.md) requires two separately challenged and accepted observations, and can optionally check GitHub commit ancestry under an exact explicit network flag. This never enrolls real-world owners.
