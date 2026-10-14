"""Workspace continuity contracts; no implicit task admission or scheduling."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace import WorkspaceStore, workspace_view


class WorkspaceContinuityTests(unittest.TestCase):
    def setUp(self):
        self.store = WorkspaceStore()
        self.a = self.store.open_lane("research", label="Research", referent="finite chatbot", actor_id="james", sources=("work/arc_like_maze/chatbot/README.md",))
        self.b = self.store.open_lane("factory", label="Factory", referent="build a physical part", actor_id="james", sources=("systems/factory/README.md",))

    def test_two_lanes_keep_independent_return_points(self):
        first = self.store.record_movement("research", changes="CP result witnessed", preserved="old witnesses", next_movement="inspect next boundary", evidence_refs=("commit:abc",))
        factory = self.store.get_lane("factory")
        self.assertEqual(factory.latest_event_id, self.b.latest_event_id)
        self.assertEqual(factory.movements, 0)
        self.assertNotEqual(first.latest_event_id, factory.latest_event_id)

    def test_link_does_not_mutate_either_lane(self):
        before = (self.store.get_lane("research"), self.store.get_lane("factory"))
        c = self.store.connect("research", "factory", relation="control evidence needed", evidence_refs=("research:note",))
        self.assertEqual(before, (self.store.get_lane("research"), self.store.get_lane("factory")))
        self.assertEqual(c.relation, "control evidence needed")
        self.assertEqual(len(workspace_view(self.store)["connections"]), 1)

    def test_focus_switch_preserves_both_lanes(self):
        x = self.store.record_movement("research", next_movement="reproduce")
        y = self.store.record_movement("factory", walls=("no measured part",))
        self.store.set_focus("research")
        self.store.set_focus("factory")
        self.assertEqual(self.store.get_lane("research"), x)
        self.assertEqual(self.store.get_lane("factory"), y)
        self.assertEqual(self.store.focused_lane(), "factory")

    def test_focus_can_be_cleared_without_closing_work(self):
        self.store.set_focus("factory")
        self.store.set_focus(None)
        self.assertIsNone(self.store.focused_lane())
        self.assertEqual(len(self.store.lanes()), 2)

    def test_living_or_play_can_remain_a_lane_without_task(self):
        x = self.store.open_lane("play", label="Just exploring", referent="playing a game", actor_id="james")
        self.assertEqual(x.movements, 0)
        self.assertEqual(x.next_movement, "")
        self.assertEqual(len(self.store.events()), 3)

    def test_no_task_or_handoff_side_effect(self):
        self.store.record_movement("research", changes="noted something interesting")
        view = workspace_view(self.store)
        self.assertNotIn("handoffs", view)
        self.assertNotIn("tasks", view)
        self.assertEqual(len(view["lanes"]), 2)

    def test_projection_is_pure_and_has_return_point(self):
        self.store.record_movement("factory", preserved="mechanical drawing still valid", next_movement="measure prototype")
        start = self.store.events()
        view = workspace_view(self.store)
        self.assertEqual(start, self.store.events())
        factory = next(x for x in view["lanes"] if x["lane_id"] == "factory")
        self.assertEqual(factory["next_movement"], "measure prototype")
        self.assertEqual(factory["return_event_id"], self.store.get_lane("factory").latest_event_id)

    def test_person_scoped_view_does_not_leak_lanes_or_connections(self):
        self.store.open_lane("other", label="Other", referent="independent", actor_id="someone-else")
        self.store.connect("research", "other", relation="cross-person source")
        v = workspace_view(self.store, actor_id="james")
        self.assertEqual({x["lane_id"] for x in v["lanes"]}, {"research", "factory"})
        self.assertFalse(v["connections"])

    def test_rejects_duplicate_lane_and_unknown_connection(self):
        with self.assertRaises(ValueError):
            self.store.open_lane("research", label="Duplicate", referent="other", actor_id="james")
        with self.assertRaises(ValueError):
            self.store.connect("factory", "missing", relation="x")
        with self.assertRaises(ValueError):
            self.store.connect("factory", "factory", relation="self")

    def test_rejects_unknown_focus(self):
        with self.assertRaises(ValueError):
            self.store.set_focus("nonexistent")
        self.assertIsNone(self.store.focused_lane())

    def test_rejects_missing_movement_information(self):
        with self.assertRaises(ValueError):
            self.store.record_movement("research")
        self.assertEqual(self.store.get_lane("research").movements, 0)

    def test_rejects_empty_referent_without_writing(self):
        before = self.store.events()
        with self.assertRaises(ValueError):
            self.store.record_movement("research", referent="", changes="changed")
        self.assertEqual(before, self.store.events())

    def test_return_history_preserves_ancestry(self):
        self.store.record_movement("research", changes="A", preserved="base")
        second = self.store.record_movement("research", changes="B", preserved="A", evidence_refs=("source:1",))
        moves = [x for x in self.store.history("research") if x["event_type"] == "LANE_MOVED"]
        self.assertEqual(len(moves), 2)
        self.assertEqual(moves[1]["data"]["prior_event_id"], moves[0]["event_id"])
        self.assertEqual(second.evidence_refs, ("source:1",))

    def test_return_history_is_not_mutable_internal_state(self):
        output = self.store.events()
        output[0]["data"]["label"] = "hijacked"
        self.assertEqual(self.store.get_lane("research").label, "Research")

    def test_persistent_restart_preserves_links_and_focus(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "private" / "workspace.jsonl"
            a = WorkspaceStore(p)
            a.open_lane("r", label="Research", referent="question", actor_id="james", sources=("source:r",))
            a.open_lane("f", label="Factory", referent="part", actor_id="james")
            a.record_movement("r", next_movement="continue", evidence_refs=("witness:123",))
            a.connect("r", "f", relation="measurement interface")
            a.set_focus("f")
            b = WorkspaceStore(p)
            self.assertEqual(workspace_view(a), workspace_view(b))
            self.assertEqual(len(b.events()), 5)

    def test_corrupted_history_fails_closed(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "workspace.jsonl"
            p.write_text('{"event_id":"fake","event_type":"FOCUS_SET","occurred_at":"now","data":{"lane_id":"phantom"}}\n')
            with self.assertRaises(ValueError):
                WorkspaceStore(p)

    def test_unrecognized_event_is_rejected(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "workspace.jsonl"
            p.write_text(json.dumps({"event_id":"e1","event_type":"TASK_CREATED","occurred_at":"now","data":{}})+'\n')
            with self.assertRaises(ValueError):
                WorkspaceStore(p)

    def test_walls_do_not_convert_to_tasks(self):
        result = self.store.record_movement("factory", walls=("measurement not available",), preserved="CAD placeholder")
        self.assertEqual(result.walls, ("measurement not available",))
        self.assertEqual(result.next_movement, "")


if __name__ == "__main__":
    unittest.main()
