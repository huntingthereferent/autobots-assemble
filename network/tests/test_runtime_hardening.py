import unittest
import tempfile
from pathlib import Path
from runtime.journal import RuntimeJournal
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

    def test_journal_replay_and_duplicate_event_rejection(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "runtime.jsonl"
            rt = HandoffRuntime(event_store=RuntimeJournal(path))
            rt.submit(Handoff(handoff_id="one", referent="fixture",
                              from_actor="a", to_actor="b", required_relation="check"))
            rt.return_result("one", actor_id="b",
                             result=ExecutionResult(status="UNKNOWN"))
            restored = HandoffRuntime(event_store=RuntimeJournal(path))
            self.assertEqual(restored.state("one").status, "UNKNOWN")
            event = restored.event_store.all()[-1]
            with self.assertRaisesRegex(ValueError, "duplicate"):
                restored.event_store.append(event)

    def test_replay_rejects_broken_parent(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "runtime.jsonl"
            rt = HandoffRuntime(event_store=RuntimeJournal(path))
            rt.submit(Handoff(handoff_id="one", referent="fixture",
                              from_actor="a", to_actor="b", required_relation="check"))
            rt.return_result("one", actor_id="b",
                             result=ExecutionResult(status="UNKNOWN"))
            import json
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            rows[-1]["event"]["parents"] = ["nonexistent-event"]
            path.write_text("".join(json.dumps(row) + "\n" for row in rows))
            with self.assertRaisesRegex(ValueError, "parent"):
                RuntimeJournal(path)

    def test_reopen_replay_preserves_history_but_resets_current_witnesses(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "runtime.jsonl"
            rt = HandoffRuntime(event_store=RuntimeJournal(path))
            rt.submit(Handoff(handoff_id="retry", referent="fixture",
                              from_actor="a", to_actor="b", required_relation="check",
                              required_witnesses=("verified",)))
            rt.return_result("retry", actor_id="b", result=ExecutionResult(
                status="COMPLETE", evidence=(
                    EvidenceRecord(condition="verified", kind="test", source="fixture"),
                )))
            rt.reopen("retry", actor_id="a", reason="new attempt")
            restored = HandoffRuntime(event_store=RuntimeJournal(path))
            state = restored.state("retry")
            self.assertEqual(state.status, "READY")
            self.assertEqual(state.evidence, ())
            self.assertEqual(state.missing_witnesses, ("verified",))
            self.assertEqual(len(restored.event_store.all()), 3)

if __name__ == "__main__":
    unittest.main()
