# Tracework

**Tracework** is the public name for the existing research continuity, execution, observation and provenance environment developed in this repository. It was formerly described as the *workstation* or *AI-workstation*. The original finite mathematical and language-referent inquiry is separate; Tracework supports and records its experiments without renaming that research.

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

## Status and evidence limits

Tracework is an operating environment with implemented local components and public execution/source views. Individual capabilities and trials have their own native verifiers. The public GitHub Actions viewer does not expose private journals, infer unrecorded work, or independently verify every result. This is not a claim that every integration runs as one permanently hosted, fully unattended loop. Nor does an unclosed loop mean the recorded operating subsystems are merely proposed.

## Canonical naming

- **Public name:** Tracework.
- **Historical and technical identifiers retained:** workstation; Process Workstation; `ProcessWorkstation`; `systems/workspace/`; files named `workstation-*`; journal schema and event identifiers. Preserve these where changing them would break source imports, replay, provenance, or evidence.
- **Not renamed:** Language Referent, finite A/B mathematics, ARC, WORLD, NIH and other domain-specific research.
- **Repository address remains:** `huntingthereferent/autobots-assemble`. A GitHub repository slug is not a product name.

Current prose and viewer headings should use **Tracework** for the overall environment. Old code identifiers and dated historical quotations remain intact. If an older document says *workstation*, it refers to this evolving system or a specifically named subsystem—not to another newly built product.
