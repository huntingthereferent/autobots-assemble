"""Real Chromium source-fidelity and independent routing witness for Trial 05.

The smaller standalone viewer links to the original physical WORLD and
reconstructs Trial04B's observed receiver geometry using the same declared
source parameters. It does not run a continuous multi-body/multi-contact engine
and does not prove real-world source-material assembly.
"""
from __future__ import annotations
from hashlib import sha256
import argparse,json
from pathlib import Path
from systems.workspace.world_ab_connected_routing import run
from network.tests.test_world_ab_connected_routing import verify_source_geometry,independently_verify_route
from scripts.verify_world_ab_contact_browser import diff

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"docs/world_ab_connected_routing.html"
SOURCE_PAGE=ROOT/"docs/world_ab_oblique_disc_factorial.html"
OUTPUT_SCHEMA="world-ab-connected-crossrun-receiver-browser-witness/v1"

def verify(folder):
    from playwright.sync_api import sync_playwright
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    text=PAGE.read_text()
    if (not SOURCE_PAGE.exists() or
        'href="world_ab_oblique_disc_factorial.html"' not in text or
        text.count('id="connected-routing"')!=0):
        # The standalone page must link to the original WORLD, not
        # impersonate the full physical-world runtime.
        raise ValueError("source-owned original WORLD link missing")
    expected=run()
    if not verify_source_geometry(expected["geometry"]) or not independently_verify_route(expected["geometry"],expected):
        raise ValueError("native route lacks independent evidence")
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1150,"height":900})
            errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(PAGE.resolve().as_uri(),wait_until="load")
            page.wait_for_selector("#run")
            if page.evaluate("window.worldABConnectedRouting.receipt()") is not None:
                raise ValueError("playable viewer invented source history before running")
            page.locator("#run").click()
            actual=page.evaluate("window.worldABConnectedRouting.receipt()")
            if actual is None:raise ValueError("source-generated branch outcomes not available in browser")
            diff(actual,expected)
            verify_source_geometry(actual["geometry"])
            independently_verify_route(actual["geometry"],actual)
            for index in range(len(actual["probe_y_levels"])):
                page.locator("#choice").select_option(str(index))
                visible=page.locator("#status").inner_text()
                b=actual["assembled_two_faces"][index]
                if (str(actual["probe_y_levels"][index]) not in visible or
                    (b["source_first_contact"] or "no hit") not in visible):
                    raise ValueError("browser probe selection displayed wrong source result")
            page.locator("#choice").select_option("1")
            page.screenshot(path=str(folder/"world_ab_connected_browser.png"),full_page=True)
            (folder/"world_ab_connected_browser.json").write_text(
                json.dumps(actual,indent=2,sort_keys=True)+"\n")
            page.locator("#reset").click()
            if page.evaluate("window.worldABConnectedRouting.receipt()") is not None:
                raise ValueError("reset retained observed path evidence")
            if errors:raise ValueError("browser error in source reconstruction "+str(errors))
        finally:browser.close()
    evidence={
      "schema":OUTPUT_SCHEMA,
      "original_world_playable_source_preserved":True,
      "standalone_physical_companion_linked_to_original_WORLD":True,
      "source_04B_original_branches_preserved":True,
      "native_browser_complete_receipts_match":True,
      "independent_finite_source_intersection_witness":True,
      "independent_swept_disc_first_contact_oracle_passed":True,
      "two_distinct_first_contact_faces_observed":True,
      "probe_trajectory_levels_tested":actual["probe_y_levels"],
      "route_changed_probe_levels":actual["route_changed_probe_levels"],
      "generated_intersecting_segments":2,
      "intersection":actual["geometry"]["junction"],
      "independently_authenticated_simultaneous_source_self_assembly":False,
      "complete_guide_or_funnel_verified":False,
      "continuous_multi_contact_navigation_verified":False,
      "real_Earth_physics_verified":False,
      "official_NIH_submission":False,
      "native_receipt_sha256":sha256(json.dumps(expected,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    }
    (folder/"world_ab_connected_witness.json").write_text(
      json.dumps(evidence,indent=2,sort_keys=True)+"\n")
    print(json.dumps({key:evidence[key] for key in (
     "schema","intersection","route_changed_probe_levels","native_browser_complete_receipts_match",
     "complete_guide_or_funnel_verified")},sort_keys=True))
    return evidence

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True)
    args=parser.parse_args()
    verify(args.output_dir)
