"""Native and real Chromium witness for the Phase 1-contained Phase 2 WORLD blueprint.

Browser controls must alter source-qualified assertion values, reconstruct a
graph, and move temporal answers, while exact original W13 receipt independently
replays against the pinned upstream original W12/W13 source. No claims of
authenticated browser origin, clinical findings or NIH competition status.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from systems.workspace.world_temporal_blueprint import validate,evaluate,graph
from systems.workspace.world_blueprint_rdf import write_exports

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"docs/world_phase1_phase2_blueprint.html"
FIXTURE=ROOT/"network/tests/fixtures/world_nih_phase1_phase2_blueprint_v1.json"

def witness_original_w13(reference,receipt):
    script="""import sys,json
from network.witness_w13_independent import independent_w13_replay
from systems.workspace.game_w13_engine import play
source=json.load(sys.stdin)
actual=independent_w13_replay(source)
if not actual.get('valid') or not actual.get('solved') or actual.get('worlds_completed')!=2 or actual.get('boundaries_checked')!=1:
    raise SystemExit('original W13 independent witness rejected')
worlds=[{'id':x['id'],'spec':x['spec']} for x in source['worlds']]
played=play(worlds,source['actions'])
if not played['solved'] or played['worlds_completed']!=2:
    raise SystemExit('original native game does not agree with browser')
print(json.dumps({'witness':'original W13 independent replay',
                  'worlds_completed':2,'boundaries_checked':1,'browser_origin_authenticated':False,
                  'w13_checkpoint_promoted':False}))
