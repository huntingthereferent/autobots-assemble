"""Browser checks for focus-safe Pony Trail controls (independent of source-token tests)."""
import re
import unittest
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

PAGE = Path(__file__).resolve().parents[2] / "docs/live/pony-trail.html"


def distance(text):
    return int(re.search(r"\d+", text).group())


@unittest.skipUnless(sync_playwright, "Playwright required for browser checks")
class PonyTrailBrowserTests(unittest.TestCase):
    def test_focused_trail_selector_owns_keyboard(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                page = browser.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(PAGE.as_uri(), wait_until="domcontentloaded")
                page.locator("#start").click()
                page.wait_for_function(
                    "parseInt(document.querySelector('#distance').textContent, 10) > 20",
                    timeout=6000,
                )
                page.locator("#trail").focus()
                self.assertTrue(page.locator("#trail").evaluate("(el) => el === document.activeElement"))
                before = distance(page.locator("#distance").inner_text())
                page.keyboard.press("r")
                page.wait_for_timeout(120)
                after = distance(page.locator("#distance").inner_text())
                self.assertGreaterEqual(after, before, "Typing in a focused selector restarted the ride")
                self.assertFalse(errors, errors)
            finally:
                browser.close()

    def test_unfocused_game_restart_shortcut_still_works(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                page = browser.new_page()
                page.goto(PAGE.as_uri(), wait_until="domcontentloaded")
                page.locator("#start").click()
                page.wait_for_function(
                    "parseInt(document.querySelector('#distance').textContent, 10) > 20",
                    timeout=6000,
                )
                before = distance(page.locator("#distance").inner_text())
                page.locator("#game").click(position={"x": 25, "y": 25})
                page.keyboard.press("r")
                page.wait_for_timeout(120)
                self.assertLess(distance(page.locator("#distance").inner_text()), before)
            finally:
                browser.close()


if __name__ == "__main__":
    unittest.main()
