# A/B worker evidence in the editable Workflow Workstation

This bridge joins two existing, independently tested lines **without** redefining
either: the real A/B Swallow Repo package's provenance graph and ancestry API
(PRs #129/#134/#212), and the editable workflow/pinned-branch construction
(PR #207).

## Operator flow (local only)

1. Start from an existing workflow draft and generate/inspect its declared
   graph. Structural link generation is based on actual typed source manifests,
   **not** a guessed free-form relationship or a native-job verdict.
2. The original source-owning worker supplies its **already recorded** task ID,
   repository source paths and exact SHA-256 digests. The A/B package reopens
   each source file and checks the bytes. If a file differs or escapes the
   repository, the observation fails.
3. Bind each workflow step to the original worker task ID. Unbound steps remain
   explicitly visible and are not silently attributed to another bot.
4. Inspect the resulting A/B provenance and ancestry graph. It is a source
   relationship projection, marked `SOURCE_REFERENCES_ONLY`.
5. Pin the exact workflow revision as a **candidate** using the existing pin
   mechanism, then optionally attach this A/B source observation. The
   association journal is append-only with a SHA-256 chain. Revising the
   workflow produces a different revision rather than modifying its ancestor.

### Run locally

```sh
python -m pip install ./tools/ab-provenance
python -m systems.workspace.workflow_editor_server --data-dir runtime/data
```

For the original Continuity pool, use **Load original local bot records** in the
editor. It reads the existing `runtime.jsonl` `AGENT_AB_OBSERVED` events from
the original Continuity actor, extracts task/source pairs, and rechecks each
file digest before presenting it. The UI also accepts manual references for
other worker families. In either case, local journal labels and caller-supplied
task identities are **not cryptographic proof of actor identity or execution**.
Only genuine source bytes, the original local record lineage (when available),
and unresolved scope are reported.

The visual editor at http://127.0.0.1:8054/ now includes the optional
**A/B native source ancestry** section. Paste native worker source-reference
records and a map of workflow step IDs to native task IDs, then inspect.
Only an explicit **Attach to pinned revision** action writes the local
association journal.

Equivalent Python operations:

```python
from pathlib import Path
from systems.workspace.workflow_ab_bridge import ABWorkflowSources
bridge = ABWorkflowSources(Path("."), Path("runtime/data"))
report = bridge.inspect(draft, native_worker_source_records,
                        {"step_id": "original-native-task-id"})
# After explicitly pinning that exact draft:
saved = bridge.record_for_pinned_branch(
    draft, native_worker_source_records,
    {"step_id": "original-native-task-id"})
```

The saved record contains only source locators, exact hashes, step/task bindings,
source-graph summary and the digest of the actual A/B graph. It does not copy
source file contents into the local source-link journal.

## Native result feedback (finite worker first)

The Workstation now additionally supports real **completed native results**,
not just source references. The local editor's **Source-verified native
results** panel accepts an exact job ID from either the original
finite-correspondence process or the Factory **simulated machine-stage**
worker. `systems.workspace.controls.reverify_job` dispatches to the
respective source owner's existing verifier. The original selected edition
and recorded output are independently rechecked without running another
worker. Factory's result is strictly a *simulation*, never evidence that a
physical object was manufactured.

**Attach to pinned step** binds that exact verified job and its original
`RESULT` event, source-edition fingerprint, input digest, output digest,
evidence digest and scoped finite verdict counts to an already pinned
workflow revision. Earlier associations are append-only and changing a step
requires a *new workflow revision*, not silently substituting a job.

**Compare pinned native results** requires two different native job IDs,
a direct pinned-parent/branch revision relationship and the **same
source-owned worker family and comparable operation inputs**. Both results
are freshly reverified before comparison. For finite jobs, *all native inputs*
must match; the comparison reports bounded verdict-count differences. For
Factory's simulated machine stage, two distinct native order IDs are required:
the order identifiers remain recorded, while product/material/quantity and
all other machine-operation inputs must match. The comparison reports whether
the two simulated outputs match, **not** a quality score or evidence of
physical production. In particular:

- More `CONTRADICTED` outcomes do **not** establish a better mathematical
  correspondence or application workflow.
- `NOT_CONTRADICTED` does **not** establish an admitted mathematical relation.
- Equality under a finite experiment does **not** prove universal equivalence.
- The source-owned adapters support only these two bounded families:
  finite prefilter and simulated Factory machine stage. Other families need
  their own verifier, domain contracts, and explicit native-result admission.
- The editor does not execute or restart workers. Native results must already
  have been executed through their original explicit permission gates.
- This is local source re-verification, not authentication of who operated
  the computer, and not a hosted multi-customer system.

The native-result association history lives at
`runtime/data/workflow_native_result_links.jsonl`, separate from the
pinned-branch journal, A/B source-link journal, and native source-owner
`runtime.jsonl`. It is SHA-256 chained but not a multi-writer database.
The independent native result recheck must succeed on every inspection and
comparison; a historical pin is not enough.

`network/tests/test_workflow_native_results.py` runs the **real finite
worker subprocess** on two source editions and replays their results.
`network/tests/test_workflow_factory_native_results.py` additionally
executes the existing Factory machine-stage simulator on two distinct
source-owned orders/editions, then independently verifies both results.
Together they test idempotency, source drift, absent native results, distinct
order identity, incompatible machine parameters, and the explicitly
simulation-only comparison. The `workstation-ab-bridge` CI job runs both.
Neither is a generic AI workflow optimizer.

## Deliberate separations

- A/B source matching **is not** native job success, worker code execution,
  correct software behavior, or branch quality. Flags explicitly remain false.
- A/B Swallow Repo's original REA source-edition mutations remain separately
  admitted and verified; the editor does **not** invoke those operations.
- Pin candidates can still be promoted only under the existing independent
  quality-observation route; a source-link record never performs promotion.
- This is an opt-in **localhost editor**, not authenticated multi-tenant
  hosting, subscription billing, remote code execution, or a deployed product.
- The original read-only workstation view, game-world workers, ARC research,
  and finite A/B mathematical sources are not replaced.
- A/B's All Rights Reserved license and upstream REA MIT terms remain separate.

## Verification

```sh
python -m unittest -v \
  network.tests.test_workstation_ab_workflow_bridge \
  network.tests.test_workstation_ab_workflow_http
```

The `workstation-ab-bridge` CI job also rechecks original workflow editor,
pin ledger, native A/B bot, and Program Foundation tests. Bounded tests do
not establish broad claims about reliable autonomous workflow generation.
