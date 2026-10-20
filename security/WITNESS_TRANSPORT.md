# Witness-only authenticated transport and independent observer anchors

**Status:** opt-in, loopback-only laboratory implementation in draft PR #262.
No workstation deployment, remote worker authorization, public endpoint, or
production certificate-issuance workflow is included.

## Separation of owners

The native source keeps its AES-GCM decryption key and encrypted event journal.
Its operator signs a precise journal checkpoint and exports a bounded witness
span of ciphertext hashes and frames. The *observer* retains its own SQLite
witness ledger. It cannot decrypt, execute, or reinterpret source work.

The observer's operator must independently establish and protect **three
different references** before accepting a remote witness:

1. The source's Ed25519 **public** checkpoint signing key and an already
   witnessed checkpoint, enrolled locally in `RemoteWitnessLedger`.
2. The TLS client's **exact DER certificate SHA-256 fingerprint**, mapped by
   trusted host configuration to that source ID and signing key.
3. A separate, **independently retained observer checkpoint**, signed by the
   observer's own Ed25519 key. This protects the observer's *observed prefix*
   from silent local database rollback while the independent anchor survives.

No received JSON can enroll a certificate, source public key or anchor. A
valid client certificate does not override source signed-history checks,
and a valid source checkpoint signature does not bypass TLS identity policy.

## Transport

`security.witness_transport.WitnessOnlyHTTPServer` is a deliberately
non-deploying Python class. The host must explicitly provide a TLS 1.3 server
SSL context with `CERT_REQUIRED` and out-of-band client certificate pins.
Its constructor refuses non-loopback binding. There is one application
operation: `POST /v1/witness`, with bounded JSON containing an enrolled
source ID and a ciphertext witness bundle.

Requests are bounded to 1 MiB, require one unambiguous Content-Length and
Content-Type, and reject chunked transfer, duplicate JSON keys and
nonfinite JSON values. The server derives source authorization from the
**verified TLS peer certificate**, never from a user-supplied actor ID.
The endpoint rejects other paths and does not expose native worker
scheduling, agent results, notes, secrets, or key enrollment.

The response is only the source ID and recorded checkpoint sequence. It
does not return any decrypted native research material. Request logs are
suppressed rather than containing research payloads.

A loopback TLS test can be exercised via independently managed transport
or tunneling only after a separate operational review. No route in this PR
automatically exposes a public listener or configures external networking.

## Observer checkpoint

`issue_observer_anchor` signs the current observer-owned source identity,
latest signed source checkpoint, count and digest of previously observed
source-specific movements. The operator must **export the anchor outside**
the observer ledger's rollback domain. Calling the signing function does
not publish or back up anything.

`verify_observer_anchor` validates both the observer signature and the
previously pinned source signing key. It recomputes the archived movement
prefix, verifies its continuity and requires the source's last recorded
state to agree with its record history. Later observations may extend an
anchored prefix; older whole-database snapshots or changed anchored rows
must be refused.

The witness receiver checks this independent anchor on construction and
**before each received observation**. A separately restored older
observer database cannot continue through this entrance once a newer
authentic anchor has been retained.

The operator must explicitly update the receiver's independent anchor when
a new one has been signed and safely stored. No background publisher or
implicit checkpoint advancement is implemented.

## Evidence, limits and deployment blockers

Tests construct temporary locally signed CA/server/client certificates,
require actual TLS 1.3 client-certificate verification, and send real
localhost HTTPS requests. They also exercise wrong/unpinned certificates,
no client certificate, false source identities, prohibited endpoints,
duplicate headers, duplicate JSON fields, and observer rollback.

These tests prove **local authenticated transport and bounded verification
for the tested examples**. They do **not** test two physically separate
hosts, certificate revocation in a production PKI, network partitions,
distributed locks, multi-host consensus, remote scheduler control, tamper
resistance against a compromised observer host, or trustworthiness of
source scientific claims.

The observer database is still an ordinary local SQLite file. Signatures
only protect what an independent custodian actually retains; an attacker
who can steal or replace both keys and anchors defeats that trust boundary.
History after the most recently exported observer anchor is not
independently anchored.

**External deployment remains blocked** until complete key custody,
certificate enrollment/revocation, off-host checkpoint retention,
host authorization, receiver data policy, independent review and tested
operational recovery are provided. None of those are inferred from CI.

## Reproduction

```sh
python -m pip install 'cryptography>=45,<47' 'rdflib>=7,<8'
python -W error::ResourceWarning -m unittest discover \
  -s network/tests -p 'test_security_*.py' -v
```

The TLS and observer tests use temporary fixtures and destroy their
certificates and decryption keys after the test. They do not deploy
private keys into the workstation.

## Operator certificate lifecycle (B14)

The witness TLS listener requires an existing `OperatorPinLedger`
containing the exact **DER SHA-256 client certificate fingerprint** for
each pre-enrolled source. The local source name is
`ab-witness-client:{source_id}`, edition `ab-witness-client-cert/v1`.
The certificate digest, source Ed25519 public key and independently retained
observer checkpoint are **separate inputs**. A TLS request cannot enroll
or rotate any of them.

The trusted host must enroll the certificate digest through B14 only
after independent identity/certificate verification, **before constructing
the witness listener**. Construction fails if the expected certificate
pin is absent, revoked or no longer current. The running listener then
re-reads the B14 policy at the start of every witness POST and again
after checking the source/observer checkpoint, just before recording the
movement. Revocation, rotation, or an invalid local operator policy
file deny later witness requests even if an earlier TLS handshake
succeeded. Already recorded movements are not erased.

Rotating the certificate requires explicit operator enrollment of the
new DER fingerprint, followed by trusted construction of a receiver
with the new certificate-to-source map. The old listener does **not**
silently trust a new certificate, and policy changes are never accepted
from request JSON. Separately manage the CA chain and TLS private keys;
pinning a leaf certificate does not constitute independent proof of
a real person's identity.

**Remaining race:** B14's local policy file and the observer SQLite
database are not a single atomic transaction. A revocation after the
final policy read but before SQLite COMMIT may allow an already in-flight
observation. Production-grade immediate revocation would require a
coordinated admission fence across the policy and observer commit. B14's
unanchored local audit file can itself be replaced by a compromised host.
This bounded test is not production PKI revocation, and does not support
remote network deployment.
