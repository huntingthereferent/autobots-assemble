# Unstupid — frozen project provenance

**Recorded:** 2026-10-23
**Status:** Design baseline, not an implemented connector
**Product name:** Unstupid (confirmed 2026-10-23)
**Technical namespace:** `math`
**Origin:** James's proposal to give AI tools a mathematical reference they can return to across conversations, clients and research lanes. This document freezes the design discussed before implementation.

## Intent

Build a usable interface *around* the existing finite mathematical constructions. AI participants submit actions, interpretations, objections and results. The interface returns source-pinned mathematical evaluations, records what participants actually said or did, and supports reproducible continuation. An objection is an observable protocol input, not something the interface must suppress. The protocol being finite does not imply that an entire AI system is finite-state.

The interface is not a new chatbot and does not replace ChatGPT, coding assistants or workstation workers. It is an executable reference and connector usable by them.

## Frozen architecture

1. **Reference engine:** source revision, finite state, permitted operations, declared relations and constraints, transition evaluator and comparator.
2. **Interaction protocol:** READY → PROPOSED → EVALUATING → RETURNED → CONTINUING; allow repeated cycles and explicit mismatch, unresolved and invalid returns.
3. **Adapters:** command-line interface first; local API and MCP-compatible client integration next; independently test multiple clients.
4. **Evidence/continuity:** retain input, pinned source, evaluator output, participant output, mismatch, replay and handoff. Never confuse an AI's implementation choice with a mathematically derived consequence.

## Proposed operations

- `math.open`: load a named construction and source revision.
- `math.state`: read the declared state.
- `math.step`: execute a permitted operation.
- `math.compare`: evaluate a proposed relationship or result.
- `math.observe`: record an external observation without promoting it to a theorem.
- `math.handoff`: export and restore a reproducible continuation.

Returns distinguish MATCH, MISMATCH, UNKNOWN/UNRESOLVED and INVALID, with scope and evidence. These are proposed protocol categories, not existing API guarantees.

## Proposed layout

```text
interfaces/math/
  engine.py
  protocol.py
  references.py
  compare.py
  handoff.py
  server.py
  adapters/
  tests/
  README.md
  PROJECT_PROVENANCE.md
```

Reuse, do not copy, source mathematics and handoff facilities already in the workstation: `work/arc_like_maze/math.py`, `runtime/handoff.py`, `systems/workspace/main_referent_selector.py`, `protocols/core/handoff.md`, `LANGUAGE_REFERENT_CONTRACT.md`.

## Four implementation lanes

| Lane | Output | Acceptance |
| --- | --- | --- |
| A — Mathematics | Executable reference engine | Reproduce the original finite A/B witness exactly |
| B — Protocol | Typed finite interaction | Distinguish valid result, mismatch, unresolved and invalid proposal |
| C — Connector | Local API and MCP-compatible adapter | Two independent clients query the same pinned reference |
| D — Continuity | Source pins, replay and handoff | Fresh session resumes without conversational memory |

## First experiment

Use the original finite convergence witness: two action sequences `BBAA` and `ABABB` reach state `[2, 2, 1]` in the specified construction. Original source: [operators](https://github.com/huntingthereferent/autobots-assemble/blob/702326a0d9c0dc8e9225b4cdd4d9a8c333b778f5/work/arc_like_maze/math.py), [receipt](https://github.com/huntingthereferent/autobots-assemble/blob/702326a0d9c0dc8e9225b4cdd4d9a8c333b778f5/views/motion/convergence-receipt.json), [step verifier](https://github.com/huntingthereferent/autobots-assemble/blob/702326a0d9c0dc8e9225b4cdd4d9a8c333b778f5/systems/workspace/ab_relational_cluster.py).

Have independent AI clients propose actions and interpretations against the same pinned source. Preserve their responses; detect changed assumptions and mismatched results; verify a fresh-session handoff. Do not hardcode the expected receipt as the evaluator's answer.

## Design boundaries

- This document freezes a **proposal**, not proof of successful multi-client continuity.
- The mathematics is a source of defined relationships; AI-generated code and workflows are not automatically consequences of it.
- Do not start with a dashboard; prove command-line behavior and replay first.
- Product name is **Unstupid**. Keep the technical directory `interfaces/math/` and `math` operation namespace stable.
- Subsequent design changes should be recorded as amendments rather than silently rewriting this initial baseline.

## Naming amendment — 2026-10-23

James selected **Unstupid** as the product name. This naming amendment does not change the frozen architecture, scope, or acceptance criteria.
