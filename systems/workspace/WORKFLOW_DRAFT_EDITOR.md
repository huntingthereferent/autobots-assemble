# Workstation — editable workflows and pinned branches

This is an additive operator surface over existing, separately owned foundations:

- `foundation/program_kernel/graph.py` supplies non-executing graph validation and the existing strict execution graph contract.
- `systems/workspace/workstation_construction.py` (B9) remains the source-owned **proposed** branch / alternative / dependency journal.
- `systems/workspace/workflow_draft.py` translates user-edited, manifest-backed workflow graphs into B9 candidate construction, without adding runnable jobs.
- `systems/workspace/workflow_pins.py` retains preferred branches and bounded quality discoveries in a separate append-only ledger.

**This is workflow construction, not an inverse A/B mathematical proof.** Existing correspondence mathematics and B9 observational determination are unchanged.

## Start the interactive local editor

From the repository root:

```bash
python -m systems.workspace.workflow_editor_server --data-dir runtime/data --port 8054
```

Open **http://127.0.0.1:8054/** on the same computer. The browser page can add steps from existing Program Foundation manifests, edit their labels/inputs, add or remove explicit edges, inspect the graph, generate uniquely compatible edges, record a proposal into B9, branch from any pinned revision, compare it with its pinned ancestor, pin another edition, and export/import JSON.

The server binds **only to 127.0.0.1**, checks the exact Host and Origin and requires an unpredictable server-local token for each write. It has no worker-execution route. Start it only on a computer you authorize; a local editor is **not** an authenticated cloud multi-tenant service.

The existing `workstation.html` remains a GET-only independent research observer. This is a new *separate opt-in editor*, not a replacement.

## What a user can do now

1. Open an existing bounded draft (see `examples/workstation_workflow_draft.json`). Edit step names, source manifests, declared inputs, prerequisite edges, and alternative paths. A `parent_revision` allows a later draft to identify its earlier version.
2. Generate plausible edges by setting `auto_connect: true`. Generation uses real declared port names and compatible types, **not** a guessed dependency based on superficial descriptions. Ambiguous matches stay visible as unresolved and are not automatically linked.
3. Preview and validate links and cycles without importing or executing a worker. A validated draft is still **PROPOSED**, not a verified native workflow.
4. Commit the exact graph as B9 candidate paths, linked by the real source manifest revisions and the original construction journal. All execution and native-admission gates remain separate.
5. Compare your branched graph with its pinned parent, and pin a branch you want to preserve. Optionally compare it with a pinned parent using a measured, source-scoped metric; an improved branch can be pinned automatically as a **candidate**. A separate independent source-native verifier callback is needed to label even that measurement verified, and this is never a blanket proof of the full workflow.

### Local commands (no execution)

```bash
python -m systems.workspace.workflow_draft preview --draft examples/workstation_workflow_draft.json
python -m systems.workspace.workflow_draft commit --draft examples/workstation_workflow_draft.json --data-dir runtime/data
python -m systems.workspace.workflow_draft pin --draft examples/workstation_workflow_draft.json --reason "Save original graph" --data-dir runtime/data
python -m systems.workspace.workflow_draft pins --data-dir runtime/data
python -m systems.workspace.workflow_draft diff --draft /path/to/branched-draft.json --data-dir runtime/data
```

For another branch, add its exact prior pinned SHA-256 as `parent_revision`, change the graph, and preview it. For an explicitly supplied quality comparison:

```json
{
  "metric": "passed_independent_checks",
  "parent_value": 6,
  "branch_value": 7,
  "direction": "HIGHER",
  "comparison_scope": "same declared source, checks and test inputs",
  "source_ref": "source:<identity>",
  "witness_ref": "record:<actual witness>"
}
```

Save the actual observed comparison to `runtime/data/assessment.json`; then:

```bash
python -m systems.workspace.workflow_draft consider --draft /path/to/branched-draft.json --assessment runtime/data/assessment.json --data-dir runtime/data
```

This CLI route **does not independently verify** the claimed numbers; it can pin the improved branch only as `CANDIDATE`. Hosts integrating a real source-native observation provider can supply `WorkflowPins.consider_discovery(..., verify_observation=...)`; the resulting state is `QUALITY_OBSERVATION_VERIFIED` for that one metric, not for the whole workflow. If the branch was first pinned as a candidate, a later verified measurement can be appended through `WorkflowPins.promote_pin(revision, verify_observation=...)`, preserving the original candidate entry and exactly the same workflow revision. The local browser cannot self-certify a measurement.

## Persistence and boundaries

- A draft revision covers the normalized graph, its parent revision, input values, exact manifest content digests, and resolved links.
- Pins preserve previous versions and their source-bound comparisons; changing a pinned version requires another distinct revision. The pin ledger is SHA-256 chained and detects file modifications; **it does not authenticate who made a record**.
- B9 proposals include original candidate relations and source hints, but a hint is not verified capability, a READY spec is not an executable job, and a verified metric is not full workflow correctness.
- The existing source-copy workstation, existing B9 construction, and the Program Foundation executor are not changed to run code automatically.
- No remote multi-user authentication, concurrent writer support, security sandbox, cloud service, user billing, automated model interpretation, or general automatic workflow discovery is claimed here.
- The user's private journals are never collected by this code. The draft/ledger are local.
- The pin feature is **opt-in** by an explicit local call or a separately authorized integration; no telemetry or automatic public exposure.

## Tests

```bash
python -m unittest -v network.tests.test_workstation_workflow_draft network.tests.test_workstation_workflow_pins network.tests.test_workstation_workflow_editor_http network.tests.test_program_foundation network.tests.test_workstation_construction
```

The PR's `workstation-workflow-drafts` check runs these tests and previews the example. Even a passing CI run establishes the bounded construction and ledger contracts, **not** hosted reliability or end-user success. The local interactive editor is now available as an opt-in construction interface. Authenticated multi-tenant hosting, customer isolation, native worker integration, and end-user effectiveness remain separate unverified product work.
