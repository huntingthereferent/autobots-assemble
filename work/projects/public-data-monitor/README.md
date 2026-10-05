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
- [ ] Fetch live USGS GeoJSON.
- [ ] Validate and normalize events.
- [ ] Idempotently persist events.
- [ ] Serve event JSON through FastAPI.
- [ ] Render a small dashboard.
- [ ] Run locally through Docker Compose.
- [ ] Pass automated tests in GitHub Actions.

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
