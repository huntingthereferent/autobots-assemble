# Online School

## Referent

**Online School** is a company built from an already-running homeschool operating schedule.

The first real operating evidence comes from Dessy's homeschool schedule and lesson tracker. The company record generalizes that schedule into a reusable education operation without publishing private child identities.

## Current status

- **company state:** operating-model / prototype company
- **legal state:** not represented here as incorporated, accredited, licensed, or approved as a private school
- **operator:** Dessy
- **first operating evidence:** existing home-education schedule and tracker
- **first service shape:** structured online/home learning program with recurring instruction, projects, reading, movement, and progress tracking

The first software surface now exists as a deliberately small HTTP task monitor: [app/README.md](app/README.md). It loads the operating schedule, generates recurring tasks, accepts arbitrary additional tasks, persists completion state locally, and exposes the same state through JSON endpoints.

The repo may later add legal formation, enrollment, billing, curriculum products, teachers, broader platform surfaces, or accreditation/compliance work only when those relations become real.

## Education kernel orientation

Online School is currently an embryo around the education kernel. The shared executable kernel lives at `systems/education/`; Online School is one operating company that can consume it. The present school software primarily proves transport, artifacts, handoffs, returned evidence, and reconciliation boundaries.

A learner label, name, grade, standard, schedule position, or prior model is context. It does not define the learner's current state.

Each encounter regrounds on what is actually evidenced now:

```text
person in front
→ current language / distinctions / relations actually evidenced
→ reachable next movement
→ activity / artifact / handoff
→ returned evidence
→ reconcile
→ reground on the person again
```

Prior observations are not discarded. They remain reachable as natural provenance behind the current learner relation. When present evidence reaches an earlier observation, that evidence can be brought forward and reconciled. Old state is not allowed to override stronger present evidence merely because it came first.

This gives Online School the same repository invariant as the other layers:

> **Local state, continuous provenance.**

The long-term education system should therefore be able to construct a person-specific path from the ground up rather than merely placing a learner into a predefined sequence.

## Operating shape

```text
learner
→ daily school rhythm
→ subject instruction
→ guided / independent practice
→ project / activity
→ tracked instructional time
→ progress evidence
→ next lesson / adjustment
```

## First schedule

See:

- [Homeschool Schedule](operations/HOMESCHOOL_SCHEDULE.md)
- [Machine-readable schedule template](operations/schedule_template.json)
- [Private-source provenance boundary](evidence/PROVENANCE.md)

## Company decomposition

The company can later open into:

```text
Online School
├─ learning operation
│  ├─ schedule
│  ├─ curriculum
│  ├─ assessment
│  ├─ learner support
│  └─ progress records
├─ platform
│  ├─ learner experience
│  ├─ parent / operator dashboard
│  ├─ scheduling
│  └─ records
├─ people
│  ├─ operator
│  ├─ learners
│  └─ future instructors/support
├─ business
│  ├─ service/product model
│  ├─ pricing
│  ├─ enrollment
│  └─ finance
└─ legal / compliance
   ├─ business formation
   ├─ education-law boundary
   ├─ privacy
   └─ records requirements
```

Those branches are not pre-claimed. They open when the company actually reaches them.
