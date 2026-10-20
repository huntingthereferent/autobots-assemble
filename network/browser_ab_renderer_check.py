"""Real Chromium tests of A/B's own source-driven Canvas2D renderer.

Not part of general unittest discovery: this needs Playwright + Chromium.
No Godot engine, simulated physics or native worker launch.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread
import unittest

from work.arc_like_maze.math import World

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "build_ab_renderer_receipts"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class ABNativeRendererBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=str(DOCS)))
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)
        cls.url = "http://127.0.0.1:" + str(cls.server.server_port) + "/live/ab-renderer.html"

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        self.page = self.browser.new_page(viewport={"width": 1365, "height": 860})
        self.addCleanup(self.page.close)
        self.page.goto(self.url, wait_until="load")
        self.page.wait_for_function(
            "window.__ABNativeView && (window.__ABNativeView.loaded || window.__ABNativeView.error)")
        self.assertTrue(self.page.evaluate("window.__ABNativeView.loaded"),
                        self.page.locator("#status").inner_text())

    def state(self):
        return self.page.evaluate("({current:window.__ABNativeView.current,"
                                  "actions:window.__ABNativeView.actions,"
                                  "selected:window.__ABNativeView.selected})")

    def test_actual_browser_source_a_b_history_and_reset(self):
        native = World(3, (0, 1, 2))
        self.assertEqual(self.page.evaluate("window.__ABNativeView.edgeCount"), 54)
        self.assertEqual(self.state()["current"], "0,0,0")
        for action, button in [("A", "#step-a"), ("B", "#step-b"),
                               ("A", "#step-a")]:
            self.page.locator(button).click()
            self.assertEqual(self.state()["current"],
                             ",".join(map(str, native.apply(self.state()["actions"]))))
        self.assertEqual(self.state()["actions"], "ABA")
        self.page.locator("#undo").click()
        self.assertEqual(self.state()["actions"], "AB")
        self.assertEqual(self.state()["current"], ",".join(map(str, native.apply("AB"))))
        self.page.locator("#reset").click()
        self.assertEqual(self.state(), {"current": "0,0,0",
                                         "actions": "", "selected": "0,0,0"})
        self.assertTrue(self.page.locator("#undo").is_disabled())

    def test_real_keyboard_and_demo_source_replay(self):
        self.page.keyboard.press("a")
        self.page.keyboard.press("b")
        self.assertEqual(self.state()["actions"], "AB")
        self.page.keyboard.press("Backspace")
        self.assertEqual(self.state()["actions"], "A")
        self.page.keyboard.press("r")
        self.page.locator("#play").click()
        self.page.wait_for_function("window.__ABNativeView.actions.length === 9",
                                    timeout=15000)
        record = self.state()
        self.assertEqual(record["actions"], "ABAABBABA")
        self.assertEqual(record["current"],
                         ",".join(map(str, World(3, (0, 1, 2)).apply(record["actions"]))))
        EVIDENCE.mkdir(exist_ok=True)
        self.page.screenshot(path=str(EVIDENCE/"ab_owned_renderer_actual_chromium.png"),
                             full_page=True)
        (EVIDENCE/"ab_owned_renderer_native_replay.json").write_text(
            json.dumps(record, indent=2)+"\n", encoding="utf8")

    def test_pan_and_zoom_only_change_view_not_native_state(self):
        self.page.locator("#step-b").click()
        saved = self.state()
        canvas = self.page.locator("#ab-canvas")
        box = canvas.bounding_box()
        self.assertIsNotNone(box)
        self.page.mouse.move(box["x"]+box["width"]/2,box["y"]+box["height"]/2)
        self.page.mouse.wheel(0, -280)
        self.page.mouse.down()
        self.page.mouse.move(box["x"]+box["width"]/2+63,
                             box["y"]+box["height"]/2+40,steps=4)
        self.page.mouse.up()
        self.assertEqual(saved,self.state())
        self.page.locator("#fit").click()
        self.assertEqual(saved,self.state())
        self.assertGreater(self.page.evaluate("window.__ABNativeView.drawCount"),0)

    def test_corrupted_scene_is_refused_before_any_movement(self):
        # Modify exact source edge in transit without altering repository data.
        page=self.browser.new_page()
        self.addCleanup(page.close)
        target="**/ab-renderer-scene.json"
        def corrupt(route):
            value=json.loads((DOCS/"live"/"ab-renderer-scene.json").read_text())
            value["nodes"][0]["transitions"]["A"]="2,2,2"
            route.fulfill(content_type="application/json",body=json.dumps(value))
        page.route(target,corrupt)
        page.goto(self.url,wait_until="load")
        page.wait_for_function("window.__ABNativeView && window.__ABNativeView.error")
        self.assertFalse(page.evaluate("window.__ABNativeView.loaded"))
        self.assertIn("SOURCE REFUSED",page.locator("#status").inner_text())
        page.locator("#step-a").click()
        self.assertEqual(page.evaluate("window.__ABNativeView.actions"),"")
        self.assertEqual(page.evaluate("window.__ABNativeView.current"),"")


if __name__=="__main__":
    unittest.main()
