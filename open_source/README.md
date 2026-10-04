# Open Source Lane

This lane is for contributing to public/open-source projects.

Yes, people still do this constantly: code, docs, tests, issue triage, reproductions, reviews, tooling, scientific software, standards work, and community-maintained infrastructure all receive outside contributions.

## What belongs here

- public `help wanted` / `good first issue` work;
- bugs/features explicitly open to outside contribution;
- documentation/tests/reproduction work;
- scientific and research software contributions;
- public tooling and infrastructure;
- standards/RFC/community proposals;
- open-data utilities and maintenance.

## What does not automatically belong here

- paid client work → Money / Jobs;
- a random academic rabbit hole → Theory / Research;
- an issue we merely notice → not active until contribution scope/rules are checked;
- a private repository → only if we legitimately have access and the project is intentionally collaborative.

## Standard lifecycle

```text
DISCOVERED
→ ORIENTED
→ PICKED_UP
→ IN_PROGRESS
→ PR_OPEN
→ REVIEW
→ MERGED / DECLINED / CLOSED
```

Do not collapse these states:

```text
found ≠ invited
invited ≠ picked up
implemented ≠ tested
tested ≠ submitted
submitted ≠ reviewed
reviewed ≠ merged
merged ≠ released
merged ≠ paid
```

## Before doing significant work

Read the project's contribution boundary:

- `CONTRIBUTING.md`
- issue/PR templates
- maintainer instructions
- tests/lint/build requirements
- code of conduct
- whether the issue is already assigned/in progress

For a large or unlabeled change, asking maintainers before building may be the correct next movement.

## Durable records

Each contribution we actually pick up can live under:

```text
open_source/contributions/
└── OSS-0001_short-slug/
    ├── contribution.json
    └── CONTRIBUTION.md
```

That record should preserve upstream repo/issue/PR links, scope, tests, review feedback, status, and next movement.
