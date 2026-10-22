# State — preserved routing records

`current.json` currently contains a **historical** Continuity/live-feed routing record (`status: historical`). It is retained to explain an earlier source-specific context and its recorded next movement. **It is not an active repository-wide queue, a present project selection, or an instruction for a new session to continue that feed.**

The active problem is determined by the explicit request in the current conversation, following [ENTRY.md](../ENTRY.md) and [SCOPE.md](../SCOPE.md). A project's own source may separately record its current or last-verified experimental state. The two must not be silently conflated.

## Preservation rule

Keep past routing and provenance recoverable. If a future specifically authorized workflow requires a new current pointer, record its source, scope, date and status without rewriting the historical state to pretend it never existed. Historical evidence belongs with its source records, commits or the [evidence layer](../evidence/README.md).

For human-facing project descriptions, use [PROJECTS.md](../PROJECTS.md), not this historical JSON pointer.
