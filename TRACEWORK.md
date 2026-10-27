# Tracework

**Tracework** is a finite-system environment for carrying problems through defined states, relationships, handoffs, observations and evidence-backed continuation. It connects otherwise different kinds of work without requiring them to share one internal model. It was formerly described as the *workstation* or *AI-workstation*. The original finite mathematical and language-referent inquiry remains distinct; Tracework supports and records its experiments without renaming that research.

**GitHub is the public proof of concept and development preview, not the full standalone Tracework product.** This repository contains implemented runtime and journal components, source-edition tooling, finite examples, tests and source-owned research. The GitHub Pages viewer is a read-only demonstration of visible source records and GitHub execution, not a control surface for every private process. The larger mathematical architecture is a development target; individual formal properties are claimed only where their specific implementation and tests support them.

## Finite-system demonstration

A finite working context specifies the current referent, admitted inputs/actions, relationships and boundaries. A transition yields a return that can be inspected against expectations and required witnesses. Recorded evidence and ancestry determine what may continue. **Finite** describes the explicit scope of a particular working context; it is not a claim that the overall environment or every real-world problem has a globally finite state space.

The current GitHub demonstration exposes pieces of that pattern through the handoff runtime, append-only journal, finite A/B examples, source-linked research and read-only public viewer. Those pieces are connected by evidence contracts, not by a claim that all research lanes share the same mathematical theorem.

## Operating relationship

```text
real problem / original referent
  → source-owned inputs and bounded handoff
  → human, program, AI, machine or simulator
  → returned result with native evidence
  → append-only history and derived current state
  → inspect, reconcile, and continue from supported relationships
```

A lane preserves its own referent and source identity. Recorded movement, native task execution, mathematical evidence and successful CI checks are not interchangeable claims. Tracework can support multiple lanes while preserving what changed, what survived, the evidence path, and a return point. Its role in managing AI drift is to keep source and state traceable when conversational language or execution changes; no blanket drift-free claim follows.

## Source-owned implementation

| Responsibility | Reference |
| --- | --- |
| Complete-stack architecture and referent boundary | [Architecture](ARCHITECTURE.md) · [Category contract](CATEGORY_CONTRACT.md) |
| Handoffs, event history and evidence boundaries | [Runtime](runtime/README.md) · [Provenance](protocols/core/provenance.md) |
| Independent lane continuity | [Workspace](systems/workspace/README.md) |
| Source copying, branching and inspection | [Source edition component](systems/workspace/WORKSTATION.md) |
| Read-only execution and evidence presentation | [Tracework live](https://huntingthereferent.github.io/autobots-assemble/live/work.html) · [Viewer notes](docs/live/README.md) |
| Research that produces native witnesses | [Research](research/README.md) · [Repository index](README.md) |
| Durable public native evidence | [Original Actions artifact archive contract](docs/TRACEWORK_NATIVE_EVIDENCE_ARCHIVE.md) · [archive implementation](systems/workspace/github_native_evidence_archive.py) |

## Public Actions evidence retention

This GitHub version must retain the **original source-owned witness**, not just an expiring Actions URL or a derived summary. The [bounded native evidence archive](docs/TRACEWORK_NATIVE_EVIDENCE_ARCHIVE.md) records an exact original run, source commit, artifact ZIP SHA-256, member hashes, and original success/failure conclusion; it uses non-clobbering, run-specific GitHub Releases and checks the published bytes again. Approved ARC, WORLD31, and W13 workflows are the initial scope. A failed archival attempt is an explicit evidence boundary. The preservation workflow only becomes operational once merged into the default branch; private operator journals must not be published to the public archive.

## Status and evidence limits

Tracework is an operating environment with implemented local components and public execution/source views. Individual capabilities and trials have their own native verifiers. The public GitHub Actions viewer does not expose private journals, infer unrecorded work, or independently verify every result. This is not a claim that every integration runs as one permanently hosted, fully unattended loop. Nor does an unclosed loop mean the recorded operating subsystems are merely proposed.

## Canonical naming

- **Public name:** Tracework.
- **Historical and technical identifiers retained:** workstation; Process Workstation; `ProcessWorkstation`; `systems/workspace/`; files named `workstation-*`; journal schema and event identifiers. Preserve these where changing them would break source imports, replay, provenance, or evidence.
- **Not renamed:** Language Referent, finite A/B mathematics, ARC, WORLD, NIH and other domain-specific research.
- **Repository address remains:** `huntingthereferent/autobots-assemble`. A GitHub repository slug is not a product name.

Current prose and viewer headings should use **Tracework** for the overall environment. Old code identifiers and dated historical quotations remain intact. If an older document says *workstation*, it refers to this evolving system or a specifically named subsystem—not to another newly built product.
