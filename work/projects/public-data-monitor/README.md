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

### Use Case 002 — HTML + API dual-representation reconciliation

Hacker News is used here because the same stories are exposed through HTML and the official public API, with stable numeric item IDs. The API documentation identifies items by unique integer IDs and exposes top stories separately, which gives a clean cross-representation identity witness.

**Verified**
- live HTML acquisition
- live API acquisition
- HTML parser emits the same canonical-key shape as the API adapter
- fixture-based parser regression
- shared story IDs discovered across both live representations
- canonical pairing uses stable item identity rather than title text
- reconciliation distinguishes agreement from field-level conflict
- full unit, live-source, and PostgreSQL CI lanes remain green

**Still open**
- retry/backoff
- source failure handling
- persisted observation history
- persisted reconciliation results
- fuzzy identity matching across genuinely independent systems

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
- [x] add real HTML scraper adapter
- [x] source-adapter interface
- [ ] raw/source provenance model
- [x] canonical observation model independent of source/domain
- [x] change classification for new / changed / unchanged / disappeared
- [x] multi-source comparison on shared canonical identity
- [x] conflict representation without an invented winner
- [x] fixture-based parser regression
- [x] retry/backoff and typed source failure handling

### Platform Slice 3 — reconciliation + history
- [ ] cross-source identity model
- [x] observation history
- [ ] reconciliation rules with explicit evidence boundary
- [ ] disappeared/stale state handling
- [x] persisted reconciliation state queryable through API
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


## Platform generalization evidence

The first source-specific implementation has now been lifted into a reusable platform layer:

- `SourceAdapter` defines a source boundary independent of domain.
- `SourceObservation` carries source identity, canonical identity, timestamps, provenance URL, entity type, and source payload.
- change classification is tested for NEW, CHANGED, UNCHANGED, and DISAPPEARED states.
- reconciliation is tested for SINGLE_SOURCE, AGREEMENT, and CONFLICT states.
- conflicting fields are named explicitly and no source is silently selected when evidence disagrees.
- the original live JSON source is wrapped as an adapter that emits canonical observations.
- unit, live-source, and PostgreSQL integration CI lanes all pass after the abstraction.

The next missing witness is heterogeneous-source comparison: a real HTML adapter must emit the same observation contract, after which cross-source identity and reconciliation can be exercised on actual independent sources.


## Heterogeneous-source evidence

Use Case 002 proves that the platform can ingest the same underlying entities through two different representations and carry both into one canonical observation contract.

A live CI run fetched Hacker News HTML and the official public API, found overlapping story identities by stable item ID, paired them by canonical key, and passed reconciliation with either AGREEMENT or explicit CONFLICT as valid outcomes. No title-based guessing is used for identity.

This closes the first heterogeneous-source witness. The next layer is persistence of observation history and reconciliation state so change/conflict can be queried over time rather than only computed in memory.


## Persistence and resilience evidence

- append-only observation history is persisted in PostgreSQL rather than overwriting prior state.
- the second observation for the same source identity is classified against the previous persisted observation.
- persisted history retains both the old and new payloads.
- reconciliation outcomes are persisted independently from source observations.
- field-level conflicts remain explicit after persistence; unresolved conflicts do not gain a selected payload.
- observation history and reconciliation history are queryable through dedicated FastAPI routes.
- acquisition retry behavior is isolated behind a reusable helper with exponential backoff.
- transient failures recover within the configured attempt budget.
- exhausted retries raise a typed source failure containing source, URL, attempt count, and final error evidence.
- unit, live-source, acquisition-resilience, and PostgreSQL integration CI lanes pass.

The next operational layer is schema migration + recurring execution + source-run status. That will replace implicit table creation with versioned database evolution and make scheduled acquisition inspectable as its own state.


## Persistence and resilience evidence

- append-only observation history is persisted in PostgreSQL.
- later observations are classified against the previous stored observation.
- prior payloads remain queryable instead of being overwritten.
- reconciliation outcomes are persisted separately from observations.
- field-level conflicts remain explicit after persistence.
- observation history and reconciliation history are exposed through FastAPI.
- acquisition retry uses exponential backoff.
- transient failures recover within the configured attempt budget.
- exhausted retries raise a typed source failure with source, URL, attempts, and final error.
- unit, live-source, acquisition-resilience, and PostgreSQL integration CI lanes pass.

