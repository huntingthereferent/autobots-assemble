"""Fresh Chromium witness for four native oblique/friction/rotational trials.

Browser independently computes all impulses and positions from interactive
experiment controls. Its receipts are checked against native Python and a
separate analytical two-event rigid-body oracle. Original W13/Trial03 script
spans are compared unchanged. No original diagram target enters generation.
"""
from __future__ import annotations
from hashlib import sha256
import argparse,json,re
from pathlib import Path
from systems.workspace.world_ab_oblique_rotation import run
from network.tests.test_world_ab_oblique_rotation import independently_verify_case
from scripts.verify_world_ab_contact_browser import diff

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"docs/world_ab_iterated_surfaces.html"
PAGE=ROOT/"docs/world_ab_oblique_disc_factorial.html"
SCHEMA="world-ab-oblique-disc-four-branch-browser-witness/v1"

def verify(folder):
    from playwright.sync_api import sync_playwright
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    original=BASE.read_text()
    derived=PAGE.read_text()
    scripts=lambda txt:re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",txt,re.S)
    if scripts(derived)[:-1]!=scripts(original):
        raise ValueError("prior WORLD physics or W13 movement scripts silently rewritten")
    if (derived.count('id="physical-world"')!=1 or
        derived.count('id="ab-iteration"')!=1 or
        derived.count('id="disc-experiment"')!=1):
        raise ValueError("new experiment replaced instead of extending original WORLD")
    native=run()
    for branch in native["branches"]:independently_verify_case(branch)
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1320,"height":1050})
            errors=[];page.on("pageerror",lambda error:errors.append(str(error)))
            page.goto(PAGE.resolve().as_uri(),wait_until="load",timeout=28000)
            page.wait_for_selector("#disc-experiment")
            if page.evaluate("window.worldABObliqueDisc.receipt()") is not None:
                raise ValueError("browser invented physics output before running")
            if page.evaluate("window.physicalWorld.receipt().layout.dimensions.area_cells")!=144:
                raise ValueError("original 144-cell physical WORLD was replaced")
            page.locator("#disc-run").click()
            browser_result=page.evaluate("window.worldABObliqueDisc.receipt()")
            if browser_result is None:raise ValueError("actual browser physics failed to start")
            diff(browser_result,native)
            for case in browser_result["branches"]:independently_verify_case(case)
            if browser_result["branches"][0]["nonzero_spin_generated"]:
                raise ValueError("frictionless vertical source spuriously spun")
            if not browser_result["branches"][3]["nonzero_spin_generated"]:
                raise ValueError("angled frictional source failed to generate rotation")
            for idx in range(4):
                page.locator("#disc-branch").select_option(str(idx))
                if page.evaluate("window.worldABObliqueDisc.cursor()")!=0:
                    raise ValueError("branch change retained future observation")
                for step in range(33):
                    page.locator("#disc-next").click()
                if page.evaluate("window.worldABObliqueDisc.cursor()")!=33:
                    raise ValueError("live next-look frames incomplete")
                visible=page.locator("#disc-readout").inner_text()
                expected=browser_result["branches"][idx]["constructed_receiver"]["normal_angle_degrees"]
                if str(expected) not in visible:
                    raise ValueError("source-derived receiver normal not shown in physical view")
                page.locator("#disc-prev").click()
                if page.evaluate("window.worldABObliqueDisc.cursor()")!=32:
                    raise ValueError("previous physical look did not work")
                page.locator("#disc-next").click()
            page.locator("#disc-branch").select_option("3")
            page.screenshot(path=str(folder/"world_ab_oblique_disc_browser.png"),full_page=True)
            (folder/"world_ab_oblique_disc_browser.json").write_text(
                json.dumps(browser_result,sort_keys=True,indent=2)+"\n")
            # The existing 144-cell physical-world and trial03 remain callable
            if not page.evaluate("typeof window.worldABIteration.run==='function'"):
                raise ValueError("original Trial03 construction was removed")
            page.locator("#disc-reset").click()
            if page.evaluate("window.worldABObliqueDisc.receipt()") is not None:
                raise ValueError("reset did not clear physical observations")
            if errors:raise ValueError("Chromium console page errors: "+repr(errors))
        finally:browser.close()
    witness={"schema":SCHEMA,"original_W13_world_preserved":True,
       "original_Trial03_script_preserved":True,
       "native_browser_four_branch_receipts_agree":True,
       "independent_two_impact_oracle_passed":True,
       "real_chromium_frames_each_case":34,
       "experimental_branches":4,
       "physical_world_virtual_cells":144,
       "angle_and_friction_tested_independently":True,
       "generated_receiver_witnessed_but_not_original_shapes":True,
       "original_visual_blueprint_equivalence":False,
       "full_Earth_physics_verified":False,
       "original_sketch_used_as_generator_input":False,
       "source_native_sha256":sha256(json.dumps(native,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
       "NIH_submission":False}
    (folder/"world_ab_oblique_disc_witness.json").write_text(
        json.dumps(witness,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"schema":SCHEMA,
        "branch_source_angles":[x["source_angle_degrees"] for x in native["branches"]],
        "receiver_face_angles":[x["constructed_receiver"]["normal_angle_degrees"] for x in native["branches"]],
        "spin_generated":[x["nonzero_spin_generated"] for x in native["branches"]],
        "native_and_browser_agree":True,
        "original_blueprint_reproduced":False},sort_keys=True))
    return witness

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output-dir",required=True)
    a=p.parse_args();verify(a.output_dir)
