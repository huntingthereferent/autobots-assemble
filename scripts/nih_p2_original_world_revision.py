"""Independent original W13 game-world source correction/withdrawal observation.

The exact original emitted temporal_query.py is run unchanged against three
explicitly constructed snapshot datasets. A Playwright game panel chooses
snapshots at actual turns. The outer host checks the result without treating
a source withdrawal as a rule inside the original temporal program. This is
not a 13th worker, historical registry evidence, or a clinical claim.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.nih_phase1_world_frontier import GAME_JOB, PROTOTYPE_JOB, digest
from systems.workspace.nih_prototype_native import invoke
from systems.workspace.nih_scope_native import validate_scope

SCHEMA="nih-p2-original-world-source-revision-chronology/v1"
SNAPSHOTS=("baseline","corrected","withdrawn")
TARGET="2026-01-04"
OVERLAY=r"""
<script id="nih-p2-revision-world">
(()=>{
  if(!document.querySelector("#phase1-axis") ||
     !document.querySelector("#phase1-frontier")) throw Error("original two-clock game absent");
  const section=document.createElement("section");
  section.id="nih-revision-panel";
  section.style.cssText="padding:14px;margin:12px 0;background:#20282c;color:#eee;font:14px monospace;border:1px solid #94a3ae";
  section.innerHTML='<h2 style="font-size:16px">NIH P2 / fictional source correction and withdrawal</h2>'+
    '<div id="nih-revision-choices"></div><p id="nih-revision-status">Awaiting original Python...</p>'+
    '<p>Explicitly synthetic counterfactual snapshots; the native temporal executable has no withdrawal operator.</p>';
  document.querySelector("#phase1-axis").insertAdjacentElement("afterend",section);
  let selected="baseline",seq=0;
  for(const name of ["baseline","corrected","withdrawn"]){
    const btn=document.createElement("button");
    btn.dataset.snapshot=name;btn.textContent=name;
    btn.style.cssText="padding:6px;margin:3px";
    document.querySelector("#nih-revision-choices").append(btn);
  }
  async function refresh(){
    const turn=Number(document.querySelector("#turns").textContent.replace(/[^0-9]/g,""));
    const n=++seq, response=await window.nihRevisionProbe({turn,snapshot:selected});
    if(n!==seq)return;
    if(response.kind!=="synthetic-bitemporal-query/v1" ||
       response.snapshot!==selected || response.target_at!=="2026-01-04" ||
       response.clinical_verdict!=="NOT_EVALUATED")throw Error("wrong original source");
    const d=section.dataset;
    d.completed=String(n);d.turn=String(turn);d.snapshot=selected;
    d.known=response.known_at;d.target=response.target_at;
    d.visible=response.temporal_ids.join(",");d.withheld=response.future_leakage_ids.join(",");
    d.static=response.static_snapshot_ids.join(",");
    d.outside=response.outside_validity_ids.join(",");
    d.conflicts=JSON.stringify(response.declared_conflicts);
    d.programSha=response.original_program_sha256;d.datasetSha=response.snapshot_dataset_sha256;
    d.clinical=response.clinical_verdict;
    document.querySelector("#nih-revision-status").textContent="Turn "+turn+
      " | snapshot="+selected+" | K="+response.known_at+
      " | visible="+(response.temporal_ids.join(",")||"none")+
      " | withheld="+(response.future_leakage_ids.join(",")||"none");
  }
  for(const btn of section.querySelectorAll("button"))
    btn.onclick=()=>{selected=btn.dataset.snapshot;refresh().catch(e=>section.dataset.error=e.message);};
  for(const name of ["up","down","left","right","interact","reset"])
    document.querySelector("#"+name).addEventListener("click",()=>refresh().catch(e=>section.dataset.error=e.message));
  document.addEventListener("keyup",()=>refresh().catch(e=>section.dataset.error=e.message));
  refresh().catch(e=>section.dataset.error=e.message);
})();
</script>
"""

def apply_overlay(html):
    if (type(html) is not str or html.count("</body>")!=1
        or html.count('id="phase1-world-two-clock"')!=1
        or html.count('id="phase1-world-frontier-source"')!=1
        or 'id="nih-p2-revision-world"' in html):
        raise ValueError("requires exact original two-clock game HTML")
    return html.replace("</body>",OVERLAY+"</body>")

def snapshots(scope,original_dataset):
    """Derived synthetic immutable source editions; never edit the native scope."""
    source=validate_scope(scope)
    rows=source["observations"]
    if len(rows)!=2 or {r["id"] for r in rows}!={"prior-note","delayed-result"}:
        raise ValueError("unrecognized native synthetic observation identities")
    if original_dataset.get("observations")!=rows or original_dataset.get("synthetic") is not True:
        raise ValueError("original emitted dataset and native Phase 1 scope disagree")
    baseline=deepcopy(original_dataset)
    revised=deepcopy(original_dataset)
    corrected=deepcopy(next(r for r in rows if r["id"]=="delayed-result"))
    corrected.update(id="corrected-result",object="synthetic-corrected-value",
                     source_ref="synthetic-correction-source",known_at="2026-01-06")
    revised["observations"]=[deepcopy(r) for r in rows if r["id"]!="delayed-result"]+[corrected]
    withdrawn=deepcopy(original_dataset)
    withdrawn["observations"]=[deepcopy(r) for r in rows if r["id"]!="delayed-result"]
    for name,data in (("baseline",baseline),("corrected",revised),("withdrawn",withdrawn)):
        if data["synthetic"] is not True or data["functional_predicates"]!=original_dataset["functional_predicates"]:
            raise ValueError("synthetic source edition violates original code contract")
        if len({r["id"] for r in data["observations"]})!=len(data["observations"]):
            raise ValueError("duplicate source observation in revision")
    return {"baseline":baseline,"corrected":revised,"withdrawn":withdrawn}

def independent_oracle(dataset, *, known, target):
    # Independent host reconstruction: no import from emitted source-program.
    rows=dataset["observations"]
    valid=[r for r in rows if r["valid_from"]<=target<r["valid_to"]]
    visible=[r for r in valid if r["known_at"]<=known]
    withheld=[r for r in valid if r["known_at"]>known]
    conflicts=[]
    for pred in dataset["functional_predicates"]:
        for index,a in enumerate(visible):
            if a["predicate"]!=pred:continue
            for b in visible[index+1:]:
                if b["subject"]==a["subject"] and b["predicate"]==pred and a["object"]!=b["object"]:
                    conflicts.append(sorted((a["id"],b["id"])))
    return {"kind":"synthetic-bitemporal-query/v1",
        "known_at":known,"target_at":target,
        "temporal_ids":sorted(r["id"] for r in visible),
        "future_leakage_ids":sorted(r["id"] for r in withheld),
        "static_snapshot_ids":sorted(r["id"] for r in valid),
        "outside_validity_ids":sorted(r["id"] for r in rows if r not in valid),
        "declared_conflicts":sorted(conflicts),
        "visible_source_refs":sorted(set(r["source_ref"] for r in visible)),
        "clinical_verdict":"NOT_EVALUATED"}

def frame_for_verifier(*,turn,snapshot,known,result,program,edition):
    """One canonical schema for both actual Chromium captures and negative tests."""
    if (type(turn) is not int or turn<0 or snapshot not in SNAPSHOTS
        or type(known) is not str or len(known)!=10
        or type(result) is not dict or result.get("known_at")!=known
        or result.get("target_at")!=TARGET
        or result.get("clinical_verdict")!="NOT_EVALUATED"
        or any(type(x) is not str or len(x)!=64 for x in (program,edition))):
        raise ValueError("invalid original Python source-frame receipt")
    return {"turn":turn,"snapshot":snapshot,
        "known_at":known,"target_at":TARGET,
        "temporal_ids":result["temporal_ids"],
        "future_leakage_ids":result["future_leakage_ids"],
        "snapshot_dataset_sha256":edition,
        "original_program_sha256":program,
        "independent_host_agreement":True}

def validate_frames(frames, *, actions, cutover, program, editions):
    if type(actions) is not int or actions<3 or type(cutover) is not int or cutover<1 or cutover>=actions:
        raise ValueError("original game lacks enough turns to witness withdrawal")
    if type(frames) is not list or len(frames)!=(actions+1)*len(SNAPSHOTS):
        raise ValueError("missing browser revision frames")
    keyed={}
    for row in frames:
        if type(row) is not dict:raise ValueError("not actual original browser frame")
        key=(row.get("turn"),row.get("snapshot"))
        if key in keyed:raise ValueError("duplicate source edition/browser frame")
        keyed[key]=row
    if set(keyed)!={(t,s) for t in range(actions+1) for s in SNAPSHOTS}:
        raise ValueError("missing source edition or turn")
    last={s:None for s in SNAPSHOTS}
    for turn in range(actions+1):
        same_time={keyed[turn,s]["known_at"] for s in SNAPSHOTS}
        if len(same_time)!=1:raise ValueError("source selection changed original game clock")
        for snapshot in SNAPSHOTS:
            row=keyed[turn,snapshot]
            if (row.get("original_program_sha256")!=program
                or row.get("snapshot_dataset_sha256")!=editions[snapshot]
                or row.get("independent_host_agreement") is not True):
                raise ValueError("native program/dataset/browser provenance drifted")
            if last[snapshot] is not None:
                prev=last[snapshot]
                if (prev["known_at"]>row["known_at"] or
                    not set(prev["temporal_ids"]).issubset(row["temporal_ids"])):
                    raise ValueError("fixed-source monotonicity failed")
            last[snapshot]=row
    first=keyed[cutover,"baseline"]
    corrected=keyed[cutover,"corrected"]
    dropped=keyed[cutover,"withdrawn"]
    if ("delayed-result" not in first["temporal_ids"]
        or "corrected-result" not in corrected["temporal_ids"]
        or "delayed-result" in corrected["temporal_ids"]
        or "corrected-result" in dropped["temporal_ids"]
        or "delayed-result" in dropped["temporal_ids"]
        or dropped["temporal_ids"]!=["prior-note"]):
        raise ValueError("synthetic correction or source withdrawal was not actually observed")
    # Explicit staged-source chronology: unchanged original K after the native
    # cutover, changing only which attributed source snapshot is selected.
    timeline=[keyed[cutover,"baseline"],keyed[cutover,"corrected"],
              keyed[cutover+1,"withdrawn"]]
    if not (timeline[0]["known_at"]==timeline[1]["known_at"]==timeline[2]["known_at"]):
        raise ValueError("timeline confounded source change with known-time change")
    if (set(timeline[0]["temporal_ids"]).issubset(timeline[1]["temporal_ids"])
        or set(timeline[1]["temporal_ids"]).issubset(timeline[2]["temporal_ids"])):
        raise ValueError("revision counterexamples did not falsify global monotonicity")
    return [
        {"source_snapshot":"baseline","game_turn":cutover,
         "visible":timeline[0]["temporal_ids"]},
        {"source_snapshot":"corrected","game_turn":cutover,
         "visible":timeline[1]["temporal_ids"]},
        {"source_snapshot":"withdrawn","game_turn":cutover+1,
         "visible":timeline[2]["temporal_ids"]}]

def run_revision(*,data_dir,output_dir,two_clock):
    from playwright.sync_api import sync_playwright
    root,out=Path(data_dir),Path(output_dir)
    if (two_clock.get("schema")!="nih-phase1-original-w13-world-two-clock/v1"
        or two_clock.get("original_native_jobs")!=12
        or two_clock.get("both_clock_dimensions_observed") is not True
        or two_clock.get("preserved_original_native_ancestry") is not True):
        raise ValueError("independently witnessed original two-clock parent required")
    runtime=HandoffRuntime(event_store=RuntimeJournal(root/"runtime.jsonl"))
    if len(runtime.snapshot())!=12:
        raise ValueError("original native workstation changed before research extension")
    scope=validate_scope(runtime.get("nih-scope-001").inputs)
    python=runtime.state(PROTOTYPE_JOB).output["prototype"]["python_source"]
    original=json.loads((out/"temporal_dataset.json").read_text())
    editions=snapshots(scope,original)
    config=json.loads((out/"game-temporal-config.json").read_text())
    plan=runtime.state(GAME_JOB).output["build"]["plan"]
    cut=config["cutover_turn"]
    if (type(plan) is not list or len(plan)<3 or
        type(cut) is not int or cut<1 or cut>=len(plan)
        or config.get("synthetic") is not True):
        raise ValueError("game cutover/witness geometry changed")
    if (out/"temporal_query.py").read_text()!=python:
        raise ValueError("the exact original emitted Python was replaced")
    original_before={name:sha256((root/name).read_bytes()).hexdigest()
        for name in ("runtime.jsonl","coordinator-windows.jsonl")}
    browser_before=sha256((out/"game-temporal-query-events.jsonl").read_bytes()).hexdigest()
    html=apply_overlay((out/"nih-phase1-two-clock-world.html").read_text())
    program=digest(python)
    frames,calls=[],[]
    with TemporaryDirectory(prefix="w13-source-revision-") as folder:
        tmp=Path(folder)
        for name in ("temporal_bridge_server.py","temporal_query.py",
                     "temporal_dataset.json","game-temporal-config.json"):
            (tmp/name).write_bytes((out/name).read_bytes())
        (tmp/"temporal-game.html").write_text(html)
        locations={}
        editions_sha={}
        for name,payload in editions.items():
            raw=json.dumps(payload,sort_keys=True,indent=2)+"\n"
            f=tmp/("temporal_revision_"+name+".json")
            f.write_text(raw)
            locations[name]=f
            editions_sha[name]=digest(raw)
        def game_known(turn):
            return config["known_at_after"] if turn>=cut else config["known_at_before"]
        def query(payload):
            if type(payload) is not dict or set(payload)!={"turn","snapshot"}:
                raise ValueError("unowned original game query")
            turn,snapshot=payload["turn"],payload["snapshot"]
            if type(turn) is not int or not 0<=turn<=len(plan) or snapshot not in SNAPSHOTS:
                raise ValueError("game turn or source edition outside bounds")
            req={"known_at":game_known(turn),"target_at":TARGET}
            observed=invoke(tmp/"temporal_query.py",locations[snapshot],req)
            expected=independent_oracle(editions[snapshot],known=req["known_at"],target=TARGET)
            if observed!=expected:
                raise ValueError("unchanged generated Python diverged from source-independent host oracle")
            calls.append({"turn":turn,"snapshot":snapshot,"request":req,
                          "program_sha256":program,"source_dataset_sha256":editions_sha[snapshot],
                          "response_sha256":digest(json.dumps(observed,sort_keys=True))})
            return {**observed,"snapshot":snapshot,
                "original_program_sha256":program,
                "snapshot_dataset_sha256":editions_sha[snapshot]}
        server=subprocess.Popen([sys.executable,"-I",str(tmp/"temporal_bridge_server.py"),
                    str(tmp),"0"],cwd=tmp,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            port=server.stdout.readline().strip()
            if not port.isdecimal():
                raise ValueError("original generated game loopback bridge failed")
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True)
                try:
                    page=browser.new_page()
                    page.expose_binding("phase1OriginalPythonProbe",
                        lambda _src,payload: {
                        **invoke(tmp/"temporal_query.py",locations["baseline"],
                           {"known_at":game_known(payload["turn"]),
                            "target_at":payload["target"]}),
                        "source_program_sha256":program})
                    page.expose_binding("nihRevisionProbe",lambda _src,payload:query(payload))
                    page.goto(f"http://127.0.0.1:{int(port)}/")
                    for turn in range(len(plan)+1):
                        if turn:
                            action=plan[turn-1]
                            if action not in ("up","down","left","right","interact"):
                                raise ValueError("original game action differs")
                            page.locator("#"+action).click()
                            page.wait_for_function(
                                "(t)=>document.querySelector('#temporal-panel')?.dataset.turn===String(t)",
                                arg=turn,timeout=15000)
                        for name in SNAPSHOTS:
                            panel=page.locator("#nih-revision-panel")
                            last=panel.get_attribute("data-completed")
                            last=int(last) if last is not None else 0
                            page.locator(f'#nih-revision-choices button[data-snapshot="{name}"]').click()
                            page.wait_for_function(
                                "(x)=>{const d=document.querySelector('#nih-revision-panel')?.dataset;"
                                "return d&&Number(d.completed||0)>x.before&&d.turn===String(x.turn)"
                                "&&d.snapshot===x.name;}",
                                arg={"before":last,"turn":turn,"name":name},timeout=15000)
                            expected=independent_oracle(editions[name],
                                known=game_known(turn),target=TARGET)
                            expected_fields={
                                "turn":str(turn),"snapshot":name,
                                "known":game_known(turn),"target":TARGET,
                                "visible":",".join(expected["temporal_ids"]),
                                "withheld":",".join(expected["future_leakage_ids"]),
                                "static":",".join(expected["static_snapshot_ids"]),
                                "outside":",".join(expected["outside_validity_ids"]),
                                "conflicts":json.dumps(expected["declared_conflicts"],separators=(",",":")),
                                "program-sha":program,"dataset-sha":editions_sha[name],
                                "clinical":"NOT_EVALUATED"}
                            actual={key:panel.get_attribute("data-"+key) for key in expected_fields}
                            if actual!=expected_fields:
                                raise ValueError("real Chromium source revision disagrees with independent oracle")
                            if not any(c["turn"]==turn and c["snapshot"]==name and
                                       c["request"]=={"known_at":game_known(turn),"target_at":TARGET}
                                       for c in calls):
                                raise ValueError("UI panel did not execute source-owned original Python")
                            frames.append(frame_for_verifier(turn=turn,
                                snapshot=name,known=game_known(turn),result=expected,
                                program=program,edition=editions_sha[name]))
                    if page.locator("body").get_attribute("data-solved")!="true":
                        raise ValueError("original played game did not solve")
                    page.screenshot(path=str(out/"nih-p2-world-source-revision.png"),full_page=True)
                finally:
                    browser.close()
        finally:
            server.terminate()
            try:server.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill();server.communicate()
    chron=validate_frames(frames,actions=len(plan),cutover=cut,program=program,editions=editions_sha)
    if ({name:sha256((root/name).read_bytes()).hexdigest()
            for name in original_before}!=original_before
        or sha256((out/"game-temporal-query-events.jsonl").read_bytes()).hexdigest()!=browser_before
        or len(HandoffRuntime(event_store=RuntimeJournal(root/"runtime.jsonl")).snapshot())!=12):
        raise ValueError("original W13 journal or browser source history changed")
    report={"schema":SCHEMA,"original_native_jobs":12,
        "native_nih_p2_benchmark_witnessed":True,
        "source_editions":editions_sha,
        "original_program_sha256":program,"original_world_actions":len(plan),
        "actual_browser_snapshot_frames":frames,
        "original_python_snapshot_calls":calls,
        "chronology_counterexample":chron,
        "fixed_snapshot_monotonicity_verified":True,
        "source_changes_break_global_visible_id_monotonicity":True,
        "source_mutations_only_in_disposable_test_datasets":True,
        "original_journals_and_browser_source_unchanged":True,
        "new_native_job":False,"new_NIH_checkpoint":False,
        "synthetic_only":True,"real_historical_source_withdrawal_authenticated":False,
        "clinical_verdict":"NOT_EVALUATED","official_NIH_submission":False}
    (out/"nih-p2-world-source-revision.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report
