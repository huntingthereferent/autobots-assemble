import unittest
from runtime import Handoff, HandoffRuntime, ExecutionResult, EvidenceRecord

class RuntimeHardeningTests(unittest.TestCase):
    def test_dependency_cycle_rejected(self):
        rt = HandoffRuntime()
        rt.submit(Handoff(handoff_id="a", referent="test", from_actor="x", to_actor="y", required_relation="go", dependencies=("b",)))
        with self.assertRaisesRegex(ValueError, "cyclic"):
            rt.submit(Handoff(handoff_id="b", referent="test", from_actor="x", to_actor="y", required_relation="go", dependencies=("a",)))

    def test_reopened_evidence_is_not_current(self):
        rt = HandoffRuntime()
        rt.submit(Handoff(handoff_id="a", referent="test", from_actor="x", to_actor="y", required_relation="go", required_witnesses=("ok",)))
        rt.return_result("a", actor_id="y", result=ExecutionResult(status="COMPLETE", evidence=(EvidenceRecord(condition="ok", kind="test", source="fixture"),)))
        rt.reopen("a", actor_id="x", reason="retry")
        self.assertEqual(rt.state("a").missing_witnesses, ("ok",))
        self.assertEqual(rt.state("a").evidence, ())
        self.assertEqual(len(rt.event_store.all()), 3)

if __name__ == "__main__":
    unittest.main()
