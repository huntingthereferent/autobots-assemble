from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from foundation.program_kernel.compose import CompositionError, Link, execute_linked
from foundation.program_kernel.contracts import ContractError
from foundation.program_kernel.graph import GraphError, GraphLink, GraphNode, execute_graph
from foundation.program_kernel.recurrence import Feedback, RecurrenceError, execute_recurrence
from foundation.program_kernel.manifest import ManifestError, load_manifest
from foundation.program_kernel.runtime import execute


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "foundation" / "program_examples"


class ProgramFoundationTests(unittest.TestCase):
    def test_stateless_shape_reuses_produced_value_as_next_input(self):
        manifest = load_manifest(EXAMPLES / "stateless.json")
        record = execute(manifest, {"text": "  ONE   two THREE "})

        self.assertEqual(record.values["normalized"], "one two three")
        self.assertEqual(record.values["count"], 3)
        self.assertEqual(
            [step.operation for step in record.steps],
            ["normalize", "count"],
        )
        self.assertEqual(record.steps[0].produced, ["normalized"])
        self.assertEqual(record.steps[1].consumed, ["normalized"])
        self.assertTrue(all(w["passed"] for w in record.witnesses))

    def test_stateful_shape_uses_same_kernel(self):
        manifest = load_manifest(EXAMPLES / "stateful.json")
        record = execute(manifest, {"delta": 2}, initial_state={"count": 5})

        self.assertEqual(record.values["count"], 7)
        self.assertEqual(len(record.steps), 1)
        self.assertTrue(all(w["passed"] for w in record.witnesses))

    def test_event_device_shape_uses_same_kernel(self):
        manifest = load_manifest(EXAMPLES / "event_device.json")
        samples = [
            False, False,
            True, False, True, False,
            True, True, True, True,
        ]
        record = execute(manifest, {"samples": samples})

        self.assertEqual(record.values["toggle_count"], 1)
        self.assertIs(record.values["led_on"], True)
        self.assertTrue(all(w["passed"] for w in record.witnesses))

    def test_invalid_manifest_fails_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / "bad.json"
            bad.write_text('{"id": "broken"}', encoding="utf-8")

            with self.assertRaises(ManifestError):
                load_manifest(bad)

    def test_input_contract_mismatch_is_rejected(self):
        manifest = load_manifest(EXAMPLES / "stateless.json")
        with self.assertRaises(ContractError):
            execute(manifest, {"text": 123})

    def test_operation_output_contract_is_rejected(self):
        manifest = load_manifest(EXAMPLES / "stateless.json")
        changed = copy.deepcopy(manifest)
        changed["outputs"]["count"]["type"] = "string"

        with self.assertRaises(ContractError):
            execute(changed, {"text": "one two three"})

    def test_all_shapes_emit_same_execution_record_structure(self):
        cases = [
            (load_manifest(EXAMPLES / "stateless.json"), {"text": "one two three"}, None),
            (load_manifest(EXAMPLES / "stateful.json"), {"delta": 2}, {"count": 5}),
            (
                load_manifest(EXAMPLES / "event_device.json"),
                {"samples": [False, True, True, True]},
                None,
            ),
        ]

        for manifest, inputs, state in cases:
            record = execute(manifest, inputs, initial_state=state)
            self.assertEqual(record.manifest_id, manifest["id"])
            self.assertEqual(record.referent, manifest["referent"])
            self.assertTrue(record.steps)
            self.assertTrue(record.witnesses)
            self.assertIsInstance(record.values, dict)

    def test_cross_program_output_becomes_input_with_provenance(self):
        source_manifest = load_manifest(EXAMPLES / "stateless.json")
        target_manifest = load_manifest(EXAMPLES / "composition_target.json")

        source = execute(source_manifest, {"text": "one two three"})
        target = execute_linked(
            source_manifest=source_manifest,
            source_record=source,
            target_manifest=target_manifest,
            link=Link(source_output="count", target_input="count"),
        )

        self.assertEqual(target.values["description"], "3 is odd")
        self.assertEqual(target.parent_executions, [source.execution_id])
        self.assertEqual(
            target.provenance["count"]["source_execution_id"],
            source.execution_id,
        )
        self.assertEqual(
            target.provenance["count"]["source_output"],
            "count",
        )
        self.assertTrue(all(w["passed"] for w in target.witnesses))

    def test_incompatible_cross_program_contract_is_rejected(self):
        source_manifest = load_manifest(EXAMPLES / "stateless.json")
        target_manifest = load_manifest(EXAMPLES / "stateful.json")
        source = execute(source_manifest, {"text": "one two three"})

        with self.assertRaises(CompositionError):
            execute_linked(
                source_manifest=source_manifest,
                source_record=source,
                target_manifest=target_manifest,
                link=Link(source_output="normalized", target_input="delta"),
                initial_state={"count": 5},
            )

    def test_generic_graph_executes_relations_without_domain_kernel_changes(self):
        stateless = load_manifest(EXAMPLES / "stateless.json")
        describe = load_manifest(EXAMPLES / "composition_target.json")

        graph = execute_graph(
            nodes={
                "source": GraphNode(
                    manifest=stateless,
                    inputs={"text": "one two three"},
                ),
                "describe": GraphNode(manifest=describe),
                "reuse": GraphNode(manifest=stateless),
            },
            links=[
                GraphLink("source", "count", "describe", "count"),
                GraphLink("describe", "description", "reuse", "text"),
            ],
        )

        self.assertEqual(graph.order, ["source", "describe", "reuse"])
        self.assertEqual(graph.records["source"].values["count"], 3)
        self.assertEqual(graph.records["describe"].values["description"], "3 is odd")
        self.assertEqual(graph.records["reuse"].values["normalized"], "3 is odd")
        self.assertEqual(graph.records["reuse"].values["count"], 3)

        describe_record = graph.records["describe"]
        reuse_record = graph.records["reuse"]
        self.assertEqual(
            describe_record.provenance["count"]["source_node"],
            "source",
        )
        self.assertEqual(
            reuse_record.provenance["text"]["source_node"],
            "describe",
        )
        self.assertIn(
            graph.records["source"].execution_id,
            describe_record.parent_executions,
        )
        self.assertIn(
            describe_record.execution_id,
            reuse_record.parent_executions,
        )

    def test_graph_rejects_cycle_without_explicit_state_time_model(self):
        stateless = load_manifest(EXAMPLES / "stateless.json")
        describe = load_manifest(EXAMPLES / "composition_target.json")

        with self.assertRaises(GraphError):
            execute_graph(
                nodes={
                    "a": GraphNode(manifest=stateless),
                    "b": GraphNode(manifest=describe),
                },
                links=[
                    GraphLink("a", "count", "b", "count"),
                    GraphLink("b", "description", "a", "text"),
                ],
            )

    def test_graph_rejects_missing_required_relation(self):
        stateless = load_manifest(EXAMPLES / "stateless.json")

        with self.assertRaises(GraphError):
            execute_graph(
                nodes={"only": GraphNode(manifest=stateless)},
                links=[],
            )

    def test_bounded_recurrence_reuses_output_under_same_contract(self):
        manifest = load_manifest(EXAMPLES / "recurrence.json")

        run = execute_recurrence(
            manifest,
            seed_inputs={"value": 0},
            feedback=Feedback(source_output="value", target_input="value"),
            steps=4,
        )

        self.assertEqual(
            [record.values["value"] for record in run.records],
            [1, 2, 3, 4],
        )

        for index, record in enumerate(run.records):
            self.assertTrue(all(w["passed"] for w in record.witnesses))
            if index == 0:
                self.assertEqual(record.parent_executions, [])
                self.assertEqual(
                    record.provenance["value"]["kind"],
                    "operation_output",
                )
            else:
                previous = run.records[index - 1]
                self.assertEqual(
                    record.parent_executions,
                    [previous.execution_id],
                )
                # The final value provenance records the operation that produced
                # the current output, while the step's consumed input lineage
                # is preserved by the parent execution relation.
                self.assertEqual(
                    record.provenance["value"]["execution_id"],
                    record.execution_id,
                )

    def test_recurrence_rejects_zero_steps(self):
        manifest = load_manifest(EXAMPLES / "recurrence.json")

        with self.assertRaises(RecurrenceError):
            execute_recurrence(
                manifest,
                seed_inputs={"value": 0},
                feedback=Feedback(source_output="value", target_input="value"),
                steps=0,
            )

    def test_recurrence_rejects_incompatible_feedback_contract(self):
        source = load_manifest(EXAMPLES / "stateless.json")

        with self.assertRaises(RecurrenceError):
            execute_recurrence(
                source,
                seed_inputs={"text": "one two"},
                feedback=Feedback(source_output="count", target_input="text"),
                steps=2,
            )


if __name__ == "__main__":
    unittest.main()
