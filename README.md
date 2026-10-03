# Language Network

A persistent external operating environment for using AI across work, research, tools, and domains.

The repository is **not A/B itself**. A/B remains the recursively reusable mathematical operation and witness/evidence contract. This repository is an operational environment whose protocols are constrained by that shape: preserve the current referent, require admissible evidence for movement, expose walls instead of inventing continuity, preserve provenance, and make each output reusable as the next valid input under the same contract.

## Start here

For an AI session, read in this order:

1. [\`ENTRY.md\`](ENTRY.md) — how to enter the network.
2. [\`AB_CONTRACT.md\`](AB_CONTRACT.md) — what “using A/B” means here and what it does **not** mean.
3. [\`state/current.json\`](state/current.json) — the current preferred referent and next movement.
4. [\`protocols/README.md\`](protocols/README.md) — protocol routing.
5. The active work record or domain protocol reached from the current referent.

For a human review:

- [\`JOBS.md\`](JOBS.md) — browsable external-work ledger.
- [\`TASKS.md\`](TASKS.md) — current work view.
- [\`SCOPE.md\`](SCOPE.md) — compatibility scope notes from the earlier task environment.
- [\`evidence/archive/v0.17-summary.json\`](evidence/archive/v0.17-summary.json) — provenance summary for the packaged v0.17 archive.

## Layers

The layers are separate **referents**, not separate theories:

- **A/B boundary** — mathematical invariant and witness/evidence constraint.
- **Network** — append-only relations, snapshots, and movement records.
- **Protocols** — reusable contracts for entering, moving, hitting a wall, handing off, and returning.
- **Domain/work adapters** — job hunting, OSINT, coding, spreadsheets, sports, research, and future domains.
- **Work/evidence** — actual jobs, experiments, artifacts, tests, and historical snapshots.

A lower layer may be evidence for a higher layer. It does not automatically become the current referent.

## Core rule

**Current referent → admissible evidence → witnessed movement or explicit wall → preserved provenance → next referent.**

If the current evidence does not support movement, retain \`UNKNOWN\`/\`PARTIAL\` or emit a \`WALL\`. Do not manufacture the missing edge.

## Compatibility

The existing \`jobs/\` records remain valid work records. Older source and evidence from the packaged v0.17 environment are preserved as provenance rather than silently rewritten into the new architecture.
