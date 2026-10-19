"""Native/Chromium independent witness for iterative source-derived WORLD geometry.

Original W13 24x6 physical world and previous trial scripts are preserved.
This tests live browser motion (not a prepainted reference), independent
contact/restitution chronology, insufficient-clearance rejections, and
temporal nonretroactivity of newly constructed surfaces.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from hashlib import sha256
from playwright.sync_api import sync_playwright

from systems.workspace.world_ab_iterated_surfaces import run
from systems.workspace.world_ab_contact_trial import initial
from network.tests.test_world_ab_iterated_surfaces import independent_trace
from scripts.verify_world_ab_contact_browser import diff

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"docs/world_ab_relation_growth.html"
PAGE=ROOT/"docs/world_ab_iterated_surfaces.html"

def verify(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    old=BASE.read_text()
    new=PAGE.read_text()
    scripts=lambda text:re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",text,re.S)
    if scripts(new)[:-1]!=scripts(old) or new.count('id="physical-world"')!=1 or new.count('id="ab-iteration"')!=1:
        raise ValueError("physical WORLD or previous experiment code was replaced")
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1300,"height":940})
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(PAGE.resolve().as_uri(),wait_until="load",timeout=30000)
            page.wait_for_selector("#ab-iteration")
            if page.evaluate("window.worldABIteration.get()") is not None:
                raise ValueError("constructed surfaces appeared before any physical observation")
            page.locator("#iter-run").click()
            if page.evaluate("window.worldABIteration.get()") is not None:
                raise ValueError("browser constructed without source trial")
            page.locator("#ab-run").click()
            page.locator("#iter-run").click()
            result=page.evaluate("window.worldABIteration.get()")
            if result is None:raise ValueError("physical iteration never ran in Chromium")
            independent_trace(result)
            native=run()
            diff(result,native)
            if (result["generated_surface_count"]!=3 or
                len(result["events"])!=13 or
                not any(p["reason"]=="FACES_TOO_CLOSE_FOR_BLOCK" for p in result["construction_attempts"] if not p["accepted"])):
                raise ValueError("growth/saturation not witnessed on original virtual floor")
            # Newly constructed faces are not visible in the past.
            page.locator("#iter-next").click()
            if page.evaluate("window.worldABIteration.cursor()")!=1:
                raise ValueError("next-look control did not advance physical event")
            while page.evaluate("window.worldABIteration.cursor()")<4:
                page.locator("#iter-next").click()
            if page.evaluate("window.worldABIteration.cursor()")!=4:
                raise ValueError("third derived surface did not enter time-indexed observation")
            while page.evaluate("window.worldABIteration.cursor()")<len(result["motions"])-1:
                page.locator("#iter-next").click()
            page.screenshot(path=str(output/"world_ab_iterated_browser.png"),full_page=True)
            (output/"world_ab_iterated_browser_receipt.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
            # Change restitution: derived geometry must change, without
            # introducing unobserved original blueprint shapes.
            page.locator("#ab-e").fill("0.5")
            page.locator("#ab-run").click()
            page.locator("#iter-run").click()
            reduced=page.evaluate("window.worldABIteration.get()")
            independent_trace(reduced)
            diff(reduced,run(initial(restitution=.5)))
            if reduced["surfaces"][1]["face_x"]==result["surfaces"][1]["face_x"]:
                raise ValueError("derived geometry ignores outgoing physical velocity")
            # No contact and fully absorbed normal motion both prohibit growth.
            page.locator("#ab-y").fill("3.5")
            page.locator("#ab-vy").fill("0")
            page.locator("#ab-run").click()
            page.locator("#iter-run").click()
            missed=page.evaluate("window.worldABIteration.get()")
            diff(missed,run(initial(y=3.5,vy=0,restitution=.5)))
            if missed["generated_surface_count"]:
                raise ValueError("constructed without source contact")
            page.locator("#ab-y").fill("1.35")
            page.locator("#ab-vy").fill("0.12")
            page.locator("#ab-e").fill("0")
            page.locator("#ab-run").click()
            page.locator("#iter-run").click()
            absorbed=page.evaluate("window.worldABIteration.get()")
            diff(absorbed,run(initial(restitution=0)))
            if absorbed["generated_surface_count"]!=0:
                raise ValueError("fabricated new face from stopped source block")
            page.locator("#iter-reset").click()
            if page.evaluate("window.worldABIteration.get()") is not None:
                raise ValueError("physical reset failed")
            source=page.evaluate("window.physicalWorld.receipt()")
            if source["layout"]["dimensions"]["area_cells"]!=144:
                raise ValueError("original WORLD geometry no longer intact")
            if errors:raise ValueError("browser errors: "+repr(errors))
        finally:browser.close()
    receipt={"schema":"world-ab-iterated-original-physical-world-browser-witness/v1",
       "original_WORLD_scripting_preserved":True,
       "original_144_cell_geometry_preserved":True,
       "original_wall_first_hit_preserved":True,
       "independent_source_contact_chronology_passed":True,
       "browser_native_full_receipts_match":True,
       "collision_events":len(result["events"]),
       "generated_surface_count":result["generated_surface_count"],
       "accepted_faces":[s["face_x"] for s in result["surfaces"][1:]],
       "rejected_proposals":sum(not p["accepted"] for p in result["construction_attempts"]),
       "zero_rebound_or_no_contact_generates_no_geometry":True,
       "unknown_actual_material_physics":True,
       "all_generated_faces_parallel":True,
       "complex_original_blueprint_reproduced":False,
       "phase2_NIH_submission":False,
       "original_physics_model_scope":result["physics"],
       "generated_source_sha256":sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()}
    (output/"world_ab_iterated_browser_witness.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:receipt[k] for k in ("schema","collision_events","generated_surface_count",
           "accepted_faces","rejected_proposals","browser_native_full_receipts_match",
           "complex_original_blueprint_reproduced")},sort_keys=True))
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output-dir",required=True)
    args=p.parse_args();verify(args.output_dir)
