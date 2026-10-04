# Research Protocol — Source

This protocol subsumes the earlier standalone `work.osint` protocol.

“OSINT” remains a useful human/domain label for open-source investigation. It is **not** a separate primitive in the protocol network because its operational witness/evidence contract is the same general source-research contract used for job listings, public documentation, papers, filings, news, community reports, web pages, repositories, and other externally inspectable sources.

## Current referent

A bounded external question, entity, claim, opportunity, document, event, or relation being investigated.

Broad collection without a referent is not itself movement.

## Input

- current referent/question;
- source discovery results;
- opened source content;
- files/documents/repositories;
- timestamps and versions;
- prior source/evidence relations;
- explicit search boundaries.

## Source movement

The default source path is:

```text
question / referent
      ↓
discover candidate sources
      ↓
inspect underlying source
      ↓
classify role + time + scope
      ↓
extract bounded claim/evidence
      ↓
compare / conflict / corroborate
      ↓
SUPPORTED / PARTIAL / UNKNOWN / WALL
      ↓
next question or return
```

Discovery is not proof. A search result, snippet, index, citation list, social post, or aggregator may point toward evidence without itself satisfying the target witness.

## Witness contract

Before a source supports movement, preserve enough to recover:

- source identity / URL / file / repository;
- source role: primary / secondary / community / index / derived;
- relevant timestamp/version when time can change the claim;
- exact relation to the current referent;
- what the source directly supports;
- what is interpretation/inference;
- unresolved contradictions;
- search boundary if an absence claim is being considered.

## Preferred source behavior

Prefer the source closest to the claim being tested when accessible, but do not use “primary” as a magic trust label. Authority, scope, time, methodology, authenticity, and correspondence still matter.

Examples:

- official API docs outrank a blog paraphrase for the API contract;
- the live job listing outranks a search snippet for current availability;
- a court filing is closer to what was filed than commentary about the filing;
- a user/community report can be the primary source for that person's reported experience;
- independent measurements may outrank official marketing for measured performance.

## Conflict

When sources disagree:

1. keep both;
2. compare referent, date/version, jurisdiction, scope, methodology, and source lineage;
3. resolve only the distinction supported by evidence;
4. otherwise preserve `UNKNOWN`/`PARTIAL`.

## Absence / negative search

“Not found” is not “does not exist.”

An absence claim requires an explicit search boundary appropriate to the claim, such as a complete registry, exhaustive local dataset, or other bounded source set. Otherwise return “not found within searched sources.”

## Recency

If the referent can change with time, freshness is part of the witness contract. Older correct evidence remains evidence of the older state; it does not silently establish the present state.

## Output

A source-research movement should return:

- bounded answer/claim state;
- source relations actually used;
- unresolved conflicts/unknowns;
- search boundary where relevant;
- next smallest question, return target, or wall.

## Closure

The output can be handed to the same protocol again as the next bounded source question without changing the evidence standard.

## Compatibility

Historical references to `work.osint` route here. They remain provenance and vocabulary; they are not deleted.
