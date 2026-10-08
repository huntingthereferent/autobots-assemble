import tempfile
from dataclasses import asdict
from pathlib import Path
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff, HandoffEvent, SimulatedActor
from runtime.journal import RuntimeJournal
from runtime.orchestrator import Orchestrator, SystemBinding, SystemEmission
from runtime.swallow_first import (
    NativeWitness, ReferenceAdmission, SwallowFirstBoundary, SwallowReport,
)


WITNESS = NativeWitness(
    source_kind="native_document",
    locator="https://example.org/native/manual",
    native_ref="revision-4",
    relation="contains exactly the missing contract",
)
EVIDENCE = EvidenceRecord(
    condition="condition proven", kind="native", source="verified revision-4",
    ref=WITNESS.locator, depth="verified",
)
ADMISSION = ReferenceAdmission(
    admitted=True, reference_id="reference/native/revision-4",
    evidence=(EvidenceRecord(
        condition="native source compared", kind="comparison", source="A/B checker",
        ref=WITNESS.locator, depth="tested",
    ),),
)


def build_runtime(*, store=None):
    runtime = HandoffRuntime(event_store=store)
    handoff = Handoff(
        handoff_id="wall-one", referent="precise current referent",
        from_actor="router", to_actor="worker",
        required_relation="exact missing contract",
        required_witnesses=("condition proven",),
        admissible_evidence={"condition proven": ("native",)},
    )
    runtime.submit(handoff)
    runtime.return_result(
        handoff.handoff_id, actor_id="worker",
        result=ExecutionResult(
            status="UNKNOWN", output={"wall": "exact missing contract"},
            note="do not replace this wall",
        ),
    )
    return runtime


