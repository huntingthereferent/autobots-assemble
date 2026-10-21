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
        for marker in ("MEOW LAB 2 · Workstation sound keyboard", "window.AudioContext",
                       "pointerdown", "prefers-reduced-motion",
                       "meow-machine/score-v1", "stopRecording",
                       "patternPreset", "16-step meow studio", "id=\"sound-file\"", "function swallowSound()",
                       "function playBankSample(", "function handoffSample()",
                       "native_verification:\'NOT_RUN_BY_BROWSER\'", "CHORD_LIBRARY",
                       "Save template", "realizeProgression",
                       "meow-machine/chord-templates-v1"):
            self.assertIn(marker, page)
        for forbidden in ("<script src=", "fetch(", "EventSource"):
            self.assertNotIn(forbidden, page)

    def test_roseys_high_note_page_preserved(self):
        rosey = (ROOT / "docs/live/roseys-cat-keyboard.html").read_text(encoding="utf-8")
        studio = PAGE.read_text(encoding="utf-8")
        self.assertIn('href="roseys-cat-keyboard.html"', studio)
        for marker in ("Real chord progressions", "HIGH_SHORTCUTS", "KEY_COUNT=25",
                       "TEMPLATES", "save", "chords", "tapetext"):
            self.assertIn(marker, rosey)
        self.assertIn("id=\"sound-file\"", studio)
        self.assertIn("CHORD_LIBRARY", studio)

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
const m=vm.runInNewContext(process.env.CAT_RULES+'\n({hz,midiFor,validScore,patternPreset,SHORTCUTS,CHORD_LIBRARY,parseChordSymbol,progressionFromSymbols,realizeProgression,validUserTemplates})');
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
a.equal(m.validScore({...s,events:[s.events[0],{...s.events[1],note:62}]}),null);
a.equal(m.CHORD_LIBRARY.length,9);
const named=(id,key)=>m.realizeProgression(m.CHORD_LIBRARY.find(t=>t.id===id),key).map(c=>c.name).join(' ');
a.equal(named('pop-lift',0),'C G Am F');
a.equal(named('pop-lift',2),'D A Bm G');
a.equal(named('dark-pop',9),'Am F C G');
a.equal(named('minor-cadence',9),'Am Dm E Am');
a.equal(named('jazz-turnaround',0),'Cmaj7 Am7 Dm7 G7');
a.equal(named('blues',0),'C7 F7 C7 G7');
for(const t of m.CHORD_LIBRARY){
 const p=m.realizeProgression(t,0);a.equal(p.length,4);
 a(p.every(c=>c.notes.length>=3&&c.notes.length<=4&&c.notes.every(n=>Number.isInteger(n)&&n>=48&&n<=82)));
}
a.equal(m.parseChordSymbol('Bbmaj7').pc,10);
a.equal(m.parseChordSymbol('F#m7').quality,'min7');
a.equal(m.parseChordSymbol('H7'),null);
a.equal(m.progressionFromSymbols('Am F C G',9).map(s=>s[0]).join(','),'0,8,3,10');
a.equal(m.progressionFromSymbols('C G Am',0),null);
a.equal(m.progressionFromSymbols('C G Wm F',0),null);
a.equal(m.realizeProgression({steps:m.progressionFromSymbols('Am F C G',9)},9).map(c=>c.name).join(' '),'Am F C G');
const good=[{id:'custom-1',name:'My chord loop',steps:m.progressionFromSymbols('Am F C G',9)}];
a.equal(m.validUserTemplates(good).length,1);
a.equal(m.validUserTemplates([...good,...good]),null);
a.equal(m.validUserTemplates([{...good[0],steps:[[99,'maj'],[7,'maj'],[9,'min'],[5,'maj']]}]),null);
a.equal(m.validUserTemplates([{...good[0],name:''}]),null);
a.equal(m.validUserTemplates(Array.from({length:25},(_,i)=>({...good[0],id:'custom-'+(i+1)}))),null);
"""
        result = subprocess.run(["node", "-e", checks], text=True,
                                capture_output=True, timeout=10,
                                env=dict(os.environ, CAT_RULES=pure))
        self.assertEqual(result.returncode, 0, result.stderr)
