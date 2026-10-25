import unittest
from runtime import Handoff, HandoffRuntime, ExecutionResult
from harness.tracework_projection import compare_handoff, project

class ProjectionTests(unittest.TestCase):
    def test_match_and_mismatch(self):
        rt = HandoffRuntime()
        rt.submit(Handoff(handoff_id="one", referent="fixture",
                          from_actor="a", to_actor="b", required_relation="check",
                          expected_output={"value": 2, "ok": True}))
        self.assertEqual(project(rt)["states"]["one"], "READY")
        rt.return_result("one", actor_id="b", result=ExecutionResult(
            status="PARTIAL", output={"value": 3}))
        before = rt.event_store.all()
        result = compare_handoff(rt, "one")
        self.assertEqual(result.differing_keys, ("value",))
        self.assertEqual(result.missing_keys, ("ok",))
        self.assertEqual(rt.event_store.all(), before)
        self.assertEqual(project(rt)["unresolved_parent_ids"], ())

    def test_dependency(self):
        rt = HandoffRuntime()
        rt.submit(Handoff(handoff_id="child", referent="fixture",
                          from_actor="a", to_actor="b", required_relation="move",
                          dependencies=("absent",), boundaries=("offline",)))
        self.assertEqual(project(rt)["states"]["child"], "WAITING")
        self.assertEqual(compare_handoff(rt, "child").blocked_by, ("absent",))

    def test_reopen_is_read_only_and_does_not_reuse_old_result(self):
        rt = HandoffRuntime()
        rt.submit(Handoff(handoff_id="parent", referent="fixture",
                          from_actor="a", to_actor="b", required_relation="check",
                          expected_output={"value": 2}))
        rt.submit(Handoff(handoff_id="child", referent="fixture",
                          from_actor="a", to_actor="b", required_relation="move",
                          dependencies=("parent",)))
        rt.return_result("parent", actor_id="b",
                         result=ExecutionResult(status="COMPLETE", output={"value": 2}))
        self.assertEqual(project(rt)["states"]["child"], "READY")
        rt.reopen("parent", actor_id="a", reason="new attempt")
        before = rt.event_store.all()
        measured = project(rt)
        self.assertEqual(measured["states"]["parent"], "READY")
        self.assertEqual(measured["states"]["child"], "WAITING")
        self.assertEqual(measured["mismatches"]["parent"].observed, {})
        self.assertEqual(measured["unresolved_parent_ids"], ())
        self.assertEqual(rt.event_store.all(), before)

if __name__ == "__main__":
    unittest.main()
