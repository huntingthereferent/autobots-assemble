# Visual Provenance

Visual provenance preserves **why a surface looks the way it looks**.

It is not a screenshot archive and it is not permission to copy another product. A visual witness is observed, reduced to a reusable visual grammar, and then translated into the local system.

The purpose is to prevent visual drift—especially generic AI-generated interfaces—while preserving source, distinctions, adaptation decisions, and the boundary between inspiration and implementation.

## Movement

```text
visual witness
→ observed visual relations
→ extracted visual grammar
→ approved visual template
→ surface binding
→ implementation
→ visual review
→ revised template when evidence changes
```

## Repository structure

```text
design/visual-provenance/
  schema/
    visual-template.schema.json
    surface-binding.schema.json
  templates/
    <template-id>.json
    <template-id>.md
  registry.json
  tests/
    test_visual_provenance.py

<website-or-app>/
  visual-provenance.json
```

A **template** owns the reusable visual grammar.

A **surface binding** says which template a concrete page or application surface uses, what it preserves, and what it deliberately changes.

## Required provenance

Every template records:

- the visual layer/category;
- source witnesses and observation dates;
- observed relations rather than copied implementation details;
- layout, hierarchy, density, typography, controls, surface treatment, and motion;
- anti-patterns / anti-AI constraints;
- adaptation rules;
- confidence and review status.

Every surface binding records:

- the concrete surface;
- its approved template;
- local additions required by the product/domain;
- deliberate deviations;
- the last visual review.

## Boundary

Visual provenance does **not** mean pixel copying.

Do not preserve logos, brand marks, proprietary illustrations, copyrighted copy, or distinctive trade dress as implementation assets. Preserve the relations that made the witness useful: hierarchy, density, grouping, rhythm, interaction clarity, restraint, print behavior, and similar visual structure.

A source witness is evidence. The local implementation must still belong to the local system.
