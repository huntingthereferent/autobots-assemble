"""Contract checks against staged copies of James's current runtime classes."""
from __future__ import annotations

import unittest
from runtime.activation import ActivationRegistry, ActivationRoute
from runtime.agent_lineage import AgentLineage, AgentMove
from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, Handoff, HandoffState
from runtime.observed_evaluator import NativeABEvaluator, ObservedTransition, compare_observations


def witness(**kwargs):
    values = {
        "referent": "same referent",
        "before": {"x": 0, "color": 9},
        "after": {"x": 1, "color": 9},
        "predicted_after": {"x": 1, "color": 9},
        "before_ref": "native://cell/state0",
        "after_ref": "native://cell/state1",
        "source": "native-observer",
        "action": "right",
        "evidence_kind": "measurement",
    }
    values.update(kwargs)
    return ObservedTransition(**values)


def handoff(*, required_witnesses=("movement witness",), **kwargs):
    opts = {
        "handoff_id": "task-1",
        "referent": "same referent",
        "from_actor": "test",
        "to_actor": "agent-ab",
        "required_relation": "A/B compare admitted referent",
        "required_witnesses": required_witnesses,
        "admissible_evidence": {"movement witness": ("measurement",)} if required_witnesses else {},
    }
    opts.update(kwargs)
    return Handoff(**opts)


READY = HandoffState(handoff_id="task-1", status="READY")


