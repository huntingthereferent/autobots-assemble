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
- Hacker News public API;
- Reuters YouTube Atom feed;
- BBC News RSS.

Unavailable providers remain visible as unavailable rather than receiving generated stand-in data. At the current host, Bluesky's public API returns HTTP 403, so it is shown as unavailable.

The frontage exposes two useful views over the same live items:

- **Balanced** — round-robin across provider streams so high-volume feeds do not erase slower sources;
- **Latest** — cross-source chronology before grouping; groups occupy their first witness's position and retain witness order inside.

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

The frontpage also offers compact, expandable tickers for every provider and
the All Feeds, News, Social, Video and Community layers. Each ticker shows the
latest dated headline, witness count and contributing feed count in the fetched
sample. Expansion shows publication range, fetch time, undated-item count and
every original source card. These are bounded sample summaries, not whole-layer
population totals, performance rankings or merged claims. Layers can overlap.
Tickers stay independent of the main feed filter so their layer scope stays
consistent. Unavailable providers remain explicit, and no item is fabricated.

Choose tickers supports individual visibility, Show all and Hide all (including
future providers while Hide all is active). Only display identifiers are saved
in browser local storage; headlines and other feed content remain ephemeral.
Open ticker sections survive refresh. Browser-local choices are not yet synced
between devices or accounts.

Broad ticker layers now include World, Industry / Factory, Markets, Sports,
Work, Learning, Research, Personal / Household and Culture / Social, with 39
registered subcategories. These are selectable nested entrances; a parent may
be hidden while a selected child stays visible on its own. Sources nest under
each domain, retaining native claims and click targets. Open category and
source branches survive refresh.

Only explicit item topics admit domain membership. For example,
`sports:results`, `markets:stocks` or `world:countries:usa:missouri` put the same
report into the relevant overlapping projections; namespaced paths generate
their concrete ancestry without needing a stored map of every country or city.
Each parent counts its native witnesses once, independently of how many child
categories they touch. Child totals must not be added as a disjoint partition.
Generic news roles, provider names and headline keywords do not assign domains.
Items without domain labels remain reachable in All Feeds and source tickers.

Nine public report feeds now connect the broad domain layers:

| Layer | Report source |
| --- | --- |
| World | BBC World |
| Industry / Factory | BLS Productivity and Costs |
| Markets | SEC Press Releases |
| Sports | BBC Sport |
| Work | BLS Job Openings and Labor Turnover |
| Learning | BBC Education |
| Research | NSF Research News |
| Personal / Household | CPSC Product Recalls |
| Culture / Social | Library of Congress Performing Arts |

These adapters record their documented publisher feed scope in `topic_basis`,
including feed and documentation URLs. Cards display this basis. Native titles,
excerpts, URLs, publication dates, authors and category labels remain separate
source witnesses. Scope membership does not establish claim-specific subject
classification, stock prices, sports scores, learner progress or personal tasks.
Configured sources remain nested even when unavailable or returning no items.
Unconnected subcategories explicitly show No connected witnesses. Validating
native category mappings, internal-system witnesses, measurement units,
temporal changes and comparable performance remains separate work. The
100-report conservation check is a synthetic test fixture, not live report data.

Country-native report connections also include:

| Source jurisdiction | Publisher feeds | Layer scopes |
| --- | --- | --- |
| Canada | Statistics Canada manufacturing, labour, education, families/households, science/technology | Industry, Work, Learning, Household, Research |
| Australia | Reserve Bank of Australia media releases and research papers | Markets, Research |
| Germany | Deutsche Bundesbank latest releases and discussion papers | Markets, Research |
| Japan | Bank of Japan latest releases, Japanese and English editions | Markets |
| Brazil | Agência Brasil latest news, education and sports, Portuguese edition | World, Learning, Sports |

These country feeds additionally enter `world:countries:<country>`.
`country_basis: publisher_jurisdiction` describes the institution's jurisdiction,
not an inferred location for every claim. `language` records the selected feed
edition, not automatic language detection; original text is retained without
translation. Configured country branches remain present through outages and
empty samples. Coverage is partial: these five country connections do not fill
all countries or all categories. Other countries, additional native-language editions,
structured statistical series, units and cross-country comparability remain
unresolved. Official feed documentation is linked in each source's metadata.

