# NIH Phase 2 — OWL entailment and ontology inconsistency scope

**Trace:** existing [parent PR #285](https://github.com/huntingthereferent/autobots-assemble/pull/285) → [tracking issue #400](https://github.com/huntingthereferent/autobots-assemble/issues/400) → this independent branch.

## Current referent
[#285](https://github.com/huntingthereferent/autobots-assemble/pull/285) verified 402/402 finite 1–6-edge source-reachability questions against independent SPARQL property paths. This did not establish general OWL entailment or original ontology consistency. Historical edge-time cutoffs were synthetic.

## Independent movement
Pin original OBO Relations Ontology release, distinguish true source axioms from experiment-added fixtures, and predeclare a finite test battery for entailment, subclass/property inference, disjointness contradictions, and unsatisfiable-class detection under a named reasoner profile. Compare independent engines or implementations with the **same source axioms**.

## Measured outcomes
Report source-edge proofs, profile coverage, original-vs-injected contradiction counts, logical failure and unknown counts, class/property/triple counts, runtime and memory. Explicitly mark `NOT_MEASURED` for unsupported complete OWL DL/class satisfiability and never report synthetic fixture inconsistency as a real original source defect.

## Test gates
Independent source identity/hash verification, contradictory fixture isolation, unexpected inference and cyclic-path counterexamples, reasoner-profile mismatch detection and original source controls.

## Lane boundaries
- **Status (2026-10-22): OPEN / SPECIFIED, NOT EXECUTED.** No new scientific finding, worker job, checkpoint, native CI PASS or NIH submission is asserted by opening this branch.
- Source-owned work stays in its parent code area; this file specifies an independently auditable branch without changing other NIH source, W13 native 12-job journal/executable, WORLD, ARC or license.
- A failure, empty result or unavailable upstream source is retained as evidence, not repaired with fictional examples.
- Before any merge: implement finite source-owned tests, run dedicated authentic-source GitHub Actions, record artifact hashes and negatives, then review whole-repo protocol CI against the same exact branch head.
- This is independent research connected to NIH-style requirements, not institutional affiliation, clinical validation, patient-level inference, official challenge scoring or a grant application.
