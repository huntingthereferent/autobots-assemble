"""Regression: B9 native workstation event contracts survive append and replay.

Source-verified fixture observations are explicitly local tests, not live native proof.
"""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.handoff import Handoff, HandoffEvent
from runtime.journal import RuntimeJournal, event_to_dict
from systems.workspace.workstation_construction import (
    WorkstationConstruction, ObservationalDetermination, LINK, OBSERVED,
    SOURCE_SUGGESTED, SOURCE,
)
from systems.workspace.cp_motion import checkpoint_frontier, workstation_cp_view


class ConstructionJournalContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "runtime.jsonl"
        self.graph = WorkstationConstruction(self.root)
        self.goal = self.graph.goal("A bounded game proof", provenance="user:exact-referent")
        self.a = self.graph.candidate(self.goal, "Recover missing native input",
                                      provenance="source:unknown")
        self.b = self.graph.candidate(self.goal, "Try alternate input",
                                      provenance="source:unknown")

    def _event(self, type_, handoff_id, data, actor="workstation-candidate-construction"):
        current = self.graph._runtime().state(handoff_id)
        return HandoffEvent.create(
            handoff_id=handoff_id, event_type=type_, actor_id=actor, data=data,
            parents=(current.last_event_id,),
        )

    def _source(self):
        return self.graph.suggest_source(
            self.a, worker_id="candidate-worker", edition_ref="edition-1",
            source_locator="repo:possible-code", reason="possibly fits")

    def _observation(self, verdict="CONTRADICTED"):
        observer = ObservationalDetermination(
            self.graph, verify_native_receipt=lambda receipt: (
                receipt.native_source == "fixture:local-only"))
        return observer.record(observer.receipt_for(
            self.a, verdict=verdict, witness_ref="fixture:neg-1",
            native_source="fixture:local-only", relation_scope="single candidate",
            source_report_sha256="a" * 64))

    def test_actual_b9_events_survive_append_and_restart_and_preserve_ancestry(self):
        link = self.graph.propose_connection(
            self.a, self.b, reason="hypothetical upstream join")
        source = self._source()
        observation = self._observation()
        before = self.path.read_bytes()
        fresh = RuntimeJournal(self.path)
        kinds = [x.event_type for x in fresh.all()]
        self.assertEqual(kinds.count(LINK), 1)
        self.assertEqual(kinds.count(SOURCE_SUGGESTED), 1)
        self.assertEqual(kinds.count(OBSERVED), 1)
        self.assertTrue(link.startswith("whlink-"))
        self.assertTrue(source.startswith("whsource-"))
        self.assertTrue(observation.startswith("whdetermination-"))
        self.assertEqual(self.path.read_bytes(), before)
        node = next(x for x in self.graph.inspect(self.goal)["nodes"] if x["id"] == self.a)
        self.assertEqual(node["historical_verdict"], "CONTRADICTED")
        self.assertFalse(node["current_native_verification"])
        self.assertFalse(node["native_execution_admitted"])

    def test_bad_actor_other_domain_and_execution_promotion_rejected_before_write(self):
        self._source()
        before = self.path.read_bytes()
        cases = [
            self._event(SOURCE_SUGGESTED, self.a,
                        next(e.data for e in self.graph._runtime().event_store.all()
                             if e.event_type == SOURCE_SUGGESTED), actor="claimed-owner"),
            self._event(SOURCE_SUGGESTED, self.goal,
                        next(e.data for e in self.graph._runtime().event_store.all()
                             if e.event_type == SOURCE_SUGGESTED)),
        ]
        for event in cases:
            with self.subTest(type=event.event_type, actor=event.actor_id), self.assertRaises(ValueError):
                self.graph._runtime().event_store.append(event)
            self.assertEqual(self.path.read_bytes(), before)
        external = self.graph._runtime()
        external.submit(Handoff("external-cp", "historical CP30", "a", "b", "work",
                                metadata={"source_system": "process-workstation"}))
        now = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "exact B9 source"):
            external.event_store.append(self._event(
                SOURCE_SUGGESTED, "external-cp", {"execution_authorized": False}))
        self.assertEqual(self.path.read_bytes(), now)

    def test_tampered_source_claim_not_accepted_as_native_proof(self):
        self._source()
        event = next(e for e in self.graph._runtime().event_store.all()
                     if e.event_type == SOURCE_SUGGESTED)
        for field, value in (("execution_authorized", True),
                             ("capability_fit", "SUPPORTED"),
                             ("source_presence", "NATIVELY_VERIFIED"),
                             ("worker_id", "different-edition")):
            data = {**event.data, field: value}
            bad = self._event(SOURCE_SUGGESTED, self.a, data)
            before = self.path.read_bytes()
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.graph._runtime().event_store.append(bad)
            self.assertEqual(self.path.read_bytes(), before)

    def test_recorded_observation_cannot_become_whole_chain_certification(self):
        self._observation("SUPPORTED")
        event = next(e for e in self.graph._runtime().event_store.all()
                     if e.event_type == OBSERVED)
        for change in ({"observation_scope": "whole-chain approved"},
                       {"candidate_id": self.b}, {"verdict": "VERIFIED_COMPLETE"},
                       {"candidate_spec_sha256": "f" * 64}):
            bad = self._event(OBSERVED, self.a, {**event.data, **change},
                              actor="workstation-native-observation")
            before = self.path.read_bytes()
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.graph._runtime().event_store.append(bad)
            self.assertEqual(self.path.read_bytes(), before)

    def test_replay_rejects_forged_b9_event_without_mutation(self):
        self._source()
        original = self.path.read_bytes()
        record = next(e for e in self.graph._runtime().event_store.all()
                      if e.event_type == SOURCE_SUGGESTED)
        forged = HandoffEvent.create(
            handoff_id=self.a, event_type=SOURCE_SUGGESTED,
            actor_id="workstation-candidate-construction",
            parents=(record.event_id,),
            data={**record.data, "execution_authorized": True},
        )
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"record_type": "EVENT", "event": event_to_dict(forged)}) + "\n")
        with self.assertRaises(ValueError):
            RuntimeJournal(self.path)
        self.path.write_bytes(original)
        self.assertEqual(len(RuntimeJournal(self.path).all()),
                         len(self.graph._runtime().event_store.all()))

    def test_b9_record_cannot_become_checkpoint_frontier_witness(self):
        self._observation("SUPPORTED")
        # B9 observations live in the canonical journal but are not CP worker jobs.
        native = workstation_cp_view(self.root)
        frontier = checkpoint_frontier(native)
        self.assertEqual(frontier["witnessed"], [])
        self.assertEqual(frontier["started_workers"], 0)
        self.assertFalse(self.graph.inspect(self.goal)["claims_native_completion"])
        self.assertEqual(self.graph._runtime().get(self.a).metadata["source_system"], SOURCE)

    def test_cp_help_return_cannot_skip_assignment_or_change_source(self):
        rt = self.graph._runtime()
        rt.submit(Handoff(
            "cp-help-fixture", "CP assistance", "cp-coordinator", "capability-router",
            "bounded helper", metadata={"source_system": "cp-worker-help-opening"}))
        before = self.path.read_bytes()
        current = rt.state("cp-help-fixture")
        forged = HandoffEvent.create(
            handoff_id="cp-help-fixture", event_type="HELP_RETURNED",
            actor_id="cp-help-coordinator",
            data={"job_id": "invented-worker", "native_verifier_confirmed": True,
                  "claim_scope": "all native tasks"},
            parents=(current.last_event_id,))
        with self.assertRaisesRegex(ValueError, "prior exact assignment"):
            rt.event_store.append(forged)
        self.assertEqual(self.path.read_bytes(), before)

    def test_unknown_construction_event_fails_without_file_change(self):
        event = self._event("WORKSTATION_CONSTRUCTION_FAKE_EXECUTED", self.a,
                            {"status": "COMPLETE"})
        before = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "invalid runtime event type"):
            self.graph._runtime().event_store.append(event)
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
