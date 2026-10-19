"""Real Chromium and separately recomputed native/independent WORLD Trial06 witness."""
from __future__ import annotations
import argparse,json
from hashlib import sha256
from pathlib import Path
from systems.workspace.world_ab_junction_continuous import run
from network.tests.test_world_ab_junction_continuous import check
from scripts.verify_world_ab_contact_browser import diff

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"docs/world_ab_junction_continuous.html"
BASE=ROOT/"docs/world_ab_connected_routing.html"
OUT="world-ab-connected-continuous-browser-witness/v1"

def verify(folder):
    from playwright.sync_api import sync_playwright
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    source=PAGE.read_text()
    if (not BASE.is_file() or
        'href="world_ab_connected_routing.html"' not in source or
        'world_ab_junction_geometry.js' not in source or
        'world_ab_junction_physics.js' not in source):
        raise ValueError("original WORLD source chain or executable client files absent")
    native=run()
    if not check(native):
        raise ValueError("independent native physical constraint witness refused")
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1200,"height":890})
            page.on("pageerror",lambda err:errors.append(str(err)))
            page.goto(PAGE.resolve().as_uri(),wait_until="load",timeout=24000)
            page.wait_for_selector("#run")
            if page.evaluate("window.worldABContinuous.receipt()") is not None:
                raise ValueError("browser fabricated measured motion before running")
            page.locator("#run").click()
            actual=page.evaluate("window.worldABContinuous.receipt()")
            if actual is None:
                raise ValueError("real browser did not compute finite-contact paths")
            diff(actual,native)
            check(actual)
            for i in range(10):
                page.locator("#probe").select_option(str(i))
                if page.evaluate("window.worldABContinuous.cursor()")!=0:
                    raise ValueError("time did not reset when selecting new probe")
                for _ in range(30):page.locator("#next").click()
                if page.evaluate("window.worldABContinuous.cursor()")!=30:
                    raise ValueError("next look did not preserve 31-frame horizon")
                label=f"probe y={float(actual['probe_levels'][i]):.9g}"
                if label not in page.locator("#status").inner_text():
                    raise ValueError("physical stage displays incorrect source probe")
                page.locator("#prev").click()
                if page.evaluate("window.worldABContinuous.cursor()")!=29:
                    raise ValueError("previous look did not move")
            page.locator("#probe").select_option("1")
            page.screenshot(path=str(folder/"world_ab_junction_browser.png"),full_page=True)
            (folder/"world_ab_junction_browser.json").write_text(
                json.dumps(actual,sort_keys=True,indent=2)+"\n")
            page.locator("#reset").click()
            if page.evaluate("window.worldABContinuous.receipt()") is not None:
                raise ValueError("reset left derived physical outcome frozen")
            if errors:
                raise ValueError("actual Chromium page errors: "+repr(errors))
        finally:
            browser.close()
    result={
        "schema":OUT,
        "native_and_client_full_receipts_agree":True,
        "original_trial05_source_geometry_unchanged":True,
        "independently_reconstructed_finite_capsule_and_impulses":True,
        "original_probe_cases":7,
        "junction_adversarial_probes":3,
        "measured_connected_full_horizon_cases":native["completed_cases"],
        "baseline_world_edge_cases":sum(x["status"]=="world-edge-reached-no-boundary-response"
                                         for x in native["baseline_finite_capsule"]),
        "connected_unresolved_cases":native["unresolved_cases"],
        "simultaneous_multicontact_physics_verified":False,
        "finite_endpoint_contact_included":True,
        "original_blueprint_shapes_generated":False,
        "material_earth_scale_verified":False,
        "source_sha256":sha256(json.dumps(native,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    }
    (folder/"world_ab_junction_witness.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in (
        "schema","native_and_client_full_receipts_agree",
        "measured_connected_full_horizon_cases","baseline_world_edge_cases",
        "connected_unresolved_cases","original_blueprint_shapes_generated")},sort_keys=True))
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True)
    a=parser.parse_args()
    verify(a.output_dir)