class SwallowFirstTests(unittest.TestCase):
    def resolver(self, runtime, **overrides):
        defaults = dict(
            swallow_agent=lambda h, s: SwallowReport(
                searched=("https://example.org/native/",), witnesses=(WITNESS,),
            ),
            admit_reference=lambda h, s, w: ADMISSION,
            resume_worker=lambda h, w, a: ExecutionResult(
                status="COMPLETE", output={"movement": "resumed"},
                evidence=(EVIDENCE,),
            ),
        )
        defaults.update(overrides)
        return SwallowFirstBoundary(runtime, **defaults)

    def test_native_reference_admission_resumes_original_handoff(self):
        runtime = build_runtime()
        boundary = self.resolver(runtime)
        self.assertFalse(boundary.ready_for_james("wall-one"))
        closed = boundary.resolve("wall-one")
        self.assertEqual(closed.status, "COMPLETE")
        self.assertEqual(closed.output, {"movement": "resumed"})
        self.assertFalse(boundary.ready_for_james("wall-one"))
        self.assertEqual(runtime.get("wall-one").referent, "precise current referent")
        events = runtime.event_store.for_handoff("wall-one")
        self.assertEqual(
            [e.data["status"] for e in events if e.event_type == "RESULT"],
            ["UNKNOWN", "COMPLETE"],
        )
        self.assertTrue(any(e.event_type == "REFERENCE_ADMITTED" for e in events))
        self.assertFalse(any(e.event_type == "REOPENED" for e in events))
        self.assertTrue(any(e.event_type == "SWALLOW_ATTEMPT" for e in events))
        self.assertTrue(any(e.condition == "native source compared"
                            for e in closed.evidence))

    def test_failed_swallow_keeps_exact_wall_and_rotates_reground_agents(self):
        runtime = build_runtime()
        initial = runtime.state("wall-one")
        seen = []
        def reground(handoff, wall, report):
            seen.append((handoff.referent, wall.status, wall.output, report.searched))
            return ExecutionResult(status="UNKNOWN", output={"different": "wall"})
        boundary = self.resolver(
            runtime,
            swallow_agent=lambda h, s: SwallowReport(
                searched=("https://example.org/native/",), witnesses=(),
            ),
            reground_agents=(reground,),
        )
        after = boundary.resolve("wall-one")
        self.assertEqual((after.status, after.output),
                         (initial.status, initial.output))
        self.assertEqual(seen[0][1:], ("UNKNOWN", initial.output,
                                     ("https://example.org/native/",)))
        self.assertTrue(boundary.ready_for_james("wall-one"))
        events = runtime.event_store.for_handoff("wall-one")
        self.assertEqual(len([e for e in events if e.event_type == "RESULT"]), 1)
        self.assertTrue(any(e.event_type == "REGROUND_ATTEMPT" for e in events))
        self.assertEqual(events[-1].data["original_output"], initial.output)

    def test_rejected_admission_cannot_fake_worker_move(self):
        runtime = build_runtime()
        boundary = self.resolver(
            runtime,
            admit_reference=lambda h, s, w: ReferenceAdmission(admitted=False),
            resume_worker=lambda h, w, a: self.fail("rejected reference resumed worker"),
        )
        self.assertEqual(boundary.resolve("wall-one").status, "UNKNOWN")
        self.assertTrue(boundary.ready_for_james("wall-one"))
        self.assertTrue(any(e.event_type == "REFERENCE_REJECTED"
                            for e in runtime.event_store.for_handoff("wall-one")))

    def test_invalid_complete_evidence_cannot_erase_original_wall(self):
        runtime = build_runtime()
        boundary = self.resolver(
            runtime,
            resume_worker=lambda h, w, a: ExecutionResult(status="COMPLETE"),
        )
        self.assertEqual(boundary.resolve("wall-one").status, "UNKNOWN")
        self.assertEqual(runtime.state("wall-one").output,
                         {"wall": "exact missing contract"})
        self.assertTrue(boundary.ready_for_james("wall-one"))
        self.assertFalse(any(e.event_type == "REOPENED"
                             for e in runtime.event_store.for_handoff("wall-one")))

    def test_swallow_agent_error_is_not_outward_traversal(self):
        runtime = build_runtime()
        def broken(handoff, wall):
            raise RuntimeError("source unavailable")
        boundary = self.resolver(runtime, swallow_agent=broken)
        self.assertEqual(boundary.resolve("wall-one").status, "UNKNOWN")
        self.assertFalse(boundary.ready_for_james("wall-one"))
        events = runtime.event_store.for_handoff("wall-one")
        attempt = next(e for e in events if e.event_type == "SWALLOW_ATTEMPT")
        self.assertEqual(attempt.data["searched"], [])
        self.assertIn("source unavailable", attempt.data["error"])

    def test_durable_unresolved_wall_not_researched_on_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "journal.jsonl"
            runtime = build_runtime(store=RuntimeJournal(path))
            one = self.resolver(runtime, swallow_agent=lambda h, s: SwallowReport(
                searched=("https://example.org/native/",),
            ))
            self.assertTrue(one.ready_for_james("wall-one") is False)
            one.resolve("wall-one")
            reloaded = HandoffRuntime(event_store=RuntimeJournal(path))
            def duplicate(h, s):
                self.fail("already unresolved wall searched twice")
            two = self.resolver(reloaded, swallow_agent=duplicate)
            self.assertEqual(two.resolve("wall-one").status, "UNKNOWN")
            self.assertTrue(two.ready_for_james("wall-one"))

    def test_orchestrator_automatically_swallow_first_before_reconcile(self):
        runtime = HandoffRuntime()
        boundary = self.resolver(runtime)
        orchestrator = Orchestrator(runtime, boundary_resolver=boundary)
        handoff = Handoff(
            handoff_id="wall-one", referent="precise current referent",
            from_actor="router", to_actor="worker",
            required_relation="exact missing contract",
            required_witnesses=("condition proven",),
            admissible_evidence={"condition proven": ("native",)},
        )
        seen = []
        emission = SystemEmission("source", "local-one", handoff)
        orchestrator.register_system(SystemBinding(
            "source", lambda: (emission,),
            lambda e, s: seen.append((e.local_ref, s.status, s.output)),
        ))
        orchestrator.register_actor(SimulatedActor(
            actor_id="worker", capabilities=("exact missing contract",),
            handler=lambda h: ExecutionResult(
                status="UNKNOWN", output={"wall": "exact missing contract"},
            ),
        ))
        orchestrator.step()
        self.assertEqual(seen, [
            ("local-one", "COMPLETE", {"movement": "resumed"}),
        ])
        self.assertEqual(runtime.state("wall-one").status, "COMPLETE")

    def test_interrupted_swallow_reuses_durable_native_witness(self):
        runtime = build_runtime()
        terminal = next(e for e in runtime.event_store.for_handoff("wall-one")
                        if e.event_type == "RESULT")
        runtime.event_store.append(HandoffEvent.create(
            handoff_id="wall-one", event_type="SWALLOW_ATTEMPT",
            actor_id="swallow-boundary",
            data={
                "terminal_event_id": terminal.event_id,
                "searched": ["https://example.org/native/"],
                "witnesses": [asdict(WITNESS)],
                "outward_traversal": True,
            },
        ))
        def no_second_search(h, s):
            self.fail("interrupted native search must not execute again")
        boundary = self.resolver(runtime, swallow_agent=no_second_search)
        self.assertEqual(boundary.resolve("wall-one").status, "COMPLETE")
        self.assertEqual(sum(e.event_type == "SWALLOW_ATTEMPT"
                             for e in runtime.event_store.for_handoff("wall-one")), 1)

    def test_interrupted_admission_does_not_compare_twice(self):
        runtime = build_runtime()
        terminal = next(e for e in runtime.event_store.for_handoff("wall-one")
                        if e.event_type == "RESULT")
        runtime.event_store.append(HandoffEvent.create(
            handoff_id="wall-one", event_type="SWALLOW_ATTEMPT",
            actor_id="swallow-boundary",
            data={
                "terminal_event_id": terminal.event_id,
                "searched": ["https://example.org/native/"],
                "witnesses": [asdict(WITNESS)],
                "outward_traversal": True,
            },
        ))
        runtime.event_store.append(HandoffEvent.create(
            handoff_id="wall-one", event_type="REFERENCE_ADMITTED",
            actor_id="swallow-boundary",
            data={
                "terminal_event_id": terminal.event_id,
                "reference_id": ADMISSION.reference_id,
                "native_witness": asdict(WITNESS),
            },
            evidence=ADMISSION.evidence,
        ))
        def no_second_admission(h, s, w):
            self.fail("previous admission must replay")
        boundary = self.resolver(
            runtime, swallow_agent=lambda h, s: self.fail("no new search"),
            admit_reference=no_second_admission,
        )
        self.assertEqual(boundary.resolve("wall-one").status, "COMPLETE")
        self.assertEqual(sum(e.event_type == "REFERENCE_ADMITTED"
                             for e in runtime.event_store.for_handoff("wall-one")), 1)

    def test_reference_comparator_failure_is_same_wall(self):
        runtime = build_runtime()
        initial = runtime.state("wall-one")
        def fails(h, s, w):
            raise RuntimeError("A/B comparator unavailable")
        boundary = self.resolver(runtime, admit_reference=fails)
        after = boundary.resolve("wall-one")
        self.assertEqual((after.status, after.output),
                         (initial.status, initial.output))
        self.assertTrue(boundary.ready_for_james("wall-one"))
        events = runtime.event_store.for_handoff("wall-one")
        self.assertTrue(any(
            e.event_type == "REFERENCE_REJECTED"
            and "comparator unavailable" in e.data.get("reason", "")
            for e in events
        ))

    def test_reground_can_close_same_wall_with_real_evidence(self):
        runtime = build_runtime()
        attempts = []
        def one(h, s, report):
            attempts.append(s.output)
            return ExecutionResult(status="UNKNOWN", output={"new": "incorrect"})
        def two(h, s, report):
            attempts.append(s.output)
            return ExecutionResult(status="COMPLETE", evidence=(EVIDENCE,),
                                   output={"reground": "resolved"})
        boundary = self.resolver(
            runtime,
            swallow_agent=lambda h, s: SwallowReport(
                searched=("https://example.org/native/",)),
            reground_agents=(one, two),
        )
        end = boundary.resolve("wall-one")
        self.assertEqual(end.status, "COMPLETE")
        self.assertEqual(end.output["reground"], "resolved")
        self.assertEqual(attempts, [{"wall": "exact missing contract"}] * 2)
        self.assertFalse(boundary.ready_for_james("wall-one"))

    def test_manual_orchestrator_result_also_triggers_swallow(self):
        runtime = HandoffRuntime()
        boundary = self.resolver(runtime)
        orch = Orchestrator(runtime, boundary_resolver=boundary)
        handoff = Handoff(
            handoff_id="wall-one", referent="precise current referent",
            from_actor="router", to_actor="worker",
            required_relation="exact missing contract",
            required_witnesses=("condition proven",),
            admissible_evidence={"condition proven": ("native",)},
        )
        seen = []
        emission = SystemEmission("source", "local-one", handoff)
        orch.register_system(SystemBinding(
            "source", lambda: (emission,),
            lambda e, s: seen.append(s.status),
        ))
        self.assertEqual(orch.step().waiting_for_actor, ("wall-one",))
        state = orch.return_result(
            "wall-one", actor_id="worker",
            result=ExecutionResult(status="BLOCKED",
                                   output={"wall": "exact missing contract"}),
        )
        self.assertEqual(state.status, "COMPLETE")
        self.assertEqual(seen, ["COMPLETE"])

    def test_refuses_mismatched_runtime(self):
        first = HandoffRuntime()
        second = HandoffRuntime()
        with self.assertRaises(ValueError):
            Orchestrator(first, boundary_resolver=self.resolver(second))


if __name__ == "__main__":
    unittest.main()