class TestNativeABEvaluator(unittest.TestCase):
    def test_move_preserves_and_changes_real_relations(self):
        x = NativeABEvaluator(lambda h,s:witness())(handoff(),READY)
        self.assertIsInstance(x, AgentMove)
        self.assertEqual(x.result.status,"COMPLETE")
        self.assertEqual(x.result.output["ab_state"],"MOVE")
        self.assertEqual(x.result.output["survived"],{"color":9})
        self.assertEqual(x.result.output["changed"]["x"]["before"],0)
        self.assertEqual(x.result.output["changed"]["x"]["after"],1)
        self.assertEqual(x.result.evidence[0].ref,"native://cell/state1")
        self.assertFalse(x.next_referent)

    def test_unconnected_observer_fails_closed(self):
        x=NativeABEvaluator(lambda h,s:None)(handoff(),READY)
        self.assertEqual(x.result.status,"UNKNOWN")
        self.assertFalse(x.result.evidence)

    def test_failed_prediction_preserves_counterexample_without_complete(self):
        x=NativeABEvaluator(lambda h,s:witness(predicted_after={"x":2,"color":9}))(handoff(),READY)
        self.assertEqual(x.result.status,"PARTIAL")
        self.assertEqual(x.result.output["observed"]["x"],1)
        self.assertEqual(x.result.output["predicted"]["x"],2)
        self.assertFalse(x.result.output["prediction_matched"])
        self.assertFalse(x.result.evidence)

    def test_same_state_preservation_not_a_claimed_move(self):
        x=NativeABEvaluator(lambda h,s:witness(after={"x":0,"color":9}))(handoff(),READY)
        self.assertEqual(x.result.status,"PARTIAL")
        self.assertEqual(x.result.output["survived"],{"x":0,"color":9})

    def test_simulated_witness_is_not_promoted(self):
        x=NativeABEvaluator(lambda h,s:witness(evidence_kind="simulation"))(handoff(),READY)
        self.assertEqual(x.result.status,"UNKNOWN")

    def test_missing_before_after_distinction_is_not_promoted(self):
        x=NativeABEvaluator(lambda h,s:witness(after_ref="native://cell/state0"))(handoff(),READY)
        self.assertEqual(x.result.status,"UNKNOWN")

    def test_current_referent_not_replaced(self):
        x=NativeABEvaluator(lambda h,s:witness(referent="other"))(handoff(),READY)
        self.assertEqual(x.result.status,"UNKNOWN")

    def test_source_kind_must_be_admitted(self):
        x=NativeABEvaluator(lambda h,s:witness(evidence_kind="source"))(handoff(),READY)
        self.assertEqual(x.result.status,"UNKNOWN")

    def test_extra_required_witness_cannot_be_fabricated(self):
        h=handoff(required_witnesses=("movement witness","human approval"),
                  admissible_evidence={"movement witness":("measurement",)})
        x=NativeABEvaluator(lambda h,s:witness())(h,READY)
        self.assertEqual(x.result.status,"UNKNOWN")

    def test_observer_exception_is_unknown(self):
        def bad(h,s):raise OSError("offline")
        x=NativeABEvaluator(bad)(handoff(),READY)
        self.assertEqual(x.result.status,"UNKNOWN")

    def test_added_removed_keys_preserve_presence_information(self):
        surv,ch=compare_observations({"old":1,"same":2},{"new":3,"same":2})
        self.assertEqual(surv,{"same":2})
        self.assertEqual(ch["old"]["after_present"],False)
        self.assertEqual(ch["new"]["before_present"],False)

    def test_real_lineage_step_witness_admission(self):
        r=HandoffRuntime()
        registry=ActivationRegistry((ActivationRoute(
            activation_id="explicit-test",surfaces=("a/b-test",),
            actor_id="tester",referent="same referent",projection="agent_lineage",
        ),))
        lineage=AgentLineage(
            r,registry,evaluate=NativeABEvaluator(lambda h,s:witness()),
            allow_simulation=False,
        )
        root=lineage.activate("a/b-test",actor_id="tester",instance_id="one")
        self.assertIsNotNone(root)
        self.assertEqual(r.state(root).status,"READY")
        ran=lineage.step(root)
        self.assertEqual(ran.executed,(root,))
        self.assertEqual(r.state(root).status,"COMPLETE")
        self.assertEqual(r.state(root).output["ab_state"],"MOVE")
        self.assertEqual(r.state(root).evidence[0].condition,"movement witness")
        self.assertEqual(lineage.step(root).executed,())
        self.assertEqual(len([e for e in r.event_store.for_handoff(root) if e.event_type=="RESULT"]),1)

    def test_real_lineage_missing_observer_remains_unknown(self):
        r=HandoffRuntime()
        registry=ActivationRegistry((ActivationRoute(
            activation_id="explicit-test",surfaces=("a/b-test",),
            actor_id="tester",referent="same referent",projection="agent_lineage",
        ),))
        lineage=AgentLineage(
            r,registry,evaluate=NativeABEvaluator(lambda h,s:None),
            allow_simulation=False,
        )
        root=lineage.activate("a/b-test",actor_id="tester",instance_id="two")
        ran=lineage.step(root)
        self.assertEqual(ran.executed,(root,))
        self.assertEqual(r.state(root).status,"UNKNOWN")
        self.assertEqual(r.state(root).evidence,())

    def test_real_lineage_next_referent_only_when_witnessed(self):
        r=HandoffRuntime()
        registry=ActivationRegistry((ActivationRoute(
            activation_id="explicit-test",surfaces=("a/b-test",),
            actor_id="tester",referent="same referent",projection="agent_lineage",
        ),))
        lineage=AgentLineage(
            r,registry,evaluate=NativeABEvaluator(
                lambda h,s:witness(next_referent="next observed referent")),
            allow_simulation=False,
        )
        root=lineage.activate("a/b-test",actor_id="tester",instance_id="three")
        ran=lineage.step(root)
        self.assertEqual(len(ran.born),1)
        child=r.get(ran.born[0])
        self.assertEqual(child.referent,"next observed referent")
        self.assertEqual(child.inputs["parent_output"]["ab_state"],"MOVE")
        # The next task has no observer matching its new referent.
        # A real native observer is required again before another MOVE.
        newer=lineage.step(root)
        self.assertEqual(r.state(ran.born[0]).status,"UNKNOWN")
        self.assertEqual(newer.born,())


if __name__=="__main__":
    unittest.main(verbosity=2)
