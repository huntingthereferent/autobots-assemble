"""Real Chromium physics-receipt replay: independently derive the Trial 08 candidate."""
import argparse,json
from pathlib import Path
from hashlib import sha256
from systems.workspace.world_ab_two_contact_candidate import run
from network.tests.test_world_ab_two_contact_candidate import verify
from network.tests.test_world_ab_junction_continuous import source_equivalent

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"docs/world_ab_two_contact_candidate.html"
OUT="world-ab-two-contact-candidate-browser-witness/v1"

def replay(folder):
    from playwright.sync_api import sync_playwright
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    native=run()
    verify(native)
    if "world_ab_junction_geometry.js" not in PAGE.read_text():
        raise ValueError("browser cannot reconstruct original source geometry")
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1200,"height":880})
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(PAGE.resolve().as_uri(),wait_until="load")
            if page.evaluate("window.worldTrial08.receipt()") is not None:
                raise ValueError("browser fabricated physics before running")
            page.locator("#run").click()
            actual=page.evaluate("window.worldTrial08.receipt()")
            if actual is None:raise ValueError("browser candidate was rejected")
            expected={key:native[key] for key in ("schema","geometry")}
            expected["candidate"]={k:v for k,v in native["candidate"].items() if k!="original_stop"}
            if not source_equivalent(expected,actual):
                raise ValueError("browser and independent Python source/candidate evidence differ")
            for i in range(30):
                page.locator("#next").click()
            if page.evaluate("window.worldTrial08.cursor()")!=30:
                raise ValueError("candidate did not show complete finite motion")
            if "frictional contact remains unresolved" not in page.locator("#status").inner_text():
                raise ValueError("original physics misleadingly reported solved")
            page.locator("#prev").click()
            if page.evaluate("window.worldTrial08.cursor()")!=29:
                raise ValueError("previous observation did not move")
            page.screenshot(path=str(folder/"world_trial08_chromium.png"),full_page=True)
            (folder/"world_trial08_browser.json").write_text(json.dumps(actual,sort_keys=True,indent=2)+"\n")
            page.locator("#reset").click()
            if page.evaluate("window.worldTrial08.receipt()") is not None:
                raise ValueError("reset left unsupported observation")
            if errors:raise ValueError("real Chromium errors: "+repr(errors))
        finally:browser.close()
    (folder/"world_trial08_native.json").write_text(json.dumps(native,sort_keys=True,indent=2)+"\n")
    result={"schema":OUT,
            "original_source_geometry_and_native_candidate_agree":True,
            "finite_31_frame_movement_verified":True,
            "independent_two_normal_momentum_and_energy":True,
            "original_trial06_two_face_stop":native["baseline_trial06_status"],
            "original_friction_retained_as_comparison":native["original_trial06_friction"],
            "new_candidate_friction":native["candidate_friction"],
            "real_physical_manifold_solved":False,
            "full_blueprint_generated":False,
            "source_sha256":sha256(json.dumps(native,sort_keys=True,separators=(",",":")).encode()).hexdigest()}
    (folder/"world_trial08_verification.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True)
    replay(parser.parse_args().output_dir)
