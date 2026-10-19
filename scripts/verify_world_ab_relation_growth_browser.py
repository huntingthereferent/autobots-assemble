"""Real Chromium evidence for source-relation constructed second physical surface.

Original W13 and 24x6 physical WORLD scripts must be byte identical to the
previously verified file. An independent Python native program and *separate*
closed-form two-collision analytic oracle check every browser output frame.
The original visual blueprint is used only by the independent comparator.
"""
from __future__ import annotations
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re

from network.tests.test_world_ab_relation_growth import independent_oracle,check_original_blueprint_after
from scripts.verify_world_ab_contact_browser import diff
from systems.workspace.world_ab_relation_growth import experiment
from systems.workspace.world_ab_contact_trial import initial

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"docs/world_ab_relation_growth.html"
BASE=ROOT/"docs/world_ab_contact_trial.html"
OUT_SCHEMA="world-ab-generated-second-face-independent-browser-witness/v1"

def run(folder):
    from playwright.sync_api import sync_playwright
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    src=PAGE.read_text(encoding="utf8")
    original=BASE.read_text(encoding="utf8")
    js=lambda x:re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",x,re.S)
    if js(src)[:-1]!=js(original):
        raise ValueError("earlier WORLD / native A/B scripts silently changed")
    if src.count('id="physical-world"')!=1 or src.count('id="ab-contact"')!=1 or src.count('id="relation-growth"')!=1:
        raise ValueError("new generator replaced previous WORLD referent")
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1250,"height":900})
            errors=[];page.on("pageerror",lambda ex:errors.append(str(ex)))
            page.goto(PAGE.resolve().as_uri(),wait_until="load",timeout=25000)
            page.wait_for_selector("#relation-growth")
            if page.evaluate("window.worldABGrowth.get()") is not None:
                raise ValueError("new physical structure already declared without contact")
            # Actual materialization has a source prerequisite.
            page.locator("#grow-construct").click()
            if page.evaluate("window.worldABGrowth.get()") is not None:
                raise ValueError("construction was possible without initial LOOK")
            page.locator("#ab-run").click()
            page.locator("#grow-construct").click()
            generated=page.evaluate("window.worldABGrowth.get()")
            if generated is None or generated["assembly"]["constructed"] is not True:
                raise ValueError("native observed wall relation did not construct receiver")
            if generated["assembly"]["surface"]["face_x"]!=9.5:
                raise ValueError("wrong face inferred from measured post-contact motion")
            if generated["second_motion"] is not None:
                raise ValueError("second motion was fabricated before explicit replay")
            page.locator("#grow-replay").click()
            actual=page.evaluate("window.worldABGrowth.get()")
            native=experiment()
            diff(actual,native)
            first=independent_oracle(actual)
            if (actual["observed_contacts"]!=["source-wall","relation-surface-1"] or
                actual["second_motion"]["final"]["x"]!=11.0 or
                first["second_contact_time"]<=first["first_contact_time"]):
                raise ValueError("new generated physical surface was not actually hit")
            for i in range(16):
                page.locator("#grow-next").click()
                if page.evaluate("window.worldABGrowth.frame()")!=i+1:
                    raise ValueError("next LOOK did not advance physical observation")
            page.screenshot(path=str(folder/"world_ab_relation_growth_second_contact.png"),full_page=True)
            page.locator("#grow-prev").click()
            if page.evaluate("window.worldABGrowth.frame()")!=15:
                raise ValueError("previous LOOK failed")
            (folder/"world_ab_relation_growth_generated.json").write_text(
                json.dumps(actual,indent=2,sort_keys=True)+"\n")
            # Re-run at half restitution; geometry and both impacts MUST move.
            page.locator("#ab-e").fill("0.5")
            page.locator("#ab-run").click()
            page.locator("#grow-construct").click()
            page.locator("#grow-replay").click()
            damped=page.evaluate("window.worldABGrowth.get()")
            diff(damped,experiment(initial(restitution=0.5)))
            independent_oracle(damped)
            if damped["assembly"]["surface"]["face_x"]==actual["assembly"]["surface"]["face_x"]:
                raise ValueError("construction ignored changed outgoing physics")
            # A block missing the source wall cannot magically build a new face.
            page.locator("#ab-y").fill("3.5")
            page.locator("#ab-vy").fill("0")
            page.locator("#ab-run").click()
            page.locator("#grow-construct").click()
            no_contact=page.evaluate("window.worldABGrowth.get()")
            if (no_contact["assembly"]["constructed"] is not False or
                no_contact["second_motion"] is not None):
                raise ValueError("source-free new structure fabricated")
            # Total dissipation prohibits rebound-based extension.
            page.locator("#ab-y").fill("1.35")
            page.locator("#ab-vy").fill("0.12")
            page.locator("#ab-e").fill("0")
            page.locator("#ab-run").click()
            page.locator("#grow-construct").click()
            zero=page.evaluate("window.worldABGrowth.get()")
            if zero["assembly"]["reason"]!="NO_OUTGOING_REBOUND":
                raise ValueError("stopped block somehow generated outgoing structure")
            page.locator("#grow-reset").click()
            if page.evaluate("window.worldABGrowth.get()") is not None:
                raise ValueError("composite physical source was not cleared by reset")
            original_world=page.evaluate("window.physicalWorld.receipt()")
            if original_world["layout"]["dimensions"]["area_cells"]!=144:
                raise ValueError("composite trial changed original 144-cell WORLD")
            if errors:raise ValueError("real WORLD Chromium JS error: "+repr(errors))
        finally:browser.close()
    comparison=check_original_blueprint_after(actual)
    if (not comparison["new_collision_face_emerged"] or
        not comparison["repeated_collisions_observed"] or
        comparison["full_original_blueprint_generated"]):
        raise ValueError("new collision face falsely promoted to complete original drawing")
    receipt={"schema":OUT_SCHEMA,"inherited_original_WORLD_scripts_unchanged":True,
        "native_physics_and_browser_receipts_match":True,
        "independent_event_time_oracle_passed":True,
        "source_wall_preserved":True,
        "assembled_new_face_from_observation":True,
        "new_surface_acted_on_subsequent_moving_block":True,
        "two_actual_collision_events":2,
        "original_W13_physical_cells_preserved":144,
        "original_visual_blueprint_comparison":comparison,
        "zero_rebound_and_no_contact_construction_refused":True,
        "changed_restitution_changed_constructed_geometry":True,
        "full_physical_blueprint_reproduced":False,
        "actual_Earth_material_physics_verified":False,
        "NIH_submission":False,
        "source_generated_evidence_sha256":sha256(
            json.dumps(actual,sort_keys=True,separators=(",",":")).encode()).hexdigest()}
    (folder/"world_ab_relation_growth_independent_witness.json").write_text(
        json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
       "schema":OUT_SCHEMA,"new_face_x":actual["assembly"]["surface"]["face_x"],
       "contacts":actual["observed_contacts"],
       "first_and_second_times":first,
       "native_browser_and_independent_oracle":True,
       "missing_original_blueprint_shapes":comparison["missing_original_shapes"],
       "original_blueprint_equal":False},sort_keys=True))
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output-dir",required=True)
    x=p.parse_args();run(x.output_dir)
