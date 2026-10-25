# Tracework — final target architecture and whole-system convergence harness

**Decision:** The dynamical, relational, mismatch-driven, embodied and stability architecture below is the **final target design**, not a proposal to be accepted or rejected wholesale. The harness exists to move **all layers** of Tracework toward that target and demonstrate conformance. It must not rewrite the historical record or pretend unimplemented features already exist.

**Pinned starting point:** `56553415946d065baaf7d59eaf727032f6af589c` (2026-10-25). The pinned commit is the historical baseline; this branch is the evolving migration/harness implementation. Production `main` is not silently replaced.

## Target mathematical contracts

1. **State and trajectory:** Define a typed system state `x` including source identity, lane graph, journal frontier, task receipts, evidence and execution status. Model native discrete transitions first, `x_{k+1}=F(x_k,u_k,w_k)`; supply a separately justified continuous embedding `dx/dt=f(x,u)+w` where supported. A trace `tau` must preserve observable transitions, time/order, and provenance.
2. **A/B relational operator:** Define explicit source and target domains, admitted actions and a relation or mapping `R_AB`. Where full correspondence is claimed, test rooted bijective action-preserving conjugacy `h(T_a(s))=T'_a(h(s))` for reachable states. Metric distortion / Gromov–Wasserstein objectives are target extensions only when metrics and measures are declared; they do not replace the existing finite proofs.
3. **Mismatch engine:** Declare expectation, native observation, comparator, mismatch magnitude, correction policy and evidence. Implement measurable mismatch propagation across handoffs and source revisions. Predictive coding / variational free energy requires an explicit probabilistic model `p(x,y)`, approximation `q(x)`, objective and update rule before being reported as implemented.
4. **Embodied relational coupling:** Encode bounded resources, latency, authority and source access as real execution constraints. Define typed time-varying relations `R_ijk(t)` where a three-index representation is useful and measurable; do not call ordinary links a tensor without semantics.
5. **Stability and scaling:** Specify invariant sets, perturbation classes, finite horizons, drift metrics and load measures. Claim Lyapunov stability only after exhibiting `V` and verifying its conditions for the scoped dynamics. Benchmark event lookup, replay, memory, concurrency and interruption; do not assert unsupported complexity classes.

These are **target obligations**, not claims that the current code already satisfies them.

## Whole-system migration coverage

| Layer | Source entry | Required convergence |
| --- | --- | --- |
| Core language and finite mathematics | `LANGUAGE_REFERENT_CONTRACT.md`, `work/arc_like_maze/math.py` | Preserve original referent; formalize and test typed operators, correspondences, negative controls |
| Runtime and journal | `runtime/` | Typed states/transitions, provenance-complete traces, replay, failure/interrupt semantics |
| Workspace and workers | `systems/workspace/` | Relational dependencies, mismatch correction, bounded resources, deterministic handoff receipts |
| ARC / WORLD / NIH | `research/`, `work/` | Native adapters and model-to-observation comparisons; no cross-domain proof inflation |
| Viewer and GitHub Pages | `docs/live/` | Render state, trajectory, relation, mismatch, evidence and unknowns from native sources |
| API / server / clients | `runtime/http/` and client interfaces | Shared typed contracts for terminal, browser, remote clients and future applications |
| Other applications | `companies/`, `network/tests/` | Conform to common state/evidence APIs without erasing domain-specific behavior |
| GitHub delivery | repository workflows, READMEs, source links, CI | Architecture docs, traceable commits, executable tests, migration status, reproducible results |

## Convergence sequence

**Gate 0 — Freeze and inventory:** retain baseline SHA; enumerate all modules, interfaces, dependencies, active lanes and external/private boundaries. No claim of full coverage until inventory completes.

**Gate 1 — Common mathematical kernel:** introduce typed state, action, relation, observation, mismatch, trace and evidence contracts. Preserve old interfaces through adapters.

**Gate 2 — Runtime and journal:** implement transitions, replay, interrupted-run recovery, source identities and parent relationships. Exercise positive and negative controls.

**Gate 3 — Lane integration:** migrate workers, independent source editions, handoffs and correction across all operating lanes; use isolated fixtures before real sources.

**Gate 4 — Scientific operators:** add and test relational geometry, predictive/probabilistic models, coupling and stability analysis against real scoped witnesses. Missing prerequisites remain explicit implementation tasks, not assumed facts.

**Gate 5 — GitHub, viewer, server and clients:** make the same mathematical contracts visible in source, API, execution view, documentation and CI. Never fabricate live workers or unobserved results.

**Gate 6 — Promotion:** run regression, native verification, drift/interrupt/load tests, publish pass/fail/unknown matrix and promote independently reviewed increments to `main`. GitHub branch protections / required checks can enforce this boundary.

## Every change must provide

`target_contract`, `source_commit`, `affected_layers`, `migration_adapter`, `test_command`, `native_witness`, `negative_control`, `status`, `limitations`, `next_dependency`.

Statuses: **NOT STARTED**, **IMPLEMENTING**, **TESTED**, **BLOCKED**, **PROMOTED**. Do not label an architecture-wide gate complete because one module passes.

## Immediate next implementation

1. Generate repository-wide module and workflow inventory against the pinned baseline.
2. Implement a small dependency-free typed mathematical kernel and deterministic conformance tests.
3. Connect journal/handoff adapters without replacing native evidence.
4. Add CI and viewer status based on verified test returns.
5. Continue through remaining layers with recorded handoffs and source-pinned results.

**Present state:** target architecture and convergence contract established; baseline preserved. Full implementation and system-wide validation remain outstanding.
