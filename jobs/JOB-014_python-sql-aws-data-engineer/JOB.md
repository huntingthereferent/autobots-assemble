# JOB-014 — Data Engineer — Python / SQL / AWS

## Identity

- **Source:** Freelancer
- **Project ID:** 40744784
- **Reward observed:** $15–25 USD / hour
- **Date added:** 2026-10-03
- **Work status:** blocked (local acceptance analog complete)
- **Submission:** not submitted
- **Payment:** not paid
- **Source URL:** https://www.freelancer.com/projects/sql/data-engineer-40744784

## Scope

- **📍 External Python/SQL/AWS data-pipeline specification**
- Build reproducible ETL/ELT around structured MySQL data, versioned/testable transformations, one-command execution, AWS automation, monitoring, and setup/scheduling/rollback documentation.

## Acceptance

The real acceptance requires an end-to-end AWS run using the client's test data, reproducible version-controlled transformations, and an operational README.

## Current result

**LOCAL ANALOG PASS.** The repo contains a deterministic Python/SQL ETL prototype with idempotent loads, analytics-ready aggregates, MySQL target SQL/indexes, pipeline-run monitoring, automated tests, Makefile, Docker packaging, ECS/Fargate example, CloudWatch logging, EventBridge scheduling guidance, and rollback documentation. End-to-end and repeat-run tests pass locally.

## Evidence

- `prototype/README.md`
- `prototype/etl/pipeline.py`
- `prototype/etl/cli.py`
- `prototype/sql/001_schema_mysql.sql`
- `prototype/sql/002_transform_mysql.sql`
- `prototype/tests/test_pipeline.py`
- `prototype/fixtures/orders.csv`
- `prototype/Dockerfile`
- `prototype/docker-compose.yml`
- `prototype/Makefile`
- `prototype/aws/ecs-task-definition.example.json`
- `prototype/aws/eventbridge-schedule.example.txt`
- `prototype/warehouse.db`
- `submission.txt`
- `acceptance_report.txt`

## Blockers

- Client MySQL schema/test data are unavailable.
- Client AWS account/runtime/IAM are unavailable.
- Production alert destination and schedule are unspecified.

## Next movement

Run the same contract against the client's MySQL/AWS environment: profile schema/query plans, map existing views/procedures, deploy to Lambda/ECS as appropriate, connect monitoring/alerts, and verify the one-command end-to-end run.
