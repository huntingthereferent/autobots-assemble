"""Browser-level Suno Intake checks over actual local source bytes, not Suno API."""
from __future__ import annotations

import io
import json
import math
import struct
import unittest
import wave
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

PAGE = Path(__file__).resolve().parents[2] / "docs/live/suno-intake.html"


def sample_wav() -> bytes:
    out = io.BytesIO()
    with wave.open(out, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        samples = [
            round(10000 * math.sin(i * 2 * math.pi * 220 / 8000))
            for i in range(16000)
        ]
        wav.writeframes(struct.pack("<" + "h" * len(samples), *samples))
    return out.getvalue()


@unittest.skipUnless(sync_playwright, "Playwright required for browser checks")
class SunoIntakeBrowserTests(unittest.TestCase):
    def test_source_import_selection_wav_export_and_manifest(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                page = browser.new_page(accept_downloads=True)
                failures = []
                page.on("pageerror", lambda error: failures.append(str(error)))
                page.goto(PAGE.as_uri(), wait_until="domcontentloaded")
                page.locator("#files").set_input_files({
                    "name": "test-source.wav",
                    "mimeType": "audio/wav",
                    "buffer": sample_wav(),
                })
                page.wait_for_function(
                    "document.querySelector('#status').textContent.includes('Audio decoded')",
                    timeout=15000,
                )
                self.assertEqual(page.locator(".asset.selected").count(), 1)
                self.assertFalse(page.locator("#export").is_disabled())
                page.locator("#start").fill("0.25")
                page.locator("#end").fill("0.75")
                self.assertIn("SELECTED MOMENT / 0.25–0.75 s",
                              page.locator("#brief-preview").inner_text())
                with page.expect_download() as result:
                    page.locator("#export").click()
                downloaded = result.value.path().read_bytes()
                self.assertEqual(downloaded[:4], b"RIFF")
                self.assertEqual(downloaded[8:12], b"WAVE")
                decoded_rate = struct.unpack_from("<I", downloaded, 24)[0]
                with page.expect_download() as result:
                    page.locator("#manifest").click()
                source = json.loads(result.value.path().read_text(encoding="utf-8"))
                self.assertEqual(source["source"]["fileName"], "test-source.wav")
                self.assertEqual(source["source"]["kind"], "audio")
                # decodeAudioData may resample into the browser AudioContext rate.
                self.assertEqual(decoded_rate, source["observation"]["sampleRate"])
                self.assertEqual(source["transform"]["slice"],
                                 {"startSeconds": 0.25, "endSeconds": 0.75})
                self.assertFalse(failures, failures)
            finally:
                browser.close()

    def test_direction_is_manually_editable_and_exports_without_source(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                page = browser.new_page(accept_downloads=True)
                failures = []
                page.on("pageerror", lambda error: failures.append(str(error)))
                page.goto(PAGE.as_uri(), wait_until="domcontentloaded")
                page.locator('[data-preset="lift"]').click()
                self.assertEqual(
                    page.locator('[data-preset="lift"]').get_attribute("aria-pressed"), "true"
                )
                page.locator("#d-title").fill("Prototype session")
                page.locator("#d-style").fill("Sparse piano and percussion")
                self.assertEqual(
                    page.locator('[data-preset="lift"]').get_attribute("aria-pressed"), "false"
                )
                page.locator("#add-kind").select_option("Instrumental")
                original = page.locator("#arranger .arranger-row").count()
                page.locator("#add-section").click()
                self.assertEqual(page.locator("#arranger .arranger-row").count(), original + 1)
                self.assertIn("Sparse piano and percussion",
                              page.locator("#brief-preview").inner_text())
                with page.expect_download() as result:
                    page.locator("#export-direction").click()
                brief = json.loads(result.value.path().read_text(encoding="utf-8"))
                self.assertEqual(brief["project"], "Prototype session")
                self.assertEqual(brief["style"], "Sparse piano and percussion")
                self.assertEqual(brief["arrangement"][-1]["section"], "Instrumental")
                self.assertIsNone(brief["source"])
                self.assertEqual(brief["type"], "manual-creative-brief")
                self.assertFalse(failures, failures)
            finally:
                browser.close()


if __name__ == "__main__":
    unittest.main()
