# Native A/B observations — existing AgentLineage

The ARC observer is an **adapter**, not another agent, solver, game actuator, or general-purpose autonomous worker.

- `runtime.observed_evaluator.NativeABEvaluator` compares independently located before/after observations using the existing `AgentMove`, `ExecutionResult`, and `EvidenceRecord` types.
- `runtime.arc_native_observer.ARCFrameObservationProvider` captures already-performed ARC-AGI-3 SDK frame transitions. The supplied action description is recorded but **not independently attested** by the frame pair.
- `EcosystemService(native_observer=provider)` registers that provider in the existing lineage. Without a provider, `ab_evaluator_connected` remains false.
- A native observer with no capture for a handoff leaves it `READY`, preventing an automatic fake `UNKNOWN` before an external action can occur. Explicitly invoked evaluators without observations continue to return `UNKNOWN`.
- A successful native observation is a *movement witness*, not an ARC level solve, task completion, proven action provenance, or autonomously running agent.

## Trusted in-process connection

The operator or authorized ARC worker creates an agent handoff, performs the native action **outside** the evaluator, records the SDK's native before/after observations, then steps the existing lineage:

```python
from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from runtime.service import EcosystemService
from runtime.arc_native_observer import ARCFrameObservationProvider

provider = ARCFrameObservationProvider("ft09")
service = EcosystemService(data_dir="./state", native_observer=provider)
root = service.agent_lineage.activate(
    "begin comparison", actor_id="james",
    instance_id="ft09-explicit-run-1", referent="ft09 current board",
)

arcade = Arcade(operation_mode=OperationMode.NORMAL)
game = arcade.make("ft09")
before = game.observation_space
after = game.step(GameAction.ACTION6, data={"x": 36, "y": 36})
# Set a real independent prediction before applying the action. The
# example omits a prediction; observed change alone is not a solved level.
provider.record_native_step(
    handoff_id=root, referent="ft09 current board",
    before=before, after=after, action="ACTION6 click(36,36)",
    x=36, y=36,
)
step = service.agent_lineage.step(root)
```

This example is explicitly an actuator operated by its caller. Do **not** automate repeated calls to `game.step` on failed evaluation/restart: action replay needs a durable idempotency key and action-specific retry protocol. The evaluator itself never calls `game.step`. In-memory captures are scoped to the handoff ID and are not persisted as a general event bus; successful comparison results are persisted in the existing runtime journal.

## Checks

```powershell
python -m unittest network.tests.test_observed_evaluator network.tests.test_arc_native_observer network.tests.test_agent_lineage network.tests.test_agent_service network.tests.test_repository_connections
# Optional, with the ARC SDK installed: performs a real game action.
$env:CONTINUITY_ARC_NATIVE_TESTS='1'
python -m unittest network.tests.test_arc_native_observer
```

**Deployment boundary:** the HTTP server does not connect an ARC game or start a native action worker automatically. Its `ab_evaluator_connected` status remains false unless the hosting process explicitly supplies a native observation provider. No arbitrary HTTP caller can register native captures. Operators must arrange a trusted capture source before treating a live environment as connected.
