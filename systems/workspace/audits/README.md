# Tracework bounded audits

An audit is the originating referent of motion. Workflows, repairs and checks are children of that audit, not replacement audits. The original audit is `tracework-self-audit-2026-10-25.json`.

## Operating contract

1. Start with a fixed audit ID, original referent, and bounded acceptance requirements.
2. Record new work under the correct existing parent using `bounded_audit.add_child`. No orphan work, cycles, or implicit replacement of the referent.
3. Perform the work using existing GitHub workflows or a source-backed repair. Workflow execution is an instrument; its completion alone does not close an audit.
4. Record exact evidence on each node: `verified: true`, `source`; workflow nodes additionally require `run_id`, `head_sha`, `conclusion: success`. Set `state: passed` only after validating the requirement against that evidence. A label alone is insufficient.
5. Evaluate using `python -m systems.workspace.tracework_self_audit`. An unresolved node means an intentionally failing evaluation. The evaluator does not repair work, dispatch other workflows, reopen closed audits, or create new audits.
6. Once all descendants pass, call `bounded_audit.close` and persist the closed audit. Closed audits cannot receive new children. A later audit gets a new ID and referent.

## Limits

This is the **finite audit data model and closure gate**, not a fully automatic worker that can independently discover, repair, or run all children. GitHub Actions workflow dispatch remains explicit. No claim of a healthy workstation follows merely from passing these audit model tests. Do not silently alter the original referent to satisfy a later workflow run.

## A/B connection (implementation)

The initial audit remains A. Each admitted source observation is B. The comparison is explicit; no successful claim may substitute for its source. The evaluator reads GitHub Actions with read-only credentials for admitted workflow runs and stores the comparison alongside its decision. The finite tree returns leaf-first `next_handoffs` carrying the original referent, parent, and acceptance requirement. These are **proposals for work**, not evidence that work executed.

The self-audit workflow remains manual-only; an open audit deliberately fails its closure gate and retains the report artifact. To advance it, execute a handoff, attach independently verifiable evidence to its node, and rerun evaluation. The existing GitHub workflows are not automatically dispatched by this harness. The root audit cannot close while any descendant remains unresolved.
