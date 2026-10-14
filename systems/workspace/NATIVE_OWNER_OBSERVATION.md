# CP30 in-process owner observation — separate from external evidence

**Status: staged.** This is the first source-controlled, live *native-local*
observation interface. It does **not** attach a public GitHub file, an Ed25519
signature, or a claim about an external organization to CP30's local owner
registry. It does **not** modify recovered CP20–CP30 research source or create
runtime handoffs.

## What the source must provide

The owner-controlled Python process supplies a trusted `source_capture()`
callback. The callback returns a dictionary of one to sixteen already-admitted
CP30 `RouteBoundTask` **objects**, not JSON declarations. Every task must be a
different native object tied to the **same exact route instance** and pinned
fingerprint. The caller must load the CP30 native modules from one explicitly
selected, reviewed source directory (`native_source_root`). The adapter rejects
modules imported from another directory.

On each observation, the adapter calls the historical native CP29 `_bound()`
contract, verifies all six (old/new × donor/middle/final) live owner pins using
the original `OwnerPinRegistry.verify()`, and checks each captured bridge's
`LOCAL_OWNER_VERIFIED` provenance and exact live snapshot. It captures
`_route_evidence()` and native object identities. It then calls the
source-owned callback **a second time** and refuses changed owner bindings,
source evidence, route structure or task objects.

Native pin verification may mark an invalid pin inactive **in memory**, as the recovered native verifier specifies. This does not append to the workstation or evidence journals.

No owner pins or snapshots are constructed from serialized content. Only the
**original live objects provided by the source** are evaluated.

## Native route auditing is a separate opt-in action

By default, observation **does not run a route audit** or test obligations. An
explicit `allow_native_audit=True` invokes CP28 `audit_route()` for its current
two-pass selected-route audit, then `consume()` for each *distinct* exact task.
The adapter reports independently which tasks completed and which obligations
remain unproved. It does not replay a CP29 portable receipt or perform CP30's
separate-process cryptographic verification. `audit_route()` is the *native
in-process* operation, not an external remote observation.

```python
# Run inside a trusted process that already imports native CP30 from CP30_DIR.
# source_capture is implemented by that process's owner; it returns live tasks.
from systems.workspace.native_owner_observation import observe_native_owners

inspection = observe_native_owners(
    native_source_root=CP30_DIR,
    source_capture=source_capture,
)  # default: read-only capture only

result = observe_native_owners(
    native_source_root=CP30_DIR,
    source_capture=source_capture,
    allow_native_audit=True,
)  # explicit synchronous CP28 two-pass audit
```

The actual source-owning caller must implement `source_capture`; no generic
command accepts an arbitrary file and pretends to construct native owner
objects. Python callbacks are trusted code, **not sandboxed** or suitable for
untrusted remote registration. The adapter is deliberately not a listening
server and has no implicit scheduler.

## Evidence table

| Condition | Established by this adapter? |
| --- | --- |
| Live native in-process source objects and exact registry-issued pins | Yes, if supplied and valid at both captures |
| Native source consistency across capture and current two-pass route audit | Only with explicit audit flag |
| Individual exact task obligations | Checked individually only with audit flag |
| Signature from enrolled public GitHub source key | No |
| Correspondence between GitHub bytes and native snapshots | **No** |
| Real-world external source identity | **No** |
| CP29 portable handoff receipt accepted | No |
| CP30 three-scope independent-process signature audit | No |
| HandoffRuntime job admission, persistence, deployment | No |

External evidence and native-local observation now have **two distinct
interfaces**. A future source-controlled bridge would have to demonstrate how
an external source actually owns and can observe the native snapshot before
connecting them. Matching a signed SHA-256 to a local declaration is not that
bridge. This step provides the live-native receiving end without inventing that
missing relation.

## Reproduce tests

First reconstruct the historical CP30 source using the checked-in assembler:

```sh
python work/arc_like_maze/chatbot/research/integrated/assemble.py \
  --stage 30 --out /tmp/cp30-native
CP30_NATIVE_SOURCE_DIR=/tmp/cp30-native python -m unittest -v \
  network.tests.test_native_owner_observation
```

The test objects come from the original historical **synthetic** owner
fixture. No external provider or real-world owner has been enrolled or probed.
No live GitHub API call occurs.

You can exercise the opt-in **synthetic local** demonstration after reconstructing CP30:

```sh
python -m runtime.examples.native_cp30_owner --native-source-dir /tmp/cp30-native
python -m runtime.examples.native_cp30_owner --native-source-dir /tmp/cp30-native --audit
```

## Subsequent partial content matching (separate adapter)

A separate [external-to-native cached-edge matcher](EXTERNAL_NATIVE_BINDING.md)
compares previously signed and observed public-source declarations to **already
cached** native transitions in these live objects. This is content matching
only: no new owner pins, full-table proof, native route-audit authorization, or
external source identity is inferred.
