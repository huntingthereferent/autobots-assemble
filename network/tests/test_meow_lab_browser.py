"""End-to-end verification of Meow Lab 2's actual browser sample bank."""
from pathlib import Path
from tempfile import TemporaryDirectory
import math
import struct
import unittest
import wave

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

PAGE = Path(__file__).resolve().parents[2] / "docs/live/cat-keyboard.html"


@unittest.skipUnless(sync_playwright, "Playwright required for real browser suite")
class MeowLabBrowserTests(unittest.TestCase):
    def test_desktop_upload_play_and_native_handoff(self):
        with TemporaryDirectory() as root:
            wav_path = Path(root) / "sample-cat.wav"
            with wave.open(str(wav_path), "wb") as source:
                source.setnchannels(1)
                source.setsampwidth(2)
                source.setframerate(16000)
                data = [round(12000 * math.sin(2*math.pi*260*j/16000)) for j in range(16000)]
                source.writeframes(struct.pack("<"+"h"*len(data),*data))
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=True,args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"])
                try:
                    page=browser.new_page(accept_downloads=True)
                    errors=[]
                    downloads=[]
                    page.on("pageerror",lambda error:errors.append(str(error)))
                    page.on("download",lambda d:downloads.append(d.suggested_filename))
                    page.goto(PAGE.as_uri(),wait_until="domcontentloaded")
                    self.assertEqual(page.locator(".piano-key").count(),13)
                    self.assertEqual(page.locator(".bank-slot").count(),4)
                    self.assertEqual(page.locator("#seq .step").count(),80)
                    page.locator("#audition-sound").click()
                    page.locator("#bank-target").select_option("mochi")
                    page.locator("#sound-file").set_input_files(str(wav_path))
                    page.locator("#clip-position").evaluate("(el)=>{el.value='42';el.dispatchEvent(new Event('input',{bubbles:true}))}")
                    page.locator("#swallow-sound").click()
                    page.wait_for_function("document.querySelector('#bank-status').textContent.includes('Swallowed')",timeout=15000)
                    self.assertIn("sample-cat.wav",page.locator("#bank-evidence").inner_text())
                    self.assertIn("local-file",page.locator("#bank-evidence").inner_text())
                    page.locator("#audition-sound").click()
                    page.locator("#handoff-sound").click()
                    page.wait_for_timeout(1200)
                    self.assertTrue(any(name.endswith(".wav") for name in downloads),downloads)
                    self.assertTrue(any(name.endswith(".json") for name in downloads),downloads)
                    self.assertFalse(errors,errors)
                finally:
                    browser.close()

    def test_mobile_layout_and_sounds(self):
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"])
            try:
                page=browser.new_page(viewport={"width":390,"height":844},is_mobile=True,has_touch=True)
                errors=[]
                page.on("pageerror",lambda error:errors.append(str(error)))
                page.goto(PAGE.as_uri())
                page.locator(".bank-slot[data-slot=bean]").click()
                self.assertEqual(page.locator(".bank-slot[aria-pressed=true]").get_attribute("data-slot"),"bean")
                self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"),392)
                self.assertEqual(page.locator(".piano-key").count(),13)
                self.assertFalse(errors,errors)
            finally:
                browser.close()
