# AI Protocol — PURGE

## Purpose

Keep the repository clean without deleting by assumption.

PURGE is a neutral review protocol. It does not convert review into automatic cleanup.

## Movement

When PURGE is invoked:

1. scan the current repository state neutrally;
2. identify one item that may be obsolete, redundant, duplicated, superseded, misplaced, generated noise, or no longer necessary;
3. present only that item;
4. state the concrete evidence for removal and any evidence for keeping it;
5. stop for an explicit KEEP or REMOVE decision;
6. apply only that decision;
7. continue only after the current item is resolved.

## Constraints

- no batch deletion by implication;
- silence is not authorization;
- uncertainty preserves the item;
- generated caches and replaceable artifacts may be recommended for removal, but still require the explicit decision;
- historical evidence is not treated as junk merely because it is old;
- a REMOVE decision authorizes only the named item.

PURGE governs removals/review only. It does not authorize repository additions.
