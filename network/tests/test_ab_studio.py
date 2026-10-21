"""Independent DAW browser and source-contract tests; no Suno service needed."""
from pathlib import Path
from tempfile import TemporaryDirectory
import math
import shutil
import struct
import subprocess
import unittest
import wave

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "docs/live/ab-studio.html"
JS = ROOT / "docs/live/ab-studio.js"
CSS = ROOT / "docs/live/ab-studio.css"
WORK = ROOT / "docs/live/work.html"

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


class StudioSourceTests(unittest.TestCase):
    def test_dependency_and_projections(self):
        page = PAGE.read_text(encoding="utf-8")
        code = JS.read_text(encoding="utf-8")
        self.assertIn('href="ab-studio.html"', WORK.read_text(encoding="utf-8"))
        for field in ("project-name", "bpm", "meter", "ruler", "lanes", "piano-roll",
                      "master-volume", "store-a", "recall-b", "import-midi",
                      "export-wav", "export-stems", "record", "undo", "redo"):
            self.assertIn('id="' + field + '"', page)
        self.assertIn("audio-intake-core.js", page)
        for marker in ("OfflineAudioContext", "decodeAudioData", "createOscillator",
                       "createWaveShaper", "createStereoPanner", "MediaRecorder",
                       "createBiquadFilter", "schema:'ab-studio-v1'", "validateProject"):
            self.assertIn(marker, code)
        self.assertNotIn("fetch(", code)
        self.assertNotIn("localStorage", code)
        self.assertNotIn("api.suno", code)
        self.assertTrue(CSS.exists())

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_javascript_parses(self):
        for path in (JS, ROOT / "docs/live/audio-intake-core.js"):
            r = subprocess.run(["node", "--check", str(path)], text=True,
                               capture_output=True, timeout=12)
            self.assertEqual(r.returncode, 0, (path.name, r.stderr))


@unittest.skipUnless(sync_playwright, "Playwright/Chromium required")
class StudioBrowserTests(unittest.TestCase):
    def setUp(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True, args=["--no-sandbox", "--autoplay-policy=no-user-gesture-required"])
        self.page = self.browser.new_page(accept_downloads=True, viewport={"width": 1500, "height": 1050})
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.goto(PAGE.as_uri(), wait_until="domcontentloaded")

    def tearDown(self):
        self.browser.close()
        self.playwright.stop()

    def test_real_timeline_notes_snapshots_and_midi_export(self):
        p = self.page
        self.assertEqual(p.locator(".lane").count(), 4)
        self.assertEqual(p.locator(".clip").count(), 3)
        self.assertEqual(p.locator("#keys button").count(), 13)
        self.assertEqual(p.locator(".bar-label").count(), 16)
        p.locator("#meter").select_option("3/4")
        self.assertEqual(p.locator(".bar-label").count(), 22)
        p.locator("#meter").select_option("4/4")
        p.locator("#play").click()
        p.wait_for_function("document.querySelector('#audio-state').textContent.includes('Live')", timeout=10000)
        p.locator("#stop").click()
        p.locator("#add-midi").click()
        self.assertEqual(p.locator(".lane").count(), 5)
        p.locator("#store-a").click()
        p.locator("#bpm").fill("146")
        p.locator("#bpm").dispatch_event("change")
        p.locator("#store-b").click()
        self.assertIn("Δ BPM 26", p.locator("#ab-info").inner_text())
        p.locator("#recall-a").click()
        self.assertEqual(p.locator("#bpm").input_value(), "120")
        p.locator(".lane:last-child [data-action=add]").click()
        self.assertEqual(p.locator(".clip").count(), 4)
        p.locator(".roll-cell").first.click()
        self.assertTrue(p.locator(".roll-cell.filled").count() > 0)
        with p.expect_download(timeout=10000) as dl:
            p.locator("#export-midi").click()
        self.assertTrue(dl.value.suggested_filename.endswith(".mid"))
        self.assertEqual(self.errors, [])

    def test_import_audio_save_reopen_and_offline_bounce(self):
        with TemporaryDirectory() as d:
            wav_file = Path(d) / "test-tone.wav"
            with wave.open(str(wav_file), "wb") as out:
                out.setnchannels(1)
                out.setsampwidth(2)
                out.setframerate(16000)
                samples = [int(3500 * math.sin(2 * math.pi * 350 * j / 16000)) for j in range(4000)]
                out.writeframes(struct.pack("<" + "h" * len(samples), *samples))
            p = self.page
            p.locator("#audio-file").set_input_files(str(wav_file))
            p.wait_for_function("document.querySelectorAll('#assets button').length===1", timeout=12000)
            self.assertEqual(p.locator(".clip").count(), 4)
            p.locator(".lane").nth(2).locator(".lane-head").click()
            p.locator("#instrument").select_option("sampler")
            p.locator("#sampler-asset").select_option(index=1)
            p.locator("#keys button").first.click()
            self.assertIn("sampler", p.locator(".lane").nth(2).locator(".lane-type").inner_text().lower())
            p.locator("#store-a").click()
            p.locator("#bpm").fill("134")
            p.locator("#bpm").dispatch_event("change")
            p.locator("#store-b").click()
            with p.expect_download(timeout=15000) as dl:
                p.locator("#save-project").click()
            archive = Path(d) / "saved.abstudio.json"
            dl.value.save_as(str(archive))
            self.assertGreater(archive.stat().st_size, 1000)
            p.locator("#new-project").click()
            self.assertEqual(p.locator(".lane").count(), 0)
            p.locator("#project-file").set_input_files(str(archive))
            p.wait_for_function("document.querySelectorAll('.lane').length===4", timeout=12000)
            self.assertEqual(p.locator("#assets button").count(), 1)
            self.assertIn("Δ BPM 14", p.locator("#ab-info").inner_text())
            with p.expect_download(timeout=30000) as bounce:
                p.locator("#export-wav").click()
            self.assertTrue(bounce.value.suggested_filename.endswith(".wav"))
            self.assertFalse(self.errors, self.errors)
