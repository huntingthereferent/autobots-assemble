"""Bounded twin experiment using the established recurrence kernel.

This tests identical branch inputs and independent continuation; it does not
assert that the experiment exhausts James's mathematical definition of twins.
"""
from pathlib import Path
import unittest

from foundation.program_kernel.manifest import load_manifest
from foundation.program_kernel.recurrence import Feedback, execute_recurrence

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "foundation" / "program_examples" / "recurrence.json"


class TwinRecurrenceExperiment(unittest.TestCase):
    def test_equal_branches_continue_with_distinct_lineage(self):
        manifest = load_manifest(MANIFEST)
        feedback = Feedback(source_output="value", target_input="value")
        # Same finite contract and same seed, separately executed.
        twins = [
            execute_recurrence(
                manifest, seed_inputs={"value": 0},
                feedback=feedback, steps=4,
            )
            for _ in range(2)
        ]
        left, right = twins
        self.assertEqual(
            [r.values["value"] for r in left.records],
            [r.values["value"] for r in right.records],
        )
        self.assertEqual([r.values["value"] for r in left.records], [1, 2, 3, 4])
        for branch in twins:
            for i, record in enumerate(branch.records):
                self.assertTrue(all(w["passed"] for w in record.witnesses))
                self.assertEqual(
                    record.parent_executions,
                    [] if i == 0 else [branch.records[i - 1].execution_id],
                )
        self.assertTrue(
            set(r.execution_id for r in left.records).isdisjoint(
                r.execution_id for r in right.records
            )
        )


if __name__ == "__main__":
    unittest.main()
