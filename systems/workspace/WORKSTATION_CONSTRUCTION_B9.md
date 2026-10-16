# B9 — Continuous Handoff: construction separate from observational determination

## Canonical contract alignment (2026-10-16)

The repository's [Continuous Handoff observational contract](../../language/handoff/CONTINUOUS_HANDOFF.md)
and [read-only sidecar example](../../runtime/examples/continuous_handoff/README.md)
now live on `main` at `3dba1722ede321a9a03b38ec6c41407fd90857f5`.
B9 does **not** replace either. The reference demonstrates stateless sidecar
traversal; B9 is an optional **append-only candidate construction journal**
using the existing native handoff runtime. It remains separate from actual
source observation, worker admission, and execution.

The published vocabulary is PROPOSED / UNKNOWN / SUPPORTED / CONTRADICTED.
B9 preserves its historical `UNDETERMINED` (no report) and `UNRESOLVED`
(legacy report) spellings, but projects them **read-only** to PROPOSED and
UNKNOWN respectively. Newly supplied UNKNOWN reports are accepted only through
the same external native-verifier callback. The callback used by these local
tests is explicitly a fixture, not an authenticated source owner. Neither
normalization nor the receipt hash constitutes determination.

## Core correction

**Continuous handoff preserves relationships through movement.** It can carry a
possible relationship or a missing intermediate requirement without claiming
that the relationship is correct. **Observational determination** belongs to
the native source system that can observe, reproduce, or verify the evidence.

Previous B2–B8 gates are still appropriate for **admission** and **execution**.
They are not prerequisites for drafting a *possible* route toward a required
result. B9 preserves this difference directly, without embedding James's
observational A/B language in runtime mathematics.

## Construction

`WorkstationConstruction(data_dir)` opens a requirement as a `GOAL` and creates
candidate prerequisite or alternative paths working backward from it.
It can branch further while upstream relationships remain unobserved, append
possible cross-candidate links, and point to a possible worker source without
asserting that source exists or fits. Every record uses the existing
`RuntimeJournal` and `HandoffRuntime`.

New nodes are separate immutable `Handoff` specifications with
`metadata.source_system=workstation-candidate-construction/v1`. They do not
appear as B2 witnessed `BRANCH`/`RELATION` observations. Their `HandoffState`
may be `READY` because the generic runtime considers a submitted spec ready;
that **does not imply** the candidate is supported, admissible, or executable.
The authoritative construction truth remains `UNDETERMINED` until an
observation is independently checked.

`path_role=REQUIRED` means *this proposed path posits it as a prerequisite*;
`path_role=ALTERNATIVE` makes a proposed option explicit. Neither describes
verified dependencies or a complete proof of the result.

`propose_connection()` records a possible inter-node dependency. It rejects
cross-goal links and cycles, but neither those checks nor equal labels prove
that two source systems agree. `suggest_source()` records an edition hint with
`capability_fit=UNDETERMINED` and `source_presence=NOT_VERIFIED_HERE`.

## Construction frontier — movement without determination

`next_construction_handoffs(goal_id)` is a **read-only** projection of possible
upstream steps, preserving the full downstream route to the requested result,
including explicitly proposed alternative inter-node links. A result with no
upstream candidates remains a constructible root handoff. New branches do not
require successful observation, and all paths carry the original requirement,
source and candidate-specification provenance.

The projection gives the next construction movement an explicit purpose:
`OBSERVE_OR_DECOMPOSE_FURTHER`, `REVISE_OR_EXPLORE_ALTERNATIVE` after a
historical contradiction, or `RECHECK_OR_CONSTRUCT_REMAINDER` after historical
support. Those are **construction suggestions**, not admitted proofs.
Historical receipts are *never* marked freshly source-verified by this
projection. Possible source editions retain `capability_fit=UNDETERMINED`
and `execution_authorized=False`. Multiple possible routes remain distinct;
`max_paths_per_leaf`, `max_total_paths`, `max_path_depth`, and
`max_total_route_steps` reject an
oversized graph rather than silently omitting or recursively exhausting paths.
The route walk is iterative; backward chains with more than 1,000 candidate
steps remain constructible when the caller provides an explicit depth budget.

