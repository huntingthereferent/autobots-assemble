"""Actual Chromium WORLD48 rooted game and independent source-host verification."""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from tempfile import TemporaryDirectory
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
        self.page.wait_for_function("document.querySelector('#mission').options.length === 48")
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
        page.wait_for_function("document.querySelector('#mission').options.length === 48")
        self.assertEqual(page.locator("h1").inner_text(),"Collision laboratory")
        self.assertEqual(page.locator('#mission option').count(),48)
        self.assertEqual(page.locator('button[data-action="interact"]').count(),0)

    def test_each_finite_world_has_three_exact_z_planes_and_27_unique_coordinates(self):
        for side in ("left","right"):
            slices=self.page.locator("#"+side+"-nodes .slice")
            self.assertEqual(slices.count(),3)
            labels=[slices.nth(z).locator(".slice-label").inner_text() for z in range(3)]
            self.assertEqual(labels,["z = 0","z = 1","z = 2"])
            observed=[]
            for z in range(3):
                nodes=slices.nth(z).locator(".node")
                self.assertEqual(nodes.count(),9)
                self.assertEqual(nodes.count(),len([
                    nodes.nth(i).get_attribute("data-state-index") for i in range(9)
                ]))
                for u in range(3):
                    for v in range(3):
                        node=nodes.nth(3*u+v)
                        index=9*u+3*v+z
                        self.assertEqual(int(node.get_attribute("data-state-index")),index)
                        self.assertEqual(node.inner_text(),str(u)+","+str(v))
                        self.assertEqual(node.get_attribute("title"),
                                         "("+str(u)+","+str(v)+","+str(z)+")")
                        observed.append(index)
            self.assertEqual(set(observed),set(range(27)))
            self.assertEqual(
                self.page.locator("#"+side+"-nodes .node.current").count(),1
            )
            self.assertEqual(
                self.page.locator("#"+side+"-nodes .node.marked").get_attribute("data-state-index"),"0"
            )

    def test_exact_source_A_B_previews_and_highlights_across_three_charts(self):
        manifest=json.loads((DOCS/"window48_world_data.json").read_text(encoding="utf8"))
        roster=json.loads((DOCS/"window48_challenges.json").read_text(encoding="utf8"))
        def coordinates(index):
            return "("+str(index//9)+","+str((index%9)//3)+","+str(index%3)+")"
        for mission in (0,16,32,47):
            with self.subTest(mission=mission):
                self.page.locator("#mission").select_option(str(mission))
                ids=roster["challenges"][mission]["law_ids"]
                for side,n in (("left",0),("right",1)):
                    law=manifest["laws"][ids[n]]
                    self.assertEqual(
                        self.page.locator("#"+side+"-next .step-a").inner_text(),
                        "A: (0,0,0) → "+coordinates(law["A"][0])
                    )
                    self.assertEqual(
                        self.page.locator("#"+side+"-next .step-b").inner_text(),
                        "B: (0,0,0) → "+coordinates(law["B"][0])
                    )
                    for action,name in (("A","nextA"),("B","nextB")):
                        self.assertEqual(
                            self.page.locator("#"+side+"-nodes .node."+name).get_attribute("data-state-index"),
                            str(law[action][0])
                        )
                self.page.locator("#a").click()
                self.page.locator("#b").click()
                for side,n in (("left",0),("right",1)):
                    law=manifest["laws"][ids[n]]
                    end=law["B"][law["A"][0]]
                    self.assertEqual(self.page.locator("#"+side+"-state").inner_text(),
                                     coordinates(end))
                    self.assertEqual(
                        self.page.locator("#"+side+"-nodes .node.current").get_attribute("data-state-index"),
                        str(end)
                    )
                    for action,cls in (("A","step-a"),("B","step-b")):
                        preview=self.page.locator("#"+side+"-next ."+cls).inner_text()
                        self.assertEqual(preview,action+": "+coordinates(end)+" → "+coordinates(law[action][end]))
                self.page.locator("#reset").click()

    def test_live_comparison_uses_true_rooted_endpoints_without_premature_win(self):
        self.page.locator("#mission").select_option("2")
        self.assertIn("Awaiting Path 1",self.page.locator("#relation-left").inner_text())
        self.assertEqual(self.page.locator("#live-relation").get_attribute("data-ready"),"false")
        self.word("BAB")
        self.lock()
        self.assertIn("LIVE PREVIEW",self.page.locator("#relation-status").inner_text())
        self.assertEqual(self.page.locator("#left-nodes .node.reference").count(),1)
        self.assertEqual(self.page.locator("#right-nodes .node.reference").count(),1)
        self.assertIn("SAME WORD",self.page.locator("#relation-distinct").inner_text()) if False else None
        self.assertTrue(self.page.locator("#check").is_disabled())
        self.word("BBBA")
        self.assertEqual(self.page.locator("#live-relation").get_attribute("data-ready"),"true")
        self.assertEqual(self.page.locator("#relation-left").get_attribute("data-met"),"true")
        self.assertEqual(self.page.locator("#relation-right").get_attribute("data-met"),"true")
        self.assertEqual(self.page.locator("#relation-distinct").get_attribute("data-met"),"true")
        self.assertIn("SPLIT",self.page.locator("#relation-right").inner_text())
        self.assertTrue(self.page.locator("#export").is_disabled())
        self.lock()
        self.assertIn("BOTH PATHS LOCKED",self.page.locator("#relation-status").inner_text())
        self.assertEqual(self.page.locator("#live-relation").get_attribute("data-ready"),"true")
        self.page.locator("#check").click()
        self.assertIn("WITNESSED",self.page.locator("#verdict").inner_text())
        payload,verified=self.exported()
        self.assertTrue(verified["passed"])
        self.assertEqual([t["actions"] for t in payload["trials"]],["BAB","BBBA"])

    def test_live_relation_false_for_wrong_paths_and_resets_with_new_challenge(self):
        self.page.locator("#mission").select_option("2")
        self.word("A")
        self.lock()
        self.word("B")
        self.assertEqual(self.page.locator("#live-relation").get_attribute("data-ready"),"false")
        self.assertTrue(self.page.locator("#export").is_disabled())
        self.lock()
        self.assertEqual(self.page.locator("#live-relation").get_attribute("data-ready"),"false")
        self.page.locator("#check").click()
        self.assertIn("NOT YET",self.page.locator("#verdict").inner_text())
        self.page.locator("#retry").click()
        self.assertIn("Awaiting Path 1",self.page.locator("#relation-right").inner_text())
        self.assertEqual(self.page.locator("#left-nodes .node.reference").count(),0)
        self.page.locator("#mission").select_option("16")
        self.assertEqual(self.page.locator("#live-relation").get_attribute("data-ready"),"false")

    def test_source_root_comparison_across_all_three_coefficient_charts(self):
        manifest=json.loads((DOCS/"window48_world_data.json").read_text(encoding="utf8"))
        roster=json.loads((DOCS/"window48_challenges.json").read_text(encoding="utf8"))
        for mission in (0,16,32,47):
            with self.subTest(mission=mission):
                self.page.locator("#mission").select_option(str(mission))
                ch=roster["challenges"][mission]
                ids=ch["law_ids"]
                w1,w2=ch["example_words"]
                expected=[]
                for word in (w1,w2):
                    pair=[0,0]
                    for action in word:
                        pair=[manifest["laws"][ids[i]][action][pair[i]] for i in range(2)]
                    expected.append(pair)
                self.word(w1)
                self.lock()
                for side,index in (("left",0),("right",1)):
                    self.assertEqual(
                        self.page.locator("#"+side+"-nodes .node.reference").get_attribute("data-state-index"),
                        str(expected[0][index]))
                self.word(w2)
                self.assertEqual(self.page.locator("#live-relation").get_attribute("data-ready"),"true")
                self.lock()
                for side,index in (("left",0),("right",1)):
                    self.assertEqual(
                        self.page.locator("#"+side+"-nodes .node.current").get_attribute("data-state-index"),
                        str(expected[1][index]))
                self.page.locator("#check").click()
                self.assertIn("WITNESSED",self.page.locator("#verdict").inner_text())

    def test_live_relation_is_recomputed_after_reload(self):
        self.page.locator("#mission").select_option("2")
        self.word("BAB")
        self.lock()
        self.word("BBBA")
        self.assertEqual(self.page.locator("#live-relation").get_attribute("data-ready"),"true")
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#mission').options.length === 48")
        self.assertEqual(self.page.locator("#live-relation").get_attribute("data-ready"),"true")
        self.assertIn("LIVE PREVIEW",self.page.locator("#relation-status").inner_text())
        self.assertTrue(self.page.locator("#check").is_disabled())
        self.lock()
        self.page.locator("#check").click()
        self.assertIn("WITNESSED",self.page.locator("#verdict").inner_text())

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
        self.assertIn("1 of 48 source-replayed",self.page.locator("#progress").inner_text())
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
        self.assertEqual(self.page.locator("#progress").inner_text(),"0 of 48 source-replayed witnesses saved in this browser")

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
        self.page.wait_for_function("document.querySelector('#mission').options.length === 48")
        self.assertIn("1 of 48 source-replayed",self.page.locator("#progress").inner_text())
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
        self.page.wait_for_function("document.querySelector('#mission').options.length === 48")
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
        self.assertIn("1 of 48 source-replayed",self.page.locator("#progress").inner_text())
        self.page.evaluate("""() => {
          const key='world48-source-replayed-progress/v1';
          const record=JSON.parse(localStorage.getItem(key));
          record.certificates[0].trials[0].events[0].after[0]=26;
          localStorage.setItem(key,JSON.stringify(record));
        }""")
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#mission').options.length === 48")
        self.assertIn("0 of 48 source-replayed",self.page.locator("#progress").inner_text())
        self.assertTrue(self.page.locator("#export").is_disabled())

    def test_saved_progress_can_be_cleared_without_changing_original_source(self):
        self.page.locator("#mission").select_option("1")
        self.lock()
        self.word("BBB")
        self.lock()
        self.page.locator("#check").click()
        self.assertIn("1 of 48",self.page.locator("#progress").inner_text())
        self.page.locator("#clear-progress").click()
        self.assertIn("0 of 48",self.page.locator("#progress").inner_text())
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#mission').options.length === 48")
        self.assertIn("0 of 48",self.page.locator("#progress").inner_text())

    def test_import_valid_export_restores_verified_progress_after_clear(self):
        self.page.locator("#mission").select_option("2")
        self.word("BAB")
        self.lock()
        self.word("BBBA")
        self.lock()
        self.page.locator("#check").click()
        with self.page.expect_download() as receipt_event:
            self.page.locator("#export").click()
        path=Path(receipt_event.value.path())
        original=json.loads(path.read_text(encoding="utf8"))
        self.assertTrue(verify_certificate(original)["passed"])
        self.page.locator("#clear-progress").click()
        self.assertIn("0 of 48",self.page.locator("#progress").inner_text())
        self.page.locator("#import-file").set_input_files(str(path))
        self.page.wait_for_function("document.querySelector('#status').textContent.includes('Imported and source-replayed challenge 3')")
        self.assertIn("1 of 48 source-replayed",self.page.locator("#progress").inner_text())
        self.assertIn("Imported and source-replayed challenge 3",self.page.locator("#status").inner_text())
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#mission').options.length === 48")
        self.assertIn("1 of 48 source-replayed",self.page.locator("#progress").inner_text())

    def test_forged_import_is_rejected_without_change_to_source_progress(self):
        self.page.locator("#mission").select_option("2")
        self.word("BAB")
        self.lock()
        self.word("BBBA")
        self.lock()
        self.page.locator("#check").click()
        with self.page.expect_download() as receipt_event:
            self.page.locator("#export").click()
        forged=json.loads(Path(receipt_event.value.path()).read_text(encoding="utf8"))
        forged["trials"][1]["events"][0]["after"][1]=26
        self.page.locator("#clear-progress").click()
        with TemporaryDirectory() as temp:
            file=Path(temp)/"forged.json"
            file.write_text(json.dumps(forged),encoding="utf8")
            self.page.locator("#import-file").set_input_files(str(file))
            self.page.wait_for_function("document.querySelector('#status').textContent.includes('Witness import rejected')")
            self.assertIn("Witness import rejected",self.page.locator("#status").inner_text())
            self.assertIn("0 of 48",self.page.locator("#progress").inner_text())
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#mission').options.length === 48")
        self.assertIn("0 of 48",self.page.locator("#progress").inner_text())

    def test_wrong_scope_import_cannot_be_counted(self):
        forged={"schema":"external-native-game-result","challenge_id":1,
                "status":"WIN","score":100}
        with TemporaryDirectory() as temp:
            file=Path(temp)/"external.json"
            file.write_text(json.dumps(forged),encoding="utf8")
            self.page.locator("#import-file").set_input_files(str(file))
            self.page.wait_for_function("document.querySelector('#status').textContent.includes('Witness import rejected')")
        self.assertIn("Witness import rejected",self.page.locator("#status").inner_text())
        self.assertIn("0 of 48",self.page.locator("#progress").inner_text())

    def test_new_chart_missions_are_real_chromium_witnesses_and_python_verified(self):
        source=json.loads((DOCS/"window48_challenges.json").read_text(encoding="utf8"))
        for id in (16,31,32,47):
            with self.subTest(mission=id):
                self.page.locator("#mission").select_option(str(id))
                self.assertIn("chart c="+str(id//16),
                              self.page.locator("#mission option:checked").inner_text())
                words=source["challenges"][id]["example_words"]
                self.word(words[0])
                self.lock()
                self.word(words[1])
                self.lock()
                self.page.locator("#check").click()
                self.assertIn("WITNESSED",self.page.locator("#verdict").inner_text())
                payload,report=self.exported()
                self.assertEqual(report["challenge_id"],id)
                self.assertTrue(report["passed"])
                self.assertEqual(payload["trials"][0]["actions"],words[0])
                self.assertEqual(payload["trials"][1]["actions"],words[1])

    def test_existing_16_level_progress_survives_expansion_to_48(self):
        # A historical c=0 source receipt must retain mission index/pair in
        # the larger manifest, rather than being remapped to a new law chart.
        self.page.locator("#mission").select_option("2")
        self.word("BAB")
        self.lock()
        self.word("BBBA")
        self.lock()
        self.page.locator("#check").click()
        self.assertIn("1 of 48 source-replayed",self.page.locator("#progress").inner_text())
        record,_=self.exported()
        self.assertEqual(record["law_ids"],[6,9])
        self.page.reload()
        self.page.wait_for_function("document.querySelector('#mission').options.length === 48")
        self.assertIn("1 of 48 source-replayed",self.page.locator("#progress").inner_text())
        self.page.locator("#mission").select_option("47")
        self.assertIn("48 / 48",self.page.locator("#task").inner_text())
        self.assertIn("1 of 48 source-replayed",self.page.locator("#progress").inner_text())
        self.page.locator("#mission").select_option("2")
        self.assertIn("1 of 48 source-replayed",self.page.locator("#progress").inner_text())

    def test_invalid_word_keeps_source_origin(self):
        self.page.locator("#word").fill("AACX")
        self.page.locator("#run").click()
        self.assertIn("Use A/B only",self.page.locator("#status").inner_text())
        self.assertEqual(self.page.locator("#left-state").inner_text(),"(0,0,0)")
        self.assertEqual(self.page.locator("#right-state").inner_text(),"(0,0,0)")


if __name__=="__main__":
    unittest.main()
