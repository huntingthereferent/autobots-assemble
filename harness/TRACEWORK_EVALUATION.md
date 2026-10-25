# Tracework — frozen-baseline evaluation harness

Baseline repository commit: `56553415946d065baaf7d59eaf727032f6af589c` (2026-10-25).
This branch is an **evaluation workspace**, not a replacement of the operating source. Compare experiments to the pinned baseline. Do not treat subsequent changes to `main` as part of the frozen specimen.

## Question

Which mathematical descriptions of Tracework's **observed implementation** survive explicit tests? In particular, assess the proposed dynamical-systems, A/B relational mapping, predictive-error/free-energy, and tensor/stability descriptions without presuming any is implemented.

## Boundaries

1. **Tracework is the environment**, not a synonym for the Language Referent/A/B inquiry or for any one finite example.
2. **Native sources and evidence win** over descriptions. Preserve original event IDs, parent references, source revisions, timestamps, inputs, outputs, error paths and missing observations.
3. **No ungrounded conversion:** discrete event journals are not continuous trajectories unless an explicit embedding is constructed and tested; A/B is not automatically two metric spaces; mismatch does not imply variational free energy; a graph does not imply a tensor; a successful run does not imply Lyapunov stability.
4. Label every claim **OBSERVED**, **DERIVED**, **HYPOTHESIS**, **COUNTEREXAMPLE**, **UNKNOWN**, or **UNSUPPORTED**.
5. Preserve negative outcomes, incomplete runs, inaccessible private journals and provenance boundaries. Never fabricate an absent witness.
6. Run tests read-only against source snapshots or isolated temporary data. Do not launch production workers, modify private archives, or publish private records as a side effect.
7. Treat `main` as a moving source. Only explicit, reviewed promotions may change production.

## Whole-system inventory and evaluation layers

| Layer | Source of truth | Initial harness question |
| --- | --- | --- |
| Referent and evidence contracts | `LANGUAGE_REFERENT_CONTRACT.md`, `protocols/core/provenance.md` | Can every accepted move be tied to an admissible source/witness? |
| Finite A/B constructions | `work/arc_like_maze/math.py` and its tests | Are roots, bijections and action-labeled transition relations preserved? |
| Runtime, journals and handoffs | `runtime/`, `systems/workspace/` | Do event replay, parent identity, interruption and continuation retain their contracts? |
| Source editions and independent lanes | `systems/workspace/`, `work/` | Are source versions, dependencies, isolation and negative returns recoverable? |
| ARC / WORLD / NIH and other native research | `research/`, `work/` | Do claims match native witnesses and scoped limits? |
| Public viewer and frontages | `docs/live/`, `runtime/http/` | Are displayed claims traceable to their real sources rather than inferred execution? |
| Applications and experiments | `companies/`, `network/tests/` | Which functions are implemented, testable, or only proposed? |

This table is a **coverage plan**, not a statement that every subsystem has been exercised.

## Proposed scientific model tests

### H1: Discrete state-space description
Define a minimal observable state tuple (source identity, lane state, journal frontier, receipts, and pending handoffs) and a transition relation from native event records. Check replay determinism and whether all observed transitions fit the relation. Only consider continuous-time models if independently justified by observed data.

### H2: Relational correspondence
For explicitly finite models, test rooted, bijective, action-preserving correspondence:
`h(T_a(s)) == T'_a(h(s))` for each reachable `s` and admitted action `a`. Compare with negative controls that violate the origin, bijection, or commuting-square requirements. Do not substitute metric-distortion optimization without a separately stated metric and objective.

### H3: Mismatch and correction
Define expected and returned records, a comparator, and correction outcome. Measure mismatch detection and continuation. Predictive coding, variational free energy and active inference remain **hypotheses** until probabilistic generative models, objective functions and observed update rules exist.

### H4: Long-run stability and drift
Operationally define drift (source/parent identity lost, ungrounded result, contradictory journal replay, or unsupported claim promotion). Test bounded sequences and perturbations. Lyapunov claims require a declared state, positive-definite function, dynamics and verified decrease conditions; do not infer convergence from successful bounded runs.

### H5: Scale and computational cost
Measure journal size, event lookup cost, replay latency, memory, concurrent readers/writers, and worker recovery under increasing controlled loads. Report actual measured scaling rather than assumed `O(n^k)`.

## Execution gates

- **Gate 0: Inventory.** Identify entry points, tests, fixtures, external services and private dependencies. Produce a coverage matrix with UNKNOWN for uninspected subsystems.
- **Gate 1: Reproduction.** Run existing tests at the pinned commit and capture commands, environment, exit codes and native outputs.
- **Gate 2: Contracts.** Add explicit positive/negative controls for source identity, event replay, finite A/B alignment, interrupted jobs and viewer provenance.
- **Gate 3: Model discrimination.** Test H1–H5 against the observed implementation; record counterexamples.
- **Gate 4: Load and adversarial.** Exercise bounded replay, corruption, interruption, concurrent access and scaling without production side effects.
- **Gate 5: Review.** Publish a claim/evidence/limit table and only promote source changes with reproducible witnesses.

## Report schema

Each result must record:
`claim_id`, `hypothesis`, `source_commit`, `source_path`, `test_command`, `environment`, `input_or_fixture`, `observed_return`, `expected_return`, `status`, `limitations`, `next_test`.

**Initial status:** Baseline branch created; evaluation protocol specified. No whole-system test execution, full inventory, performance measurement or scientific validation is claimed by this document.
