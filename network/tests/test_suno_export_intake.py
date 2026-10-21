"""Independent intake: source inspection, bounded MIDI and audio math, not Suno internals."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / 'docs/live/suno-intake.html'
CORE = ROOT / 'docs/live/audio-intake-core.js'
WORK = ROOT / 'docs/live/work.html'


class InlineScripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.active = False

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.active = True
            if not dict(attrs).get('src'):
                self.scripts.append('')

    def handle_data(self, data):
        if self.active and self.scripts:
            self.scripts[-1] += data

    def handle_endtag(self, tag):
        if tag == 'script':
            self.active = False


class SunoIntakeTests(unittest.TestCase):
    def test_workstation_link_and_source_boundary(self):
        html = PAGE.read_text(encoding='utf8')
        self.assertIn('href="suno-intake.html"', WORK.read_text(encoding='utf8'))
        for term in ('audio-intake-core.js', 'type="file"', 'canvas id="wave"',
                     'local-origin-preserving-export', 'SHA-256', 'encodeWav',
                     'parseMidi', 'not affiliated with Suno', 'not the audio itself'):
            # schema appears in script, not necessarily plain prose
            self.assertIn(term, html)
        self.assertNotIn('EventSource', html)
        self.assertNotIn('fetch(', html)
        self.assertNotIn('localStorage', html)
        self.assertNotIn('<iframe', html)

    @unittest.skipUnless(shutil.which('node'), 'Requires Node')
    def test_javascript_program_parses(self):
        p = InlineScripts()
        p.feed(PAGE.read_text(encoding='utf8'))
        self.assertEqual(len(p.scripts), 1)
        script = p.scripts[0]
        for source in (script, CORE.read_text(encoding='utf8')):
            r = subprocess.run(['node', '--check', '-'], input=source, text=True,
                               capture_output=True, timeout=12)
            self.assertEqual(r.returncode, 0, r.stderr)

    @unittest.skipUnless(shutil.which('node'), 'Requires Node')
    def test_audio_math_and_midi_finite_cases(self):
        code = r'''
const a=require('node:assert/strict');
const C=require(process.argv[1]);
a.equal(C.pitchRate(72,60),2);
a.equal(C.pitchRate(60,60),1);
a.throws(()=>C.pitchRate(128,60));
const data=new Float32Array(48000);
for(let i=0;i<data.length;i++)data[i]=Math.sin(i/12)*.25;
const buf={sampleRate:48000,numberOfChannels:1,length:data.length,duration:1,getChannelData:()=>data};
const stats=C.summarizeAudio(buf);a(stats.rms>.16&&stats.rms<.20);
a.equal(C.envelope(buf,80).length,80);
const wav=C.encodeWav(buf,0,.5),v=new DataView(wav);
a.equal(String.fromCharCode(...new Uint8Array(wav,0,4)),'RIFF');
a.equal(v.getUint32(24,true),48000);a.equal(v.getUint32(40,true),48000);
a.throws(()=>C.encodeWav(buf,0,1.5));
const midi=Uint8Array.from([0x4d,0x54,0x68,0x64,0,0,0,6,0,0,0,1,1,0xe0,
0x4d,0x54,0x72,0x6b,0,0,0,20,0,0xff,0x51,3,0x07,0xa1,0x20,
0,0x90,60,100,0x87,0x40,0x80,60,0,0,0xff,0x2f,0]);
const m=C.parseMidi(midi);a.equal(m.notes.length,1);a.equal(m.notes[0].startMs,0);a.equal(m.notes[0].endMs,1000);
a.equal(m.tempoEvents,1);a.throws(()=>C.parseMidi(midi.subarray(0,12)));
const bad=midi.slice();bad[12]=0x81; a.throws(()=>C.parseMidi(bad));
console.log('audio math and MIDI parser PASS');
'''
        r = subprocess.run(['node', '-e', code, str(CORE)], text=True, capture_output=True, timeout=14)
        self.assertEqual(r.returncode, 0, r.stderr)