# Core Protocol — Traversal

Continuity is used to move through things without losing the thread.

It is **not a container for the internet**.

News sites, social feeds, search engines, videos, forums, documentation, marketplaces, job boards, maps, public data, external apps, and other sources remain where they are. Continuity preserves the relational path made while a person moves through them.

## Core movement

```text
current referent
→ touch something external
→ observe the relation it adds
→ preserve the touch/path
→ move to the next relevant thing
→ keep prior touches reachable behind the new current referent
↺
```

A touch does not imply ingestion, ownership, agreement, endorsement, or permanent storage of the external thing.

The invariant is:

> **External state stays external; Continuity preserves the trace of movement through it.**

## Touch

A **touch** is the smallest useful record that Continuity interacted with something while following a referent.

Examples:

- opening a news article;
- following a social post into a reply thread;
- moving from a search result into documentation;
- opening a company page from a job listing;
- following a cited paper;
- opening a product from a review;
- moving from a map result to a local business;
- following a video into a referenced source.

A touch may preserve, when available:

- external locator or provider reference;
- source/surface kind;
- observation time;
- current referent before the touch;
- relation/reason that caused the touch;
- bounded title/label/metadata needed to identify what was touched;
- evidence or artifact references deliberately admitted;
- what changed in the current relation;
- what remained unresolved;
- parent/previous touch;
- next movement when one occurs.

Do not copy an entire external service into Continuity merely because Continuity touched it.

## Trace

A **trace** is the reachable ancestry of touches for a movement.

```text
question
→ search
→ result
→ article
→ company
→ person
→ post
→ document
→ tool
→ output
```

The user may see a simple current view, but the path remains reconstructable enough to answer:

- Where did I come from?
- Why did I open this?
- What did this add?
- Which source did that claim come from?
- What branch did I leave behind?
- Where did I go next?
- What output or tool came from this path?

A trace is not browser history. Browser history records navigation. Continuity records **relational movement**.

## Internet surfaces

Different external surfaces remain different locally:

```text
news
social feeds
search
video
forums
documentation
marketplaces
job boards
maps / places
public data
external tools/apps
...
```

Continuity does not need a separate architecture for each surface. Surface-specific adapters may extract useful bounded relations, but all of them return to the same traversal contract.

## News

News is traversed, not absorbed.

```text
current referent
→ news/search/feed
→ source/report
→ relation added
→ another report / primary source / person / place / topic
→ continue
```

A report remains attributable to its external source. Multiple reports may relate to the same event, but Continuity must not erase source distinctions or manufacture consensus.

## Social feeds

Social platforms are traversed the same way.

```text
post
→ reply
→ profile
→ linked source
→ another conversation
→ project / question / person / place
```

Continuity preserves the branch and relation; it does not need to reproduce Facebook, Reddit, TikTok, X, YouTube, Discord, or another platform internally.

## Branching

Traversal may branch.

```text
current referent
├→ source A
├→ source B
└→ source C
```

A branch may be paused and returned to later. Older branches remain provenance; they are not automatically current.

## Outputs

Traversal can produce durable local outputs:

- note;
- saved source reference;
- research finding;
- task;
- plan;
- artifact;
- tool;
- project change;
- learning movement;
- comparison;
- handoff.

The output is local Continuity state. The external thing that led to it remains externally owned/referenced.

## Boundary

Do not:

- mirror the internet into Continuity by default;
- create a new top-level subsystem for every website/content type;
- confuse a touched source with a Continuity-owned object;
- turn every touch into work;
- treat browsing/navigation alone as evidence that a claim is true;
- let old trace ancestry override the present referent;
- collapse unlike external sources merely because they discuss the same subject;
- erase source attribution when information crosses layers.

The trace exists so movement can become broad without becoming confusing.
