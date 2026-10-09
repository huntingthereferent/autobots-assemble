from pathlib import Path
repo = Path(r"C:\Users\teepa\continuity-live")
def replace(rel, old, new):
    p=repo/rel
    s=p.read_text(encoding="utf-8")
    count=s.count(old)
    assert count==1, (rel, count, old[:40])
    p.write_text(s.replace(old,new),encoding="utf-8")

replace("runtime/service.py",
    "from runtime.agent_lineage import AgentLineage, Evaluator, ClosureAdmitter\n",
    "from runtime.agent_lineage import AgentLineage, Evaluator, ClosureAdmitter\nfrom runtime.observed_evaluator import NativeABEvaluator, Observer\n")
replace("runtime/service.py",
    "        ab_evaluator: Evaluator | None = None,\n        closure_admitter:",
    "        ab_evaluator: Evaluator | None = None,\n        native_observer: Observer | None = None,\n        closure_admitter:")
replace("runtime/service.py",
    "        self.agent_lineage = AgentLineage(\n            self.runtime, self.activations,\n            evaluate=ab_evaluator, admit_closure=closure_admitter,",
    "        if native_observer is not None and ab_evaluator is not None:\n            raise ValueError('choose either an A/B evaluator or its native observer')\n        evaluated = (NativeABEvaluator(native_observer)\n                     if native_observer is not None else ab_evaluator)\n        self.agent_lineage = AgentLineage(\n            self.runtime, self.activations,\n            evaluate=evaluated, admit_closure=closure_admitter,")
replace("runtime/agent_lineage.py",
    '            if state.status == "READY" and self.evaluate is not None:\n                decision = self.evaluate(agent, state)',
    '            if state.status == "READY" and self.evaluate is not None:\n                # Read-only native observers cannot run before an actual capture.\n                # Leave READY for swallow/observation; do not persist invented UNKNOWN.\n                ready = getattr(self.evaluate, "has_observation", None)\n                if ready is not None and not ready(agent.handoff_id):\n                    continue\n                decision = self.evaluate(agent, state)')
replace("runtime/observed_evaluator.py",
    '"""Native-witness A/B evaluator candidate, staged outside the repository.',
    '"""Native-witness A/B evaluator using the existing lineage contract.')
replace("runtime/observed_evaluator.py",
    '    def __init__(self, observe: Observer) -> None:\n        self.observe = observe\n',
    '    def __init__(self, observe: Observer) -> None:\n        self.observe = observe\n\n    def has_observation(self, handoff_id: str) -> bool:\n        """Readiness is optional for observers without a native capture queue."""\n        available = getattr(self.observe, "has_capture", None)\n        return bool(available(handoff_id)) if callable(available) else True\n')
replace("runtime/arc_native_observer.py",
    '        self._captured: dict[str, ObservedTransition] = {}\n\n    def record_native_step(',
    '        self._captured: dict[str, ObservedTransition] = {}\n\n    def has_capture(self, handoff_id: str) -> bool:\n        return handoff_id in self._captured\n\n    def record_native_step(')
replace("runtime/arc_native_observer.py",
    '        self, *, referent: str, before: Any, after: Any,\n',
    '        self, *, handoff_id: str, referent: str, before: Any, after: Any,\n')
replace("runtime/arc_native_observer.py",
    '        if not referent.strip() or not action.strip() or not 0 <= x < 64 or not 0 <= y < 64:\n            raise ValueError("referent, native action, and in-bounds cell are required")\n',
    '        if not handoff_id.strip() or not referent.strip() or not action.strip() or not 0 <= x < 64 or not 0 <= y < 64:\n            raise ValueError("handoff, referent, native action, and in-bounds cell are required")\n        if handoff_id in self._captured:\n            raise ValueError("native step already captured for this handoff")\n')
replace("runtime/arc_native_observer.py",
    '        self._captured[referent] = observation\n        return observation\n\n    def __call__(self, handoff, state) -> ObservedTransition | None:\n        return self._captured.get(handoff.referent)\n',
    '        self._captured[handoff_id] = observation\n        return observation\n\n    def __call__(self, handoff, state) -> ObservedTransition | None:\n        return self._captured.get(handoff.handoff_id)\n')
replace("network/tests/test_observed_evaluator.py",
    '"""Contract checks against staged copies of James\'s current runtime classes."""',
    '"""Contract checks against the actual repository runtime and handoff classes."""')
print("edits_applied")
