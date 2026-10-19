"""Actual Chromium physical WORLD fit test with independent movement replay.

Tests the *constructed* grid geometry, not the existing W13 tiny-room preview.
The six relational bays form navigable virtual physical space and the browser
receipts must survive an independent Python reconstruction, without promoting
a simulation unit to actual metres, patient outcomes or an NIH result.
"""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from systems.workspace.world_physical_construction import (
    ORIGIN,GOAL,GATE,SOURCE,QUERY,footprint,witness,verify_geometry,neighbors)
from systems.workspace.world_temporal_blueprint import validate,evaluate
import argparse

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"docs/world_phase1_phase2_physical.html"
BASE=ROOT/"docs/world_phase1_phase2_blueprint.html"
FIXTURE=ROOT/"network/tests/fixtures/world_nih_phase1_phase2_blueprint_v1.json"

def independent_receipt(receipt):
    if (type(receipt) is not dict or
        receipt.get("schema")!="world-phase1-phase2-physical-play-receipt/v1" or
        receipt.get("browser_origin_authenticated") is not False or
        receipt.get("exact_real_publication_instant_authenticated") is not False or
        receipt.get("completed") is not True):
        raise ValueError("physical-world proof not completed")
    original=validate(json.loads(FIXTURE.read_text()))
    expected=footprint(original)
    m=receipt["layout"]
    verify_geometry(expected)
    actual={k:v for k,v in m.items() if k!="blueprint_sha256"}
    check={k:v for k,v in expected.items() if k!="blueprint_sha256"}
    if actual!=check:raise ValueError("constructed physics no longer maps to pinned original blueprint")
    if not witness(expected)["gate_required"]:raise ValueError("native physical gate topology invalid")
    actor=list(ORIGIN)
    current="construct";built=None;last=None;completed=False
    seen={"construct":0,"advance":0,"query":0,"finish":0,"move":0}
    for i,step in enumerate(receipt["actions"]):
        kind=step.get("action")
        if kind=="move":
            to=step.get("after")
            if (step.get("before")!=actor or step.get("stage")!=current or
                type(to) is not list or len(to)!=2 or
                tuple(to) not in set(neighbors(expected,tuple(actor),False))):
                raise ValueError("physical movement illegally crossed a wall or stage")
            actor=list(to)
        elif kind=="construct":
            if (current!="construct" or actor!=[SOURCE["x"],SOURCE["y"]] or built is not None or
                step.get("at")!=actor):
                raise ValueError("source built outside its original physical station")
            built=validate(receipt["constructed_blueprint"])
            if (step.get("assertion_count")!=len(built["sample_sets"]["synthetic"]) or
                step.get("source_schema")!=built["schema"]):
                raise ValueError("constructed blueprint evidence count or identity drifted")
        elif kind=="advance":
            if (current!="construct" or built is None or actor!=GATE["from"] or
                step.get("before")!=GATE["from"] or step.get("after")!=GATE["to"] or
                step.get("requires")!="source-constructed"):
                raise ValueError("physical crossing was unauthorized")
            actor=deepcopy(GATE["to"]);current="reason"
        elif kind=="query":
            if current!="reason" or actor!=[QUERY["x"],QUERY["y"]] or built is None or step.get("at")!=actor:
                raise ValueError("temporal query outside constructed reasoning station")
            mode=step.get("mode")
            if mode not in ("synthetic","registry"):raise ValueError("unknown source mode")
            prepared=deepcopy(built)
            prepared["queries"][mode]={"knowledge_cutoff":step.get("knowledge_cutoff"),
                                       "valid_target":step.get("valid_target")}
            expected_query=evaluate(prepared,mode)
            supported=("eligible","withheld_future","outside_validity","unresolved_validity",
                       "owner_day_states","static_union_valid","static_future_leakage",
                       "source_partition","query","clinical_verdict")
            if any(expected_query[k]!=step.get("result",{}).get(k) for k in supported):
                raise ValueError("independent host source/time query diverged from physical world")
            last=step["result"]
        elif kind=="finish":
            if (actor!=GOAL or current!="reason" or last is None or
                step.get("at")!=actor or completed):
                raise ValueError("physical world ended without its complete source reasoning handoff")
            completed=True
        else:raise ValueError("unknown construction or movement action")
        seen[kind]+=1
    if (actor!=receipt["actor"] or current!=receipt["stage"] or
        last!=receipt["last_query"] or not completed or
        seen["advance"]!=1 or seen["construct"]!=1 or
        seen["query"]<2 or seen["move"]<10 or seen["finish"]!=1):
        raise ValueError("recorded physical end state or original movement handoff not reproduced")
    return {"schema":"world-phase1-phase2-physical-independent-witness/v1",
            "physical_grid_cells":expected["dimensions"]["area_cells"],
            "geometry":"24x6, six four-unit lanes, two three-unit stages",
            "original_4x3_and_3x3_W13_contract_unchanged":True,
            "original_gate_required":True,
            "solid_block_count":len(expected["solid_blocks"]),
            "source_and_reasoning_stations_reached":True,
            "movements_verified":seen["move"],
            "source_builds_verified":seen["construct"],
            "boundary_crossings_verified":seen["advance"],
            "real_browser_queries_verified":seen["query"],
            "independent_native_physical_receipt_verified":True,
            "metric_scale_authenticated":False,
            "original_2019_realtime_publication_authenticated":False,
            "official_NIH_submission":False}