"""
    proc=subprocess.run([sys.executable,"-c",script],cwd=reference,
        input=json.dumps(receipt),text=True,capture_output=True,timeout=25,
        env={**os.environ,"PYTHONPATH":str(reference)})
    if proc.returncode:
        raise ValueError("independent original W13 verifier rejected browser receipt: "+proc.stderr[-2400:])
    return json.loads(proc.stdout)

def cross_check(actual,mode):
    bp=validate(actual["blueprint"])
    if actual["active_source"]!=mode or actual["browser_origin_authenticated"] is not False:
        raise ValueError("browser source or evidence class promoted")
    expected=evaluate(bp,mode)
    observed=actual["query_result"]
    keys=("eligible","withheld_future","outside_validity","unresolved_validity",
          "owner_day_states","static_union_valid","static_future_leakage",
          "source_partition","query","clinical_verdict","publication_instant_authenticated")
    if type(observed) is not dict or any(expected[k]!=observed.get(k) for k in keys):
        raise ValueError("real browser temporal result does not match host-owned native oracle")
    nodes=graph(bp,mode)["nodes"]
    actual_nodes=actual.get("graph_nodes")
    if (type(actual_nodes) is not list or len(actual_nodes)!=len(nodes) or
        [(x["id"],x["row"],x["col"],x["lane"],x["value"]) for x in actual_nodes]!=
        [(x["id"],x["row"],x["column"],x["lane"],x["label"]) for x in nodes]):
        raise ValueError("graph geometry, identity, or source-linked label drifted")
    return expected

def run(reference,output):
    from playwright.sync_api import sync_playwright
    reference=Path(reference).resolve()
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    base=(reference/"docs/game_w13_preview.html").read_text(encoding="utf8")
    page_source=PAGE.read_text(encoding="utf8")
    base_js=base.split("<script>",1)[1].split("</script>",1)[0]
    derived_js=page_source.split("<script>",1)[1].split("</script>",1)[0]
    if base_js!=derived_js:
        raise ValueError("original W13 browser game script was replaced rather than extended")
    fixture=validate(json.loads(FIXTURE.read_text()))
    initial_sha=sha256(FIXTURE.read_bytes()).hexdigest()
    if fixture["base_world"]["version"]!="game-w13-multiworld-v1":
        raise ValueError("W13 contract version changed")
    evidence={"schema":"world-phase1-phase2-blueprint-build-browser-evidence/v1",
              "original_browser_js_sha256":sha256(base_js.encode()).hexdigest(),
              "original_blueprint_fixture_sha256":initial_sha,
              "browser_origin_authenticated":False,
              "nih_phase1_draft_submitted":False,
              "nih_phase2_award_claimed":False}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1250,"height":950},accept_downloads=False)
            failures=[]
            page.on("pageerror",lambda err:failures.append(str(err)))
            rsp=page.goto(PAGE.resolve().as_uri(),wait_until="load",timeout=25000)
            page.wait_for_selector("#world-blueprint")
            if page.locator("#bp-map .bp-map-node").count()!=12 or not page.locator("#bp-run").is_disabled():
                raise ValueError("original W13 movement gate or blueprint 2D nodes absent")
            if not page.locator("#advance").is_disabled():
                raise ValueError("W13 allowed advance before first-room collection")
            page.locator("#bp-add").click()
            if (page.locator("#bp-map .bp-map-node").count()!=18
                or len(page.evaluate("window.worldBlueprintExport().blueprint.sample_sets.synthetic"))!=3):
                raise ValueError("fixed tiny room dimensions improperly bound graph size")
            page.locator("#bp-remove").click()
            if page.locator("#bp-map .bp-map-node").count()!=12:
                raise ValueError("removed graph assertion left stale displayed nodes")
            page.locator("#bp-assertion").select_option("delayed-result")
            page.locator("#bp-object").fill("changed-observation")
            page.locator("#bp-known").fill("2026-01-03")
            page.locator("#bp-apply").click()
            if ("2026-01-03" not in page.locator("#bp-clocks").inner_text()
                or page.locator("#bp-clocks .bp-clock").count()!=7):
                raise ValueError("all five independent source clocks not rendered after editing")
            initial=page.evaluate("window.worldBlueprintExport()")
            if ("changed-observation" not in page.locator("#bp-map").inner_text()
                or initial["blueprint"]["sample_sets"]["synthetic"][1]["known_day"]!="2026-01-03"
                or initial["query_result"] is not None):
                raise ValueError("editing the blueprint did not reconstruct source graph")
            page.locator('button[data-action="right"]').click()
            page.locator('button[data-action="interact"]').click()
            if page.locator("#advance").is_disabled():
                raise ValueError("W13 first room collection did not permit advance")
            first=page.evaluate("window.worldBlueprintExport()")["w13"]
            page.locator("#advance").click()
            if page.locator("#bp-run").is_disabled():
                raise ValueError("the temporal query did not cross the actual W13 advance boundary")
            page.locator("#bp-run").click()
            synthetic=page.evaluate("window.worldBlueprintExport()")
            result=cross_check(synthetic,"synthetic")
            if result["eligible"]!=["prior-note","delayed-result"] or result["static_future_leakage"]:
                raise ValueError("editing known day did not change native temporal answer")
            page.locator("#bp-k").fill("2026-01-02")
            page.locator("#bp-run").click()
            shifted=page.evaluate("window.worldBlueprintExport()")
            shifted_result=cross_check(shifted,"synthetic")
            if shifted_result["eligible"]!=["prior-note"] or shifted_result["withheld_future"]!=["delayed-result"]:
                raise ValueError("future evidence leakage guard lost in original game")
            page.locator("#bp-mode").select_option("registry")
            if not page.locator("#bp-apply").is_disabled():
                raise ValueError("real source version public evidence was editable")
            page.locator("#bp-scale").fill("9")
            page.locator("#bp-scale").dispatch_event("change")
            if page.locator("#bp-map .bp-map-node").count()!=12:
                raise ValueError("map layout scale incorrectly changed logical graph")
            if ("2019-08-02" not in page.locator("#bp-clocks").inner_text()
                or "UNKNOWN interval" not in page.locator("#bp-clocks").inner_text()):
                raise ValueError("real owner posting-day evidence or missing validity not shown")
            page.locator("#bp-assertion").select_option("ctgov-v105")
            if "2019-11-25" not in page.locator("#bp-clocks").inner_text():
                raise ValueError("selected original version does not update observed posting day")
            page.locator("#bp-run").click()
            registry=page.evaluate("window.worldBlueprintExport()")
            real=cross_check(registry,"registry")
            if (real["eligible"]!=[] or
                real["unresolved_validity"]!=["ctgov-v94","ctgov-v105"] or
                real["owner_day_states"]["ctgov-v105"]!="SAME_DAY_TIME_UNRESOLVED"):
                raise ValueError("unknown original public release/validity was fabricated by the map")
            page.locator('button[data-action="right"]').click()
            page.locator('button[data-action="interact"]').click()
            final=page.evaluate("window.worldBlueprintExport()")
            if final["w13"]["final"]["solved"] is not True:
                raise ValueError("two original W13 rooms did not finish")
            native=witness_original_w13(reference,final["w13"])
            final_compare=cross_check(final,"registry")
            page.screenshot(path=str(output/"world_phase1_phase2_blueprint.png"),full_page=True)
            (output/"world_phase1_phase2_blueprint_receipt.json").write_text(
                json.dumps(final,sort_keys=True,indent=2)+"\n")
            page.locator("#bp-reset").click()
            reset=page.evaluate("window.worldBlueprintExport()")
            if (reset["w13"]["final"]["solved"] is not False or
                reset["w13"]["actions"]!=[] or
                reset["blueprint"]!=fixture or
                reset["active_source"]!="synthetic"):
                raise ValueError("reset did not restore original world plus untouched blueprint")
            if failures:raise ValueError("page JavaScript errors: "+repr(failures))
            rdf_receipts=write_exports(final["blueprint"],output)
            if (len(rdf_receipts)!=2 or
                any(r["parsed_graph_query_oracle_agreed"] is not True for r in rdf_receipts)):
                raise ValueError("source graph RDF parsing/independent temporal oracle failed")
            evidence.update({
                "original_two_room_browser_source_unchanged":True,
                "phase1_ontology_aligned_rdf_receipts":rdf_receipts,
                "original_w13_independent_native_witness":native,
                "actual_played_world_actions":final["w13"]["actions"],
                "first_room_actions_preserved":first["worlds"][0]["actions"]==final["w13"]["worlds"][0]["actions"],
                "synthetic_before_edit_withheld_delayed":True,
                "synthetic_after_edit_admitted_delayed":result["eligible"]==["prior-note","delayed-result"],
                "shifted_cutoff_withheld_future":shifted_result["withheld_future"]==["delayed-result"],
                "real_original_version_valid_time_unresolved":real["unresolved_validity"],
                "real_publication_UTC_instant_authenticated":False,
                "two_dimensional_projection_does_not_limit_logical_clocks":len(fixture["clocks"])==5,
                "reset_restored_source_and_session":True,
                "real_browser_test_passed":True,
            })
        finally:browser.close()
    (output/"world_phase1_phase2_browser_witness.json").write_text(
        json.dumps(evidence,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"original_w13_replayed":True,
        "original_rooms_completed":2,"source_edit_changed_query":True,
        "real_registry_validity_unresolved":True,"reset_passed":True,
        "original_JS_unchanged":True,"independently_parsed_RDF_graphs":2},sort_keys=True))
    return evidence

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--reference-dir",required=True)
    p.add_argument("--output-dir",required=True)
    a=p.parse_args()
    run(a.reference_dir,a.output_dir)
