# Continuity Layer

A continuity layer for moving through people, conversations, time, work, knowledge, connected systems, and the wider internet without losing the thread.

Continuity does **not** try to put the internet inside itself. People use Continuity while moving through external pages, feeds, searches, videos, forums, maps, marketplaces, job boards, documentation, and tools. Those things stay external; Continuity preserves the relational path through them so the current referent, source, branch, and outputs remain traceable.

The homepage is a shared entrance: people log in once, then move across conversations, school, calendar, work, research, jobs, projects, household systems, companies, and external internet surfaces. Each local system keeps its own state, each external source stays externally owned, and Continuity keeps the thread intact as movement crosses between them.

## Human areas

The portal does not expose repository folders as its main categories. It collapses the repo into ordinary entrances:

```text
LEARN
BUILD
WORK
EXPLORE
CONNECT
WORLD
ORGANIZE
MAKE MONEY
CREATE
HEALTH / LIFE
LIBRARY
TOOLS
```

These areas are peers, not a hierarchy with education or production at the center. Each area may expose existing capabilities, let a person manipulate the pieces underneath, and produce reusable tools or outputs. Movement can cross between areas whenever the current referent requires it.

Connected systems such as Online School, Calendar, Personal Operations, Research, Jobs, and Factory remain source systems underneath those areas rather than becoming the site's top-level ontology.

## Traverse the internet without losing the thread

News, social media feeds, search results, videos, forums, documentation, marketplaces, job boards, maps, public data, and external apps are **surfaces Continuity moves through**, not subsystems Continuity tries to recreate.

The core movement is:

```text
current referent
→ touch an external thing
→ preserve why it was touched and what relation it added
→ move to the next relevant thing
→ keep the prior path reachable
↺
```

A trace is richer than browser history: it preserves the relational reason for movement, source locator, current referent, branch ancestry, admitted evidence/artifacts, and what changed. See [protocols/core/traversal.md](protocols/core/traversal.md).

## Live mixed-feed frontage test

The homepage can project live external movement without persisting the feed contents. The first public, credential-free test adapters are:

- Reddit public RSS;
- Lemmy public API;
- Hacker News public API;
- Reuters YouTube Atom feed;
- BBC News RSS.

Unavailable providers remain visible as unavailable rather than receiving generated stand-in data. At the current host, Bluesky's public API returns HTTP 403, so it is shown as unavailable.

The frontage exposes two useful views over the same live items:

- **Balanced** — round-robin across provider streams so high-volume feeds do not erase slower sources;
- **Latest** — strict cross-source chronology so source-volume collisions remain observable.

Live items do not have one exclusive category. Their identity is relational:

```text
provider
publisher
medium
roles[]
topics[]
```

For example, a Reuters report carried by YouTube is simultaneously provider=`YouTube`, publisher=`Reuters`, medium=`video`, and role=`news`. The same item can therefore appear in both News and Video projections without being duplicated.

Opening an external item records a bounded traversal touch and then opens the original external source. The feed itself remains ephemeral.

## Start here

1. [COMPLETE_STACK.md](COMPLETE_STACK.md)
2. [CATEGORY_CONTRACT.md](CATEGORY_CONTRACT.md)
3. [ENTRY.md](ENTRY.md)
4. [AB_CONTRACT.md](AB_CONTRACT.md)
5. [state/current.json](state/current.json)
6. [capabilities/README.md](capabilities/README.md)
7. the active work/evidence reached from the current referent

## Core structure

- **Complete Stack** — top-level problem orientation.
- **capabilities/** — broad problem-spaces already demonstrated or being expanded.
- **work/** — concrete problems and projects.
- **companies/** — persistent operating organizations that may contain operations, products/services, people, assets, finance, compliance, and work.
- **artifacts/** — working representations produced by traversal: programs, CAD-like geometry, system landscapes, math models, schematics, BOMs, tests/measurements.
- **foundation/** — preserved demonstrated evidence.
- **research/**, **open_source/**, **money/** — goal/source lanes for work; **jobs/** holds only currently retained external opportunities.
- **protocols/** — reusable bounded operating contracts.
- **language/** — interpretation/rendering of human language.
- **network/** — preserved relation structures.
- **runtime/** — live cross-layer handoffs, append-only events, derived state, and task/job/command projections.
- **systems/** — concrete operating systems that keep their own local state and exchange supported movement through the shared handoff carrier.
- **activations/** — explicit human-language entrances into current ecosystem state.
- **state/** — current routing pointer.
- **views/** — read-only/generated projections.
- **design/visual-provenance/** — reusable visual witnesses, extracted visual grammar, surface bindings, and web-surface contracts so interfaces preserve visual provenance instead of drifting into generic AI aesthetics.
- **domains/** — specialized adapters only when a distinct domain witness contract is actually needed.

## First capability proof

The first broad capability proof is **Programs**.

The program foundation demonstrated shared structure across unlike program shapes, composition, relation graphs, bounded recurrence, provenance, and external effects/ports.

It is now frozen as evidence. It should be reopened only when a real problem exposes a missing relation.

## Current expansion

The next broad expansion is toward **integrated physical systems / machines**, where complete-stack traversal must survive non-digital layers without pretending simulation or placeholders are physical witnesses.

## Provenance invariant

**Local state, continuous provenance.**

Every layer keeps its own native state and meaning. Cross-layer continuity comes from preserved relational ancestry, not from forcing unlike systems into one universal schema. See [protocols/core/provenance.md](protocols/core/provenance.md).

## Core rule

**current referent → required relation → enter required layer → witness/model/build/measure → preserve provenance → return result as valid input → continue**

The current referent stays front-facing; prior movements remain reachable behind it as provenance. Do not stop merely because the next dependency belongs to another discipline.
