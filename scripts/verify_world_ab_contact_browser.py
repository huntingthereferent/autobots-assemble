"""Chromium physical WORLD A/B contact observation; independently computed math.

Loads the new page extending the earlier physical WORLD intact. Verifies actual
browser controls, trajectories, step observations, source wall identity, and
negative cases against an analytic trajectory oracle. The *separate* original
A/B sketch target is loaded by the verifier only after physical states exist.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from math import isclose
from pathlib import Path
import re

from systems.workspace.world_ab_contact_trial import initial,trial
from network.tests.test_world_ab_contact_trial import independently_compare,contrast

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"docs/world_phase1_phase2_physical.html"
PAGE=ROOT/"docs/world_ab_contact_trial.html"
OUTPUT_SCHEMA="world-ab-physical-contact-original-comparison/v1"

def diff(a,b,path="root"):
    """Compare generated receipts exactly in shape, numerics with tolerance."""
    if isinstance(a,bool) or isinstance(b,bool):
        if a is not b:raise ValueError(f"{path} Boolean mismatch")
    elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
        if not isclose(a,b,abs_tol=3e-8,rel_tol=0):
            raise ValueError(f"{path} physics number mismatch: {a} vs {b}")
    elif type(a) is dict and type(b) is dict:
        if set(a)!=set(b):raise ValueError(f"{path} keys mismatch")
        for k in a:diff(a[k],b[k],f"{path}.{k}")
    elif type(a) is list and type(b) is list:
        if len(a)!=len(b):raise ValueError(f"{path} length mismatch")
        for i,(x,y) in enumerate(zip(a,b)):diff(x,y,f"{path}[{i}]")
    elif a!=b:raise ValueError(f"{path} value mismatch")

def run(output):
    from playwright.sync_api import sync_playwright
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    old=BASE.read_text(encoding="utf8")
    new=PAGE.read_text(encoding="utf8")
    scripts=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",old,re.S)
    derived=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",new,re.S)
    if derived[:-1]!=scripts:
        raise ValueError("previous physical WORLD or original W13 movement scripts were overwritten")
    if new.count('id="physical-world"')!=1 or new.count('id="ab-contact"')!=1:
        raise ValueError("new contact experiment replaced rather than extended the physical world")
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1280,"height":920})
            errors=[];page.on("pageerror",lambda error:errors.append(str(error)))
            page.goto(PAGE.resolve().as_uri(),wait_until="load",timeout=25000)
            page.wait_for_selector("#ab-contact")
            source_map=page.evaluate("window.physicalWorld.receipt().layout")
            if (source_map["dimensions"]["area_cells"]!=144 or
                source_map["solid_blocks"][0]["x"]!=12 or
                source_map["solid_blocks"][0]["y"]!=1):
                raise ValueError("the original constructed physical world wall moved")
            if page.evaluate("window.worldABContact.get()") is not None:
                raise ValueError("physics experiment result invented before running")
            page.locator("#ab-run").click()
            default=page.evaluate("window.worldABContact.get()")
            if default is None:raise ValueError("actual native browser physics did not execute")
            native=trial(initial())
            diff(default,native)
            independently_compare(default)
            if page.evaluate("window.worldABContact.cursor()")!=0:
                raise ValueError("observation did not begin at initial state")
            for _ in range(12):page.locator("#ab-next").click()
            if (page.evaluate("window.worldABContact.cursor()")!=12 or
                "contact recorded" not in page.locator("#ab-look").inner_text()):
                raise ValueError("next-look failed to reflect numeric collision")
            page.locator("#ab-prev").click()
            if page.evaluate("window.worldABContact.cursor()")!=11:
                raise ValueError("previous look moved wrong turn")
            # Model A/B must truly distinguish wall/no-wall at the same starting state.
            if (default["A_without_wall"]["final"]["x"]!=15 or
                default["B_with_wall"]["final"]["x"]!=8.5 or
                len(default["B_with_wall"]["contacts"])!=1):
                raise ValueError("two A/B branches did not diverge due to physical wall")
            page.locator("#ab-y").fill("3.5")
            page.locator("#ab-vy").fill("0")
            page.locator("#ab-run").click()
            miss=page.evaluate("window.worldABContact.get()")
            diff(miss,trial(initial(y=3.5,vy=0)))
            independently_compare(miss)
            if miss["B_with_wall"]["contacts"]:
                raise ValueError("block incorrectly bounced from an untouched wall")
            page.locator("#ab-y").fill("1.35")
            page.locator("#ab-vy").fill("0.12")
            page.locator("#ab-e").fill("0.5")
            page.locator("#ab-run").click()
            partial=page.evaluate("window.worldABContact.get()")
            diff(partial,trial(initial(restitution=0.5)))
            independently_compare(partial)
            if partial["B_with_wall"]["contacts"][0]["energy_after"]>=partial["B_with_wall"]["contacts"][0]["energy_before"]:
                raise ValueError("damped restitution did not dissipate normal kinetic energy")
            page.locator("#ab-vy").fill("0.9")
            page.locator("#ab-run").click()
            if page.evaluate("window.worldABContact.get()") is not None:
                raise ValueError("outside-of-contract physical controls improperly accepted")
            page.locator("#ab-reset").click()
            if page.evaluate("window.worldABContact.get()") is not None:
                raise ValueError("reset retained invalid generated evidence")
            page.locator("#ab-run").click()
            repeated=page.evaluate("window.worldABContact.get()")
            diff(repeated,default)
            independently_compare(repeated)
            for _ in range(16):page.locator("#ab-next").click()
            page.screenshot(path=str(output/"world_ab_physical_contact_final.png"),full_page=True)
            (output/"world_ab_physical_contact_generated.json").write_text(
                json.dumps(repeated,sort_keys=True,indent=2)+"\n")
            if errors:raise ValueError("Chromium WORLD physics errors: "+repr(errors))
        finally:browser.close()
    assessment=contrast(repeated)
    if (not all(assessment["relation_matches"].values()) or
        assessment["all_required_physical_blueprint_structures_emerged"] is not False or
        assessment["generated_structures_missing"]!=["guide","funnel","diverter","spiral"]):
        raise ValueError("original blueprint comparison misclassified generated physics")
    result={
        "schema":OUTPUT_SCHEMA,
        "original_W13_physical_world_source_scripts_unchanged":True,
        "same_24x6_source_wall_geometry":True,
        "world_source_wall_location":[12,1],
        "browser_original_initial_state_replayed_by_native":True,
        "browser_frames_per_branch":17,
        "default_collision_events":len(repeated["B_with_wall"]["contacts"]),
        "browser_default_path_analytic_oracle_passed":True,
        "browser_missed_contact_rejected":True,
        "browser_variable_restitution_replayed":True,
        "invalid_controls_rejected":True,
        "reset_deterministically_reproduced":True,
        "original_visual_blueprint_independent_comparison":assessment,
        "full_physical_blueprint_equivalence_established":False,
        "full_Earth_physics_supported":False,
        "physical_unit":"virtual W13 movement cell (no metric calibration)",
        "NIH_phase2_submission":False,
        "source_contact_trial_sha256":sha256(
            json.dumps(repeated,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    }
    (output/"world_ab_physical_contact_verified.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"schema":OUTPUT_SCHEMA,
        "A_final":repeated["A_without_wall"]["final"],
        "B_final":repeated["B_with_wall"]["final"],
        "contact_time":repeated["B_with_wall"]["contacts"][0]["time"],
        "relations":assessment["relation_matches"],
        "missing_structure_types":assessment["generated_structures_missing"],
        "full_blueprint_reproduced":False,
        "independent_analytic_oracle_passed":True},sort_keys=True))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output-dir",required=True)
    a=p.parse_args();run(a.output_dir)
