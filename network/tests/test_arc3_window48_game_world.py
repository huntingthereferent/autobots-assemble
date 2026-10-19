"""Source and hostile-export checks for playable ORIGINAL Window48 math worlds."""
from __future__ import annotations

from copy import deepcopy
import html.parser
from itertools import product
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest

from work.arc_like_maze.window_combined import family, classify_pair
from work.arc3.window48_world_export import (
    DEST, RECEIPT, SCHEMA, SCOPE, build_manifest, state_index, verify_receipt,
)

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "docs/window48_world.html"


def actual_receipt(ids=(6,9), word="ABABAB"):
    worlds = family()
    states = [(0,0,0), (0,0,0)]
    events = []
    for action in word:
        before = [state_index(s) for s in states]
        states = [worlds[ids[i]].step(states[i], action) for i in range(2)]
        events.append({"action":action, "before":before,
                       "after":[state_index(s) for s in states]})
    return {"schema":RECEIPT, "scope":SCOPE, "law_ids":list(ids),
            "root_index":0, "actions":word, "events":events,
            "final":[state_index(s) for s in states]}


class SourceWorld48GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DEST.read_text(encoding="utf8"))
        cls.worlds = family()

    def test_exact_source_export_and_law_count(self):
        self.assertEqual(self.data, build_manifest())
        self.assertEqual(self.data["schema"], SCHEMA)
        self.assertEqual((self.data["concrete_laws"], self.data["rooted_classes"],
                          self.data["full_state_classes"]), (48,16,14))
        self.assertEqual(len(self.data["laws"]), 48)
        self.assertEqual(len({tuple(row["rooted_class"]) for row in self.data["laws"]}),16)

    def test_all_2592_browser_edges_match_original_python_and_reverse(self):
        self.assertEqual(len(self.worlds),48)
        for w,row in zip(self.worlds,self.data["laws"]):
            self.assertEqual((row["support"],row["coefficient"],row["pulse"],row["balanced"]),
                             (w.support,w.coefficient,w.pulse,w.balanced))
            for state in product(range(3),repeat=3):
                for letter in "AB":
                    after=row[letter][state_index(state)]
                    expected=w.step(state,letter)
                    self.assertEqual(after,state_index(expected))
                    self.assertEqual(w.inverse(expected,letter),state)

    def test_rooted_and_nonrooted_conjugacies_remain_distinct(self):
        for k in (0,3):
            left=next(w for w in self.worlds if (w.support,w.coefficient,w.pulse,w.balanced)==(k,0,1,0))
            right=next(w for w in self.worlds if (w.support,w.coefficient,w.pulse,w.balanced)==(k,0,1,1))
            rel=classify_pair(left,right)
            self.assertFalse(rel.root_preserving)
            self.assertEqual(rel.kind,"FIBER_SHIFT")
            a,b=("BAB","BBBA") if k==0 else ("AAB","BABA")
            self.assertEqual(left.apply((0,0,0),a),left.apply((0,0,0),b))
            self.assertNotEqual(right.apply((0,0,0),a),right.apply((0,0,0),b))

    def test_valid_export_can_be_freshly_replayed(self):
        for ids,word in (((6,9),"BAB"), ((0,47),"ABABAB"), ((11,11),"")):
            data=actual_receipt(ids,word)
            self.assertTrue(verify_receipt(data)["valid"])
            self.assertEqual(verify_receipt(data)["steps"],len(word))

    def test_false_browser_success_cannot_pass_original_source(self):
        sample=actual_receipt()
        edits=[
            lambda x:x["events"][0]["after"].__setitem__(0,22),
            lambda x:x["events"][0]["before"].__setitem__(0,3),
            lambda x:x["events"][0].__setitem__("action","B"),
            lambda x:x["final"].__setitem__(1,22),
            lambda x:x["law_ids"].__setitem__(0,48),
            lambda x:x.__setitem__("scope","native-arc-game"),
            lambda x:x.__setitem__("root_index",1),
            lambda x:x.__setitem__("actions","ABABAB"*24),
            lambda x:x.__setitem__("events",[]),
            lambda x:x["events"][1].__setitem__("unsourced",True),
        ]
        for edit in edits:
            with self.subTest(edit=edit):
                sample_copy=deepcopy(sample)
                edit(sample_copy)
                with self.assertRaises(ValueError):
                    verify_receipt(sample_copy)

    def test_browser_source_contract_visible(self):
        page=PAGE.read_text(encoding="utf8")
        for required in ("WORLD48","window48_world_data.json","law-left",
                         "law-right","action-a","action-b","undo",
                         "word-input","export","marked origin",
                         "Original source","finite-mathematical-source-only"):
            self.assertIn(required.lower(), page.lower())
        self.assertNotIn("GameState.WIN",page)
        self.assertNotIn("ARC puzzle solved",page)

    @unittest.skipUnless(shutil.which("node"),"Node.js required for JS syntax check")
    def test_browser_javascript_syntax(self):
        class Parser(html.parser.HTMLParser):
            def __init__(self):
                super().__init__();self.active=False;self.scripts=[];self.buf=""
            def handle_starttag(self,tag,attrs):
                if tag=="script":self.active=True;self.buf=""
            def handle_data(self,data):
                if self.active:self.buf+=data
            def handle_endtag(self,tag):
                if tag=="script":
                    self.scripts.append(self.buf);self.active=False
        p=Parser();p.feed(PAGE.read_text(encoding="utf8"))
        self.assertEqual(len(p.scripts),1)
        with TemporaryDirectory() as d:
            path=Path(d)/"world48.js"
            path.write_text(p.scripts[0],encoding="utf8")
            finished=subprocess.run(["node","--check",str(path)],
                                    capture_output=True,text=True,timeout=20)
            self.assertEqual(finished.returncode,0,finished.stderr)


if __name__ == "__main__":
    unittest.main()
