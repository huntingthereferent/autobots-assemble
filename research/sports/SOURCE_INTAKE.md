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
