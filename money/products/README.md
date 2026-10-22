# Products — reusable candidates and implementations

This directory records product shapes that could be adapted or delivered for an external need. A recorded candidate is not automatically a working product, a sale, a contract or recurring revenue.

## Products versus client-specific work

- `money/products/` keeps reusable source, design, tests, evidence and scoped variants.
- A real client-specific request or sale should have its **own** requirement, authorization, acceptance and payment evidence. The old `jobs/` listing directory was retired; no current job ledger is assumed.
- Product versions should preserve what changed, what was retained, the relevant source lineage and any test limitations.

A product is an implementation, not a definition or proof of the [Language Referent](../../LANGUAGE_REFERENT.md).

## Product record

Create files when they are needed by the actual project rather than empty placeholder directories.

```text
money/products/P###_<name>/
  PRODUCT.md      # problem, intended user, current state and boundaries
  app/            # implementation source when present
  evidence/       # tests, artifacts and acceptance records when present
  variants/       # supported product variants when present
```

## Recorded candidates

- [P001 — Service Workflow](P001_service-workflow/PRODUCT.md) — parked, unvalidated candidate.
- [P002 — Business Health Check](P002_business-health-tracker/PRODUCT.md) — source-recorded working proof derived from an external MVP brief; this description is **not** evidence of sale or payment.

See [money overview](../README.md) and [full project guide](../../PROJECTS.md).