def run(output):
    from playwright.sync_api import sync_playwright
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    root=BASE.read_text()
    derived=PAGE.read_text()
    w13=root.split("<script>",1)[1].split("</script>",1)[0]
    witness_src=derived.split("<script>",1)[1].split("</script>",1)[0]
    if w13!=witness_src:raise ValueError("original native W13 movement JS rewritten")
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1300,"height":1100})
            errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(PAGE.resolve().as_uri(),wait_until="load",timeout=30000)
            page.wait_for_selector("#physical-world")
            before=page.evaluate("window.physicalWorld.receipt()")
            if (before["layout"]["dimensions"]["area_cells"]!=144 or
                before["layout"]["dimensions"]["width"]!=24 or
                before["layout"]["dimensions"]["height"]!=6):
                raise ValueError("actual 144-cell world not built in Chromium")
            page.locator("#phy-advance").click()
            if page.evaluate("window.physicalWorld.receipt().stage")!="construct":
                raise ValueError("unbuilt source crossed physical gate")
            page.locator("#phy-go-query").click()
            if page.evaluate("window.physicalWorld.receipt().actor")!=ORIGIN:
                raise ValueError("source room illegally navigated into query room")
            page.locator("#bp-assertion").select_option("delayed-result")
            page.locator("#bp-known").fill("2026-01-03")
            page.locator("#bp-apply").click()
            page.locator("#phy-go-source").click()
            if page.evaluate("window.physicalWorld.receipt().actor")!=[SOURCE["x"],SOURCE["y"]]:
                raise ValueError("actual source station physically unreachable")
            page.locator("#phy-construct").click()
            if page.evaluate("window.physicalWorld.receipt().constructed_blueprint.sample_sets.synthetic[1].known_day")!="2026-01-03":
                raise ValueError("physical source construction does not capture edited blueprint")
            page.locator("#phy-go-door").click()
            if page.evaluate("window.physicalWorld.receipt().actor")!=GATE["from"]:
                raise ValueError("source-built actor cannot physically reach the explicit gate")
            page.locator("#phy-advance").click()
            if page.evaluate("window.physicalWorld.receipt().stage")!="reason":
                raise ValueError("physical gate did not perform source-to-reasoning advance")
            page.locator("#phy-go-query").click()
            if page.evaluate("window.physicalWorld.receipt().actor")!=[QUERY["x"],QUERY["y"]]:
                raise ValueError("constructed reasoning station is physically unreachable")
            page.locator("#phy-query").click()
            first=page.evaluate("window.physicalWorld.receipt().last_query")
            if first["eligible"]!=["prior-note","delayed-result"] or first["static_future_leakage"]:
                raise ValueError("edited physical source failed to change actual temporal query")
            page.locator("#bp-mode").select_option("registry")
            page.locator("#phy-query").click()
            real=page.evaluate("window.physicalWorld.receipt().last_query")
            if (real["eligible"]!=[] or
                real["unresolved_validity"]!=["ctgov-v94","ctgov-v105"] or
                real["owner_day_states"]["ctgov-v105"]!="SAME_DAY_TIME_UNRESOLVED"):
                raise ValueError("physical source incorrectly treated historical day as verified instant")
            page.locator("#phy-go-finish").click()
            final=page.evaluate("window.physicalWorld.receipt()")
            independent=independent_receipt(final)
            if errors:raise ValueError("live physical world JS errors: "+repr(errors))
            page.screenshot(path=str(output/"world_physical_blueprint_144_cells.png"),full_page=True)
            (output/"world_physical_blueprint_receipt.json").write_text(
                json.dumps(final,indent=2,sort_keys=True)+"\n")
            (output/"world_physical_blueprint_independent_witness.json").write_text(
                json.dumps(independent,indent=2,sort_keys=True)+"\n")
            page.locator("#phy-reset").click()
            reset=page.evaluate("window.physicalWorld.receipt()")
            if (reset["actor"]!=ORIGIN or reset["stage"]!="construct" or
                reset["actions"] or reset["completed"] or reset["constructed_blueprint"] is not None):
                raise ValueError("physical build reset didn't restore original ground state")
        finally:browser.close()
    print(json.dumps(independent,sort_keys=True))
    return independent

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output-dir",required=True)
    args=p.parse_args();run(args.output_dir)
