# Architecture — Shared Kernel, Separate Lanes

The repository has one shared operating kernel and three intentionally separate human-goal lanes.

```text
                               SHARED KERNEL
              A/B · language · network · protocols · lenses
                    evidence · provenance · state
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
          THEORY / RESEARCH   OPEN SOURCE      MONEY / JOBS
                 │                │                │
             research/        open_source/       money/
             domains/         upstream issues    jobs/
             dives/notes      PRs/docs/tests     paid work
             experiments      community work     bids/deliverables
```

## Why three lanes

The same skill can serve different goals, and those goals should not silently replace one another.

**Theory / Research** asks:
> What is interesting, true, structurally useful, unresolved, or worth following?

**Open Source** asks:
> What public project can I contribute to under its own upstream rules?

**Money / Jobs** asks:
> What bounded external work can be completed, submitted, accepted, or paid?

## Shared kernel

All three lanes may reuse:

- A/B witness/evidence boundaries;
- language/operator phrases;
- handoff language;
- source research;
- the generic relation network;
- provenance;
- output lenses;
- tool/session protocols.

Shared machinery does not collapse the lane goal.

## Theory / Research

Typical outputs:

- research dives;
- theory notes;
- paper/source maps;
- experiments;
- domain dissections;
- unresolved questions.

No requirement to monetize or contribute upstream.

## Open Source

Typical outputs:

- public issues;
- bug fixes;
- documentation;
- tests;
- review/reproduction work;
- upstream pull requests;
- standards/RFC participation;
- scientific/open-data tooling;
- community-maintained infrastructure.

Payment may exist incidentally, but it is not assumed.

## Money / Jobs

Typical outputs:

- job opportunities;
- contracts/bounties;
- proposals;
- deliverables;
- acceptance tests;
- submission/payment state.

## Crossing lanes

A crossing is an explicit `HANDOFF.BOUNDARY`.

Examples:

```text
research dive
→ reusable public implementation
→ HANDOFF.BOUNDARY
→ open-source contribution candidate
```

```text
open-source issue has a bounty
→ compensation becomes primary
→ HANDOFF.BOUNDARY
→ money/job candidate
```

```text
open-source work reveals a novel question
→ HANDOFF.BOUNDARY
→ research dive candidate
```

The source lane remains provenance. The receiving lane re-validates the item under its own goal and witness contract.
