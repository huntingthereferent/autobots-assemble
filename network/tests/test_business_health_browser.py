"""Regression: an old optional insight cannot overwrite a later business calculation."""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "money/products/P002_business-health-tracker/app"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


@unittest.skipUnless(sync_playwright, "Playwright required for browser regression")
class BusinessHealthBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = partial(QuietHandler, directory=str(APP))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_address[1]}/index.html"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def test_late_old_insight_does_not_replace_new_calculation(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                page = browser.new_page()
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                pending = []
                page.route("**/api/insight", lambda route: pending.append(route))
                page.goto(self.url, wait_until="networkidle")
                for _ in range(4):
                    page.locator("#next").click()
                page.wait_for_function("!document.querySelector('#dashboard').hidden")
                page.wait_for_function("document.querySelector('#insight-text').textContent.length > 0")
                self.assertEqual(len(pending), 1)
                page.locator("#reset").click()
                for _ in range(3):
                    page.locator("#next").click()
                page.locator("#monthlySales").fill("260")
                page.locator("#next").click()
                page.wait_for_function("!document.querySelector('#dashboard').hidden")
                self.assertEqual(len(pending), 2)
                pending[1].fulfill(status=200, content_type="application/json",
                                   body='{"insight":"CURRENT CALCULATION","source":"openai"}')
                page.wait_for_function(
                    "document.querySelector('#insight-text').textContent === 'CURRENT CALCULATION'"
                )
                pending[0].fulfill(status=200, content_type="application/json",
                                   body='{"insight":"OUTDATED CALCULATION","source":"openai"}')
                page.wait_for_timeout(150)
                self.assertEqual(page.locator("#insight-text").inner_text(),
                                 "CURRENT CALCULATION")
                self.assertFalse(errors, errors)
            finally:
                browser.close()


if __name__ == "__main__":
    unittest.main()
