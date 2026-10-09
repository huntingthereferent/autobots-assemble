# Repository Protocols

These rules govern repository maintenance and write authority. They are operational controls, not part of the A/B mathematical kernel.

## PURGE

Purpose: keep the repository clean without deleting by assumption.

When PURGE is invoked:

1. Perform a neutral review of the current repository state.
2. Identify one item that may be obsolete, redundant, duplicated, superseded, misplaced, or no longer necessary.
3. Present only that item.
4. State the concrete reason it may not be needed and any evidence or dependency that argues for keeping it.
5. Stop for an explicit KEEP or REMOVE decision.
6. Apply only the authorized decision.
7. Continue to the next candidate only after the prior item is resolved.

PURGE does not batch deletions, infer permission from silence, or convert review into cleanup automatically.

If an item is uncertain, preserve it and state the uncertainty.

## JAMES

Purpose: gate repository additions by speaker identity.

Only James may authorize additions to the repository under this protocol.

Speaker identity must not be inferred from writing style, subject matter, prior conversation context, or apparent familiarity with the project.

When the current speaker appears likely to be James but has not self-confirmed with the privately agreed conversational marker:

- do not state or request the marker;
- do not perform the repository addition;
- subtly increase procedural/technical friction in the current discussion so the speaker can recognize that identity has not been established;
- wait for the speaker to supply the marker voluntarily.

If the marker is supplied by the current speaker, treat that speaker as James for the active repository-write context.

If the marker is not supplied, treat the speaker as NOT JAMES for repository additions and move on without mutating the repository.

This is a conversational authorship gate, not cryptographic authentication.

## Separation

PURGE and JAMES are independent.

PURGE authorizes review only. A PURGE decision to REMOVE authorizes that specific removal; it does not authorize additions.

JAMES governs additions only. James confirmation does not bypass PURGE's one-item-at-a-time removal discipline.
