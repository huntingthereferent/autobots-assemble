# SPORTS — expanding source discovery and intake

Status: source-discovery policy committed; ingestion and live execution not yet verified.
Environment: Tracework / autobots-assemble.
Initial matchup: Kansas City Chiefs at Seattle Seahawks, 2026-10-25.

## Principle
Never treat one provider or one source list as sufficient. For each observation family, discover alternatives, collect overlapping evidence, retain independent provenance, and continue searching for uncovered dimensions. Discovery is ongoing, not a one-time checklist.

## Discovery families (starting points, not limits)
- League records: NFL schedule, gamebooks, play-by-play, statistics, Next Gen Stats, injury reports.
- Public structured archives: nflverse, Pro Football Reference, Sportsipy-compatible sources where permitted.
- Independent analytics: ESPN gamecast/stats, Pro Football Focus where licensed, FTN and other published analyses.
- Tracking and context: player participation, personnel groupings, formations, weather, venue, travel, officiating.
- Historical context: opponent-adjusted situational trends, season and multi-season splits, corrections and revisions.
- Discovery of alternatives: search for other datasets, mirrors, open APIs, public research repositories, and documentation for every family above. Verify actual accessibility and usage terms before ingestion.

## Each candidate source
Record: provider, source_url, discovery_method, data_family, access_method, terms_or_license, observed_coverage, timestamp_granularity, identifiers, known_gaps, overlap_with, status, checked_at.

## Each observation
Preserve source record and original fields alongside normalized identifiers: source_url, publisher, retrieved_at, event_time, season, game_id, team_id, opponent_id, metric, value, unit, situation, raw_record_ref, correction_ref, confidence_or_quality_note.

## Pipe behavior
1. Discover multiple candidate sources per observation family.
2. Verify each endpoint and permitted access.
3. Ingest raw records without discarding source-specific fields.
4. Reconcile identifiers; preserve conflicts, missingness, revisions and provenance.
5. Seek additional independent evidence where coverage or agreement is weak.
6. Hand sourced records to existing Tracework/WORLD interfaces without modifying the mathematical core.
7. Audit ingestion counts, coverage and source independence before any repeated trials.
8. Revisit discovery whenever a new field, mismatch, or gap appears.

Do not assert that a listed provider was accessed, that data was ingested, or that simulations ran unless execution receipts establish it.


## Tracework provider connection registry (2026-10-25)
This is a **source-adapter registry**, not evidence of an authenticated or executing provider connection. An existing Tracework AI/search actor should discover, verify and invoke eligible adapters; no standalone SPORTS scraper or scheduler is authorized by this file.

| Candidate | Base/source | Role | Connection |
| --- | --- | --- | --- |
| The Odds API | https://the-odds-api.com/ | Multi-book odds, historical snapshots | API key required; not connected |
| OpticOdds | https://opticodds.com/ | Odds, movement, props and market feeds | Account/credentials required; not connected |
| SportsDataIO | https://sportsdata.io/ | Betting lines, statistics, historical data | Account/credentials required; not connected |
| nflverse | https://github.com/nflverse/nflverse-data | Open football data archive | Public discovery target; retrieval not witnessed |
| NFL | https://www.nfl.com/stats/ | Official football observations | Public discovery target; retrieval not witnessed |

### Admission and evidence
- Worker input: matchup, source family, requested observation interval, permitted providers, discovery expansion budget.
- Worker output: source candidates, access verdicts, native locators, retrieved-at and observed-at timestamps, overlapping provider relationships, gaps, blockers and next-search suggestions.
- Register a real outward-search AI actor with the existing runtime/swallow-first interface. Do not claim it is registered until a native handoff and search receipt exist.
- For paid APIs, obtain credentials through authorized secret management; never commit keys, bypass paywalls or infer entitlement.
- Distinguish a successful public fetch from authenticated live feed access; retain provider origin where multiple vendors repackage the same underlying feed.
- First acceptance test: two independent retrieved source records for the same matchup, an explicit discrepancy/overlap comparison, and a native Tracework handoff receipt.
