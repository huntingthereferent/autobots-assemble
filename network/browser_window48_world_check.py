"""Real Chromium checks for the source-derived finite WORLD48 browser.

Independent Python host replay verifies exported browser transitions against
original CombinedWorld. No native ARC instance is implied.
"""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread
import unittest

from work.arc3.window48_world_export import verify_receipt

DOCS=Path(__file__).resolve().parents[1]/"docs"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class World48BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.server=ThreadingHTTPServer(("127.0.0.1",0),
            partial(QuietHandler,directory=str(DOCS)))
        cls.thread=Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.playwright=sync_playwright().start()
        cls.browser=cls.playwright.chromium.launch(headless=True)
        cls.url="http://127.0.0.1:"+str(cls.server.server_port)+"/window48_world.html"

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
        self.page.wait_for_function("document.querySelector('#law-left').options.length === 48")
        self.assertEqual(self.page.locator("#law-left option").count(),48)
        self.assertEqual(self.page.locator("#law-right option").count(),48)
        self.assertEqual(self.page.locator("#left-nodes .node").count(),27)
        self.assertEqual(self.page.locator("#right-nodes .node").count(),27)

    def exported(self):
        with self.page.expect_download() as received:
            self.page.locator("#export").click()
        download=received.value
        self.assertEqual(download.suggested_filename,"window48_source_receipt.json")
        payload=json.loads(Path(download.path()).read_text(encoding="utf8"))
        self.assertTrue(verify_receipt(payload)["valid"])
        return payload

    def test_real_clicks_and_host_replay(self):
        self.page.locator("#law-left").select_option("6")
        self.page.locator("#law-right").select_option("9")
        self.assertIn("moves the marked origin",
            self.page.locator("#relation").inner_text())
        self.page.locator("#action-a").click()
        self.page.locator("#action-b").click()
        self.assertIn("AB",self.page.locator("#applied-word").inner_text())
        payload=self.exported()
        self.assertEqual(payload["law_ids"],[6,9])
        self.assertEqual(payload["actions"],"AB")
        self.assertEqual(len(payload["events"]),2)
        self.page.locator("#undo").click()
        self.assertEqual(self.exported()["actions"],"A")
        self.page.locator("#reset").click()
        self.assertEqual(self.exported()["actions"],"")
        self.assertEqual(self.page.locator("#left-nodes .is-current").count(),1)

    def test_exact_word_and_class_boundary(self):
        self.page.locator("#law-left").select_option("6")
        self.page.locator("#law-right").select_option("9")
        self.page.locator("#word-input").fill("BAB")
        self.page.locator("#run-word").click()
        payload=self.exported()
        self.assertEqual(payload["actions"],"BAB")
        self.page.locator("#law-left").select_option("0")
        self.page.locator("#law-right").select_option("1")
        self.assertIn("Origin-preserving conjugacy",
            self.page.locator("#relation").inner_text())
        self.assertEqual(self.exported()["actions"],"")

    def test_invalid_word_does_not_advance(self):
        self.page.locator("#word-input").fill("AQQB")
        self.page.locator("#run-word").click()
        self.assertIn("Only A/B",self.page.locator("#status").inner_text())
        self.assertEqual(self.exported()["events"],[])
        self.assertEqual(self.exported()["final"],[0,0])


if __name__=="__main__":
    unittest.main()
