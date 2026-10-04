# Protocol — Open-Source Contribution

## Protocol ID

`opensource.contribution`

## Current referent

One concrete upstream public contribution opportunity.

## Goal

Produce a contribution that satisfies the upstream project's stated contribution and acceptance boundary while preserving attribution, provenance, and review state.

Payment is not part of the default goal.

## Admission witnesses

Before moving from discovery to active work, establish:

- identifiable upstream project/repository;
- concrete issue/problem/proposal;
- evidence that outside contribution is permitted or reasonably invited;
- contribution/setup/testing rules when provided;
- a bounded proposed change.

For a large or unlabeled change, maintainer alignment may be the next movement instead of implementation.

## Movement

```text
discover
→ orient to project rules
→ select bounded issue
→ reproduce / understand
→ implement
→ test
→ submit upstream
→ respond to review
→ merged / declined / closed
```

Each stage is distinct provenance.

## Result states

- `MOVE` — the next contribution step is supported.
- `WALL` — access, setup, maintainer decision, required fixture, or another dependency blocks movement.
- `UNKNOWN` — expected behavior or contribution boundary cannot yet be resolved.
- `PARTIAL` — useful work exists, but upstream testing/review/acceptance is incomplete.

## Integrity distinctions

```text
found ≠ invited
invited ≠ picked_up
implemented ≠ tested
tested ≠ submitted
submitted ≠ reviewed
reviewed ≠ merged
merged ≠ released
merged ≠ paid
```

## Money boundary

If a bounty, sponsorship, contract, or hiring opportunity appears, record it as evidence. Do not change lanes unless compensation becomes the user's primary goal.

## Research boundary

If the contribution exposes a theoretically interesting question, create a research handoff candidate rather than converting the contribution itself into a theory claim.

## Closure

The current contribution state, feedback, and next upstream action remain valid input to this same protocol on the next pass.
