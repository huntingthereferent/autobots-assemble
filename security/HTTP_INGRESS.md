# HTTP admission boundary — native A/B handoffs

This is a bounded, **opt-in** bridge from an HTTP request to the existing
`EcosystemService`, `HandoffRuntime`, and durable `RuntimeJournal`. It is
not a second worker engine.

## Entrances

| Route | Admission |
| --- | --- |
| `POST /api/security/handoffs` | Signed and encrypted native root `Handoff` |
| `POST /api/security/handoffs/{id}/result` | Signed and encrypted native `ExecutionResult` |
| `POST /api/handoffs/{id}/result` | Legacy unsigned local interface; **not for external trust** |
| `POST /api/agents/{id}/result` | Separate agent-lineage protocol; not secured by this adapter |

Both signed endpoints require exactly `{"envelope": <signed envelope>}`.
They reject caller-supplied actor or parent policy. Missing operator
configuration returns HTTP 403; it never creates a key or trusts one from the
message.

The trusted host process must install `AuthenticatedHandoffIngress` objects
for `submit` and `result` through
`EcosystemService.register_authenticated_ingress`. Each contains a
separately pinned sender **public** key, locally held recipient **private**
key, bounded lane, exact sender/receiver actor IDs, and a private
`ReplayLedger`. The sender signs with its Ed25519 private key elsewhere.

The trusted host must additionally supply a B14 `OperatorPinLedger` and enroll the exact signer Ed25519 public-key digest under the lane/actor/receiver scope before registration. The ledger is re-read for every handoff and worker result; revocation or rotation denies the existing handler. No environment variable or public HTTP route automatically enrolls a key.
The stock `runtime.http_server` does **not** install these objects, so
these endpoints remain unavailable in its default deployment. A trusted host
integration must inject them into the service before serving requests.
An operator may use B14/B15 for its **own** supported worker lane, but
this new adapter is not implicitly enrolled by B14/B15.

## Movement

```text
authorised owner signature + encrypted handoff
    → loopback HTTP boundary + bounded same-origin JSON
    → pinned source/recipient + lane verification
    → independent replay admission
    → existing HandoffRuntime.submit
    → existing RuntimeJournal event
    → READY, not auto-execution

authorised worker signature + encrypted result
    → pinned worker verification
    → exact last native runtime event + target worker
    → existing HandoffRuntime.return_result + evidence rules
    → append-only RESULT
```

The HTTP bridge only accepts root envelopes (`parent_sha256: null`)
until a trusted server-side parent-envelope registry has been implemented.
It does **not** treat a client-supplied parent digest as independently
verified ancestry. Signed return envelopes are currently similarly
root-scoped; their **native runtime** prior event ID is checked inside
the signed payload.

## Local HTTP hardening

The existing HTTP server now refuses non-loopback `HOST` values before
binding. It checks the connecting IP and Host header against loopback,
requires the correct listening port, refuses foreign Origin and
cross-site Fetch Metadata requests, and bounds POST to JSON objects of
at most 1.5 MB. Non-JSON forms and oversize bodies are not processed.

This is **not** full local authentication. Another process with local
machine access could potentially call the legacy local APIs, and
malware controlling the host can subvert file state. Do not expose the
current HTTP service directly to a LAN or the internet or place it behind a
proxy without designing and auditing authentication for **all** routes.
Loopback does not guarantee secrecy against other processes on the host.

## Persistent state and recovery

The existing `RuntimeJournal` still writes admitted handoffs and result
contents in plaintext JSONL. The transport envelope only protects data until
it is admitted. The replay SQLite database and JSONL journal are separate
stores; a journal write failure **consumes** that event ID and requires
explicit operator reconciliation. Neither record store is tamper-resistant
against a compromised host.

Signing-key enrollment, revocation, secure key custody, distributed replay
consensus, protected at-rest journals, backup/recovery, and recovery from a
crash between separate stores remain required before public or multi-user
deployment. Native completion does not itself verify scientific truth.

## Run

```sh
python -m pip install 'cryptography>=45,<47'
python -W error::ResourceWarning -m unittest discover \
  -s network/tests -p 'test_security_*.py' -v
```

The HTTP tests use an ephemeral in-process loopback listener and temporary
native journal. They do not install or expose a production service.

## Opt-in encrypted storage

The same `EcosystemService` supports `protected_runtime_key=<32 independently managed bytes>` for a new, encrypted native handoff history. See [the protected journal record and recovery contract](SEALED_JOURNAL.md). Default execution does **not** automatically enable this; additional service logs and user data remain separate plaintext stores.
