"""Synthetic uncertain-publication research INSIDE the existing W13 native world.

The original twelve source-owned jobs and emitted temporal_query.py stay intact.
A separate provenance-admission observation layer tests a *hypothetical* bound
on when a fictional source became available. The Python program runs on an
explicitly derived conservative source dataset with known_at set to the upper
bound. It does NOT implement three-valued time logic: the independent host
labels observations as definitely withheld, indeterminate, or admitted.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .nih_phase1_world_two_clock import (
    run_two_clock,
    PROTOTYPE_JOB, GAME_JOB,
)
from .nih_phase1_world_frontier import digest
from .nih_prototype_native import invoke, oracle
from .nih_scope_native import validate_scope

SCHEMA="nih-phase1-original-world-publication-uncertainty/v1"
POLICY="constructed-synthetic-publication-bounds/v1"
CUTOFFS=("2026-01-03","2026-01-04","2026-01-06","2026-01-07")
TARGET="2026-01-04"
BOUNDS={
    "prior-note":("2026-01-01","2026-01-01"),
    "delayed-result":("2026-01-04","2026-01-07"),
}

OVERLAY=r"""
<script id="phase1-publication-uncertainty">
(()=>{
 const original=document.querySelector("#phase1-axis");
 if(!original || !document.querySelector("#phase1-frontier"))
   throw Error("the original played W13 two-clock world is absent");
 const panel=document.createElement("section");
 panel.id="phase1-uncertain-source";
 panel.style.cssText="background:#1a292b;color:#f1f3ef;border:1px solid #899b96;font-family:monospace;line-height:1.55;padding:14px;margin:12px 0";
 const h=document.createElement("h2");h.textContent="Phase 1 / uncertain source availability";
 h.style.cssText="font-size:16px;margin:0 0 8px";
 panel.appendChild(h);
 const controls=document.createElement("div");
 controls.id="phase1-availability-cutoffs";
 for(const k of ["2026-01-03","2026-01-04","2026-01-06","2026-01-07"]){
   const b=document.createElement("button");b.dataset.known=k;
   b.textContent="Ask at "+k;b.style.cssText="margin:3px;padding:5px";
   controls.appendChild(b);
 }
 panel.appendChild(controls);
 const out=document.createElement("p");out.id="phase1-availability-answer";
 out.textContent="Querying original emitted Python...";panel.appendChild(out);
 const boundary=document.createElement("p");
 boundary.textContent="Constructed fictional posting interval only (Jan 4–7). The original Python returns a conservative eligible set; this outer observation distinguishes indeterminate evidence. Not an authenticated historical registry result.";
 panel.appendChild(boundary);
 original.insertAdjacentElement("afterend",panel);
 let known="2026-01-03",token=0;
 async function refresh(){
   const turn=Number(document.querySelector("#turns").textContent.replace(/[^0-9]/g,""));
   const seq=++token;
   const r=await window.phase1UncertainSourceProbe({turn,known});
   if(seq!==token)return;
   if(r.kind!=="synthetic-source-availability-boundary/v1" ||
      r.policy!=="constructed-synthetic-publication-bounds/v1" ||
      r.clinical_verdict!=="NOT_EVALUATED" || r.target_at!=="2026-01-04")
      throw Error("source evidence policy changed");
   const d=panel.dataset;
   d.completed=String(seq);d.turn=String(turn);d.known=r.known_at;
   d.nativeKnown=r.native_game_known_at;d.target=r.target_at;
   d.admitted=r.admitted_ids.join(",");
   d.withheld=r.definitely_withheld_ids.join(",");
   d.unknown=r.indeterminate_ids.join(",");
   d.outside=r.outside_validity_ids.join(",");
   d.static=r.static_valid_ids.join(",");
   d.programSha=r.source_program_sha256;
   d.datasetSha=r.conservative_dataset_sha256;
   d.policy=r.policy;d.clinical=r.clinical_verdict;
   out.textContent="Turn "+turn+" | game K="+r.native_game_known_at+" | query K="+r.known_at+" | V="+r.target_at+
      " | admitted: "+(r.admitted_ids.join(",")||"none")+
      " | definitely withheld: "+(r.definitely_withheld_ids.join(",")||"none")+
      " | indeterminate: "+(r.indeterminate_ids.join(",")||"none")+
      " | outside validity: "+(r.outside_validity_ids.join(",")||"none");
 }
 for(const b of controls.querySelectorAll("button")){
   b.addEventListener("click",()=>{known=b.dataset.known;
      refresh().catch(e=>{panel.dataset.error=e.message;});});
 }
 for(const id of ["up","down","left","right","interact","reset"]){
   document.querySelector("#"+id).addEventListener("click",()=>{
     refresh().catch(e=>{panel.dataset.error=e.message;});
   });
 }
 document.addEventListener("keyup",()=>refresh().catch(e=>{panel.dataset.error=e.message;}));
 refresh().catch(e=>{panel.dataset.error=e.message;});
})();
</script>
"""


def attach(html):
    if (type(html) is not str or html.count("</body>")!=1 or
            html.count('id="phase1-world-two-clock"')!=1 or
            html.count('id="phase1-world-frontier-source"')!=1 or
            'id="phase1-publication-uncertainty"' in html):
        raise ValueError("requires previously independently witnessed original W13 HTML")
    return html.replace("</body>",OVERLAY+"</body>")


def source_with_bounds(scope):
    raw=validate_scope(scope)
    if {o["id"] for o in raw["observations"]}!=set(BOUNDS):
        raise ValueError("constructed example requires exactly the pinned original Phase 1 facts")
    derived=deepcopy(raw)
    for row in derived["observations"]:
        lo,hi=BOUNDS[row["id"]]
        if (not lo<=row["known_at"]<=hi or
                date.fromisoformat(lo).isoformat()!=lo or
                date.fromisoformat(hi).isoformat()!=hi):
            raise ValueError("constructed availability bound inconsistent with original fiction")
        row["known_at"]=hi
    return validate_scope(derived)


def independent_classification(scope, *, known,target):
    """Outside-original-program source-policy oracle, not a hidden output model."""
    data=validate_scope(scope)
    date.fromisoformat(known)
    date.fromisoformat(target)
    result={"admitted_ids":[],"definitely_withheld_ids":[],
            "indeterminate_ids":[],"outside_validity_ids":[],
            "static_valid_ids":[]}
    for row in data["observations"]:
        rid=row["id"]
        low,high=BOUNDS[rid]
        if not row["valid_from"]<=target<row["valid_to"]:
            result["outside_validity_ids"].append(rid)
            continue
        result["static_valid_ids"].append(rid)
        if known<low:
            result["definitely_withheld_ids"].append(rid)
        elif known>=high:
            result["admitted_ids"].append(rid)
        else:
            result["indeterminate_ids"].append(rid)
    for values in result.values():
        values.sort()
    return result


def verify_boundary(scope,conservative,program_result,*,known,target):
    independent=independent_classification(scope,known=known,target=target)
    # Caller separately replays the exact original generated code against
    # the native host oracle before this provenance-specific classification.
    if (program_result["temporal_ids"]!=independent["admitted_ids"] or
            program_result["outside_validity_ids"]!=independent["outside_validity_ids"] or
            program_result["static_snapshot_ids"]!=independent["static_valid_ids"] or
            program_result["future_leakage_ids"]!=sorted(
                independent["definitely_withheld_ids"]+independent["indeterminate_ids"])):
        raise ValueError("original Python conservative selector contradicts independent policy")
    admitted=set(independent["admitted_ids"])
    withheld=set(independent["definitely_withheld_ids"])
    uncertain=set(independent["indeterminate_ids"])
    static=set(independent["static_valid_ids"])
    outside=set(independent["outside_validity_ids"])
    if (any(x&y for x,y in ((admitted,withheld),(admitted,uncertain),(withheld,uncertain),
                           (static,outside))) or
            admitted|withheld|uncertain!=static):
        raise ValueError("loss or overlap in uncertainty source partition")
    return independent


def check_capture(frame, expected, *, turn, known,native_known,source_sha,dataset_sha):
    exact={"turn":str(turn),"known":known,"native_known":native_known,
           "target":TARGET,
           "admitted":",".join(expected["admitted_ids"]),
           "withheld":",".join(expected["definitely_withheld_ids"]),
           "unknown":",".join(expected["indeterminate_ids"]),
           "outside":",".join(expected["outside_validity_ids"]),
           "static":",".join(expected["static_valid_ids"]),
           "program_sha":source_sha,"dataset_sha":dataset_sha,
           "policy":POLICY,"clinical":"NOT_EVALUATED"}
    if frame!=exact:
        raise ValueError("browser uncertain-source labels altered from independent scope")
    return {"turn":turn,"known_at":known,"native_game_known_at":native_known,
            "target_at":TARGET,**expected,
            "source_program_sha256":source_sha,
            "conservative_dataset_sha256":dataset_sha,
            "independent_source_policy_agreement":True}


def check_grid(frames, *, actions,cutover):
    if (type(actions) is not int or actions<2 or
            type(cutover) is not int or not 1<=cutover<=actions or
            len(frames)!=(actions+1)*len(CUTOFFS)):
        raise ValueError("incomplete original-game source uncertainty evidence")
    lookup={(r["turn"],r["known_at"]):r for r in frames}
    if len(lookup)!=len(frames) or set(lookup)!={
            (turn,k) for turn in range(actions+1) for k in CUTOFFS}:
        raise ValueError("missing or repeated real browser query")
    for row in frames:
        groups=[row[key] for key in ("admitted_ids","definitely_withheld_ids",
              "indeterminate_ids","outside_validity_ids","static_valid_ids")]
        if any(type(group) is not list or group!=sorted(set(group)) for group in groups):
            raise ValueError("missing source identities or duplicated source-state labels")
        admitted,withheld,uncertain,outside,static=map(set,groups)
        if (admitted & withheld or admitted & uncertain or withheld & uncertain or
                (admitted|withheld|uncertain)!=static or static & outside or
                static|outside!=set(BOUNDS)):
            raise ValueError("source admission states do not partition actual original scope")
    for turn in range(actions+1):
        times={lookup[turn,k]["native_game_known_at"] for k in CUTOFFS}
        if len(times)!=1:
            raise ValueError("game clock depends on chosen hypothetical cutoff")
        for k in CUTOFFS:
            if lookup[turn,k]["independent_source_policy_agreement"] is not True:
                raise ValueError("missing host oracle receipt")
    for k in CUTOFFS:
        prior=None
        for turn in range(actions+1):
            f=lookup[turn,k]
            if prior and any(f[name]!=prior[name] for name in (
                "admitted_ids","definitely_withheld_ids","indeterminate_ids",
                "outside_validity_ids","static_valid_ids","source_program_sha256",
                "conservative_dataset_sha256")):
                raise ValueError("source facts changed when only original game turn advanced")
            prior=f
    # Crucial distinction: a bounded, unverified publication time cannot be
    # silently converted into a known false claim at an intermediate cutoff.
    if ("delayed-result" not in lookup[0,"2026-01-03"]["definitely_withheld_ids"] or
            "delayed-result" not in lookup[0,"2026-01-04"]["indeterminate_ids"] or
            "delayed-result" not in lookup[0,"2026-01-06"]["indeterminate_ids"] or
            "delayed-result" not in lookup[0,"2026-01-07"]["admitted_ids"]):
        raise ValueError("original-world uncertain publication boundary incorrectly resolved")
    game_early=lookup[0,CUTOFFS[0]]["native_game_known_at"]
    game_after=lookup[cutover,CUTOFFS[0]]["native_game_known_at"]
    if (not game_early<game_after or
            any(lookup[t,CUTOFFS[0]]["native_game_known_at"]!=game_early
                for t in range(cutover)) or
            any(lookup[t,CUTOFFS[0]]["native_game_known_at"]!=game_after
                for t in range(cutover,actions+1))):
        raise ValueError("original playable game failed exact two-stage native knowledge clock")
    return True


def run_world(*,data_dir,output_dir,parent=run_two_clock):
    from playwright.sync_api import sync_playwright

    data,out=Path(data_dir),Path(output_dir)
    data.mkdir(parents=True,exist_ok=True)
    out.mkdir(parents=True,exist_ok=True)
    parent_report=parent(data_dir=data,output_dir=out)
    if (parent_report.get("schema")!="nih-phase1-original-w13-world-two-clock/v1" or
            parent_report.get("original_native_jobs")!=12 or
            parent_report.get("both_clock_dimensions_observed") is not True or
            parent_report.get("independent_source_oracle_agreed") is not True or
            parent_report.get("preserved_original_native_ancestry") is not True):
        raise ValueError("original world and independently witnessed two clocks required")
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    if len(runtime.snapshot())!=12:
        raise ValueError("parent experiment invented a native worker")
    scope=validate_scope(runtime.get("nih-scope-001").inputs)
    conservative=source_with_bounds(scope)
    native=runtime.state(PROTOTYPE_JOB).output["prototype"]
    program=native["python_source"]
    program_sha=digest(program)
    dataset=json.loads((out/"temporal_dataset.json").read_text())
    if dataset["observations"]!=scope["observations"]:
        raise ValueError("source-owned original scope changed")
    derived=deepcopy(dataset)
    derived["observations"]=conservative["observations"]
    derived_bytes=json.dumps(derived,sort_keys=True,indent=2)+"\n"
    derived_sha=digest(derived_bytes)
    original_html=(out/"nih-phase1-two-clock-world.html").read_text()
    html=attach(original_html)
    config=json.loads((out/"game-temporal-config.json").read_text())
    plan=runtime.state(GAME_JOB).output["build"]["plan"]
    if (type(plan) is not list or not 2<=len(plan)<=30 or
            config.get("synthetic") is not True or
            type(config.get("cutover_turn")) is not int or
            not 1<=config["cutover_turn"]<=len(plan)):
        raise ValueError("original native game time configuration unavailable")
    old_journals={name:(data/name).read_bytes() for name in (
        "runtime.jsonl","coordinator-windows.jsonl")}
    old_browser=(out/"game-temporal-query-events.jsonl").read_bytes()
    frames,events=[],[]
    with TemporaryDirectory(prefix="nih-uncertain-publication-world-") as td:
        root=Path(td)
        for name in ("temporal_bridge_server.py","temporal_query.py",
                     "temporal_dataset.json","game-temporal-config.json"):
            (root/name).write_bytes((out/name).read_bytes())
        if (root/"temporal_query.py").read_text()!=program:
            raise ValueError("original executable changed")
        (root/"conservative_publication_dataset.json").write_text(derived_bytes)
        (root/"temporal-game.html").write_text(html)
        def game_known(turn):
            return (config["known_at_after"] if turn>=config["cutover_turn"]
                    else config["known_at_before"])
        def query_original(payload):
            if (type(payload) is not dict or set(payload)!={"turn","target"} or
                    type(payload["turn"]) is not int or
                    not 0<=payload["turn"]<=len(plan) or
                    payload["target"] not in ("2026-01-02","2026-01-04","2026-01-11")):
                raise ValueError("invalid unchanged original target selector")
            req={"known_at":game_known(payload["turn"]),"target_at":payload["target"]}
            original=invoke(root/"temporal_query.py",root/"temporal_dataset.json",req)
            owner_oracle=oracle(scope,dataset["functional_predicates"],
                                known=req["known_at"],target=req["target_at"])
            if original!=owner_oracle:
                raise ValueError("original two-clock parent program disagrees with native scope")
            return {**original,"source_program_sha256":program_sha}
        def query_uncertain(payload):
            if (type(payload) is not dict or set(payload)!={"turn","known"} or
                    type(payload["turn"]) is not int or
                    not 0<=payload["turn"]<=len(plan) or
                    payload["known"] not in CUTOFFS):
                raise ValueError("invalid bounded hypothetical posting-query click")
            turn,known=payload["turn"],payload["known"]
            req={"known_at":known,"target_at":TARGET}
            actual=invoke(root/"temporal_query.py",
                          root/"conservative_publication_dataset.json",req)
            exact=oracle(conservative,dataset["functional_predicates"],
                         known=known,target=TARGET)
            if actual!=exact:
                raise ValueError("the unchanged original Python gave unexpected answer")
            independent=verify_boundary(
                scope,conservative,actual,known=known,target=TARGET)
            events.append({"turn":turn,"request":req,
                           "actual_emitted_python_sha256":program_sha,
                           "conservative_dataset_sha256":derived_sha,
                           "original_program_result_sha256":digest(json.dumps(actual,sort_keys=True)),
                           "independent_policy_result":independent})
            return {"kind":"synthetic-source-availability-boundary/v1",
                    "policy":POLICY,"known_at":known,"target_at":TARGET,
                    "native_game_known_at":game_known(turn),
                    **independent,"source_program_sha256":program_sha,
                    "conservative_dataset_sha256":derived_sha,
                    "clinical_verdict":"NOT_EVALUATED"}
        server=subprocess.Popen(
            [sys.executable,"-I",str(root/"temporal_bridge_server.py"),
             str(root),"0"],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            port=server.stdout.readline().strip()
            if not port.isdecimal():
                raise ValueError("original native loopback HTTP bridge failed")
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True)
                try:
                    page=browser.new_page()
                    page.expose_binding("phase1OriginalPythonProbe",
                                        lambda _src,payload:query_original(payload))
                    page.expose_binding("phase1UncertainSourceProbe",
                                        lambda _src,payload:query_uncertain(payload))
                    page.goto(f"http://127.0.0.1:{int(port)}/")
                    for turn in range(len(plan)+1):
                        if turn:
                            action=plan[turn-1]
                            if action not in ("up","down","left","right","interact"):
                                raise ValueError("original game action changed")
                            page.locator("#"+action).click()
                            page.wait_for_function(
                                "(t)=>document.querySelector('#temporal-panel')?.dataset.turn===String(t)",
                                arg=turn,timeout=15000)
                        for known in CUTOFFS:
                            panel=page.locator("#phase1-uncertain-source")
                            old=panel.get_attribute("data-completed")
                            old_int=int(old) if old is not None else 0
                            page.locator(
                                f'#phase1-availability-cutoffs button[data-known="{known}"]').click()
                            page.wait_for_function(
                                "(args)=>{const d=document.querySelector('#phase1-uncertain-source')?.dataset;"
                                "return d && Number(d.completed||0)>args.prev && d.turn===String(args.turn)"
                                " && d.known===args.known;}",
                                arg={"prev":old_int,"turn":turn,"known":known},timeout=15000)
                            expected=independent_classification(scope,known=known,target=TARGET)
                            keys=("turn","known","native-known","target","admitted",
                                  "withheld","unknown","outside","static",
                                  "program-sha","dataset-sha","policy","clinical")
                            snapshot={
                                k.replace("-","_"):panel.get_attribute("data-"+k)
                                for k in keys}
                            frame=check_capture(snapshot,expected,turn=turn,known=known,
                                native_known=game_known(turn),source_sha=program_sha,
                                dataset_sha=derived_sha)
                            if not any(e["turn"]==turn and e["request"]=={
                                "known_at":known,"target_at":TARGET} for e in events):
                                raise ValueError("observed game panel did not execute original Python")
                            frames.append(frame)
                    if page.locator("body").get_attribute("data-solved")!="true":
                        raise ValueError("original played world was not solved")
                    page.screenshot(path=str(out/"nih-phase1-world-publication-uncertainty.png"),
                                    full_page=True)
                finally:
                    browser.close()
        finally:
            server.terminate()
            try:server.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.communicate()
    check_grid(frames,actions=len(plan),cutover=config["cutover_turn"])
    if ({name:(data/name).read_bytes() for name in old_journals}!=old_journals or
            (out/"game-temporal-query-events.jsonl").read_bytes()!=old_browser):
        raise ValueError("original twelve native jobs or original browser journal changed")
    report={
        "schema":SCHEMA,"original_native_jobs":12,
        "original_world_two_clock_parent_witnessed":True,
        "constructed_source_policy":POLICY,
        "constructed_fictional_publication_bounds":BOUNDS,
        "original_emitted_python_sha256":program_sha,
        "conservative_dataset_sha256":derived_sha,
        "world_actions":len(plan),"cutoff_choices":list(CUTOFFS),
        "observed_browser_frames":frames,
        "actual_original_python_calls":events,
        "played_original_game_solved":True,
        "independent_three_state_policy_verified":True,
        "original_native_journals_preserved":True,
        "three_state_logic_is_not_in_original_python":True,
        "new_native_job":False,"new_NIH_checkpoint":False,
        "real_historical_publication_authenticated":False,
        "synthetic_only":True,"clinical_verdict":"NOT_EVALUATED",
        "official_NIH_submission":False,
    }
    (out/"nih-phase1-world-publication-uncertainty.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n")
    (out/"nih-phase1-world-publication-uncertainty.html").write_text(html)
    return report


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args(argv)
    r=run_world(data_dir=a.data_dir,output_dir=a.output_dir)
    print(json.dumps({"schema":r["schema"],"native_jobs":r["original_native_jobs"],
         "world_actions":r["world_actions"],"browser_frames":len(r["observed_browser_frames"]),
         "original_python_calls":len(r["actual_original_python_calls"]),
         "clinical_verdict":r["clinical_verdict"]},sort_keys=True))


if __name__=="__main__":
    raise SystemExit(main())
