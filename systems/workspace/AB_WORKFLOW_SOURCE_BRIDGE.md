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
