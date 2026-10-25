# SPORTS — source intake

Status: source discovery opened; ingestion and execution not yet verified.
Owner environment: Tracework / autobots-assemble.
Initial matchup: Kansas City Chiefs at Seattle Seahawks, 2026-10-25.

## Scope
Collect original sports data and metadata. Do not replace WORLD mathematics, simulate invented observations, or claim a pick from unverified records.

## Source queue
- NFL official game schedule and gamebook: https://www.nfl.com/schedules/2026/reg8/
- NFL official team and player statistics: https://www.nfl.com/stats/
- NFL Next Gen Stats: https://nextgenstats.nfl.com/
- Pro Football Reference team and game history: https://www.pro-football-reference.com/
- nflverse public play-by-play data and documentation: https://github.com/nflverse/nflverse-data

## Intake fields
source_url, publisher, retrieved_at, event_time, season, game_id, team_id, opponent_id, metric, value, unit, situation, raw_record_ref, correction_ref, license_or_usage_note.

## Pipe checks
1. Verify each source endpoint and applicable access conditions.
2. Collect and retain raw records with source identifiers.
3. Normalize without discarding original timestamps or fields.
4. Mark missing, conflicting, or corrected records.
5. Pass sourced records to existing WORLD/Tracework interfaces; do not alter mathematical core.
6. Audit what was actually ingested before running 100 trials.

No game observations or simulation results are asserted by this manifest.
