"""Bounded graph scale checks over the canonical append-only RuntimeJournal.

A >1000-link backward chain must not rely on Python recursive path tracing.
Every item remains a proposed candidate, never executable evidence.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.handoff import Handoff
from systems.workspace.workstation_construction import (
    SOURCE, WorkstationConstruction,
)


class ConstructionScaleTests(unittest.TestCase):
    def test_long_unknown_chain_still_has_complete_provenance(self):
        with TemporaryDirectory() as tmp:
            graph = WorkstationConstruction(Path(tmp))
            goal = graph.goal("Required terminal output", provenance="unit:result")
            runtime = graph._runtime()
            downstream = goal
            # Submit into the same genuine runtime object to avoid repetitive
            # test-only journal reopening; no source-native execution occurs.
            for idx in range(1050):
                cid = f"whc-scale-{idx:04d}"
                runtime.submit(Handoff(
                    handoff_id=cid, referent=f"Missing prerequisite {idx}",
                    from_actor="workstation-construction", to_actor="workstation-candidate-review",
                    required_relation="propose possible upstream relationship",
                    inputs={"input_contract": "", "downstream_id": downstream},
                    metadata={"source_system": SOURCE, "node_kind": "CANDIDATE",
                              "goal_id": goal, "downstream_id": downstream,
                              "path_role": "REQUIRED", "capability_hint": ""},
                    provenance=(f"unit:{idx}",),
                ))
                downstream = cid
            view = graph.next_construction_handoffs(goal, max_path_depth=1100)
            path = view["construction_handoffs"][0]["possible_routes_to_result"][0]
            self.assertEqual(len(path), 1051)
            self.assertEqual((path[0], path[-1]), (downstream, goal))
            self.assertFalse(view["whole_chain_verified"])
            self.assertFalse(view["execution_authorized"])
            with self.assertRaisesRegex(ValueError, "depth bound"):
                graph.next_construction_handoffs(goal, max_path_depth=1050)


if __name__ == "__main__":
    unittest.main()
