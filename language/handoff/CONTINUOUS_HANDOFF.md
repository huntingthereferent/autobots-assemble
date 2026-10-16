# Continuous Handoff — Observational Determination

**Status:** scoped engineering contract with a runnable reference example; not a universal theorem, completed automation platform, or definition of James's continuing language referent (historically called A/B).

**Rule: Continuous handoff preserves relationships through movement. The observational layer determines what the available evidence supports.**

The system may work backward from an output requirement, open missing intermediate relations, branch between possible methods, and hand those requirements to existing capable systems. None of those construction steps determines that a proposed route actually occurred.

## Responsibilities and authority

| Responsibility | Permitted movement | Does not establish |
| --- | --- | --- |
| Continuity | Carry referent, sources, dependencies, branches, ancestry, and return points | Correctness of a proposed path |
| Construction | Work backward from needs, generate candidate intermediate boundaries, open branches | Observed execution or a unique solution |
| Handoff | Transfer required inputs, outputs, permissions, native witness conditions and provenance | Execution, admission or receiver understanding |
| Observation | Under native, stated conditions, support, contradict or leave a specific claim unresolved | Universally valid results beyond its scope |
| Continuation | Move with observed and unresolved relations, revisit affected dependencies | Erasure of failed or superseded history |

**Local state, continuous provenance.** Each system retains its own schema, evidence and authority; a shared handoff is not a common replacement state.

## Construct backward; determine only through observation

1. Record the actual current referent, source and requested result, including source owner and target condition.
2. Traverse required conditions **backward**. Ask what could supply each input, and preserve *every declared* viable candidate branch; do not invent missing middle actions.
3. For each candidate connection, record its input/output relation, possible capability owner, dependencies, assumptions, required observations and what remains unknown.
4. Leave missing capability **OPEN_UNSTAFFED**. A proposed branch is not permission to create or start a worker.
5. Native owners separately admit and execute exact bounded work through existing controls. The handoff itself is not execution.
6. A source-native observational verifier checks the exact claim, source edition, condition, witness and, when joining independent branches, the **join relation**. Results are scoped: SUPPORTED, CONTRADICTED or UNKNOWN.
7. Continue through supported relations while retaining unresolved openings, contradictions, and old evidence. Source changes re-open any dependent observational checks before prior evidence is reused as current proof.

A result can be examined backward without reversing time or proving that one unique intermediate route must exist. Matching labels, hashes, output shapes or receiving targets do not independently verify cross-system joins.

## Difference between candidate and determined relation

- **PROPOSED** — a declared possible relationship with no observation; useful for construction only.
- **UNKNOWN** — there is a claim or partial witness but the required conditions are not determined by an authorized source-native verifier.
- **SUPPORTED** — the specified observational conditions were checked and supported within the native scope.
- **CONTRADICTED** — a checked observation contradicts the specified required relation within its native scope.

These are **evidence judgments on particular claims**, not universal runtime states. A locally supported edge does not imply that its parent CP is COMPLETE or that the entire composed route is verified. A passing synthetic test does not establish a native production result.

## Existing infrastructure — do not duplicate

- [Core provenance](../../protocols/core/provenance.md) carries ancestry; [cross-layer provenance schema](../../protocols/core/provenance-link.schema.json) connects recorded relations, not guessed candidate execution.
- [Handoff runtime](../../runtime/README.md) and its [native Handoff carrier](../../runtime/handoff.py) retain dependencies, witness requirements, evidence types and actual state.
- [Process Workstation](../../systems/workspace/WORKSTATION.md) and [Workspace Continuity](../../systems/workspace/README.md) retain independent lanes, copies, openings and re-entry. [B2 continuation](../../systems/workspace/WORKSTATION_CONTINUATION_B2.md) already separates candidate branch/connection proposals from native observation and admission.
- [Handoff Language](README.md) renders the packet for a human without inheriting conclusions merely because the words match.
- [Language Referent](../../LANGUAGE_REFERENT.md) remains the ongoing investigation; the formal A and B operators of particular mathematical experiments remain native to those experiments.

**This document is a cross-boundary contract, not a replacement coordinator, worker, verifier, ontology or another implementation of A/B.**

## Runnable example

[Reference README](../../runtime/examples/continuous_handoff/README.md) · [Python reference](../../runtime/examples/continuous_handoff/reference.py) · [sidecar schema](../../runtime/examples/continuous_handoff/sidecar.schema.json) · [example graph](../../runtime/examples/continuous_handoff/example.json) · [tests](../../runtime/examples/continuous_handoff/test_reference.py)

The example is a **read-only sidecar** that traverses all declared predecessor branches from a desired target. Observation claims in JSON stay UNKNOWN without an injected verifier. A hard-coded toy callback is provided to demonstrate the interface, **not** to authenticate a real source. It does not schedule work, generate arbitrary adapters, or modify HandoffRuntime or RuntimeJournal.

A user applying this pattern to real automation must connect actual source owners, permission gates, independently validated observations, revision checks and verified joins. Those production interfaces are **not implemented** by the example.

## Independent reproduction checks

For a real domain adapter, check that:
1. Every declared candidate branch and missing predecessor survives backward traversal.
2. No proposal, simulated return or label match becomes a native observation.
3. All conditions required by a scoped claim are independently verified before support is reported.
4. Contradictions, missing evidence and source edition changes preserve their history and reopen dependent checking.
5. Joining independent branches requires a separately observed relation.
6. Retries and restarts do not duplicate worker admissions or silently mutate source-owned state.
7. A reader can follow both forward consumption and backward provenance from any documented boundary.

**Reader navigation:** ORCID and the public GitHub profile identify a researcher and provide entry points. Neither platform determines the correctness of what a source-native observational layer reports.