Shared coverage is grouped only in the browser projection, after balancing and
role/medium filtering. A group requires either the same HTTP(S) source URL
(fragment ignored, query preserved, homepages excluded), or the same normalized
headline across every witness with valid publication times spanning at most 24
hours. Headline comparison changes only case and whitespace; short headlines
(under 32 characters or six words) and ellipsis-truncated headlines are excluded.
The group states its matching basis rather than asserting an agreed event or
claim. Every contributing card remains visible with its own source identity,
headline, excerpt, metadata and traversal click target. No item deduplication,
claim synthesis, durable event ID or feed storage is introduced.

Unresolved: paraphrased reports; different URLs/headlines for the same event;
Reddit RSS posts whose article URL exists only in the removed transport wrapper;
redirects and tracking-query variants; missing/invalid dates for headline-only
matches; repeated generic headlines that pass the length gate. Exact headline
matching is evidence of related coverage, not proof of event identity. Group
membership may change with projection order when several competing matches
exist; groups cannot join through a transitive URL/headline bridge.

Focused checks: `python -m unittest discover -s network/tests -v` and
`node --test network/tests/test_live_event_grouping.js`. The grouping tests execute
the browser functions with a small DOM harness and verify witness conservation,
native click targets, filters, refresh replacement, time bounds and non-transitive
matching. They do not establish semantic equivalence or live provider availability.

