# P001 — Service Workflow

**status:** candidate  
**goal lane:** money / products  
**current referent:** a small service business has incoming work that must be carried to a closed paid outcome.

## Witnessed product relation

```text
lead -> quote -> accepted -> scheduled -> completed -> paid
```

The first build must preserve this movement before optional features are added.

## Minimal objects

- customer
- work item
- current state
- quote amount
- scheduled date
- notes / evidence
- payment state
- transition history

## Build rule

Start from the relation, not from a preselected application architecture.

For each requested customization:

1. establish the current valid product state;
2. identify the new relation the customer actually requires;
3. preserve everything that survives;
4. introduce only what is necessary for the new relation;
5. record the change and its witness;
6. revalidate the full movement.

## First commercial target

A configurable small-business workflow application that can be renamed and reshaped for a specific service business without rebuilding the kernel from zero.

Examples of surface vocabulary may differ while the underlying relation survives:

```text
detailer:     inquiry -> estimate -> booked -> detailing -> finished -> paid
cleaner:      lead -> walkthrough -> quote -> scheduled -> cleaned -> paid
photographer: inquiry -> consultation -> deposit -> shoot -> delivered -> paid
```

These examples are not separate products unless the trace reaches a real divergence that requires one.
