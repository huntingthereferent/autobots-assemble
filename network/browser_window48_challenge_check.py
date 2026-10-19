"""Actual Chromium WORLD48 rooted game and independent source-host verification."""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread
import unittest

from work.arc3.window48_challenges import verify_certificate

DOCS=Path(__file__).resolve().parents[1]/"docs"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*_args):
        pass


class Window48ChallengeBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.server=ThreadingHTTPServer(("127.0.0.1",0),
            partial(QuietHandler,directory=str(DOCS)))
        cls.thread=Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.playwright=sync_playwright().start()
        cls.browser=cls.playwright.chromium.launch(headless=True)
        cls.url="http://127.0.0.1:"+str(cls.server.server_port)+"/window48_challenges.html"

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        self.page=self.browser.new_page(accept_downloads=True)
        self.addCleanup(self.page.close)
        self.page.goto(self.url)
        self.page.wait_for_function("document.querySelector('#mission').options.length === 16")
        self.assertEqual(self.page.locator("#left-nodes .node").count(),27)
        self.assertEqual(self.page.locator("#right-nodes .node").count(),27)

    def word(self,letters):
        if letters:
            self.page.locator("#word").fill(letters)
            self.page.locator("#run").click()

    def lock(self):
        self.page.locator("#lock").click()

    def exported(self):
        with self.page.expect_download() as evt:
            self.page.locator("#export").click()
        data=json.loads(Path(evt.value.path()).read_text(encoding="utf8"))
        return data,verify_certificate(data)

    def test_active_game_route_opens_world48_not_historical_w13(self):
        page=self.browser.new_page()
        self.addCleanup(page.close)
        page.goto("http://127.0.0.1:"+str(self.server.server_port)+"/game/")
        page.wait_for_url("**/window48_challenges.html")
        page.wait_for_function("document.querySelector('#mission').options.length === 16")
        self.assertEqual(page.locator("h1").inner_text(),"Collision laboratory")
        self.assertEqual(page.locator('#mission option').count(),16)
        self.assertEqual(page.locator('button[data-action="interact"]').count(),0)

    def test_real_challenge_3_root_collision_and_python_host(self):
        self.page.locator("#mission").select_option("2")
        self.assertIn("laws #7 and #10",self.page.locator("#task").inner_text())
        self.assertTrue(self.page.locator("#check").is_disabled())
        self.word("BAB")
        self.lock()
        self.assertEqual(self.page.locator("#left-state").inner_text(),"(0,0,0)")
        self.word("BBBA")
        self.lock()
        self.page.locator("#check").click()
        self.assertIn("WITNESSED",self.page.locator("#verdict").inner_text())
        self.assertIn("1 of 16 source-replayed",self.page.locator("#progress").inner_text())
        payload,report=self.exported()
        self.assertEqual(report["challenge_id"],2)
        self.assertTrue(report["passed"])
        self.assertEqual([t["actions"] for t in payload["trials"]],["BAB","BBBA"])
        self.page.locator("#next").click()
        self.assertEqual(self.page.locator("#mission").input_value(),"3")
        self.assertTrue(self.page.locator("#check").is_disabled())

    def test_empty_path_and_source_hint_are_valid(self):
        self.page.locator("#mission").select_option("1")
        self.page.locator("#hint").click()
        self.assertIn("(empty)",self.page.locator("#hint").inner_text())
        self.lock()  # An empty word is the original root.
        self.word("BBB")
        self.lock()
        self.page.locator("#check").click()
        self.assertIn("WITNESSED",self.page.locator("#verdict").inner_text())
        receipt,report=self.exported()
        self.assertEqual(receipt["trials"][0]["events"],[])
        self.assertTrue(report["passed"])

    def test_failure_is_not_completion_and_can_retry(self):
        self.page.locator("#mission").select_option("2")
        self.word("A")
        self.lock()
        self.word("B")
        self.lock()
        self.page.locator("#check").click()
        self.assertIn("NOT YET",self.page.locator("#verdict").inner_text())
        self.assertTrue(self.page.locator("#next").is_disabled())
        self.assertTrue(self.page.locator("#export").is_disabled())
        self.page.locator("#retry").click()
        self.assertIn("PATH 1",self.page.locator("#phase").inner_text().upper())
        self.assertEqual(self.page.locator("#progress").inner_text(),"0 of 16 source-replayed witnesses saved in this browser")

    def test_completed_source_witness_survives_browser_reload_and_host_replay(self):
        self.page.locator("#mission").select_option("2")
        self.word("BAB")
        self.lock()
        self.word("BBBA")
        self.lock()
        self.page.locator("#check").click()
        first,verified=self.exported()
        self.assertTrue(verified["passed"])
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#mission').options.length === 16")
        self.assertIn("1 of 16 source-replayed",self.page.locator("#progress").inner_text())
        self.assertEqual(self.page.locator("#mission").input_value(),"2")
        self.assertIn("TWO LOCKED PATHS",self.page.locator("#phase").inner_text().upper())
        self.assertFalse(self.page.locator("#check").is_disabled())
        self.page.locator("#check").click()
        second,replayed=self.exported()
        self.assertEqual(first,second)
        self.assertTrue(replayed["verified"])

    def test_in_progress_words_resume_from_source_not_stored_pixel_state(self):
        self.page.locator("#mission").select_option("2")
        self.word("BAB")
        self.lock()
        self.word("BB")
        old_left=self.page.locator("#left-state").inner_text()
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#mission').options.length === 16")
        self.assertIn("PATH 2",self.page.locator("#phase").inner_text().upper())
        self.assertEqual(self.page.locator("#left-state").inner_text(),old_left)
        self.word("BA")
        self.lock()
        self.page.locator("#check").click()
        self.assertIn("WITNESSED",self.page.locator("#verdict").inner_text())
        record,check=self.exported()
        self.assertEqual([x["actions"] for x in record["trials"]],["BAB","BBBA"])
        self.assertTrue(check["passed"])

    def test_corrupt_saved_witness_is_not_restored_as_completion(self):
        self.page.locator("#mission").select_option("2")
        self.word("BAB")
        self.lock()
        self.word("BBBA")
        self.lock()
        self.page.locator("#check").click()
        self.assertIn("1 of 16 source-replayed",self.page.locator("#progress").inner_text())
        self.page.evaluate("""() => {
          const key='world48-source-replayed-progress/v1';
          const record=JSON.parse(localStorage.getItem(key));
          record.certificates[0].trials[0].events[0].after[0]=26;
          localStorage.setItem(key,JSON.stringify(record));
        }""")
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#mission').options.length === 16")
        self.assertIn("0 of 16 source-replayed",self.page.locator("#progress").inner_text())
        self.assertTrue(self.page.locator("#export").is_disabled())

    def test_saved_progress_can_be_cleared_without_changing_original_source(self):
        self.page.locator("#mission").select_option("1")
        self.lock()
        self.word("BBB")
        self.lock()
        self.page.locator("#check").click()
        self.assertIn("1 of 16",self.page.locator("#progress").inner_text())
        self.page.locator("#clear-progress").click()
        self.assertIn("0 of 16",self.page.locator("#progress").inner_text())
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#mission').options.length === 16")
        self.assertIn("0 of 16",self.page.locator("#progress").inner_text())

    def test_invalid_word_keeps_source_origin(self):
        self.page.locator("#word").fill("AACX")
        self.page.locator("#run").click()
        self.assertIn("Use A/B only",self.page.locator("#status").inner_text())
        self.assertEqual(self.page.locator("#left-state").inner_text(),"(0,0,0)")
        self.assertEqual(self.page.locator("#right-state").inner_text(),"(0,0,0)")


if __name__=="__main__":
    unittest.main()
