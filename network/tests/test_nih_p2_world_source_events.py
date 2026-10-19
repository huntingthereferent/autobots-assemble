"""Negative controls only, not a substitute for actual W13 game-browser evidence."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from scripts.nih_p2_world_source_events import (
    SCHEMA, STAGES, OBSERVED, digest, enc,
    declared_events,verified_versions,check_frames)

def fixture():
    original=json.loads(Path("network/tests/fixtures/nih_scope_example.json").read_text())
    rows=sorted(original["observations"],key=lambda r:r["id"])
    return {"synthetic":True,"observations":rows,"functional_predicates":["has-status"]}

def frames():
    original=fixture()
    events=declared_events(original)
    states=verified_versions(original,events)
    sha={name:digest(json.dumps(data,sort_keys=True,indent=2)+"\n")
         for name,data in states.items()}
    result=[]
    for turn in range(5):
        state=STAGES[0 if turn<2 else 1 if turn==2 else 2]
        known="2026-01-04" if turn<2 else "2026-01-06"
        visible=sorted(x["id"] for x in states[state]["observations"]
              if x["known_at"]<=known and x["valid_from"]<="2026-01-04"<x["valid_to"])
        result.append({"turn":turn,"snapshot":state,
                       "observed_at":OBSERVED[turn],
                       "known_at":known,"target_at":"2026-01-04",
                       "visible_ids":visible,
                       "original_program_sha256":"a"*64,
                       "source_dataset_sha256":sha[state],
                       "source_event_sha256":events[0 if turn<2 else 1 if turn==2 else 2]["event_sha256"],
                       "host_oracle_agreed":True})
    return result,events,sha

class SourceOwnedSyntheticEventTests(unittest.TestCase):
    def test_01_exact_source_event_hashes_and_native_edition_projection(self):
        raw=fixture()
        events=declared_events(raw)
        states=verified_versions(raw,events)
        self.assertEqual(tuple(states),STAGES)
        self.assertEqual(events[1]["previous_sha256"],events[0]["event_sha256"])
        self.assertEqual(events[2]["previous_sha256"],events[1]["event_sha256"])
        self.assertEqual({x["id"] for x in states["corrected"]["observations"]},
                         {"prior-note","corrected-result"})
        self.assertEqual([x["id"] for x in states["withdrawn"]["observations"]],["prior-note"])
        self.assertEqual(events[1]["observed_at"],"2026-01-06T08:00:00")
        self.assertEqual(events[2]["observed_at"],"2026-01-06T11:00:00")

    def test_02_same_game_day_revision_is_not_monotonic(self):
        rows,events,sha=frames()
        self.assertTrue(check_frames(rows,events,sha,"a"*64))
        self.assertEqual(rows[2]["known_at"],rows[3]["known_at"])
        self.assertIn("corrected-result",rows[2]["visible_ids"])
        self.assertNotIn("corrected-result",rows[3]["visible_ids"])
        self.assertEqual(rows[3]["visible_ids"],["prior-note"])

    def test_03_reject_modified_or_reordered_source_event_chain(self):
        original=fixture()
        events=declared_events(original)
        for index,key,value in ((1,"observed_at","2026-01-07T08:00:00"),
                                (1,"source_ref","unexpected-real-owner"),
                                (2,"replaces","prior-note"),
                                (2,"event_sha256","0"*64),
                                (1,"turn",1),
                                (2,"previous_sha256","f"*64)):
            fake=deepcopy(events);fake[index][key]=value
            with self.subTest(index=index,key=key),self.assertRaises(ValueError):
                verified_versions(original,fake)
        with self.assertRaises(ValueError):
            verified_versions(original,list(reversed(events)))

    def test_04_refuse_browser_frame_drift_and_future_source_use(self):
        rows,events,sha=frames()
        for index,key,value in (
            (2,"source_event_sha256","f"*64),
            (3,"source_dataset_sha256","0"*64),
            (3,"visible_ids",["corrected-result","prior-note"]),
            (3,"observed_at","2026-01-06T09:00:00"),
            (0,"host_oracle_agreed",False),
            (1,"known_at","2026-01-07"),
            (4,"original_program_sha256","0"*64),
        ):
            wrong=deepcopy(rows);wrong[index][key]=value
            with self.subTest(index=index,key=key),self.assertRaises(ValueError):
                check_frames(wrong,events,sha,"a"*64)
        for wrong in (rows[:-1], [deepcopy(rows[0])]+deepcopy(rows[:-1])):
            with self.assertRaises(ValueError):
                check_frames(wrong,events,sha,"a"*64)

if __name__=="__main__":
    unittest.main()
