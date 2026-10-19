"""Trial 09: independent real-Chromium 35-case source/physics receipt comparison."""
import argparse,json
from pathlib import Path
from hashlib import sha256
from systems.workspace.world_ab_two_contact_stress import run
from network.tests.test_world_ab_two_contact_stress import check
from network.tests.test_world_ab_junction_continuous import source_equivalent

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"docs/world_ab_two_contact_stress.html"

def verify(folder):
    from playwright.sync_api import sync_playwright
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    native=run()
    if not check(native):raise ValueError("independent Python source and physics oracle failed")
    if "world_ab_junction_geometry.js" not in PAGE.read_text():raise ValueError("original source geometry script missing")
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1210,"height":850})
            page.on("pageerror",lambda err:errors.append(str(err)))
            page.goto(PAGE.resolve().as_uri(),wait_until="load")
            if page.evaluate("window.worldTrial09.receipt()") is not None:
                raise ValueError("browser preset synthetic outcomes")
            page.locator("#run").click()
            actual=page.evaluate("window.worldTrial09.receipt()")
            if actual is None:raise ValueError("browser failed to calculate 35 controls: "+page.locator("#state").inner_text()+"; errors="+repr(errors))
            subset={k:native[k] for k in (
                "schema","original_source_geometry","incoming_angle_grid",
                "surface_rotation_grid","speed","controlled_contact_lead",
                "cases","counts","original_surface_modified",
                "rotated_faces_are_original_source",
                "general_two_contact_physics_proven","frictional_manifold_solved")}
            if not source_equivalent(actual,subset):
                # Pinpoint first diverging case for direct debugging, never a blind pass.
                if actual.get("counts")!=subset["counts"]:
                    raise ValueError("native/Chromium classification differs: "+repr((actual.get("counts"),subset["counts"])))
                for i,(x,y) in enumerate(zip(actual.get("cases",[]),subset["cases"])):
                    if not source_equivalent(x,y):
                        raise ValueError(f"native/Chromium differs on case {i}: "+repr((x["status"],y["status"],x.get("candidate"),y.get("candidate"))))
                raise ValueError("original source or bounded claim differs in browser")
            for i in range(35):
                page.locator("#case").select_option(str(i))
                if page.evaluate("window.worldTrial09.selected()")!=i:raise ValueError("browser case selector drifted")
                page.locator("#next").click()
                if page.evaluate("window.worldTrial09.cursor()")!=1:raise ValueError("browser time cursor drifted")
            page.locator("#case").select_option("17")
            page.screenshot(path=str(folder/"world_trial09_chromium.png"),full_page=True)
            (folder/"world_trial09_browser.json").write_text(json.dumps(actual,sort_keys=True,indent=2)+"\n")
            page.locator("#reset").click()
            if page.evaluate("window.worldTrial09.receipt()") is not None:raise ValueError("reset retained source experiment")
            if errors:raise ValueError("actual Chromium errors: "+repr(errors))
        finally:browser.close()
    (folder/"world_trial09_native.json").write_text(json.dumps(native,indent=2,sort_keys=True)+"\n")
    witness={"schema":"world-ab-two-contact-stress-browser-witness/v1",
             "native_and_browser_full_35_case_receipts_agree":True,
             "total_cases":len(native["cases"]),"counts":native["counts"],
             "original_source_modified":False,
             "rotated_surfaces_original_source":False,
             "frictional_multi_contact_solved":False,
             "full_original_blueprint_generated":False,
             "source_sha256":sha256(json.dumps(native,sort_keys=True,separators=(",",":")).encode()).hexdigest()}
    (folder/"world_trial09_verification.json").write_text(json.dumps(witness,sort_keys=True,indent=2)+"\n")
    print(json.dumps(witness,sort_keys=True))
    return witness

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True)
    verify(parser.parse_args().output_dir)
