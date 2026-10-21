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
                    page.wait_for_function("document.querySelector('#bank-evidence').textContent.includes('tuned-math')",timeout=15000)
                    page.locator("#audition-sound").click()
                    self.assertIn("TUNED",page.locator("#now-playing").inner_text())
                    page.locator("#bank-target").select_option("mochi")
                    page.locator("#sound-file").set_input_files(str(wav_path))
                    page.locator("#clip-position").evaluate("(el)=>{el.value='42';el.dispatchEvent(new Event('input',{bubbles:true}))}")
                    page.locator("#swallow-sound").click()
                    page.wait_for_function("document.querySelector('#bank-status').textContent.includes('Swallowed')",timeout=15000)
                    self.assertIn("sample-cat.wav",page.locator("#bank-evidence").inner_text())
                    self.assertIn("local-file",page.locator("#bank-evidence").inner_text())
                    page.locator("#audition-sound").click()
                    self.assertIn("SAMPLE",page.locator("#now-playing").inner_text())
                    page.locator("#handoff-sound").click()
                    page.wait_for_timeout(1200)
                    self.assertTrue(any(name.endswith(".wav") for name in downloads),downloads)
                    self.assertTrue(any(name.endswith(".json") for name in downloads),downloads)
                    page.locator("#reset-sound").click()
                    page.locator("#audition-sound").click()
                    self.assertIn("TUNED",page.locator("#now-playing").inner_text())
                    page.wait_for_function("document.querySelector('#bank-evidence').textContent.includes('mochi.tuned-math')",timeout=15000)
                    self.assertFalse(errors,errors)
                finally:
                    browser.close()

    def test_sixteen_bars_branches_navigation_and_finished_pass(self):
        import json
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"])
            try:
                page=browser.new_page(accept_downloads=True)
                errors=[]
                page.on("pageerror",lambda error:errors.append(str(error)))
                page.goto(PAGE.as_uri(),wait_until="domcontentloaded")
                self.assertEqual(page.locator("#chord-list .bar-tile").count(),16)
                self.assertEqual(page.locator("#seq .step").count(),80)
                self.assertEqual(page.locator("#progression-template option").count(),9)
                self.assertEqual(page.locator("#chord-list .bar-tile strong").all_inner_texts()[:4],["C","G","Am","F"])
                page.locator("#progression-key").select_option("2")
                self.assertEqual(page.locator("#chord-list .bar-tile strong").all_inner_texts()[:4],["D","A","Bm","G"])
                self.assertEqual(page.locator("#chord-list .bar-tile strong").all_inner_texts()[4],"C")
                page.locator("#seq .step[data-row='0'][data-col='2']").click()
                self.assertEqual(page.locator("#seq .step.on").count(),1)
                page.locator("#bar-next").click()
                self.assertEqual(page.locator("#seq .step.on").count(),0)
                page.locator("#bar-prev").click()
                self.assertEqual(page.locator("#seq .step.on").count(),1)
                page.locator("#chord-list .bar-tile").nth(8).click()
                page.locator("#progression-name").fill("Rosey's song")
                page.locator("#progression-chords").fill("Dm G A D")
                page.locator("#save-progression").click()
                self.assertEqual(page.locator("#progression-template option").count(),10)
                self.assertEqual(page.locator("#chord-list .bar-tile strong").all_inner_texts()[8:12],["Dm","G","A","D"])
                self.assertEqual(page.locator("#chord-list .bar-tile strong").all_inner_texts()[:4],["D","A","Bm","G"])
                page.locator("#branch-name").fill("Original song")
                page.locator("#branch-save-new").click()
                self.assertEqual(page.locator("#branch-select option").count(),2)
                page.locator("#chord-list .bar-tile").nth(15).click()
                page.locator("#bar-chord").fill("Em7")
                page.locator("#set-bar-chord").click()
                self.assertEqual(page.locator("#chord-list .bar-tile strong").all_inner_texts()[15],"Em7")
                page.locator("#branch-name").fill("Alternate ending")
                page.locator("#branch-save-new").click()
                self.assertEqual(page.locator("#branch-select option").count(),3)
                page.locator("#branch-select").select_option("branch-1")
                page.locator("#branch-load").click()
                self.assertEqual(page.locator("#chord-list .bar-tile strong").all_inner_texts()[15],"F")
                self.assertEqual(page.locator("#seq .step.on").count(),1)
                with page.expect_download() as download:
                    page.locator("#branch-export").click()
                data=json.loads(Path(download.value.path()).read_text(encoding="utf-8"))
                self.assertEqual(data["schema"],"meow-machine/arrangement-branches-v1")
                self.assertEqual(len(data["branches"]),2)
                self.assertEqual(len(data["working"]["bars"]),16)
                self.assertEqual(len(data["working"]["bars"][0]["notes"][0]),16)
                # Persistent saves survive reopening the page.
                page.reload(wait_until="domcontentloaded")
                self.assertEqual(page.locator("#branch-select option").count(),3)
                page.locator("#branch-select").select_option("branch-1")
                page.locator("#branch-load").click()
                self.assertEqual(page.locator("#chord-list .bar-tile strong").all_inner_texts()[15],"F")
                # Restoring a backup forks imported branches instead of overwriting IDs.
                page.locator("#branch-file").set_input_files(download.value.path())
                page.wait_for_function("document.querySelector('#branch-status').textContent.includes('Restored')",timeout=10000)
                self.assertEqual(page.locator("#branch-select option").count(),5)
                page.locator("#chord-list .bar-tile").nth(15).click()
                page.locator("#repeat-arrangement").uncheck()
                page.locator("#tempo").evaluate("(e)=>{e.value='180';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}")
                page.locator("#play-from-bar").click()
                page.wait_for_function("document.querySelector('#studio-status').textContent.includes('FINISHED')",timeout=17000)
                self.assertEqual(page.locator("#chord-list .bar-tile.playing").count(),0)
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
