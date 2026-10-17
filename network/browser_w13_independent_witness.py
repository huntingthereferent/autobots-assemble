"""Independent WITNESS Chromium: operate BUILD's page and distrust its exports.

Test authored separately from BUILD W13 browser smoke/verifier. Downloads come
from actual Chromium clicks and are compared with ORIGINAL W12 source plus
WORLD W13's fixed rule, never BUILD's W13 verifier.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from network.witness_w13_independent import independent_w13_replay, strict_json

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "docs/game_w13_preview.html").read_text(encoding="utf8")
EVIDENCE = ROOT / "witness_w13_observations"


class IndependentChromiumW13Witness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.tool = sync_playwright().start()
        cls.browser = cls.tool.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.tool.stop()

    def setUp(self):
        self.page = self.browser.new_page(accept_downloads=True)
        self.addCleanup(self.page.close)
        self.page.set_content(PAGE, wait_until="load")

    def act(self, verb):
        self.page.locator('button[data-action="' + verb + '"]').click()

    def export(self, name):
        with self.page.expect_download() as info:
            self.page.locator("#export").click()
        receipt = strict_json(Path(info.value.path()).read_text(encoding="utf8"))
        EVIDENCE.mkdir(exist_ok=True)
        (EVIDENCE / name).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf8")
        return receipt

    def reach_second(self):
        self.act("right")
        self.act("interact")
        self.page.locator("#advance").click()

    def test_01_real_two_room_clicks_replay_against_original_W12(self):
        self.assertTrue(self.page.locator("#advance").is_disabled())
        self.reach_second()
        self.act("right")
        self.act("interact")
        output = self.export("witness_real_browser_success.json")
        proof = independent_w13_replay(output)
        self.assertTrue(proof["solved"])
        self.assertEqual(proof["boundaries_checked"], 1)
        self.assertEqual([z["actions_verified"] for z in proof["per_world"]], [2, 2])
        self.assertEqual(output["actions"], ["right", "interact", "advance", "right", "interact"])
        self.assertEqual(output["worlds"][0]["final"],
                         {"x": 1, "y": 1, "turns": 2, "collected": True})
        self.page.screenshot(path=str(EVIDENCE / "witness_real_chromium_complete.png"), full_page=True)

    def test_02_first_room_must_not_advance_before_collection(self):
        self.assertTrue(self.page.locator("#advance").is_disabled())
        self.act("right")
        self.assertTrue(self.page.locator("#advance").is_disabled())
        output = self.export("witness_before_collection.json")
        self.assertEqual(independent_w13_replay(output)["boundaries_checked"], 0)
        self.assertFalse(output["final"]["solved"])

    def test_03_blocked_left_keeps_position_consumes_turn(self):
        self.act("left")
        self.reach_second()
        self.act("right")
        self.act("interact")
        output = self.export("witness_boundary_turn.json")
        proof = independent_w13_replay(output)
        self.assertTrue(proof["solved"])
        first_step = output["worlds"][0]["observations"][0]
        self.assertEqual(first_step["verdict"], "blocked-by-boundary")
        self.assertEqual(first_step["before"]["x"], first_step["after"]["x"])
        self.assertEqual(first_step["after"]["turns"], 1)
        self.assertEqual(output["worlds"][0]["final"]["turns"], 3)

    def test_04_diagonal_interact_is_out_of_reach(self):
        self.reach_second()
        self.act("interact")
        output = self.export("witness_diagonal_out_of_reach.json")
        proof = independent_w13_replay(output)
        self.assertFalse(proof["solved"])
        self.assertEqual(proof["worlds_completed"], 1)
        self.assertEqual(output["worlds"][1]["observations"][0]["verdict"], "out-of-reach")

    def test_05_reset_restores_original_start_and_discards_global_trace(self):
        self.reach_second()
        self.act("right")
        self.act("interact")
        self.page.locator("#reset").click()
        output = self.export("witness_reset.json")
        proof = independent_w13_replay(output)
        self.assertFalse(proof["solved"])
        self.assertEqual(output["actions"], [])
        self.assertEqual(output["boundaries"], [])
        self.assertEqual(output["final"]["world_id"], "first-room")
        self.assertEqual(output["worlds"][1]["final"]["turns"], 0)
        self.assertTrue(self.page.locator("#advance").is_disabled())

    def test_06_last_world_cannot_advance_again(self):
        self.reach_second()
        self.assertTrue(self.page.locator("#advance").is_hidden())
        self.act("right")
        self.act("interact")
        output = self.export("witness_no_third_world.json")
        self.assertEqual(output["actions"].count("advance"), 1)
        self.assertTrue(independent_w13_replay(output)["solved"])

    def test_07_keyboard_moves_actual_browser_and_preserves_order(self):
        self.page.locator("h1").click()
        self.page.keyboard.press("ArrowRight")
        self.page.keyboard.press("Enter")
        self.page.locator("#advance").click()
        self.page.locator("h1").click()
        self.page.keyboard.press("d")
        self.page.keyboard.press("Space")
        output = self.export("witness_keyboard.json")
        self.assertTrue(independent_w13_replay(output)["solved"])

    def test_08_mutated_actual_downloads_are_rejected_by_independent_oracle(self):
        self.reach_second()
        self.act("right")
        self.act("interact")
        genuine = self.export("witness_negative_source.json")
        for case in ("global", "world-before", "world-after", "world-final", "crossing", "session-final"):
            changed = deepcopy(genuine)
            if case == "global":
                changed["actions"][2] = "right"
            elif case == "world-before":
                changed["worlds"][0]["observations"][0]["before"]["x"] = 2
            elif case == "world-after":
                changed["worlds"][1]["observations"][1]["after"]["collected"] = False
            elif case == "world-final":
                changed["worlds"][0]["final"]["collected"] = False
            elif case == "crossing":
                changed["boundaries"][0]["after"]["state"]["x"] = 1
            else:
                changed["final"]["worlds_completed"] = 1
            (EVIDENCE / ("witness_reject_" + case + ".json")).write_text(
                json.dumps(changed, indent=2) + "\n", encoding="utf8")
            with self.subTest(case=case), self.assertRaises(ValueError):
                independent_w13_replay(changed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
