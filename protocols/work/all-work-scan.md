# Protocol — ALL WORK Scan

## Protocol ID

`work.all-work-scan`

## Purpose

Discover difficult work that the user can meaningfully attempt without requiring formal credentials, across **all fields, all goal lanes, and all realization layers**.

The protocol deliberately includes work that is not posted, assigned, paid, or packaged as an opportunity.

## Search universe

A scan should sample across all relevant classes:

1. **Posted paid work** — jobs, contracts, bounties, paid challenges.
2. **Open source** — issues, RFCs, public contribution queues, maintenance/reproduction work.
3. **Prize/challenge work** — competitions with externally defined acceptance.
4. **Frontier academic work** — unsolved problems, conjectures, open questions, proof/reproduction targets.
5. **Scientific work** — unresolved empirical questions, public datasets, citizen/open research with inspectable outputs.
6. **Engineering work** — unresolved design/performance/reliability problems, benchmarks, standards gaps.
7. **Physical work** — fabrication, repair, testing, measurement, inspection, operation, build challenges.
8. **Self-initiated work** — no task owner required when a real problem and external/inspectable validation boundary exist.

## Credential filter

“No credentials” means no mandatory degree, occupational license, professional certification, or formal institutional status is required to attempt/enter the work.

Do not silently equate these with credentials:

- age minimum;
- citizenship/residency;
- account creation;
- equipment/tool access;
- physical ability;
- location;
- prior experience;
- maintainer approval;
- publication/review requirements after the work is completed.

These are separate **walls/resources/eligibility constraints** and must be surfaced explicitly.

## Hardness

Do not use one scalar “hard score.”

Prefer evidence such as:

- uncertainty;
- depth of prerequisite knowledge;
- number/severity of constraints;
- interfaces crossed;
- precision/tolerance;
- scale/performance;
- consequences of error;
- validation burden;
- failed approaches/history;
- independence of external witness;
- distance from initial idea to observed result.

## Candidate admission

A candidate is worth returning when:

- it is genuinely nontrivial;
- the credential gate is absent or separable;
- there is a recoverable problem/referent;
- there is a meaningful way to tell whether progress/result is real;
- the user could in principle begin movement from available/public information, subject to surfaced walls.

## Recurrence rule

A scan is independent by default.

**Do not suppress a candidate merely because it appeared in a prior scan.**

If the same item surfaces again:

- show it again;
- optionally annotate `seen_before`;
- preserve current source/date/status;
- treat recurrence as current evidence, not duplication noise.

Only apply “new since last scan” deduplication when the user explicitly asks for it.

## Output

For each candidate expose:

- candidate/title;
- lane;
- field(s);
- realization layer;
- why it is hard;
- why credentials are not the gate;
- money/reward if any;
- other walls/resources;
- validation/acceptance boundary;
- source/provenance;
- current status/freshness.

Do not rank only by money unless requested.

## Frontier-work rule

The following are valid ALL WORK even without a task owner:

```text
unsolved theorem
unresolved conjecture
open empirical question
unreproduced result
unmet benchmark
public engineering failure mode
open standard/design problem
physical build/test target
```

The work becomes a bounded active referent only after the current question/claim/target is named precisely enough to admit evidence.

## Closure

The output of one scan may re-enter this protocol as:

- a narrower field scan;
- a candidate dissection;
- a current-status refresh;
- a “find more like this” scan;
- a later independent rescan.
