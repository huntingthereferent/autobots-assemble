# Products

This directory tracks reusable products whose primary goal is external economic value.

A product is not A/B itself. A/B may be used to trace and build a product, but the resulting software, template, service, or artifact remains an implementation/evidence layer.

## Boundary

Products differ from one-off job records:

- `jobs/` records externally bounded work for a specific opportunity or client.
- `money/products/` records reusable product shapes that can be instantiated, customized, sold, or extended.
- A client-specific sale can create a job record that points back to the product it instantiates.
- Product changes must preserve provenance: what existed, what changed, what survived, and what was newly introduced.

## Product record

Each product gets its own directory:

```text
money/products/P###_<name>/
  PRODUCT.md
  app/          # source when implementation begins
  evidence/     # tests, screenshots, acceptance records when needed
  variants/     # client/config variants when they become real
```

Do not create empty directories in advance. Add each layer only when the trace reaches it.

## Current products

- [P001 — Service Workflow](P001_service-workflow/PRODUCT.md) — parked unvalidated candidate created before an external product scan.
- [P002 — Business Health Check](P002_business-health-tracker/PRODUCT.md) — working proof traced from a current $300 external MVP brief.
