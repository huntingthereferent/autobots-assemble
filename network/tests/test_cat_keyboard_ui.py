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
                       "patternPreset", "8-bar melody loop", "id=\"sound-file\"", "function swallowSound()",
                       "function playBankSample(", "function handoffSample()",
                       "function tunedVoice(", "function renderTunedPreview(",
                       "if(soundSlots[voiceName]?.origin===\'local-file\'",
                       "native_verification:\'NOT_RUN_BY_BROWSER\'", "CHORD_LIBRARY",
                       "Save template", "realizeProgression",
                       "meow-machine/chord-templates-v1", "ARRANGEMENT_SCHEMA",
                       "function validBranches(", "function selectBar(", "function startLoop("):
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
const m=vm.runInNewContext(process.env.CAT_RULES+'\n({hz,midiFor,validScore,patternPreset,SHORTCUTS,CHORD_LIBRARY,parseChordSymbol,progressionFromSymbols,realizeProgression,validUserTemplates,defaultBars,cloneBars,validBars,validBranches,realizeBar,nextStep,melodyIndexFor,modernLayerState,MODERN_PROFILES,BAR_COUNT,MELODY_BARS,STEPS_PER_BAR})');
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
a.equal(named('club-drive',9),'Am G F G');
a.equal(named('rnb-space',0),'Cmaj7 Em7 Am7 Fmaj7');
a.equal(named('country-pop',0),'C F Am G');
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

a.equal(m.BAR_COUNT,16);a.equal(m.STEPS_PER_BAR,16);
const bars=m.defaultBars();a.equal(bars.length,16);
a.equal(bars.map(b=>m.realizeBar(b.chord).name).slice(0,4).join(' '),'C G Am F');
a(bars.every(b=>b.notes.length===5&&b.notes.every(row=>row.length===16)));
const copy=m.cloneBars(bars);copy[5].notes[1][7]=true;copy[5].chord=[11,'min'];
a.equal(bars[5].notes[1][7],false);
a.equal(m.realizeBar(copy[5].chord).name,'Bm');
a.equal(m.validBars(copy).length,16);
a.equal(m.validBars(copy.slice(1)),null);
a.equal(m.validBars(copy.map((b,i)=>i===0?{...b,chord:[99,'maj']}:b)),null);
a.equal(m.nextStep(255,false),255);
a.equal(m.nextStep(256,true),0);
a.equal(m.nextStep(256,false),null);
const branch={id:'branch-1',name:'Verse',tempo:112,bars:copy};
a.equal(m.validBranches([branch]).length,1);
a.equal(m.validBranches([branch,branch]),null);
a.equal(m.validBranches([{...branch,tempo:999}]),null);
a.equal(m.validBranches(Array.from({length:25},(_,i)=>({...branch,id:'branch-'+(i+1)}))),null);
m.validBranches([branch])[0].bars[5].notes[1][7]=false;
a.equal(copy[5].notes[1][7],true);


a.equal(m.MELODY_BARS,8);
a.equal(m.melodyIndexFor(0),0);a.equal(m.melodyIndexFor(7),7);
a.equal(m.melodyIndexFor(8),0);a.equal(m.melodyIndexFor(15),7);
a.equal(Object.keys(m.MODERN_PROFILES).length,9);
for(const p of Object.values(m.MODERN_PROFILES)){
 a.equal(p.patterns.length,4);
 a(p.patterns.every(v=>v.every(step=>Number.isInteger(step)&&step>=0&&step<16)));
}
a.equal(m.defaultBars()[0].profile,'pop');
a.equal(m.validBars(m.defaultBars()).length,16);
a.equal(m.validBars(m.defaultBars().map((b,i)=>i===3?{...b,layers:[false,1,false,true]}:b)),null);
a.equal(m.validBars(m.defaultBars().map((b,i)=>i===2?{...b,profile:'unknown'}:b)),null);
// Historical saved branches (pre-layer schema) must still parse.
a.equal(m.validBars(m.defaultBars().map(({chord,notes})=>({chord,notes}))).length,16);

"""
        result = subprocess.run(["node", "-e", checks], text=True,
                                capture_output=True, timeout=10,
                                env=dict(os.environ, CAT_RULES=pure))
        self.assertEqual(result.returncode, 0, result.stderr)
