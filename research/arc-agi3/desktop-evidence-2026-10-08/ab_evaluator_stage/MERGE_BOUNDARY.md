# A/B evaluator — isolated merger witness

Current referent: Merge ARC's observed-action comparison with the existing Continuity A/B evaluator contract.

Current repository: huntingthereferent/language-network.
Repository write state: UNCHANGED. All code in this folder is scratch and isolated from GitHub and the working repository.

## What survived
- Same current referent across evidence and handoff.
- Before/after native observations; verified survival and change.
- Predicted-vs-observed comparison, including preserved counterexamples.
- Native locator and measurement evidence attached to the existing HandoffRuntime event stream.
- AgentLineage.evaluate uses the current AgentMove shape and admits witnessed COMPLETE; no new agent architecture.
- Same shape remains available at next recursion through existing parent_output and parent_evidence.
- No observer -> UNKNOWN. Prediction mismatch or no change -> PARTIAL. Simulation, referent drift, inadmissible evidence -> UNKNOWN.
- Swallow-first remains the existing runtime boundary; this adapter does not invent external observation or autonomous actions.

## Test results
- test_observed_evaluator.py: 14/14 passed, including real staged AgentLineage.step, one-shot event persistence, recursion boundary, missing observation, prediction counterexample.
- test_real_ft09_to_lineage.py: actual FT09 ACTION6 click(36,36) changed observed color 9 -> 8; levels_completed=0 survived; prediction matched; AgentLineage accepted COMPLETE/MOVE with native frame witness; no duplicate execution when stepping again.

## Staged files
- runtime/observed_evaluator.py: candidate NativeABEvaluator and ObservedTransition.
- test_observed_evaluator.py: contract tests.
- test_real_ft09_to_lineage.py: real ARC->Continuity runtime test.
- runtime/*.py other than observed_evaluator.py: test-fixture copies of current GitHub source, not intended as repository replacements.
- runtime/__init__.py is a minimal test harness initializer, not the repo's real __init__.py.

## Exact intended connection after repository write is authorized
- Add ONLY observed_evaluator.py (or equivalent focused implementation) to existing runtime.
- Add the two test witnesses in existing network/tests or matching test suite, using the existing current files.
- Register a real trusted native observation provider with EcosystemService(ab_evaluator=NativeABEvaluator(provider)).
- Keep all other current runtime/orchestrator/agent lineage/AB information logic intact.
- Do not mark autonomous_worker_running true: comparison is verified, actual observation provider and world actuator are separate and must be connected and tested.
- Never let an evaluator execute non-idempotent physical or external actions without a durable idempotency key and retry protocol.

## Current wall
There is no live production native observation-provider registration and there has been no repository write. Therefore the live site's ab_evaluator_connected value has not changed.
