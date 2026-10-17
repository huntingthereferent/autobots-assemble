"""BUILD W13 Chromium smoke: actual clicks, keys, downloads and W12-native replay.

This file is NOT named test_*.py to keep core unittest discovery independent
of the optional browser dependency. Executed in dedicated BUILD workflow.
Not a separate WITNESS-team implementation or origin authentication.
"""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import unittest

from systems.workspace.game_w13_receipt import verify_session_receipt

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "docs/game_w13_preview.html").read_text(encoding="utf8")
BUILD_EVIDENCE = ROOT / "build_w13_browser_receipts"


class W13BrowserBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls._context = sync_playwright().start()
        cls.browser = cls._context.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls._context.stop()

    def setUp(self):
        self.page = self.browser.new_page(accept_downloads=True)
        self.addCleanup(self.page.close)
        self.page.set_content(HTML, wait_until="load")

    def press(self, action):
        self.page.locator('button[data-action="' + action + '"]').click()

    def exported(self):
        with self.page.expect_download() as saved:
            self.page.locator("#export").click()
        file = saved.value
        self.assertEqual(file.suggested_filename, "game_w13_session_receipt.json")
        data = json.loads(Path(file.path()).read_text(encoding="utf8"))
        self.assertTrue(verify_session_receipt(data)["valid"])
        return data

    def test_01_two_room_browser_success_and_actual_download(self):
        self.assertTrue(self.page.locator("#advance").is_disabled())
        self.press("right")
        self.press("interact")
        self.assertTrue(self.page.locator("#advance").is_enabled())
        self.page.locator("#advance").click()
        self.press("right")
        self.press("interact")
        payload = self.exported()
        self.assertEqual(payload["actions"], ["right", "interact", "advance", "right", "interact"])
        self.assertEqual(payload["final"], {
            "world_id": "second-room",
            "state": {"x": 1, "y": 0, "collected": True, "turns": 2},
            "worlds_completed": 2, "solved": True
        })
        self.assertEqual(payload["worlds"][0]["final"]["turns"], 2)
        BUILD_EVIDENCE.mkdir(exist_ok=True)
        (BUILD_EVIDENCE / "w13_browser_positive.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf8")
        self.page.screenshot(path=str(BUILD_EVIDENCE / "w13_browser_complete.png"), full_page=True)
        self.assertEqual(len(payload["boundaries"]), 1)
        self.assertEqual(payload["boundaries"][0]["before"]["state"], payload["worlds"][0]["final"])

    def test_02_blocked_move_consumes_first_room_turn_and_survives_advance(self):
        self.press("left")
        self.press("right")
        self.press("interact")
        self.page.locator("#advance").click()
        self.press("right")
        self.press("interact")
        payload = self.exported()
        self.assertTrue(payload["final"]["solved"])
        self.assertEqual(payload["worlds"][0]["observations"][0]["verdict"], "blocked-by-boundary")
        self.assertEqual(payload["worlds"][0]["observations"][0]["after"]["turns"], 1)
        self.assertEqual(payload["worlds"][0]["final"]["turns"], 3)
        self.assertEqual(payload["worlds"][1]["final"]["turns"], 2)

    def test_03_second_world_diagonal_interact_not_collected(self):
        self.press("right")
        self.press("interact")
        self.page.locator("#advance").click()
        self.press("interact")
        payload = self.exported()
        self.assertEqual(payload["worlds"][1]["observations"][0]["verdict"], "out-of-reach")
        self.assertEqual(payload["worlds"][1]["final"]["turns"], 1)
        self.assertFalse(payload["final"]["solved"])

    def test_04_collection_alone_never_advances_automatically(self):
        self.press("right")
        self.press("interact")
        self.assertIn("first-room", self.page.locator("#room-title").inner_text())
        payload = self.exported()
        self.assertEqual(payload["final"]["world_id"], "first-room")
        self.assertEqual(payload["final"]["worlds_completed"], 1)
        self.assertEqual(payload["boundaries"], [])
        self.assertFalse(payload["final"]["solved"])

    def test_05_second_world_move_without_interact_still_incomplete(self):
        self.press("right")
        self.press("interact")
        self.page.locator("#advance").click()
        self.press("right")
        payload = self.exported()
        self.assertEqual(payload["final"]["worlds_completed"], 1)
        self.assertFalse(payload["final"]["solved"])

    def test_06_native_replay_rejects_manipulated_actual_browser_download(self):
        self.press("right")
        self.press("interact")
        self.page.locator("#advance").click()
        self.press("right")
        self.press("interact")
        payload = self.exported()
        for edit in ("boundary", "first-room", "second-room", "final"):
            bad = deepcopy(payload)
            if edit == "boundary":
                bad["boundaries"][0]["after"]["state"]["x"] = 99
            elif edit == "first-room":
                bad["worlds"][0]["observations"][0]["before"]["x"] = 99
            elif edit == "second-room":
                bad["worlds"][1]["observations"][0]["after"]["turns"] = 99
            else:
                bad["final"]["solved"] = False
            BUILD_EVIDENCE.mkdir(exist_ok=True)
            (BUILD_EVIDENCE / ("w13_rejected_" + edit + ".json")).write_text(json.dumps(bad, indent=2) + "\n", encoding="utf8")
            with self.subTest(edit=edit), self.assertRaises(ValueError):
                verify_session_receipt(bad)

    def test_07_reset_discards_both_worlds_and_global_actions(self):
        self.press("right")
        self.press("interact")
        self.page.locator("#advance").click()
        self.press("right")
        self.press("interact")
        self.page.locator("#reset").click()
        payload = self.exported()
        self.assertEqual(payload["actions"], [])
        self.assertEqual(payload["boundaries"], [])
        self.assertEqual(payload["final"]["world_id"], "first-room")
        self.assertEqual(payload["worlds"][0]["final"]["turns"], 0)
        self.assertEqual(payload["worlds"][1]["final"]["turns"], 0)
        self.assertFalse(payload["final"]["solved"])
        self.assertTrue(self.page.locator("#advance").is_disabled())

    def test_08_keyboard_movement_and_interact_generate_native_valid_receipt(self):
        self.page.locator("h1").click()
        self.page.keyboard.press("ArrowRight")
        self.page.keyboard.press("Space")
        self.page.locator("#advance").click()
        self.page.locator("h1").click()
        self.page.keyboard.press("d")
        self.page.keyboard.press("Enter")
        payload = self.exported()
        self.assertEqual(payload["actions"], ["right", "interact", "advance", "right", "interact"])
        self.assertTrue(payload["final"]["solved"])

    def test_09_actual_last_room_has_no_advance_control(self):
        self.press("right")
        self.press("interact")
        self.page.locator("#advance").click()
        self.assertTrue(self.page.locator("#advance").is_hidden())
        self.press("right")
        self.press("interact")
        payload = self.exported()
        self.assertEqual(payload["actions"].count("advance"), 1)
        self.assertEqual(payload["worlds"][0]["final"]["turns"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
