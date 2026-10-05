from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from foundation.program_kernel.contracts import ContractError
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


if __name__ == "__main__":
    unittest.main()