The current frontage favors information density over application-style chrome: live headlines are directly clickable, the separate action-button row is removed, cards use tighter spacing, and bounded source excerpts may carry up to 640 characters. Where a provider exposes useful native text (for example Reuters descriptions in YouTube's Atom feed), that text is preserved in the live projection. Provider-specific transport/UI noise is normalized only where the boundary is clear: Reddit's RSS submission/link/comment wrapper is removed when it carries no source content, and Reuters/YouTube promotional/social tails are removed while keeping the useful description. The original external source remains the authority and is still one click away.

## Start here

1. [COMPLETE_STACK.md](COMPLETE_STACK.md)
2. [CATEGORY_CONTRACT.md](CATEGORY_CONTRACT.md)
3. [ENTRY.md](ENTRY.md)
4. [AB_CONTRACT.md](AB_CONTRACT.md)
5. [state/current.json](state/current.json)
6. [capabilities/README.md](capabilities/README.md)
7. the active work/evidence reached from the current referent

## ARC-like mathematical construction

The math-first [inverted A/B world-construction experiment](work/arc_like_maze/README.md)
generates finite candidate transition systems, automatically aligns distinct
worlds, and now tests construction operators one layer above the state graphs.
An exhaustive affine scan certifies closure for 48 reversible affine maps.
The nonlinear construction expands this to the full 384 reversible maps preserving
the same five A/B equivalence classes, with 336 nonaffine transformations.
Cross-dimensional construction now witnesses transition-preserving projections,
three-turn hidden-fiber cycles, and same-depth alignment squares without treating
higher and lower worlds as identical. The inverse-limit model proves the declared
A/B actions remain coherent at every depth and that the nine parameter towers
retain five projectively compatible relational classes. A nonlinear gauge now
constructs three distinct but exactly aligned world laws in a closed cycle;
a split nonlinear coupling supplies a new class witnessed by different
B-fixed-state counts at depth four. The next inverse construction enumerates
81 two-coupling worlds into 21 exact *origin-rooted* A/B classes.
The third independent coupling constructs 729 worlds and 85 rooted classes;
a fourth-coupling stress test reaches 6,561 worlds and 341 classes.
The chosen rooted-class permutations cycle after 36 and 648 turns
respectively, but these do not imply full-state equivalence when dormant
coordinates never move on the origin orbit. A fixed-point-count theorem
now rules out a terminal **finite depth** if arbitrary independent
coupling extensions remain admissible. The coinductive process layer
compares complete repeating construction-rule streams across every depth:
81 two-turn templates form 34 diagonal A/B process classes, with four
nontrivial templates closed under a one-turn shift. The process-operator layer
now certifies a four-element period-two coordinate-gauge group: all 324
template-to-gauge alignments and 1,296 gauge compositions survive. Re-rooting
by shifting, or adding the same coupling table to both processes, can break
previously valid equivalence despite being reversible on rule descriptions.
Root transport now carries the incoming scale through a shift using an explicit
marked A/B boundary: 81 two-rule templates form 23 transported equivalence
classes, with five shift-fixed classes and nine exchanged class pairs.
The underlying fixed-root API is unchanged, and arbitrary rule addition still
breaks equivalence. The marked-operator layer now verifies that boundary-aware
coordinate gauges compose and commute with witness-carrying shifts: eight
period-two gauges, 5,184 composition checks, 256 interchange squares, and
11 focused tests. A marked-quotient audit now distinguishes **36**
eight-gauge orbits from **34** coinductively aligned classes of **270**
marked process objects. Two finite-head witnesses bridge the difference,
and the existing stemmed-gauge system realizes both without losing the
original marked-arrow witness. This is operator-level coherence, not a
universal shift group or unbounded A/B closure. Finite-stem diagonal gauges now also compose
and commute with transported shifts; mixed operator words normalize to one
forward shift and combined endpoint gauges. Local focused tests check 12
stemmed gauges, 11,664 compositions, 864 interchange squares, and 340 short
mixed operator words, without declaring any erased process prefix recoverable. Arbitrarily long matching prefixes are not
treated as an all-depth certificate. The non-diagonal marked-world extension now explicitly conjugates A/B
by `H_c(x)_2=x_2+c*x_1^2`, producing three different concrete laws
that remain fully aligned at every dimension. Two cannot be encoded
as an old one-variable `Process` B coupling: this is a failure of the
old representation, **not** evidence of A/B inequivalence. The model
transports the original coinductive marked-arrow witness through the
nonlinear state maps and preserves its boundary under shifts. The
[two-predecessor extension](work/arc_like_maze/WINDOW_TWO.md) compiles
those non-diagonal B laws exactly into nine-entry coupling tables,
while an independently edited table changes full depth-three B-fixed
state counts from nine to six. This separates a representation
expansion from a genuinely inequivalent world. A further deliberately
bounded 12-world construction now gives **four** complete full-state A/B
classes, three nonlinear shear representatives per class. At depth three,
their B-fixed-point signatures are 9, 6, 3, and 0. The shear constructor
is a three-turn loop within each class; independent support expansion
moves between inequivalent classes and reaches an explicit scoped wall.
A second independent coupling at q0(0,0) creates **24 worlds in eight
full-state classes**. The original Fix(B) count collides, but
Fix(B^3) distinguishes the new relation: 27 versus 18 fixed states
at depth three, despite equal one-step fixed-point counts. Each
class retains three all-depth shear-conjugate worlds.
A balanced third coupling at q0(1,0)/q0(1,1) preserves
both Fix(B) and Fix(B^3). The first distinguishing
fixed-point-count word is AABAB (nine versus three fixed states
at depth three); no shorter word count separates the pair.
The [36-world extension](work/arc_like_maze/WINDOW_WORD_COLLISION.md)
certifies **12 full-state classes**, with 108 aligned
ordered pairs and 1,188 invariant-obstructed ordered pairs.
Completing both edits produces [48 constructed worlds](work/arc_like_maze/WINDOW_COMBINED.md):
**14 full-state A/B classes, but 16 origin-preserving classes**.
At two supports the previously separated branches share an exact
state conjugacy that *moves the origin*, with positive-word witnesses
proving rooted non-equivalence. A new six-letter word ABABAB separates
the same branches at two other supports.
This is a scoped
mathematical result, not universal inverse A/B closure or native ARC execution.
Focused tests:
`python -m unittest network.tests.test_arc_like_inverse_ab network.tests.test_arc_like_alignment network.tests.test_arc_like_operators network.tests.test_arc_like_affine_scan network.tests.test_arc_like_nonlinear network.tests.test_arc_like_vertical network.tests.test_arc_like_inverse_limit network.tests.test_arc_like_gauge_construction network.tests.test_arc_like_coupling_family network.tests.test_arc_like_third_coupling network.tests.test_arc_like_process_alignment network.tests.test_arc_like_process_family network.tests.test_arc_like_process_operators network.tests.test_arc_like_root_transport network.tests.test_arc_like_marked_operator_system network.tests.test_arc_like_stemmed_operator_system network.tests.test_arc_like_marked_quotient network.tests.test_arc_like_nondiagonal_transport network.tests.test_arc_like_window_two network.tests.test_arc_like_window_family network.tests.test_arc_like_window_branch network.tests.test_arc_like_window_word_collision network.tests.test_arc_like_window_combined -v`.

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
