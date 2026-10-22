# Audit-to-Action worker lane

Purpose: turn neutral audit observations into retained, typed records and independently actionable follow-ups. This is a **pipeline**, not a new research verdict or a requirement to change working results.

## Contract

1. **Ingest** a neutral audit as JSON findings with unique `id`, `lane`, `observation`, `source`, and `kind`.
2. **Classify without rewriting the observation**: `verified_result` → preserve; `defect` → investigate; `candidate` → verify; `unknown` → observe; `external_boundary` → record boundary.
3. **Keep source ownership**: a source locator is not source authentication. The output marks it `unverified_locator` until another worker checks the exact revision and witness.
4. **Dispatch later, only after evidence checks**: owner, test, repair, and viewer receipt belong to the existing lane infrastructure. The current implementation **does not automatically spawn jobs, edit source projects, or claim fixes**.
5. **Close the loop**: after independent verification, retain the original observation, test receipt, outcome, and next source-owned continuation. Do not silently delete negative findings or convert successes into problems.

## Current intake

`python systems/workspace/audit_to_action.py input.json output.json`

Test: `python -m unittest discover -s network/tests -p 'test_audit_to_action.py' -v`

## Audit seed — 2026-10-22

These are observations from the GitHub account audit, **not yet authenticated by this lane's own test run**.

| ID | Lane | Kind | Observation | Next check |
| --- | --- | --- | --- | --- |
| A2A-001 | Mathematics | verified_result | Engine 1 and Cyclic Action have source-defined finite constructions and focused tests | Pin exact source/test revisions and retain witnesses |
| A2A-002 | ARC | verified_result | Recent ARC direct-observation workflows reported success | Inspect native outcomes separately from workflow status |
| A2A-003 | CI | candidate | Multiple protocol-test runs were concurrently in progress and Pages/publish runs were cancelled | Measure redundant triggers, useful completions, and queue latency before changing concurrency |
| A2A-004 | Profile | candidate | Overlapping introductions may confuse navigation | Compare entry pages against a single canonical source map |
| A2A-005 | Viewer | candidate | Execution counts, verified findings and throughput can be conflated | Compare live counters to source-owned run API and saved evidence |
| A2A-006 | UI | unknown | Browser usability of Meow Lab, Pony Trail, Suno, school and viewer was not verified in this audit | Run browser tests and direct interaction checks by page |
| A2A-007 | Research | verified_result | Independent source adapters, observations and tests exist across scientific lanes | Verify each source receipt independently |

Do not infer a failure from an untested item. Do not collapse independently verified results into a global pass/fail score.

## Next implementation boundary

Connect this intake to the existing lane journal and audit viewer, add a source-authentication worker and receipt schema, and measure whether a proposed repair actually improved the original observation. Keep the original audit snapshot immutable.
