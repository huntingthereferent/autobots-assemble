"""Source-matched bookmarks and portable creative decisions in the Audio Intake browser."""
from __future__ import annotations

import io
import json
import math
import shutil
import struct
import subprocess
import tempfile
import unittest
import wave
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "docs/live/audio-intake.html"


def source_wav() -> bytes:
    out = io.BytesIO()
    with wave.open(out, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        pcm = [round(8000 * math.sin(i * 2 * math.pi * 220 / 8000)) for i in range(16000)]
        wav.writeframes(struct.pack("<" + "h" * len(pcm), *pcm))
    return out.getvalue()


class AudioIntakeSessionSourceTests(unittest.TestCase):
    def test_controls_and_evidence_boundary(self):
        html = PAGE.read_text(encoding="utf-8")
        for marker in (
            'id="session"', 'id="moment-title"', 'id="moment-list"',
            'id="add-moment"', 'id="save-a"', 'id="load-a"',
            'id="save-b"', 'id="load-b"', 'id="take-comparison"',
            'id="export-session"', 'id="import-session"',
            'href="work.html"', 'id="direction"', 'id="source"',
            "const SESSION_SCHEMA='ab-audio-session/v1';",
            'sourceSha256', 'sourceBytes',
            'No audio bytes', 'function safeMoment(',
            'id="loop-slice"', 'id="transport-state"', 'id="transport-time"',
            'id="cancel-moment-edit"', 'function playRange(',
            'function auditionMoment(', 'function exportMoment(',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, html)
        self.assertNotIn('localStorage', html)
        self.assertEqual(html.count('id="session"'), 1)

    @unittest.skipUnless(shutil.which("node"), "Node required for JavaScript syntax validation")
    def test_inline_javascript_parses(self):
        html = PAGE.read_text(encoding="utf-8")
        js = html.split("<script>\n", 1)[1].split("\n</script>", 1)[0]
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "audio-session.js"
            script.write_text(js, encoding="utf-8")
            result = subprocess.run(
                ["node", "--check", str(script)],
                capture_output=True, text=True, timeout=15
            )
        self.assertEqual(result.returncode, 0, result.stderr)


@unittest.skipUnless(sync_playwright, "Playwright required for interactive Audio Intake checks")
class AudioIntakeSessionBrowserTests(unittest.TestCase):
    def test_versions_markers_and_restore_do_not_invent_audio(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                page = browser.new_page(accept_downloads=True)
                errors = []
                page.on("pageerror", lambda exc: errors.append(str(exc)))
                page.goto(PAGE.as_uri(), wait_until="domcontentloaded")

                # Reversible creative versions remain user-written.
                page.locator("#d-title").fill("Session demo")
                page.locator("#d-style").fill("Quiet opening")
                page.locator("#save-a").click()
                page.locator("#d-style").fill("Louder chorus")
                page.locator("#bpm").fill("126")
                page.locator("#save-b").click()
                self.assertEqual(page.locator("#take-comparison .comparison-row").count(), 12)
                page.locator("#load-a").click()
                self.assertEqual(page.locator("#d-style").input_value(), "Quiet opening")
                self.assertEqual(page.locator("#bpm").input_value(), "120")

                source = source_wav()
                page.locator("#files").set_input_files({
                    "name": "original.wav", "mimeType": "audio/wav", "buffer": source
                })
                page.wait_for_function(
                    "document.querySelector('#status').textContent.includes('Audio decoded')",
                    timeout=15000,
                )
                page.locator("#start").fill("0.25")
                page.locator("#end").fill("0.75")
                page.locator("#moment-title").fill("Keep this hook")
                page.locator("#moment-note").fill("Make room for the voice")
                page.locator("#add-moment").click()
                self.assertIn("1 MARKER", page.locator("#moment-count").inner_text())
                self.assertEqual(page.locator("#moment-list .moment-row").count(), 1)

                # Hear a saved range, repeat it, and stop without inventing an audio render.
                page.locator("#loop-slice").check()
                page.locator("#moment-list .moment-actions button").nth(0).click()
                self.assertEqual(page.locator("#transport-state").inner_text(), "LOOPING SOURCE")
                self.assertEqual(page.locator("#transport-state").get_attribute("data-playing"), "true")
                self.assertIn("0:00.5", page.locator("#transport-time").inner_text())
                page.locator("#stop").click()
                self.assertEqual(page.locator("#transport-state").get_attribute("data-playing"), "false")

                # Export exactly this bookmark as a real PCM WAV, not a JSON promise.
                with page.expect_download() as clip:
                    page.locator("#moment-list .moment-actions button").nth(2).click()
                clip_data = clip.value.path().read_bytes()
                self.assertEqual(clip_data[:4], b"RIFF")
                self.assertEqual(clip_data[8:12], b"WAVE")
                self.assertGreater(len(clip_data), 44)

                # Revise marker notes without doubling the number of markers.
                page.locator("#moment-list .moment-actions button").nth(3).click()
                page.locator("#moment-title").fill("Stronger chorus hook")
                page.locator("#moment-note").fill("Keep vocal space; reduce drums")
                page.locator("#add-moment").click()
                self.assertEqual(page.locator("#moment-list .moment-row").count(), 1)
                self.assertIn("Stronger chorus hook", page.locator("#moment-list").inner_text())

                with page.expect_download() as downloaded:
                    page.locator("#export-session").click()
                session = json.loads(downloaded.value.path().read_text(encoding="utf-8"))
                self.assertEqual(session["schema"], "ab-audio-session/v1")
                self.assertEqual(session["takes"]["A"]["style"], "Quiet opening")
                self.assertEqual(session["takes"]["B"]["style"], "Louder chorus")
                self.assertEqual(session["moments"][0]["title"], "Stronger chorus hook")
                self.assertEqual(session["moments"][0]["note"], "Keep vocal space; reduce drums")
                self.assertNotIn("localAsset", json.dumps(session))
                self.assertNotIn("audioBytes", json.dumps(session))
                self.assertEqual(session["moments"][0]["start"], 0.25)

                # A JSON reload must not claim the original WAV was restored.
                page.reload(wait_until="domcontentloaded")
                page.locator("#import-session").set_input_files({
                    "name": "audio.session.json", "mimeType": "application/json",
                    "buffer": json.dumps(session).encode("utf-8")
                })
                page.wait_for_function(
                    "document.querySelector('#session-feedback').textContent.includes('Restored')"
                )
                self.assertEqual(page.locator("#moment-list .moment-row").count(), 1)
                self.assertTrue(page.locator("#moment-list .moment-actions button").first.is_disabled())
                self.assertTrue(page.locator("#moment-list .moment-actions button").nth(2).is_disabled())
                self.assertEqual(page.locator("#d-style").input_value(), "Quiet opening")

                # Notes remain editable without source; timecodes stay unchanged.
                page.locator("#moment-list .moment-actions button").nth(3).click()
                page.locator("#moment-note").fill("Still a keeper")
                page.locator("#add-moment").click()
                self.assertEqual(page.locator("#moment-list .moment-row").count(), 1)
                self.assertIn("Still a keeper", page.locator("#moment-list").inner_text())

                # A matching SHA-256 lets the user reattach the original source.
                page.locator("#files").set_input_files({
                    "name": "renamed.wav", "mimeType": "audio/wav", "buffer": source
                })
                page.wait_for_function(
                    "document.querySelector('#status').textContent.includes('Audio decoded')",
                    timeout=15000,
                )
                if session["moments"][0]["sourceSha256"]:
                    self.assertFalse(page.locator("#moment-list .moment-actions button").first.is_disabled())
                    page.locator("#moment-list .moment-actions button").first.click()
                    self.assertEqual(page.locator("#start").input_value(), "0.250")
                    self.assertEqual(page.locator("#end").input_value(), "0.750")
                else:
                    self.assertTrue(page.locator("#moment-list .moment-actions button").first.is_disabled())
                self.assertFalse(errors, errors)
            finally:
                browser.close()


if __name__ == "__main__":
    unittest.main()
