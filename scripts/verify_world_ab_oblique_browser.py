"""Live Chromium first-contact A/B obliquity experiment with independent oracle.

Controls an isolated variation of the existing WORLD's original source wall
and square. Compares browser-generated real contact against native authored
physics and a separate analytical body-support/impulse oracle. Only the
first event and ballistic next-look are observed; no second collision or
real material properties are falsely authenticated.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from hashlib import sha256
from playwright.sync_api import sync_playwright
from systems.workspace.world_ab_oblique_impact import experiment
from systems.workspace.world_ab_contact_trial import initial
from network.tests.test_world_ab_oblique_impact import verify_impact
from scripts.verify_world_ab_contact_browser import diff

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"docs/world_ab_iterated_surfaces.html"
PAGE=ROOT/"docs/world_ab_oblique_rotation.html"

def run(directory):
    output=Path(directory);output.mkdir(parents=True,exist_ok=True)
    old=BASE.read_text(encoding="utf8")
    new=PAGE.read_text(encoding="utf8")
    js=lambda text:re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",text,re.S)
    if js(new)[:-1]!=js(old) or new.count('id="physical-world"')!=1 or new.count('id="oblique-experiment"')!=1:
        raise ValueError("earlier WORLD/physics scripts were replaced instead of extended")
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1250,"height":990})
            errors=[];page.on("pageerror",lambda err:errors.append(str(err)))
            page.goto(PAGE.resolve().as_uri(),wait_until="load",timeout=25000)
            page.wait_for_selector("#oblique-experiment")
            if page.evaluate("window.worldABOblique.get()") is not None:
                raise ValueError("first-impact result appeared before actual browser simulation")
            if page.evaluate("window.physicalWorld.receipt().layout.dimensions.area_cells")!=144:
                raise ValueError("the existing 24x6 source-owned WORLD was removed")
            page.locator("#rot-run").click()
            result=page.evaluate("window.worldABOblique.get()")
            expected=experiment(initial(restitution=.7),angle=20)
            diff(result,expected)
            for key in ("A_original_vertical","B_oblique"):
                assert verify_impact(result[key])
            if (result["A_original_vertical"]["angular_velocity_after"]!=0 or
                result["B_oblique"]["angular_velocity_after"]==0 or
                result["A_original_vertical"]["velocity_after"]==
                   result["B_oblique"]["velocity_after"] or
                result["B_oblique"]["candidate_receiver"]["surface_built"] is not False):
                raise ValueError("source-angle effect was not independently observed")
            # The same wall geometry rotated back to vertical must return the
            # original zero-spin result and receiver orientation.
            page.locator("#rot-angle").fill("0")
            page.locator("#rot-run").click()
            vertical=page.evaluate("window.worldABOblique.get()")
            diff(vertical,experiment(initial(restitution=.7),angle=0))
            assert verify_impact(vertical["B_oblique"])
            if vertical["B_oblique"]["angular_velocity_after"]!=0:
                raise ValueError("original x-normal impact incorrectly generated spin")
            # Alter physical restitution: browser result must change in the
            # native analytical model, and energy cannot exceed source input.
            page.locator("#rot-angle").fill("20")
            page.locator("#rot-e").fill("1")
            page.locator("#rot-run").click()
            elastic=page.evaluate("window.worldABOblique.get()")
            diff(elastic,experiment(initial(restitution=1),angle=20))
            assert verify_impact(elastic["B_oblique"])
            if elastic["B_oblique"]["velocity_after"]==result["B_oblique"]["velocity_after"]:
                raise ValueError("angular impact ignored energy restitution change")
            page.locator("#rot-e").fill("1.2")
            page.locator("#rot-run").click()
            if page.evaluate("window.worldABOblique.get()") is not None:
                raise ValueError("invalid Earth-physics inputs accepted")
            page.locator("#rot-reset").click()
            if page.evaluate("window.worldABOblique.get()") is not None:
                raise ValueError("physics reset did not clear last observation")
            page.locator("#rot-run").click()
            restored=page.evaluate("window.worldABOblique.get()")
            diff(restored,expected)
            page.screenshot(path=str(output/"world_ab_oblique_browser.png"),full_page=True)
            (output/"world_ab_oblique_browser.json").write_text(json.dumps(restored,sort_keys=True,indent=2)+"\n")
            if errors:raise ValueError("Chromium error: "+repr(errors))
        finally:browser.close()
    witness={"schema":"world-ab-oblique-native-vs-chromium-independent-witness/v1",
        "original_144_cell_world_retained":True,
        "original_static_iterated_wall_history_unchanged":True,
        "original_vertical_wall_angular_velocity":result["A_original_vertical"]["angular_velocity_after"],
        "oblique_wall_angular_velocity":result["B_oblique"]["angular_velocity_after"],
        "original_outgoing_velocity":result["A_original_vertical"]["velocity_after"],
        "oblique_outgoing_velocity":result["B_oblique"]["velocity_after"],
        "first_contact_source_supported":True,
        "candidate_follow_on_surface_proposed":True,
        "candidate_follow_on_surface_physically_constructed":False,
        "receiver_second_collision_witnessed":False,
        "continuous_rotational_contact_after_first_impact_witnessed":False,
        "independent_analytic_impulse_and_energy_verified":True,
        "native_and_browser_records_match":True,
        "real_Earth_physics_validated":False,
        "guide_funnel_diverter_spiral_generated":False,
        "NIH_submission":False,
        "source_receipt_sha256":sha256(json.dumps(restored,sort_keys=True,separators=(",",":")).encode()).hexdigest()}
    (output/"world_ab_oblique_witness.json").write_text(json.dumps(witness,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"schema":witness["schema"],
         "A_spin":witness["original_vertical_wall_angular_velocity"],
         "B_spin":witness["oblique_wall_angular_velocity"],
         "A_outgoing":witness["original_outgoing_velocity"],
         "B_outgoing":witness["oblique_outgoing_velocity"],
         "browser_native_independent_oracle":True,
         "full_original_blueprint":False},sort_keys=True))
    return witness

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output-dir",required=True)
    a=p.parse_args();run(a.output_dir)
