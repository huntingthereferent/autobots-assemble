"""B7 controller invariants using the real on-disk RuntimeJournal.

B2 admission and B4 native decisions here are explicit fixtures; actual B3
subprocess/native B4 verification is covered by test_workstation_cycle_repo_native.
"""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff, HandoffEvent
from runtime.journal import RuntimeJournal
from systems.workspace.workstation_cycle import WorkstationCycle


class StubHarness:
    def __init__(self, data):
        self.path = data / "runtime.jsonl"
        self.new_child = False
        self.mutate = None
        self.calls = 0

    def _runtime(self):
        return HandoffRuntime(event_store=RuntimeJournal(self.path))

    def tick(self):
        self.calls += 1
        if self.mutate:
            self.mutate()
        if self.new_child:
            runtime = self._runtime()
            if "derived-child" not in runtime.snapshot():
                runtime.submit(Handoff(
                    "derived-child", "child", "source", "workstation", "preserve evidence",
                    metadata={"source_system": "workstation-continuation-lane/v1",
                              "lane_id": "derived-child", "parents": ["a"]}))
        return {"execution_started": False, "native_checkpoint_pass": False}


class StubReturn:
    def __init__(self, harness):
        self.harness = harness
        self.allowed = True
        self.reject = False

    def derive_next(self, lane):
        if self.reject:
            raise ValueError("native proof withdrawn")
        if not self.allowed:
            return {"state": "NO_ADMITTED_NEXT_RELATION"}
        runtime = self.harness._runtime()
        if not any(x.event_type == "WORKSTATION_RETURN_RELATION_ADMITTED"
                   for x in runtime.event_store.for_handoff(lane)):
            runtime.event_store.append(HandoffEvent.create(
                handoff_id=lane, event_type="WORKSTATION_RETURN_RELATION_ADMITTED",
                actor_id="fixture", data={"scope": "not a native proof"}))
            self.harness.new_child = True
            return {"state": "NEXT_RELATION_RECORDED"}
        return {"state": "ALREADY_RECORDED"}

    def next_pass(self):
        return self.harness.tick()


class JournalBoundsTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data = Path(tmp.name)
        self.h = StubHarness(self.data)
        runtime = self.h._runtime()
        runtime.submit(Handoff(
            "a", "A independent source", "actor", "workstation", "preserve",
            metadata={"source_system": "workstation-continuation-lane/v1",
                      "lane_id": "a", "parents": []}))
        runtime.submit(Handoff(
            "b", "B independent source", "actor", "other", "preserve",
            metadata={"source_system": "external-system"}))
        self.b4 = StubReturn(self.h)

    def note_return(self):
        self.h._runtime().event_store.append(HandoffEvent.create(
            handoff_id="a", event_type="WORKSTATION_NATIVE_RESULT_VERIFIED",
            actor_id="fixture", data={"scope": "unverified test fixture"}))

    def cycle(self, with_b4=False):
        return WorkstationCycle(self.h, return_continuation=self.b4 if with_b4 else None)

    def replace_record(self, fn):
        rows = [json.loads(line) for line in self.h.path.read_text(encoding="utf-8").splitlines()]
        fn(rows)
        self.h.path.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")

    def test_wall_requires_fresh_exact_resolution_and_keeps_history(self):
        self.note_return()
        wall = HandoffEvent.create(handoff_id="a", event_type=
            "WORKSTATION_OWNER_CANDIDATE_BINDING_WALL", actor_id="fixture",
            data={"job_id": "exact-source-job"})
        self.h._runtime().event_store.append(wall)
        self.assertEqual(self.cycle(True).run().preserved_wall_lanes, ("a",))
        calls = []
        def verify(runtime, event):
            calls.append(event.event_id)
            return event.event_id == wall.event_id and event.data["job_id"] == "exact-source-job"
        report = WorkstationCycle(self.h, return_continuation=self.b4,
                                  verify_wall_resolution=verify).run()
        self.assertEqual(report.preserved_wall_lanes, ())
        self.assertIn("a", report.derived_return_lanes)
        self.assertIn(wall.event_id, calls)
        self.assertTrue(any(e.event_id == wall.event_id for e in self.h._runtime().event_store.all()))
        # Withdrawal restores the wall on the next invocation.
        self.assertEqual(self.cycle(True).run().preserved_wall_lanes, ("a",))

    def test_empty_noop_keeps_existing_journal(self):
        before = self.h.path.read_bytes()
        result = self.cycle().run()
        self.assertEqual(result.status, "QUIESCENT")
        self.assertEqual(result.journal_events_added, 0)
        self.assertEqual(before, self.h.path.read_bytes())

    def test_fixture_next_derivation_records_single_child(self):
        self.note_return()
        result = self.cycle(True).run()
        self.assertIn("a", result.derived_return_lanes)
        self.assertEqual(result.journal_events_added, 2)
        self.assertEqual(result.passes, 2)
        self.assertEqual(self.h._runtime().get("derived-child").metadata["parents"], ["a"])
        self.assertFalse(result.native_worker_executed)
        self.assertFalse(result.native_checkpoint_pass)

    def test_restart_does_not_duplicate_child(self):
        self.note_return()
        self.cycle(True).run()
        old = self.h.path.read_bytes()
        self.assertEqual(self.cycle(True).run().journal_events_added, 0)
        self.assertEqual(self.h.path.read_bytes(), old)

    def test_withdrawn_fixture_derivation_creates_no_child(self):
        self.note_return()
        self.b4.allowed = False
        result = self.cycle(True).run()
        self.assertEqual(result.journal_events_added, 0)
        self.assertEqual(result.unresolved_return_lanes, ("a",))
        self.assertEqual(len(self.h._runtime().snapshot()), 2)

    def test_source_reverification_error_does_not_create_child(self):
        self.note_return()
        self.b4.reject = True
        before = self.h.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "native proof withdrawn"):
            self.cycle(True).run()
        self.assertEqual(self.h.path.read_bytes(), before)

    def test_changing_event_contents_without_changing_id_is_detected(self):
        self.note_return()
        def mut():
            self.replace_record(lambda rows: rows[-1]["event"]["data"].update({"changed": True}))
        self.h.mutate = mut
        with self.assertRaisesRegex(ValueError, "rewritten"):
            self.cycle().run()

    def test_changing_handoff_source_metadata_is_detected(self):
        def mut():
            self.replace_record(lambda rows: rows[0]["handoff"]["metadata"].update(
                {"source_system": "pretend-authenticated-owner"}))
        self.h.mutate = mut
        with self.assertRaisesRegex(ValueError, "handoff specification rewritten"):
            self.cycle().run()

    def test_changing_handoff_parentage_is_detected(self):
        def mut():
            self.replace_record(lambda rows: rows[0]["handoff"]["metadata"].update(
                {"parents": ["invented-parent"]}))
        self.h.mutate = mut
        with self.assertRaisesRegex(ValueError, "handoff specification rewritten"):
            self.cycle().run()

    def test_explicit_limits_and_type_safety(self):
        for kwargs in ({"max_passes": 0}, {"max_passes": True},
                       {"max_new_events": 0}, {"max_new_events": 1001}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.cycle().run(**kwargs)

    def test_max_pass_limit_returns_bounded_state(self):
        self.note_return()
        result = self.cycle(True).run(max_passes=1)
        self.assertEqual(result.status, "BOUND_REACHED")
        self.assertEqual(result.journal_events_added, 2)

    def test_no_runtime_execution_even_with_native_assignment_event(self):
        self.h._runtime().event_store.append(HandoffEvent.create(
            handoff_id="a", event_type="WORKSTATION_NATIVE_HELP_ASSIGNED",
            actor_id="fixture", data={"job_id": "native-ready-but-no-authorization"}))
        result = self.cycle().run()
        self.assertEqual(result.awaiting_native_execution, ("native-ready-but-no-authorization",))
        self.assertFalse(result.native_worker_executed)
        self.assertEqual(result.status, "WAITING_FOR_EVIDENCE_OR_AUTHORIZATION")

    def test_unrelated_native_event_never_creates_continuation_child(self):
        self.h._runtime().event_store.append(HandoffEvent.create(
            handoff_id="b", event_type="WORKSTATION_NATIVE_RESULT_VERIFIED",
            actor_id="fixture", data={"job_id": "unrelated-job"}))
        result = self.cycle(True).run()
        self.assertEqual(result.journal_events_added, 0)
        self.assertEqual(self.h._runtime().snapshot().keys(), {"a", "b"})


if __name__ == "__main__":
    unittest.main()
