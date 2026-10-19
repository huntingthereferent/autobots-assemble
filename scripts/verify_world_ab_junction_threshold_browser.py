"""Independent real-Chromium reconstruction of the Trial 07 arrival tie."""
from pathlib import Path
import argparse,json
from hashlib import sha256
from systems.workspace.world_ab_junction_threshold import run
from network.tests.test_world_ab_junction_threshold import verify
from network.tests.test_world_ab_junction_continuous import source_equivalent

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"docs/world_ab_junction_threshold.html"

def replay(output_dir):
    from playwright.sync_api import sync_playwright
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    native=run();verify(native)
    if "world_ab_junction_geometry.js" not in PAGE.read_text():
        raise ValueError("browser not linked to original source")
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1180,"height":850})
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(PAGE.resolve().as_uri(),wait_until="load")
            if page.evaluate("window.worldTrial07.receipt()") is not None:
                raise ValueError("page prefilled an unsupported contact")
            page.locator("#run").click()
            actual=page.evaluate("window.worldTrial07.receipt()")
            if not actual or actual.get("simultaneous_contact_solver") is not False:
                raise ValueError("browser falsely solved multiple-contact physics")
            expected={k:native[k] for k in ("schema","source_geometry","junction_contact")}
            if not source_equivalent({k:actual[k] for k in expected},expected):
                raise ValueError("Chromium measured source or crossing differently from independently checked Python")
            if "UNRESOLVED" not in page.locator("#status").inner_text():
                raise ValueError("unsafe physical completion claim")
            page.screenshot(path=str(output_dir/"world_trial07_chromium.png"),full_page=True)
            (output_dir/"world_trial07_browser.json").write_text(json.dumps(actual,indent=2,sort_keys=True)+"\n")
            page.locator("#reset").click()
            if page.evaluate("window.worldTrial07.receipt()") is not None:
                raise ValueError("reset retained fabricated observation")
            if errors:raise ValueError("Chromium errors: "+repr(errors))
        finally:browser.close()
    (output_dir/"world_trial07_native.json").write_text(json.dumps(native,indent=2,sort_keys=True)+"\n")
    result={"schema":"world-ab-junction-tie-browser-witness/v1",
     "two_original_source_faces_agree":True,"simultaneous_arrival_detected":True,
     "full_motion_tie_status":native["probes"][4]["status"],
     "surface_order_independent":all(x["surface_order_independent"] for x in native["probes"]),
     "multi_contact_impulse_solved":False,"new_material_assembly":False,
     "source_sha256":sha256(json.dumps(native,sort_keys=True,separators=(",",":")).encode()).hexdigest()}
    (output_dir/"world_trial07_verification.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True)
    replay(parser.parse_args().output_dir)
