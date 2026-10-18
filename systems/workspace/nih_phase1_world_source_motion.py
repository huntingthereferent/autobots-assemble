"""Witness source changes INSIDE the original playable W13/NIH two-clock world.

Reuses the original twelve source-owned native jobs, the exact emitted
temporal_query.py, and the existing NIH source-variation generator. Synthetic
counterfactual datasets are never promoted to original archival evidence or
added as workstation jobs. A new Chromium source control drives the original
Python program on each click; a separate Phase 1 scope oracle checks results.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import argparse
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .nih_dataset_sensitivity import variants
from .nih_phase1_world_two_clock import run_two_clock
from .nih_phase1_world_frontier import GAME_JOB, PROTOTYPE_JOB, digest
from .nih_prototype_native import oracle, invoke
from .nih_scope_native import validate_scope

SCHEMA = "nih-phase1-original-world-source-motion/v1"
PROFILES = ("original", "later-knowledge", "additional-conflict")
TARGET = "2026-01-04"

OVERLAY = r"""
<script id="phase1-source-motion">
(() => {
  const parent=document.querySelector("#phase1-axis");
  if(!parent || !document.querySelector("#phase1-frontier"))
    throw Error("original two-clock world not constructed");
  const panel=document.createElement("section");
  panel.id="phase1-source-motion-panel";
  panel.style.cssText="background:#17262b;border:1px solid #95a7ad;padding:12px;margin:12px 0;font-family:monospace;color:#f1f2f3;line-height:1.5";
  panel.innerHTML='<h2 style="font-size:16px;margin:0 0 8px">Phase 1 / synthetic source movement</h2>'+
    '<div id="phase1-source-choices"></div><p id="phase1-source-observed">Querying the unchanged Python program...</p>'+
    '<p>Synthetic counterfactual source records: not historical registry version evidence.</p>';
  parent.insertAdjacentElement("afterend",panel);
  const names=["original","later-knowledge","additional-conflict"];
  for(const name of names){
    const b=document.createElement("button");
    b.dataset.profile=name;b.textContent=name;b.style.cssText="padding:5px;margin:4px";
    document.querySelector("#phase1-source-choices").appendChild(b);
  }
  let profile=names[0],sequence=0;
  async function refresh(){
    const turn=Number(document.querySelector("#turns").textContent.replace(/[^0-9]/g,""));
    const token=++sequence;
    const response=await window.phase1SourceMotionProbe({turn,profile});
    if(token!==sequence)return;
    if(response.kind!=="synthetic-bitemporal-query/v1" ||
       response.clinical_verdict!=="NOT_EVALUATED" ||
       response.target_at!=="2026-01-04" ||
       response.profile!==profile)throw Error("changed original-source contract");
    panel.dataset.completed=String(token);
    panel.dataset.turn=String(turn);
    panel.dataset.profile=profile;
    panel.dataset.known=response.known_at;
    panel.dataset.target=response.target_at;
    panel.dataset.visible=response.temporal_ids.join(",");
    panel.dataset.withheld=response.future_leakage_ids.join(",");
    panel.dataset.static=response.static_snapshot_ids.join(",");
    panel.dataset.outside=response.outside_validity_ids.join(",");
    panel.dataset.conflicts=JSON.stringify(response.declared_conflicts);
    panel.dataset.programSha=response.source_program_sha256;
    panel.dataset.datasetSha=response.source_dataset_sha256;
    panel.dataset.clinical=response.clinical_verdict;
    document.querySelector("#phase1-source-observed").textContent=
      "Turn "+turn+" | "+profile+" | K="+response.known_at+" | V="+response.target_at+
      " | known="+(response.temporal_ids.join(",")||"none")+
      " | future withheld="+(response.future_leakage_ids.join(",")||"none")+
      " | declared conflicts="+JSON.stringify(response.declared_conflicts);
  }
  for(const b of document.querySelectorAll("#phase1-source-choices button")){
    b.addEventListener("click",()=>{
      profile=b.dataset.profile;
      refresh().catch(err=>{panel.dataset.error=err.message;});
    });
  }
  for(const name of ["up","down","left","right","interact","reset"]){
    document.querySelector("#"+name).addEventListener("click",()=>{
      refresh().catch(err=>{panel.dataset.error=err.message;});
    });
  }
  document.addEventListener("keyup",()=>{
    refresh().catch(err=>{panel.dataset.error=err.message;});
  });
  refresh().catch(err=>{panel.dataset.error=err.message;});
})();
</script>
"""


def extend_world(html):
    if (type(html) is not str or html.count("</body>")!=1 or
            html.count('id="phase1-world-two-clock"')!=1 or
            html.count('id="phase1-world-frontier-source"')!=1 or
            'id="phase1-source-motion"' in html):
        raise ValueError("requires exact previously verified two-clock world")
    return html.replace("</body>", OVERLAY+"</body>")


def witness_frame(frame, *, turn, profile, known, target,
                  expected, program_sha, dataset_sha):
    required={"turn","profile","known","target","visible","withheld",
              "static","outside","conflicts","program_sha","dataset_sha","clinical"}
    if type(frame) is not dict or set(frame)!=required:
        raise ValueError("actual browser source frame malformed")
    if (frame["turn"]!=str(turn) or frame["profile"]!=profile or
            frame["known"]!=known or frame["target"]!=target or
            frame["program_sha"]!=program_sha or
            frame["dataset_sha"]!=dataset_sha or
            frame["clinical"]!="NOT_EVALUATED"):
        raise ValueError("wrong source version, cutoff or original executable")
    for label, field in (
        ("visible","temporal_ids"),("withheld","future_leakage_ids"),
        ("static","static_snapshot_ids"),("outside","outside_validity_ids")):
        if frame[label]!=",".join(expected[field]):
            raise ValueError("browser source display disagrees with independently evaluated scope")
    if json.loads(frame["conflicts"])!=expected["declared_conflicts"]:
        raise ValueError("browser erased or invented explicitly declared source conflicts")
    a,b,c=(set(expected[k]) for k in (
        "temporal_ids","future_leakage_ids","static_snapshot_ids"))
    outside=set(expected["outside_validity_ids"])
    if a & b or a|b!=c or c & outside:
        raise ValueError("invalid source evidence partition")
    return {
        "turn":turn,"profile":profile,"known_at":known,"target_at":target,
        "temporal_ids":expected["temporal_ids"],
        "future_leakage_ids":expected["future_leakage_ids"],
        "static_snapshot_ids":expected["static_snapshot_ids"],
        "outside_validity_ids":expected["outside_validity_ids"],
        "declared_conflicts":expected["declared_conflicts"],
        "source_program_sha256":program_sha,
        "source_dataset_sha256":dataset_sha,
        "independent_source_oracle_agreed":True,
    }


def verify_motion(frames, *, world_actions, cutover):
    if type(frames) is not list or len(frames)!=(world_actions+1)*len(PROFILES):
        raise ValueError("missing actual browser source profile frames")
    rows={(r["turn"],r["profile"]):r for r in frames}
    if (len(rows)!=len(frames) or
            set(rows)!={(t,p) for t in range(world_actions+1) for p in PROFILES}):
        raise ValueError("repeated or missing source profile click")
    for profile in PROFILES:
        previous=None
        for turn in range(world_actions+1):
            current=rows[turn,profile]
            if current["independent_source_oracle_agreed"] is not True:
                raise ValueError("source variation has no independent oracle witness")
            if previous:
                if previous["known_at"]>current["known_at"]:
                    raise ValueError("world known-time axis moved backwards")
                if previous["source_dataset_sha256"]!=current["source_dataset_sha256"]:
                    raise ValueError("source observations changed during a fixed-profile game")
                if previous["source_program_sha256"]!=current["source_program_sha256"]:
                    raise ValueError("original emitted program changed during world")
                if not set(previous["temporal_ids"]).issubset(current["temporal_ids"]):
                    raise ValueError("new known source facts disappeared on advancing cutoff")
            previous=current
    before=rows[cutover-1,"original"]
    after=rows[cutover,"original"]
    later=rows[cutover,"later-knowledge"]
    conflict=rows[0,"additional-conflict"]
    if ("delayed-result" not in before["future_leakage_ids"] or
            "delayed-result" in before["temporal_ids"] or
            "delayed-result" not in after["temporal_ids"] or
            "delayed-result" in after["future_leakage_ids"]):
        raise ValueError("unmodified original cutover was not observed")
    if ("delayed-result" not in later["future_leakage_ids"] or
            "delayed-result" in later["temporal_ids"]):
        raise ValueError("later synthetic source posting must remain hidden after original cutover")
    if (not conflict["declared_conflicts"] or
            "synthetic-extra-conflict" not in conflict["temporal_ids"]):
        raise ValueError("explicit source-status conflict not detected by original Python")
    if len({rows[0,p]["source_dataset_sha256"] for p in PROFILES})!=len(PROFILES):
        raise ValueError("different source profiles do not provide independently distinguishable inputs")
    return True


def run_source_motion(*,data_dir,output_dir,parent=run_two_clock):
    from playwright.sync_api import sync_playwright

    data,out=Path(data_dir),Path(output_dir)
    data.mkdir(parents=True,exist_ok=True)
    out.mkdir(parents=True,exist_ok=True)
    prior=parent(data_dir=data,output_dir=out)
    if (prior.get("schema")!="nih-phase1-original-w13-world-two-clock/v1" or
            prior.get("original_native_jobs")!=12 or
            prior.get("both_clock_dimensions_observed") is not True or
            prior.get("independent_source_oracle_agreed") is not True or
            prior.get("preserved_original_native_ancestry") is not True):
        raise ValueError("the original real two-clock native/browser parent is not verified")
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    if len(runtime.snapshot())!=12:
        raise ValueError("source motion may not add or replace native jobs")
    scope=validate_scope(runtime.get("nih-scope-001").inputs)
    proto=runtime.state(PROTOTYPE_JOB).output["prototype"]
    source=proto["python_source"]
    program_sha=digest(source)
    original_dataset=json.loads((out/"temporal_dataset.json").read_text(encoding="utf8"))
    if original_dataset["observations"]!=scope["observations"]:
        raise ValueError("source scope ancestry inconsistent")
    preds=original_dataset["functional_predicates"]
    selected=variants(scope,preds)
    config=json.loads((out/"game-temporal-config.json").read_text())
    plan=runtime.state(GAME_JOB).output["build"]["plan"]
    if (type(plan) is not list or not 2<=len(plan)<=30 or
            config.get("synthetic") is not True or
            type(config.get("cutover_turn")) is not int or
            not 1<=config["cutover_turn"]<=len(plan)):
        raise ValueError("original played game configuration changed")
    journal_before={(str(data/name)):(data/name).read_bytes() for name in (
        "runtime.jsonl","coordinator-windows.jsonl")}
    browser_history_before=(out/"game-temporal-query-events.jsonl").read_bytes()
    html=extend_world((out/"nih-phase1-two-clock-world.html").read_text(encoding="utf8"))
    frames,calls=[],[]
    with TemporaryDirectory(prefix="nih-phase1-source-motion-") as td:
        root=Path(td)
        for name in ("temporal_bridge_server.py","temporal_query.py",
                     "temporal_dataset.json","game-temporal-config.json"):
            (root/name).write_bytes((out/name).read_bytes())
        if (root/"temporal_query.py").read_text()!=source:
            raise ValueError("original program source replaced")
        (root/"temporal-game.html").write_text(html,encoding="utf8")
        source_paths={}
        source_digests={}
        for profile in PROFILES:
            scope_variant=selected[profile]
            payload=deepcopy(original_dataset)
            payload["observations"]=scope_variant["observations"]
            if payload["synthetic"] is not True or payload["functional_predicates"]!=preds:
                raise ValueError("source counterfactual altered executable contract")
            path=root/("temporal_dataset_profile_"+profile+".json")
            raw=json.dumps(payload,sort_keys=True,indent=2)+"\n"
            path.write_text(raw,encoding="utf8")
            source_paths[profile]=path
            source_digests[profile]=digest(raw)
        def known_at(turn):
            return config["known_at_after"] if turn>=config["cutover_turn"] else config["known_at_before"]
        def invoke_verified(profile,turn,target,*,record):
            if type(turn) is not int or not 0<=turn<=len(plan):
                raise ValueError("outside real world turn")
            if profile not in PROFILES or target not in (TARGET,"2026-01-02","2026-01-11"):
                raise ValueError("source probe outside declared date/profile")
            if profile!="original" and target!=TARGET:
                raise ValueError("source motion changes source at fixed validity target only")
            requested={"known_at":known_at(turn),"target_at":target}
            path=source_paths[profile]
            actual=invoke(root/"temporal_query.py",path,requested)
            expected=oracle(selected[profile],preds,
                            known=requested["known_at"],target=requested["target_at"])
            if actual!=expected:
                raise ValueError("native original emitted Python contradicted independent source oracle")
            if record:
                calls.append({
                    "turn":turn,"profile":profile,"request":requested,
                    "program_sha256":program_sha,
                    "dataset_sha256":source_digests[profile],
                    "response_sha256":digest(json.dumps(actual,sort_keys=True)),
                })
            return {**actual,"profile":profile,
                    "source_program_sha256":program_sha,
                    "source_dataset_sha256":source_digests[profile]}
        server=subprocess.Popen(
            [sys.executable,"-I",str(root/"temporal_bridge_server.py"),str(root),"0"],
            cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            port=server.stdout.readline().strip()
            if not port.isdecimal():
                raise ValueError("unchanged original game bridge failed")
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True)
                try:
                    page=browser.new_page()
                    page.expose_binding("phase1OriginalPythonProbe",
                        lambda _source,payload:invoke_verified(
                            "original",payload["turn"],payload["target"],record=False))
                    def source_motion_probe(_source,payload):
                        if (type(payload) is not dict or
                                set(payload)!={"turn","profile"}):
                            raise ValueError("actual UI must request one source profile and world turn")
                        return invoke_verified(payload["profile"],payload["turn"],
                                               TARGET,record=True)
                    page.expose_binding("phase1SourceMotionProbe",source_motion_probe)
                    page.goto(f"http://127.0.0.1:{int(port)}/")
                    def observe(turn,profile):
                        expected=oracle(selected[profile],preds,
                            known=known_at(turn),target=TARGET)
                        panel=page.locator("#phase1-source-motion-panel")
                        fields={
                            k:panel.get_attribute("data-"+key)
                            for k,key in (
                                ("turn","turn"),("profile","profile"),
                                ("known","known"),("target","target"),
                                ("visible","visible"),("withheld","withheld"),
                                ("static","static"),("outside","outside"),
                                ("conflicts","conflicts"),
                                ("program_sha","program-sha"),
                                ("dataset_sha","dataset-sha"),
                                ("clinical","clinical"))
                        }
                        frames.append(witness_frame(
                            fields,turn=turn,profile=profile,
                            known=known_at(turn),target=TARGET,
                            expected=expected,program_sha=program_sha,
                            dataset_sha=source_digests[profile]))
                        if not any(c["turn"]==turn and c["profile"]==profile and
                                   c["request"]=={"known_at":known_at(turn),
                                                  "target_at":TARGET}
                                   for c in calls):
                            raise ValueError("observed source panel was not backed by original Python call")
                    for turn in range(len(plan)+1):
                        if turn:
                            action=plan[turn-1]
                            if action not in ("up","down","left","right","interact"):
                                raise ValueError("unrecognized original game action")
                            page.locator("#"+action).click()
                            page.wait_for_function(
                                "(t) => document.querySelector('#temporal-panel')?.dataset.turn===String(t)",
                                arg=turn,timeout=15000)
                        for profile in PROFILES:
                            panel=page.locator("#phase1-source-motion-panel")
                            previous=panel.get_attribute("data-completed")
                            count=int(previous) if previous is not None else 0
                            page.locator(
                                f'#phase1-source-choices button[data-profile="{profile}"]').click()
                            page.wait_for_function(
                                "(x) => { const d=document.querySelector('#phase1-source-motion-panel')?.dataset; "
                                "return d && Number(d.completed||0)>x.before && "
                                "d.turn===String(x.turn) && d.profile===x.profile; }",
                                arg={"before":count,"turn":turn,"profile":profile},timeout=15000)
                            observe(turn,profile)
                    if page.locator("body").get_attribute("data-solved")!="true":
                        raise ValueError("original played game did not finish")
                    page.screenshot(path=str(out/"nih-phase1-world-source-motion.png"),full_page=True)
                finally:
                    browser.close()
        finally:
            server.terminate()
            try:server.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.communicate()
    verify_motion(frames,world_actions=len(plan),cutover=config["cutover_turn"])
    if ({str(data/name):(data/name).read_bytes() for name in (
            "runtime.jsonl","coordinator-windows.jsonl")}!=journal_before or
            (out/"game-temporal-query-events.jsonl").read_bytes()!=browser_history_before):
        raise ValueError("original twelve-job source journals or Chromium log changed")
    (out/"nih-phase1-world-source-motion.html").write_text(html,encoding="utf8")
    report={
        "schema":SCHEMA,"native_jobs":12,"source_owner":"original Phase 1 scope",
        "prior_world_axes_witnessed":True,"actual_world_actions":len(plan),
        "selected_counterfactual_profiles":list(PROFILES),
        "source_profile_sha256":source_digests,
        "original_emitted_python_sha256":program_sha,
        "actual_browser_source_frames":frames,
        "independently_verified_original_python_calls":calls,
        "actual_world_solved":True,"source_partition_verified":True,
        "source_conflict_found_in_counterfactual":True,
        "original_journals_preserved":True,
        "new_native_job":False,"new_NIH_checkpoint":False,
        "real_historical_registry_version_authenticated":False,
        "clinical_verdict":"NOT_EVALUATED","synthetic_only":True,
        "official_NIH_submission":False,
    }
    (out/"nih-phase1-world-source-motion.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
    return report


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(argv)
    r=run_source_motion(data_dir=a.data_dir,output_dir=a.output_dir)
    print(json.dumps({
        "schema":r["schema"],"native_jobs":r["native_jobs"],
        "world_actions":r["actual_world_actions"],
        "source_frames":len(r["actual_browser_source_frames"]),
        "original_python_calls":len(r["independently_verified_original_python_calls"]),
        "official_NIH_submission":False},sort_keys=True))


if __name__=="__main__":
    raise SystemExit(main())