Next operational edge: versioned schema migration, recurring acquisition, and persisted source-run health.


## Operational run-state evidence

- every orchestrated source acquisition now creates a persisted source-run record.
- successful runs store start/end timestamps, status, and item count.
- failed runs store start/end timestamps plus exception type and message.
- source-run health is queryable through `/api/ops/source-runs`.
- a scheduler-safe one-shot runner exists so external schedulers can invoke acquisition without embedding scheduling concerns inside source adapters.
- CI exposed and then verified a packaging boundary introduced by the new `migrations/` directory; package discovery was made explicit rather than removing the migration layer.
- after that repair, unit, live-source, acquisition-resilience, and PostgreSQL/source-run integration lanes all pass.

Current operational edge: finish the first versioned migration revision, then bind recurring execution to durable infrastructure rather than an ephemeral CI database.


## Popular production-stack evidence

The operational stack now uses widely adopted components rather than a custom scheduler:

- FastAPI for the HTTP service.
- PostgreSQL for persistent application/state history.
- Redis as the Celery broker/backend.
- Celery worker for background execution.
- Celery Beat for recurring schedules.
- Docker Compose for the local multi-service topology.
- GitHub Actions for clean-environment CI.

A complete-stack CI lane now builds and starts PostgreSQL + Redis + Celery worker + Celery Beat + FastAPI, verifies the API health endpoint, receives a successful Celery worker ping through Redis, inspects running services, and tears the stack down cleanly.

## Use Case 003 — GitHub repository monitoring

GitHub is now a live scheduled source.

The adapter monitors the public `psf/requests` repository through the GitHub REST API and converts repository state into the same canonical observation contract used by the other sources.

Captured state includes repository identity, default branch, stars, forks, open-issue count, push time, archive state, source URL, and source update time.

**Verified**
- fixture-backed GitHub adapter test
- live GitHub API smoke test
- stable GitHub repository ID used as canonical identity
- Celery task registered for GitHub collection
- Celery Beat schedule registered for recurring collection
- full unit, live-source, PostgreSQL, acquisition-resilience, and complete Docker-stack CI lanes pass with GitHub included

Next edge: complete the versioned Alembic revision, then persist Celery task/run correlation and move into a genuinely ambiguous identity problem across independent systems.


## Durable identity and observability evidence

- GitHub↔PyPI identity decisions are now persisted with score, threshold, match outcome, and the exact weighted evidence used to justify the link.
- identity decisions are queryable through `/api/identity/decisions`.
- Alembic revision `0002_identity_decisions` versions the identity ledger schema.
- migration CI verifies the identity table appears on upgrade and disappears on downgrade.
- Prometheus instrumentation exposes source-run, item-count, duration, reconciliation, and identity-decision metrics.
- Prometheus 3.15.0 runs as a real service in Docker Compose and scrapes the FastAPI `/metrics` endpoint.
- complete-stack CI waits until Prometheus reports the application target as healthy rather than merely checking that the Prometheus server started.
- all current CI lanes pass: unit, live-source, PostgreSQL integration, acquisition resilience, Alembic upgrade/downgrade, and complete Docker stack.

Current edge: add Grafana visualization over the verified Prometheus layer, then continue into security/performance hardening.


## Visualization, security, and performance evidence

- Grafana is provisioned as code with Prometheus as its datasource.
- CI verifies Grafana health and confirms the provisioned `Platform Overview` dashboard by UID.
- Trivy 0.75.0 scans the built application container and fails CI on fixed CRITICAL vulnerabilities; the current image passes with no critical findings.
- k6 2.3.0 runs a 20-second, 10-VU load test against the containerized FastAPI service.
- measured k6 result: 3,858 HTTP requests, 0.00% request failures, p95 request duration 3.62 ms, 1,929 completed iterations, and 7,716/7,716 successful checks.
- the k6 thresholds are enforced in CI: failure rate <1% and p95 latency <500 ms.

The current stack now has verified acquisition, persistence, APIs, background scheduling, migrations, identity/reconciliation, observability, visualization, vulnerability scanning, and load testing.

Current edge: infrastructure-as-code for the AWS production topology. Terraform validation can prove the configuration shape; AWS deployment remains open until an actual cloud runtime witness exists.
