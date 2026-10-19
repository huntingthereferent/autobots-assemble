"""WORLD branch: synthetic source-event chronology in the retained NIH-P2 W13 game.

A real Chromium play of the original room queries the unchanged emitted Python
against snapshots *derived by replaying* a bounded event chain. This does not
implement revision handling in native Python or authenticate real source owners.
No native job is admitted and the original runtime journal is immutable.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import argparse
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

SCHEMA="world-nih-p2-synthetic-source-event-chronology/v1"
STAGES=("baseline","corrected","withdrawn")
OBSERVED=("2026-01-04T12:00:00","2026-01-04T13:00:00",
          "2026-01-06T09:00:00","2026-01-06T12:00:00",
          "2026-01-06T13:00:00")
TARGET="2026-01-04"
def digest(data):
    if isinstance(data,str): data=data.encode()
    return sha256(data).hexdigest()
def enc(data):
    return json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=True)

def declared_events(original):
    obs=original["observations"]
    match={o["id"]:o for o in obs}
    if set(match)!={"prior-note","delayed-result"} or original["synthetic"] is not True:
        raise ValueError("native Phase 1 source ids not supported by this test")
    old=match["delayed-result"]
    edited=deepcopy(old)
    edited.update(id="corrected-result",object="synthetic-corrected-value",
                  source_ref="synthetic-correction-source",known_at="2026-01-06")
    specs=(
        {"id":"synthetic-event-baseline","kind":"base","turn":0,
         "observed_at":"2026-01-04T09:00:00",
         "source_ref":old["source_ref"],"replaces":None,"replacement":None},
        {"id":"synthetic-event-correction","kind":"correction","turn":2,
         "observed_at":"2026-01-06T08:00:00",
         "source_ref":"synthetic-correction-source","replaces":"delayed-result",
         "replacement":edited},
        {"id":"synthetic-event-withdrawal","kind":"withdrawal","turn":3,
         "observed_at":"2026-01-06T11:00:00",
         "source_ref":"synthetic-correction-source","replaces":"corrected-result",
         "replacement":None},
    )
    prev="0"*64
    events=[]
    for spec in specs:
        e={**spec,"previous_sha256":prev}
        e["event_sha256"]=digest(enc(e))
        prev=e["event_sha256"]
        events.append(e)
    return events

def verified_versions(dataset,events):
    if not isinstance(dataset,dict) or not isinstance(events,list) or len(events)!=3:
        raise ValueError("wrong event-stream shape")
    expected=declared_events(dataset)
    if events!=expected: raise ValueError("source-event owner, order, time, or hash chain changed")
    rows=deepcopy(dataset["observations"])
    states={}
    for event in events:
        if datetime.fromisoformat(event["observed_at"]).isoformat()!=event["observed_at"]:
            raise ValueError("noncanonical source observation timestamp")
        kind=event["kind"]
        if kind=="base":
            if event["turn"]!=0:raise ValueError("not original game source")
        else:
            source_id=event["replaces"]
            found=[r for r in rows if r["id"]==source_id]
            if len(found)!=1:raise ValueError("nonexistent or duplicate source target")
            rows=[r for r in rows if r["id"]!=source_id]
            if kind=="correction":
                rows.append(deepcopy(event["replacement"]))
            elif kind!="withdrawal":raise ValueError("unsupported source operation")
        edition=deepcopy(dataset)
        edition["observations"]=sorted(deepcopy(rows),key=lambda r:r["id"])
        states[{"base":"baseline","correction":"corrected","withdrawal":"withdrawn"}[kind]]=edition
    if tuple(states)!=STAGES:raise ValueError("source event stages changed")
    return states

def check_frames(frames,events,editions,program_sha):
    if type(frames) is not list or len(frames)!=len(OBSERVED):
        raise ValueError("browser game events omitted")
    if len({e["turn"] for e in frames})!=len(frames) or {e["turn"] for e in frames}!=set(range(5)):
        raise ValueError("duplicate or missing original game turns")
    selected=("baseline","baseline","corrected","withdrawn","withdrawn")
    previous=None
    for turn,frame in enumerate(frames):
        stage=selected[turn]
        active_event=events[0 if turn<2 else 1 if turn==2 else 2]
        if (frame["turn"]!=turn or frame["snapshot"]!=stage
            or frame["observed_at"]!=OBSERVED[turn]
            or frame["source_event_sha256"]!=active_event["event_sha256"]
            or frame["source_dataset_sha256"]!=editions[stage]
            or frame["original_program_sha256"]!=program_sha
            or frame["target_at"]!=TARGET
            or frame["host_oracle_agreed"] is not True):
            raise ValueError("browser did not observe source-event state at its game turn")
        if active_event["observed_at"]>frame["observed_at"]:
            raise ValueError("source correction used before it was observable")
        if turn>0 and previous["known_at"]>frame["known_at"]:
            raise ValueError("original game knowledge clock ran backwards")
        previous=frame
    if (frames[2]["known_at"]!=frames[3]["known_at"]
        or frames[1]["known_at"]>=frames[2]["known_at"]
        or "corrected-result" not in frames[2]["visible_ids"]
        or "corrected-result" in frames[3]["visible_ids"]
        or frames[3]["visible_ids"]!=["prior-note"]
        or frames[0]["visible_ids"]!=["prior-note"]):
        raise ValueError("source correction/withdrawal counterexample not witnessed")
    return True

SCRIPT=r"""
<script id="world-p2-event-source">
(()=>{
 const native=document.querySelector("#phase1-axis");
 if(!native || !document.querySelector("#phase1-frontier"))throw Error("W13 original game absent");
 const section=document.createElement("section");section.id="world-event-provenance";
 section.style.cssText="background:#18292d;color:#ecf4f3;border:1px solid #91aeb7;padding:12px;margin:12px 0;font:14px monospace";
 section.innerHTML='<h2 style="font-size:16px">Phase 2 / Source events</h2><button id="source-event-inspect">Inspect actual source state</button><pre id="source-event-report">Awaiting source...</pre><p>Constructed synthetic event ownership, not authenticated real registry history.</p>';
 native.insertAdjacentElement("afterend",section);
 let counter=0;
 document.querySelector("#source-event-inspect").onclick=async()=>{
   const turn=Number(document.querySelector("#turns").textContent.replace(/[^0-9]/g,""));
   const seq=++counter,result=await window.originalWorldEventProbe({turn});
   if(seq!==counter)return;
   if(result.kind!=="synthetic-bitemporal-query/v1" || result.clinical_verdict!=="NOT_EVALUATED")throw Error("synthetic source changed");
   section.dataset.turn=String(turn);section.dataset.completed=String(seq);
   section.dataset.snapshot=result.snapshot;
   section.dataset.sourceEvent=result.source_event_sha256;
   section.dataset.visible=result.temporal_ids.join(",");
   section.dataset.known=result.known_at;
   document.querySelector("#source-event-report").textContent=
     "Turn "+turn+" / "+result.snapshot+" / K="+result.known_at+
     "\nsource-event="+result.source_event_sha256.slice(0,20)+
     "\nvisible="+result.temporal_ids.join(",");
 };
})();
</script>
"""

def run(native,out):
    from runtime.engine import HandoffRuntime
    from runtime.journal import RuntimeJournal
    from systems.workspace.nih_phase1_world_frontier import GAME_JOB,PROTOTYPE_JOB
    from systems.workspace.nih_prototype_native import invoke
    from systems.workspace.nih_scope_native import validate_scope
    from scripts.nih_p2_original_world_revision import independent_oracle,snapshots
    from playwright.sync_api import sync_playwright
    native,out=Path(native),Path(out)
    runtime=HandoffRuntime(event_store=RuntimeJournal(native/"runtime.jsonl"))
    if len(runtime.snapshot())!=12:raise ValueError("the original W13 native journal is absent")
    scope=validate_scope(runtime.get("nih-scope-001").inputs)
    original=json.loads((out/"temporal_dataset.json").read_text())
    if original["observations"]!=scope["observations"]:
        raise ValueError("source owner inputs changed")
    events=declared_events(original)
    editions=verified_versions(original,events)
    if editions!=snapshots(scope,original):
        raise ValueError("event replay differs from independently witnessed source editions")
    previous=json.loads((out/"nih-p2-world-source-revision.json").read_text())
    if (previous["schema"]!="nih-p2-original-world-source-revision-chronology/v1"
        or previous["original_native_jobs"]!=12
        or previous["original_journals_and_browser_source_unchanged"] is not True):
        raise ValueError("parent revision experiment not witnessed")
    hashes={}
    for name,edition in editions.items():
        raw=json.dumps(edition,sort_keys=True,indent=2)+"\n"
        hashes[name]=digest(raw)
    if hashes!=previous["source_editions"]:raise ValueError("source-derived snapshots differ from prior live game")
    code=runtime.state(PROTOTYPE_JOB).output["prototype"]["python_source"]
    program_sha=digest(code)
    if program_sha!=previous["original_program_sha256"]:raise ValueError("original emitted code digest changed")
    config=json.loads((out/"game-temporal-config.json").read_text())
    plan=runtime.state(GAME_JOB).output["build"]["plan"]
    if not (len(plan)==4 and config.get("cutover_turn")==2
            and config.get("synthetic") is True):
        raise ValueError("this bounded original game turn configuration is different")
    source_html=(out/"nih-phase1-two-clock-world.html").read_text()
    if (source_html.count("</body>")!=1
        or source_html.count('id="phase1-world-two-clock"')!=1
        or source_html.count('id="phase1-world-frontier-source"')!=1):
        raise ValueError("original room HTML missing")
    html=source_html.replace("</body>",SCRIPT+"</body>")
    before={name:digest((native/name).read_bytes()) for name in ("runtime.jsonl","coordinator-windows.jsonl")}
    browser_source_before=digest((out/"game-temporal-query-events.jsonl").read_bytes())
    frames=[]
    calls=[]
    with TemporaryDirectory(prefix="world-w13-p2-events-") as folder:
        root=Path(folder)
        for name in ("temporal_bridge_server.py","temporal_query.py","temporal_dataset.json","game-temporal-config.json"):
            (root/name).write_bytes((out/name).read_bytes())
        if (root/"temporal_query.py").read_text()!=code:
            raise ValueError("original executable was not preserved")
        (root/"temporal-game.html").write_text(html)
        editions_paths={}
        for stage,payload in editions.items():
            file=root/("source_edition_"+stage+".json")
            file.write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n")
            editions_paths[stage]=file
        def game_known(turn):
            return config["known_at_after"] if turn>=2 else config["known_at_before"]
        def query(turn):
            if type(turn) is not int or turn not in range(5):
                raise ValueError("not an observed W13 game turn")
            stage=STAGES[0 if turn<2 else 1 if turn==2 else 2]
            event=events[0 if turn<2 else 1 if turn==2 else 2]
            payload={"known_at":game_known(turn),"target_at":TARGET}
            result=invoke(root/"temporal_query.py",editions_paths[stage],payload)
            expected=independent_oracle(editions[stage],known=payload["known_at"],target=TARGET)
            if result!=expected:
                raise ValueError("native Python disagreed with event-derived source oracle")
            calls.append({"turn":turn,"source_event_sha256":event["event_sha256"],
                          "source_dataset_sha256":hashes[stage],"query":payload,
                          "response_sha256":digest(enc(result))})
            return {**result,"snapshot":stage,"source_event_sha256":event["event_sha256"]}
        server=subprocess.Popen([sys.executable,"-I",str(root/"temporal_bridge_server.py"),str(root),"0"],
                cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            port=server.stdout.readline().strip()
            if not port.isdecimal():raise ValueError("native room bridge not started")
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=True)
                try:
                    page=browser.new_page()
                    page.expose_binding("phase1OriginalPythonProbe",
                        lambda _src,payload:{
                            **invoke(root/"temporal_query.py",editions_paths["baseline"],
                               {"known_at":game_known(payload["turn"]),"target_at":payload["target"]}),
                            "source_program_sha256":program_sha})
                    page.expose_binding("originalWorldEventProbe",
                        lambda _src,payload:query(payload["turn"]) if type(payload) is dict
                           and set(payload)=={"turn"} else (_ for _ in ()).throw(ValueError("malformed original game event")))
                    page.goto(f"http://127.0.0.1:{int(port)}/")
                    for turn in range(5):
                        if turn:
                            action=plan[turn-1]
                            if action not in ("up","down","left","right","interact"):
                                raise ValueError("original game action changed")
                            page.locator("#"+action).click()
                            page.wait_for_function("(n)=>document.querySelector('#temporal-panel')?.dataset.turn===String(n)",
                                                arg=turn,timeout=15000)
                        panel=page.locator("#world-event-provenance")
                        previous=panel.get_attribute("data-completed")
                        prev=int(previous) if previous is not None else 0
                        page.locator("#source-event-inspect").click()
                        page.wait_for_function("(args)=>{const e=document.querySelector('#world-event-provenance')?.dataset;"
                           "return e&&Number(e.completed||0)>args.prev&&e.turn===String(args.turn);}",
                           arg={"prev":prev,"turn":turn},timeout=15000)
                        result=query(turn)
                        event=events[0 if turn<2 else 1 if turn==2 else 2]
                        if (panel.get_attribute("data-source-event")!=event["event_sha256"]
                            or panel.get_attribute("data-snapshot")!=result["snapshot"]
                            or panel.get_attribute("data-visible")!=",".join(result["temporal_ids"])):
                            raise ValueError("actual clicked browser source event does not match executed program")
                        frames.append({"turn":turn,"snapshot":result["snapshot"],
                           "observed_at":OBSERVED[turn],"source_event_sha256":event["event_sha256"],
                           "source_dataset_sha256":hashes[result["snapshot"]],
                           "original_program_sha256":program_sha,
                           "known_at":result["known_at"],"target_at":result["target_at"],
                           "visible_ids":result["temporal_ids"],"host_oracle_agreed":True})
                    if page.locator("body").get_attribute("data-solved")!="true":
                        raise ValueError("original playable room not solved")
                    page.screenshot(path=str(out/"world-nih-p2-source-event-game.png"),full_page=True)
                finally:browser.close()
        finally:
            server.terminate()
            try:server.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.communicate()
    check_frames(frames,events,hashes,program_sha)
    after={name:digest((native/name).read_bytes()) for name in before}
    if (after!=before or browser_source_before!=digest((out/"game-temporal-query-events.jsonl").read_bytes())
       or len(HandoffRuntime(event_store=RuntimeJournal(native/"runtime.jsonl")).snapshot())!=12):
        raise ValueError("native source journal changed during provenance test")
    report={"schema":SCHEMA,"original_native_jobs":12,
         "source_event_count":len(events),"source_event_chain_sha256":events[-1]["event_sha256"],
         "source_events":events,"source_datasets_sha256":hashes,
         "original_program_sha256":program_sha,"observed_game_actions":len(plan),
         "actual_browser_frames":frames,"original_python_query_receipts":calls,
         "fixed_knowledge_day_revision_falsified_global_monotonicity":True,
         "source_events_are_constructed_not_authenticated":True,
         "source_signature_authenticated":False,
         "original_native_journals_unchanged":True,"new_native_jobs":0,
         "new_NIH_checkpoint":False,"clinical_verdict":"NOT_EVALUATED",
         "official_NIH_submission":False,"historical_source_event_authenticated":False}
    (out/"world-nih-p2-source-event-report.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"schema":SCHEMA,"native_jobs":12,"source_events":len(events),
        "game_frames":len(frames),"original_python_calls":len(calls),
        "native_journals_unchanged":True,"new_native_jobs":0,
        "historical_authentication":False},sort_keys=True))
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--native",type=Path,required=True)
    ap.add_argument("--evidence",type=Path,required=True)
    args=ap.parse_args()
    run(args.native,args.evidence)
if __name__=="__main__":main()
