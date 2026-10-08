# Recursive agent lineage — connected transport and evidence boundaries

The existing handoff/runtime event stream owns the agent lineage. A/B remains a
**separate comparison/admission operation**, not redefined as a scheduler.

## Wired paths

```text
explicit POST activation (registered word, actor, instance, current referent)
  -> durable agent handoff (READY)
  -> external A/B comparator receives referent + parent evidence
  -> POST reported result + native witness to the same handoff
  -> COMPLETE witness validation / UNKNOWN or BLOCKED wall
  -> next witnessed referent spawns another READY agent
  -> optional separately registered closure verifier checks descendant claim
  -> AGENT_LOOP_CLOSED event on ancestor, then closure-born child if admitted
```

- `POST /api/agents/activate` accepts a registered activation word, actor,
  stable `instance_id` for idempotency, and an explicit `referent`. The included
  route is **`begin comparison`** for actor **`james`**. The default
  `ohayo` route is unchanged and read-only.
- `GET /api/agents?root=<root-id>` reports the lineage and READY agents.
  The parent output/witnesses are available in the existing
  `GET /api/handoffs` projection for a genuine comparator to inspect.
- `POST /api/agents/<agent-id>/result` accepts a caller-produced A/B decision,
  `status`, output, `evidence`, optional `next_referent`, optional `closes`,
  `closure_evidence` and `closure_birth_referent`. The result is recorded
  under the same durable handoff and used as input for the next agent.
- `EcosystemService(..., ab_evaluator=callable, closure_admitter=callable)`
  can instead connect direct in-process implementations to the scheduler.
  With no evaluator registered, READY work waits for an external result.
- The general `POST /api/handoffs/<id>/result` path rejects agent handoffs:
  callers cannot bypass the witness gate.
- Both agent-specific HTTP read/write endpoints are loopback-only and require
  a trusted local caller; this is **not** a multi-user authentication system.
  Do not expose the local service to an untrusted network.

## Contract example

First activation (explicitly create the parent; no GET mutation):

```bash
curl -s -X POST http://127.0.0.1:8040/api/agents/activate \
  -H 'Content-Type: application/json' \
  -d '{"surface":"begin comparison","actor_id":"james","instance_id":"experiment-1","referent":"observed ARC transition"}'
```

The response contains `root` and `ready`. Give the READY agent ID and
corresponding native evidence to the registered external A/B evaluator. When it
has produced a result (the following ref is illustrative, **not** a verified
source):

```json
{
  "actor_id": "external-comparator",
  "status": "COMPLETE",
  "output": {"relation": "observed delta between two witnessed states"},
  "evidence": [{
    "condition": "movement witness",
    "kind": "source",
    "source": "native-research-record",
    "ref": "REPLACE-WITH-ACTUAL-NATIVE-LOCATOR",
    "depth": "reported"
  }],
  "next_referent": "next admissible result to compare"
}
```

Submit the result to `POST /api/agents/<ready-agent-id>/result` and inspect
the returned `step` and `lineage.ready` values. The child remains READY
for the next real evaluation; no fabricated comparison is performed.

## Closure distinction

A result with `closes` is a **claim**. Without a separately installed
`closure_admitter` callable checking descendant/ancestor/evidence, it never
closes a loop or creates a closure child. Closure evidence must be preserved in
the `AGENT_LOOP_CLOSED` event. A saved admitted closure can recover its
unfinished birth after restart without re-running the comparator.

Transport validation checks the required `movement witness`, non-simulated
kind/depth and a non-empty native source reference. **It does not fetch or
validate the external source itself.** The provider and closure verifier
must perform independent comparison/relevance checks. The repository does
**not** currently contain the named `ABLoop` implementation, a network
agent supervisor, or a live ARC A/B comparison engine. The Eggy research
artifacts are not substitutes for this semantic admission.

`UNKNOWN`, `BLOCKED`, `PARTIAL`, `FAILED` stay unresolved. Swallow-first
is supported as an optional adapter to `AgentLineage` but requires separate
registered outward-search agents. There is no automatic escalation to James.

## Recovery and bounds

- The root uses stable activation IDs; replaying the same instance preserves
  identity and rejects attempts to bind that instance to a different referent.
- Children preserve original parent output, evidence locations, dependencies,
  generation and birth reason. The event journal survives service restart.
- A child can close a grandparent without closing its own loop.
- Distinct result- and closure-born candidates use deterministic identifiers,
  with max-birth and max-step bounds. Saved closure certificates are reused only
  with the same closing agent and identical evidence.
- This integration does not assert a solved ARC level or prove mathematical A/B.

## Tests

```bash
python -m unittest network.tests.test_agent_lineage -v
python -m unittest network.tests.test_agent_service -v
```