Every frontier handoff carries `historical_determinations`, retaining **all**
scoped earlier verdicts, not just the most recent one. A past `SUPPORTED` and
later `CONTRADICTED` result can both be inspected without treating either as
current proof. Source identifiers, witness references, and report digests are
historical metadata; the projection sets `current_native_verification=False`.


### Route-scoped observational context (B9 continuation)

A leaf-only summary is insufficient when the observation relevant to the
requested result sits **in the middle** of a proposed path. The frontier now
adds `routes_with_observational_context` alongside the original
`possible_routes_to_result`. Each route carries every upstream candidate step:

- immutable candidate and downstream IDs, requirement, input contract and source provenance;
- either `DECLARED_CANDIDATE` or `PROPOSED_CONNECTION`, including the exact
  historical rationale for proposed connections;
- all scoped historical receipt claims **at that step**, including prior
  contradiction and later support, with current native verification still false;
- suggested source/edition locators and rationale with capability fit and
  execution authorization explicitly undetermined/false;
- one route-level *historical* condition and next construction suggestion.

Two routes sharing one candidate can have different *intermediate* observation
histories. A contradiction on one branch does not erase the other branch. A
route with historical local support still has `whole_route_verified=False`
and `join_observed=False`. The route-level movement is a construction prompt,
not native worker admission. Total projected route steps have a separate bound
(`max_total_route_steps`, default 65536); exceeding it fails with an explicit
error rather than dropping routes or exhausting memory silently.

## Observation

`ObservationalDetermination` accepts source-bound `Receipt` objects with
`SUPPORTED`, `CONTRADICTED`, or `UNRESOLVED` verdicts, a scoped relation, and
an exact candidate-specification hash. It always delegates verification to
an explicitly supplied **independent source-native verifier**. There is no
permissive default. The verifier must recheck the evidence independently of
the submitted verdict and hash. **A hash or recorded label is not proof**.

A recorded verdict remains **historical**. `recheck()` asks the verifier again
and can mark old results `verified_now=False` without changing their historical
record. A subsequent contradictory result is appended, never rewritten.
Even `SUPPORTED` is strictly *candidate-local* and does not authenticate
owner identity, a whole automation chain, a B2 connecting lane, or an
executable B3/B8 job.

## Boundaries preserved

- B2 still admits only witnessed movement through its own source-owned gate.
- B7 still continues only from verified B3 returns; B9 construction entries
  cannot be mistaken for B7 native returns.
- B8 still requires exact-job approval and native controls for **every** worker
  execution; B9 cannot bypass these controls.
- Missing owner proof or unknown middle relationships remain constructible
  as candidate paths, but **not** supported or executable claims.
- The construction graph does not invent requirements, verify source owners,
  authenticate external actors, derive a correct algorithm, run a model agent,
  or claim production autonomous orchestration.
- The existing JSONL store is not a concurrent-writer lock or a signature
  scheme; a multi-process host must supply those protections separately.

## B9 repository verification and scope

B9 originated as an additive local candidate with the canonical runtime sources.
Its source and 73 construction tests were merged into GitHub `main` in
[PR #30](https://github.com/huntingthereferent/autobots-assemble/pull/30)
at merge commit `aebe6ab5bc05ba07bcea27f31976e851dedfb204`.
Native [B9 construction CI](https://github.com/huntingthereferent/autobots-assemble/actions/runs/38903000870)
passed the 73 B9 tests, the B2/B7 regression tests, and the canonical
Continuous Handoff reference tests. Post-merge workspace-continuity and
protocol suites also passed on that exact merge commit.

The test `verify_native_receipt` callback is still an explicit fixture;
B9 construction or hash comparison does not authenticate a source owner or
prove a proposed route. The separately scoped B10 continuation trial is
described in `B9_OBSERVED_CONTINUATION_BRIDGE.md` and does not modify that rule.

## Local reproduction

```sh
python -m unittest -v network.tests.test_workstation_construction network.tests.test_workstation_construction_frontier network.tests.test_workstation_construction_scale network.tests.test_workstation_construction_route_scope
python -m examples.construction_demo
python -m examples.route_scope_demo
```

Expected: 73 local tests pass (38 original + 24 frontier + 1 graph-scale + 10 route-scoped tests); the demonstration constructs branches but
claims no native result.
