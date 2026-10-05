# Multi-Source State & Reconciliation Platform

**Status:** ACTIVE MAIN BUILD  
**Purpose:** Build one reusable, deployable engine that can ingest heterogeneous external sources, preserve identity and provenance, detect change/conflict, reconcile state, and expose the result through APIs, interfaces, alerts, exports, and downstream automation.

## Stable referent

The platform is not tied to one dataset or domain.

Its reusable movement is:

external changing state
→ acquire evidence
→ normalize representation
→ preserve identity + provenance
→ persist current/history
→ compare with prior state
→ classify new / changed / unchanged / disappeared / conflicting
→ reconcile when possible
→ expose current state
→ trigger the next supported action

Human-facing products built from this engine may look like monitoring platforms, ETL pipelines, synchronization systems, change-detection services, reconciliation engines, audit systems, reporting platforms, inventory trackers, price trackers, research aggregators, compliance monitors, or other domain-specific tools.

## Core platform layers

### Sources
- REST / JSON APIs
- HTML scrapers
- CSV / JSON / XML files
- database sources
- browser-automation adapters
- future source types as required

### Acquisition
- polling and scheduled jobs
- pagination
- retries / backoff
- rate limiting
- authentication where required
- raw-source capture when useful

### Canonicalization
- source-specific representation → canonical records
- typed validation
- normalization
- explicit source-to-canonical mappings

### Identity
- stable source identity
- cross-source identity resolution
- duplicate detection
- confidence / unresolved identity when matching is not justified

### Provenance
- source
- source identifier
- observation time
- source update time
- raw or reconstructable evidence
- transformation path

### State
- current observation
- prior observation
- history
- source-specific state
- reconciled state

### Comparison
- new
- changed
- unchanged
- disappeared
- conflicting

### Reconciliation
- source agreement
- source disagreement
- deterministic precedence only when justified
- coexistence where competing observations are both valid
- human-review boundary where automatic resolution is unsupported

### Outputs
- REST API
- dashboard / web UI
- reports
- alerts
- exports
- downstream integrations

### Operations
- PostgreSQL
- migrations
- Docker
- tests
- CI/CD
- AWS deployment
- logs / metrics / alerts
- performance measurement
- backup / recovery
- security checks
- operator documentation

## Resume ability target

The platform is built backward from normal human-recognized technical abilities. A category is claimed only after the platform produces an inspectable witness for it.

| Resume ability | Required evidence |
|---|---|
| Python Development | typed application / adapter code, packaging, tests |
| Data Engineering | ingestion, canonicalization, history, reconciliation, lineage |
| PostgreSQL / Database Engineering | schema, constraints, migrations, indexes, query evidence |
| API Development | documented FastAPI interfaces and validation |
| Backend Engineering | reusable service boundaries, persistence, orchestration |
| Frontend / Web | usable state / change / conflict interface |
| Web Scraping | live HTML adapters, parser regression tests, retries |
| Systems Integration | heterogeneous sources unified under one state contract |
| Automation | recurring acquisition and downstream actions |
| Testing / QA | unit, integration, regression, failure/recovery tests |
| Docker | reproducible local runtime |
| CI/CD | automated test/build/deploy path |
| Cloud / AWS | deployed production service |
| Monitoring / Observability | health, structured logs, metrics, alerts |
| Performance Engineering | measured ingestion/query/load behavior and optimization |
| Security | secret/config handling, dependency checks, safe defaults |
| Technical Documentation | architecture, mappings, runbook, evidence trail |

## Use cases

A use case proves the engine against a concrete domain without becoming the definition of the platform.

### Use Case 001 — live public API adapter

The first adapter uses a live public JSON source to prove:
- external API acquisition
- typed parsing / validation
- source identity preservation
- source timestamps / provenance
- PostgreSQL idempotent upsert
- API exposure
- clean-environment CI

Its domain is incidental. Its evidence survives as substrate for the general engine.

**Verified**
- clean GitHub Actions unit job: PASS
- PostgreSQL 16 integration job: PASS
- idempotent replay: repeated source identity keeps row count stable while changed fields update
- API integration: persisted records are returned through the backend API
- live-source smoke: current external feed successfully fetched and validated in GitHub Actions

### Use Case 002 — HTML scraper adapter

Next use case must add capabilities not already proved by Use Case 001:
- real HTML parsing
- fixture-based parser regression
- retries / backoff
- source failure handling
- source lineage
- multi-source comparison/reconciliation

## Acceptance ladder

### Platform Slice 1 — acquisition → persistence → API
- [x] live external API acquisition
- [x] typed validation / normalization
- [x] idempotent PostgreSQL persistence in CI
- [x] persisted records exposed through FastAPI
- [x] unit + PostgreSQL integration + live-source CI
- [ ] Docker Compose runtime verification
- [ ] visual UI verification

### Platform Slice 2 — heterogeneous source + comparison
- [ ] add real HTML scraper adapter
- [ ] source-adapter interface
- [ ] raw/source provenance model
- [ ] canonical record model independent of source/domain
- [ ] change classification
- [ ] multi-source comparison
- [ ] conflict representation
- [ ] fixture-based parser regression
- [ ] retry/backoff and source failure handling

### Platform Slice 3 — reconciliation + history
- [ ] cross-source identity model
- [ ] observation history
- [ ] reconciliation rules with explicit evidence boundary
- [ ] disappeared/stale state handling
- [ ] reconciliation report
- [ ] Alembic migrations
- [ ] indexes justified by measured queries

### Platform Slice 4 — automation + production service
- [ ] scheduled acquisition
- [ ] downstream alerts/actions
- [ ] AWS deployment
- [ ] HTTPS
- [ ] secret/config handling
- [ ] logs + metrics + alarms
- [ ] backup/recovery path

### Platform Slice 5 — hardening
- [ ] load/performance benchmark
- [ ] dependency/security scan
- [ ] failure injection/recovery test
- [ ] operator runbook
- [ ] generated resume evidence summary using verified witnesses only

## Evidence rule

A resume claim is added only after its witness exists. Planned layers are not completed abilities.

Older adapters and use cases remain evidence. They do not become the preferred referent unless the current platform relation explicitly moves back to them.
