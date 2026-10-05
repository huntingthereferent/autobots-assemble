# Public Data Monitor

**Status:** ACTIVE MAIN BUILD  
**Purpose:** Build one real, deployable system that proves a complete technical stack end to end.

## Current vertical slice

USGS real-time earthquake GeoJSON feed
→ Python ingestion
→ validation
→ PostgreSQL
→ FastAPI
→ server-rendered web UI
→ Docker
→ automated tests
→ GitHub Actions
→ AWS deployment
→ monitoring

USGS explicitly recommends its real-time GeoJSON feeds for automated applications that display earthquake information. The feed is treated as an external source; source identifiers and update timestamps are preserved rather than replaced.

## Why this project exists

The target is not merely a working app. Each layer must produce inspectable evidence for a normal human resume category.

| Resume ability | Required evidence from this project |
|---|---|
| Python Development | typed ingestion/application code; packaging; tests |
| Data Engineering | source ingestion, normalization, idempotent upsert, lineage |
| PostgreSQL | schema, constraints, indexes, migrations/query evidence |
| API Development | documented FastAPI endpoints and validation |
| Frontend/Web | usable monitoring interface |
| Testing/QA | unit, integration and regression tests |
| Docker | reproducible local stack |
| CI/CD | automated test/build workflow |
| Cloud/AWS | deployed service with reproducible infrastructure |
| Monitoring/Observability | health, structured logs, metrics/alerts |
| Performance | measured ingestion/query/load behavior |
| Security | dependency/config/secret handling and safe defaults |
| Documentation | setup, architecture, runbook and evidence trail |

## Acceptance ladder

### Slice 1 — local spine
- [x] Fetch live USGS GeoJSON.
- [x] Validate and normalize events.
- [x] Idempotently persist events against PostgreSQL in CI.
- [x] Serve persisted event JSON through FastAPI.
- [ ] Render a small dashboard.
- [ ] Run locally through Docker Compose.
- [x] Pass unit, PostgreSQL integration, and live-source smoke tests in GitHub Actions.

### Slice 2 — second acquisition mode
- [ ] Add a public HTML source through a real scraper adapter.
- [ ] Preserve source lineage and scraper timestamps.
- [ ] Add fixture-based parser regression tests.
- [ ] Demonstrate retry/backoff and source failure handling.

### Slice 3 — production data layer
- [ ] Alembic migrations.
- [ ] indexes justified by measured queries.
- [ ] retention/update policy.
- [ ] reconciliation report between source counts and stored rows.

### Slice 4 — production service
- [ ] AWS deployment.
- [ ] HTTPS and secret/config handling.
- [ ] scheduled ingestion.
- [ ] logs + metrics + alarms.
- [ ] backup/recovery path.

### Slice 5 — hardening
- [ ] load/performance benchmark.
- [ ] dependency/security scan.
- [ ] failure injection/recovery test.
- [ ] operator runbook.
- [ ] resume evidence summary generated only from verified results.

## Evidence rule

A resume claim is added only after its witness exists here. Planned layers are not completed abilities.


## Verified evidence

- Clean GitHub Actions unit job: PASS.
- PostgreSQL 16 integration job: PASS.
- Idempotent replay witness: replaying the same source ID keeps row count stable while updating changed fields.
- API integration witness: a row persisted through the ingestion layer is returned through `/api/events`.
- Live-source witness: the application successfully fetched and validated the current USGS real-time feed in GitHub Actions.

Still open in Slice 1: visual dashboard verification and full Docker Compose runtime verification.
