"""Independent Chromium WITNESS on new HTML built by native workstation subprocess.

Checks actual controls, source-bound dimensions, failure-to-collect, reset,
and shortest-plan play. These are real browser interactions, not saved receipts.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WORLD_FILES = [
    ROOT / "network/tests/fixtures/game_build_world_next.json",
    ROOT / "network/tests/fixtures/game_build_world_alternate.json",
]


class GameBuilderBrowserWitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from systems.workspace.game_build_stack import construct
        cls.tmp=TemporaryDirectory()
        cls.data=Path(cls.tmp.name)
        cls.worlds=[]
        for i,p in enumerate(WORLD_FILES):
            world=json.loads(p.read_text())
            out=cls.data/("room-"+str(i))
            report=construct(data_dir=cls.data/("station-"+str(i)),
                             world=world, output_dir=out)
            cls.worlds.append((world,report,out/"built-world-room.html"))
        cls.playwright=sync_playwright().start()
        cls.browser=cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.tmp.cleanup()

    def _page(self, index):
        page=self.browser.new_page()
        self.addCleanup(page.close)
        world,report,html=self.worlds[index]
        page.goto(html.resolve().as_uri())
        return page,world,report

    def test_01_new_world_is_playable_with_native_built_controls(self):
        page, world, report=self._page(0)
        self.assertEqual(page.locator("#name").inner_text(), "Room: "+world["world_id"])
        self.assertEqual(page.locator("#grid .tile").count(),
                         world["spec"]["width"]*world["spec"]["height"])
        self.assertEqual(page.locator("body").get_attribute("data-solved"),"false")
        for action in report["plan"]:
            page.locator("#"+action).click()
        self.assertEqual(page.locator("body").get_attribute("data-solved"),"true")
        self.assertIn("WORLD COMPLETE",page.locator("#status").inner_text())
        self.assertEqual(page.locator("#turns").inner_text(),
                         "Turns: "+str(report["plan_length"]))
        page.screenshot(path=str(self.data/"room-built-browser-witness.png"),full_page=True)

    def test_02_boundary_and_out_of_reach_remain_real(self):
        page,world,_=self._page(0)
        self.assertEqual(page.locator("body").get_attribute("data-position"),"0,1")
        page.locator("#left").click()
        self.assertEqual(page.locator("body").get_attribute("data-position"),"0,1")
        page.locator("#interact").click()
        self.assertEqual(page.locator("body").get_attribute("data-solved"),"false")
        self.assertEqual(page.locator("#turns").inner_text(),"Turns: 2")
        page.locator("#reset").click()
        self.assertEqual(page.locator("#turns").inner_text(),"Turns: 0")

    def test_04_real_browser_witness_returns_to_original_build_job(self):
        import subprocess, sys
        from runtime.engine import HandoffRuntime
        from runtime.journal import RuntimeJournal
        from systems.workspace.game_build_browser_witness import EVENT
        station=self.data/"station-0"
        output=self.data/"room-0"
        def invoke():
            # A real separate browser WITNESS process, never nested in BUILD's
            # or the test suite's Playwright event loop.
            completed=subprocess.run(
                [sys.executable,"-m","systems.workspace.game_build_browser_witness",
                 "--data-dir",str(station),"--output-dir",str(output)],
                cwd=ROOT,check=True,capture_output=True,text=True,timeout=45)
            return json.loads(completed.stdout)
        first=invoke()
        self.assertTrue(first["native_journal_browser_return_recorded"])
        self.assertTrue(first["new_browser_event"])
        runtime=HandoffRuntime(event_store=RuntimeJournal(station/"runtime.jsonl"))
        returns=[e for e in runtime.event_store.for_handoff(first["job_id"])
                 if e.event_type==EVENT]
        self.assertEqual(len(returns),1)
        repeated=invoke()
        self.assertFalse(repeated["new_browser_event"])

    def test_03_second_new_world_keyboard_controls_and_reset(self):
        page,world,report=self._page(1)
        self.assertEqual(page.locator("#grid .tile").count(),
                         world["spec"]["width"]*world["spec"]["height"])
        key={"up":"ArrowUp","down":"ArrowDown","left":"ArrowLeft",
             "right":"ArrowRight","interact":"e"}
        for action in report["plan"]:
            page.keyboard.press(key[action])
        self.assertEqual(page.locator("body").get_attribute("data-solved"),"true")
        page.keyboard.press("r")
        self.assertEqual(page.locator("body").get_attribute("data-solved"),"false")
        self.assertEqual(page.locator("#turns").inner_text(),"Turns: 0")


if __name__=="__main__":
    unittest.main()
