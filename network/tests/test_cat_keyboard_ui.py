"""Regression checks for the standalone Meow Machine workstation project."""
from html.parser import HTMLParser
from pathlib import Path
import os
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "docs/live/cat-keyboard.html"
WORK = ROOT / "docs/live/work.html"


class Script(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.inside = False

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.scripts.append("")
            self.inside = True

    def handle_data(self, data):
        if self.inside:
            self.scripts[-1] += data

    def handle_endtag(self, tag):
        if tag == "script":
            self.inside = False


class CatKeyboardTests(unittest.TestCase):
    def test_standalone_entry_and_no_executive_claim(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn('href="cat-keyboard.html"', WORK.read_text(encoding="utf-8"))
        for marker in ("Meow Machine · Cat Keyboard", "window.AudioContext",
                       "pointerdown", "prefers-reduced-motion",
                       "meow-machine/score-v1", "stopRecording",
                       "patternPreset", "16-step meow studio"):
            self.assertIn(marker, page)
        for forbidden in ("<script src=", "fetch(", "localStorage", "EventSource"):
            self.assertNotIn(forbidden, page)

    @unittest.skipUnless(shutil.which("node"), "Node.js needed")
    def test_note_math_scores_and_pattern_validation(self):
        parser = Script()
        parser.feed(PAGE.read_text(encoding="utf-8"))
        self.assertEqual(len(parser.scripts), 1)
        script = parser.scripts[0]
        result = subprocess.run(["node", "--check", "-"], input=script,
                                text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        pure = script[script.index("const NOTES="):script.index("const $=id=>")]
        checks = r"""
const vm=require('node:vm'),a=require('node:assert/strict');
const m=vm.runInNewContext(process.env.CAT_RULES+'\n({hz,midiFor,validScore,patternPreset,SHORTCUTS})');
a.equal(m.SHORTCUTS.length,13);
a.equal(m.midiFor(0,4),60);a.equal(m.midiFor(12,5),84);
a.equal(Math.round(m.hz(69)),440);
for(let i=0;i<3;i++){const p=m.patternPreset(i);a.equal(p.length,5);
 a(p.every(r=>r.length===16&&r.every(x=>typeof x==='boolean')));}
const s={schema:'meow-machine/score-v1',events:[
 {ms:0,note:60,cat:'miso',type:'on',id:'n1'},
 {ms:140,note:60,cat:'miso',type:'off',id:'n1'}]};
a(m.validScore(s));
a.equal(m.validScore({...s,events:s.events.slice(0,1)}),null);
a.equal(m.validScore({...s,events:[s.events[1],s.events[0]]}),null);
a.equal(m.validScore({...s,events:[{...s.events[0],cat:'unknown'},s.events[1]]}),null);
a.equal(m.validScore({...s,events:[{...s.events[0],note:99},s.events[1]]}),null);
"""
        result = subprocess.run(["node", "-e", checks], text=True,
                                capture_output=True, timeout=10,
                                env=dict(os.environ, CAT_RULES=pure))
        self.assertEqual(result.returncode, 0, result.stderr)
