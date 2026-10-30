# Tracework main anchor — v1 (2026-10-28)

Frozen working anchor. Changes require explicit correction with provenance; do not silently rewrite.

## Referent
Grow the existing usable Tracework skeleton toward a portable, server-hosted environment. James works backward from what exists toward a larger structure, following observed differences. The larger architecture is a direction, not an implemented fact.

"Torus" is James's word describing movement: the structure grows as new things are added. Do not infer a requirement for toroidal geometry. Do not redesign Tracework, substitute a parallel harness, or build the Live Viewer first.

## Frozen operational gates
These are admission boundaries around existing A/B, NOT a new definition of A/B.

1. ENTRY: preserve current referent and James's corrections.
2. ESTABLISHED COMPARISON: compare observed existing implementation with intended capability.
3. RELATION: proposed addition must follow an evidenced difference.
4. MOVEMENT: make one bounded supported change to existing structure.
5. OUTPUT: compare observed result with intended change and evidence.
6. CONTINUITY: carry forward what survived, changed, is unresolved, and the next referent.

PASS requires an inspectable witness. WALL stops unsupported movement without modifying the referent. PARTIAL/UNKNOWN preserve uncertainty. A failed gate cannot rewrite its anchors, substitute a task, or self-certify success. Corrections are admitted explicitly and recorded.

## Intended build direction
Portable application server hosting existing Tracework runtime; durable event history and recovery; extensible API/adapters; bounded execution; growth of worlds, relationships and connections; appropriate identity and permissions; possible distribution as needs emerge; Live Viewer afterward.

Candidate established techniques: modular monolith, event sourcing, adapters, capability-based permissions, distributed systems. They are infrastructure options, not definitions of James's mathematics.

## First established comparison
| Intended capability | Existing evidence | Status / next witness |
|---|---|---|
| Persistent service | runtime/service.py EcosystemService | Code exists; test startup/restart |
| Durable events | runtime/journal.py and runtime/engine.py | Code exists; test recovery |
| Execution and routing | runtime/orchestrator.py SystemBinding and actors | Code exists; test real adapter |
| HTTP entrance | runtime/http_server.py | Code exists; inspect routes and smoke-test |
| Mathematical boundaries | AB_CONTRACT.md, ENTRY.md, CATEGORY_CONTRACT.md | Documented; not proof of enforcement |
| Portability | Not verified | UNKNOWN; inspect deployment |
| Security and distribution | Not verified | UNKNOWN; derive from real need |
| Worlds/branching | Uncommitted periodic-grid experiment is assistant-created | NOT evidence for James's model; inspect real structures |
| Live Viewer | Later | WALL on premature build |

## Next supported movement
Inspect and test the existing service, journal, orchestrator and HTTP entrance against the server goal. Record actual PASS/WALL/UNKNOWN, preserving evidence and corrections. Do not overwrite state/current.json's older feed-specific referent with an unverified claim.
