# The idea checklist and worker-local frontiers

This is the user's existing **task/to-do list** viewed as a bounded checklist
of *ideas*. It is **not** a new ontology, natural-language task generator,
or new scheduler.

## Sources

- The checklist is read from the original `TASKS.md`
  `## Active ALL WORK` section using `runtime.repository_tasks.read_active_work`.
- Only actual current `MOVE*` rows appear as ideas. Pinned/archive/frozen
  source rows are not converted into obligations. New ideas must first be
  admitted through the owner's existing task source; this feature does not
  write or invent `TASKS.md` entries.
- An idea ID is the exact existing `RepositoryWork.source_id`, derived from
  its recorded title and Markdown source link.
- Branches are exact revisions in the existing WorkflowPins ledger. An
  operator deliberately associates a pinned revision with an idea and a
  bounded **worker label**, never by semantic/title matching.
- Child branches require their actual pinned parent to already be
  associated with the **same** current source idea. Other task lanes,
  unrelated roots, fabricated parent revisions, and deep descendants
  cannot be silently linked.
- All associations and proposed help/backtrack movements are append-only
  in `runtime/data/workflow_idea_frontier.jsonl`, in a local SHA-256 chain.
  Hashes can detect accidental/tampered history; they **do not authenticate**
  the worker's personal identity or grant execution permissions.

## Two different observations

The **human editor** may click an active task item, view the branches
explicitly assigned to that one item, and fork any of those pins for an
alternative proposed structure. The originating pin and earlier history remain
unchanged.

The **worker-facing** `IdeaFrontier.worker_frontier(idea_id, revision,
step_id, worker)` reads only the current known position:
- the current source-recorded idea, pinned revision, worker label and step;
- directly adjacent declared steps in the *same* pinned graph;
- directly pinned parent, direct children and immediate siblings sharing
  that same pinned parent **within the same explicitly associated idea**;
- boundary descriptors for those related revisions, **not their full graphs**;
- incoming, explicitly recorded help proposals addressed **to this exact
  branch**, only when their source is also within the visible first hop.

The Workstation reopens current source manifests and recomputes their
fingerprints before a worker sees a pinned revision or direct neighbor.
Stale manifest bytes make that relationship unavailable rather than
silently inventing continuity.

This is deliberately *not* global omniscience. A worker can move backward
through one parent at a time, request another bounded perspective in a later
move, or propose assistance to another recorded worker at an immediately
visible branch. A source label on a parent/sibling is not independent
evidence that it works, nor that its approach is better. The native
result/source re-verifiers stay separate.

## Operator and worker actions

The existing opt-in local editor `python -m
systems.workspace.workflow_editor_server` now provides:

1. **Ideas** — exact active source task checklist.
2. **Associate selected pin with idea** — explicit operator-created link.
3. **Observe first-hop frontier** — read at a specific worker's bound position.
4. **Propose backward movement** — only to the directly pinned parent.
5. **Offer help on peer branch** — only when another explicitly recorded
   worker is directly related at a child or shared-parent sibling.

Neither a help proposal nor a backtrack proposal runs workers, merges
branches, rewrites an existing pin, imports code, or declares a better path.
A worker must still return to its actual native owner/continuation and pass
that worker family's original execution and independent verification gates.

The local editor's source task inventory is **a human-facing view**; the
worker API is `worker_frontier()`. This is an enforced read-shape in the
Python worker capability, *not security isolation against a malicious local
process*; there is no real multi-user worker authentication here.

## Source-bound tests

```sh
python -m unittest -v \
  network.tests.test_workflow_idea_frontier \
  network.tests.test_workstation_workflow_editor_http
```

Tests confirm no invented task IDs, source-only idea rows, local one-hop
visibility, no unrelated branches, no skipping ancestors, worker-label
mismatch, no silent ranking/worker execution, and refusal of tampered
history. CI runs the same tests with the existing A/B, Program Foundation,
native-result and branch construction checks.
