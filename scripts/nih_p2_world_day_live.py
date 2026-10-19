"""Live original W13 game: conditional day-granular source version experiment.

30 real Chromium day-selector interactions while four original native-game
actions advance the exact existing room. Native emitted temporal_query.py
executes unmodified for the original game; day-only conditional logic is
an EXPLICIT separate host-side research panel, never native or clinical proof.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from scripts.nih_p2_world_calendar_day_model import (
    SCHEMA as MODEL_SCHEMA,CUTOFFS,validate_source,projection,
    independent_oracle,verify_grid)

SCHEMA="world-nih-p2-owner-reported-calendar-day-live-w13/v1"
SCRIPT=r"""
<script id="world-p2-day-panel-source">
(()=>{
 if(!document.querySelector("#phase1-axis") || !document.querySelector("#phase1-frontier") ||
    !document.querySelector("#temporal-panel"))throw Error("unchanged W13 original game absent");
 const panel=document.createElement("section");panel.id="world-p2-day-panel";
 panel.style.cssText="background:#192b33;color:#edf3f4;border:1px solid #8daab6;padding:12px;margin:12px 0;font:14px monospace";
 panel.innerHTML='<h2 style="font-size:17px">Original registry version / owner-reported posting DAY</h2>'+
   '<p>Conditional day-only source comparison, NOT a verified first-publication instant or clinical outcome.</p>'+
   '<div id="world-day-actions"></div><pre id="world-day-results">Select a day.</pre>';
 document.querySelector("#phase1-axis").insertAdjacentElement("afterend",panel);
 const days=["2019-08-01","2019-08-02","2019-08-03","2019-11-24","2019-11-25","2019-11-26"];
 let count=0;
 for(const day of days){
   const b=document.createElement("button");b.textContent=day;b.dataset.day=day;
   b.style.cssText="padding:6px;margin:3px";
   b.onclick=async()=>{
     const turn=Number(document.querySelector("#turns").textContent.replace(/[^0-9]/g,""));
     const serial=++count,r=await window.originalWorldDayQuery({day,turn});
     if(serial!==count)return;
     if(r.day!==day || r.real_world_availability_authenticated!==false ||
        r.exact_known_at_utc!==null || r.boundary!=="source-reported posted DAY, unknown first-public TIME")
        throw Error("day granularity/source identity incorrectly promoted");
     panel.dataset.completed=String(serial);
     panel.dataset.turn=String(turn);panel.dataset.day=day;
     panel.dataset.ownerHash=r.owner_source_receipt_sha256;
     panel.dataset.programHash=r.original_program_sha256;
     panel.dataset.v94=r.statuses["94"];panel.dataset.v105=r.statuses["105"];
     panel.dataset.latest=JSON.stringify(r.possible_latest_versions);
     panel.dataset.exactKnown=String(r.exact_known_at_utc);
     document.querySelector("#world-day-results").textContent=
       "Game turn "+turn+" | historical date "+day+
       "\nV94: "+r.statuses["94"]+"\nV105: "+r.statuses["105"]+
       "\nPossible latest versions: "+r.possible_latest_versions.join(", ")+" "+
       "\nExact first-publication time: UNKNOWN (source only states calendar days)";
   };
   document.querySelector("#world-day-actions").append(b);
 }
})();
</script>
"""

def digest(raw):
    return sha256(raw if type(raw) is bytes else raw.encode()).hexdigest()

def validate_frames(frames,source,program_sha,owner_sha):
    verify_grid(source)
    if type(frames) is not list or len(frames)!=5*len(CUTOFFS):
        raise ValueError("real browser source-day panel has missing frames")
    keys={(r.get("turn"),r.get("day")) for r in frames}
    if keys!={(t,day) for t in range(5) for day in CUTOFFS}:
        raise ValueError("missing, duplicate or altered original-game day selection")
    for r in frames:
        d=r["day"]
        expected=independent_oracle(source,d)
        if (type(r["turn"]) is not int or
            r.get("owner_source_receipt_sha256")!=owner_sha or
            r.get("original_program_sha256")!=program_sha or
            r.get("statuses")!=expected["statuses"] or
            r.get("possible_latest_versions")!=expected["possible_latest_versions"] or
            r.get("exact_known_at_utc") is not None or
            r.get("real_world_availability_authenticated") is not False or
            r.get("browser_selected_source_day") is not True):
            raise ValueError("Chromium source-day observation failed independent host oracle")
    return True

def run(native,out):
    from runtime.engine import HandoffRuntime
    from runtime.journal import RuntimeJournal
    from systems.workspace.nih_phase1_world_frontier import PROTOTYPE_JOB,GAME_JOB
    from systems.workspace.nih_prototype_native import invoke
    from playwright.sync_api import sync_playwright
    native,out=Path(native),Path(out)
    source_file=out/"world-nih-p2-historical-posted-day-cross-witness.json"
    source_bytes=source_file.read_bytes()
    owner_sha=digest(source_bytes)
    source=json.loads(source_bytes)
    verify_grid(source)
    runtime=HandoffRuntime(event_store=RuntimeJournal(native/"runtime.jsonl"))
    if len(runtime.snapshot())!=12:raise ValueError("original W13 twelve native workers not restored")
    original_program=runtime.state(PROTOTYPE_JOB).output["prototype"]["python_source"]
    program_sha=digest(original_program)
    previous=json.loads((out/"world-nih-p2-source-event-report.json").read_text())
    if (previous.get("original_native_jobs")!=12 or
        previous.get("original_program_sha256")!=program_sha or
        previous.get("original_native_journals_unchanged") is not True):
        raise ValueError("original game source edition or journals changed")
    config=json.loads((out/"game-temporal-config.json").read_text())
    plan=runtime.state(GAME_JOB).output["build"]["plan"]
    if len(plan)!=4 or config.get("cutover_turn")!=2 or config.get("synthetic") is not True:
        raise ValueError("original native world game plan was not recovered")
    initial_html=(out/"nih-phase1-two-clock-world.html").read_text()
    if (initial_html.count("</body>")!=1 or
        initial_html.count('id="phase1-world-two-clock"')!=1 or
        initial_html.count('id="phase1-world-frontier-source"')!=1 or
        'id="world-p2-day-panel-source"' in initial_html):
        raise ValueError("the exact original source world is missing or has been rewritten")
    html=initial_html.replace("</body>",SCRIPT+"</body>")
    before={name:digest((native/name).read_bytes()) for name in ("runtime.jsonl","coordinator-windows.jsonl")}
    prior_browser_sha=digest((out/"game-temporal-query-events.jsonl").read_bytes())
    frames,native_calls,day_calls=[],[],[]
    with TemporaryDirectory(prefix="original-w13-day-calendar-") as path:
        folder=Path(path)
        for name in ("temporal_bridge_server.py","temporal_query.py","temporal_dataset.json","game-temporal-config.json"):
            (folder/name).write_bytes((out/name).read_bytes())
        if (folder/"temporal_query.py").read_text()!=original_program:
            raise ValueError("the original emitted Python program was not preserved")
        (folder/"temporal-game.html").write_text(html)
        def native_query(payload):
            if type(payload) is not dict or set(payload)!={"turn","target"}:
                raise ValueError("original emitted Python query malformed")
            turn=payload["turn"]
            if type(turn) is not int or turn not in range(5):
                raise ValueError("game out of bounds")
            q={"known_at":config["known_at_after"] if turn>=2 else config["known_at_before"],
               "target_at":payload["target"]}
            result=invoke(folder/"temporal_query.py",folder/"temporal_dataset.json",q)
            native_calls.append({"turn":turn,"target":q["target_at"],
                "response_sha256":digest(json.dumps(result,sort_keys=True))})
            return {**result,"source_program_sha256":program_sha}
        def query_day(payload):
            if (type(payload) is not dict or set(payload)!={"turn","day"} or
                type(payload["turn"]) is not int or payload["turn"] not in range(5)):
                raise ValueError("day query not bounded by actual original game turn")
            day=payload["day"]
            result=projection(source,day)
            oracle=independent_oracle(source,day)
            if (result["statuses"]!=oracle["statuses"] or
                result["possible_latest_versions"]!=oracle["possible_latest_versions"]):
                raise ValueError("independent source-date oracle disagrees at live game turn")
            day_calls.append({"turn":payload["turn"],"day":day,"owner_source_receipt_sha256":owner_sha})
            return {**result,"owner_source_receipt_sha256":owner_sha,
                    "original_program_sha256":program_sha}
        proc=subprocess.Popen(
            [sys.executable,"-I",str(folder/"temporal_bridge_server.py"),str(folder),"0"],
            cwd=folder,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            port=proc.stdout.readline().strip()
            if not port.isdecimal():raise ValueError("native W13 web game bridge did not start")
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=True)
                try:
                    page=browser.new_page()
                    page.expose_binding("phase1OriginalPythonProbe",lambda _src,payload:native_query(payload))
                    page.expose_binding("originalWorldDayQuery",lambda _src,payload:query_day(payload))
                    page.goto(f"http://127.0.0.1:{int(port)}/")
                    for turn in range(5):
                        if turn:
                            action=plan[turn-1]
                            if action not in ("up","down","left","right","interact"):
                                raise ValueError("original game action changed")
                            page.locator("#"+action).click()
                            page.wait_for_function(
                                "(n)=>document.querySelector('#temporal-panel')?.dataset.turn===String(n)",
                                arg=turn,timeout=15000)
                        for day in CUTOFFS:
                            panel=page.locator("#world-p2-day-panel")
                            old=int(panel.get_attribute("data-completed") or "0")
                            page.locator(f'#world-day-actions button[data-day="{day}"]').click()
                            page.wait_for_function(
                                "(x)=>{const d=document.querySelector('#world-p2-day-panel')?.dataset;"
                                "return d&&Number(d.completed||0)>x.old&&d.turn===String(x.turn)"
                                "&&d.day===x.day;}",arg={"old":old,"turn":turn,"day":day},timeout=15000)
                            actual=projection(source,day)
                            if (panel.get_attribute("data-v94")!=actual["statuses"]["94"]
                                or panel.get_attribute("data-v105")!=actual["statuses"]["105"]
                                or json.loads(panel.get_attribute("data-latest"))!=actual["possible_latest_versions"]
                                or panel.get_attribute("data-owner-hash")!=owner_sha
                                or panel.get_attribute("data-program-hash")!=program_sha
                                or panel.get_attribute("data-exact-known")!="null"):
                                raise ValueError("original played Chromium calendar-day panel disagrees")
                            frames.append({"turn":turn,"day":day,
                                "owner_source_receipt_sha256":owner_sha,
                                "original_program_sha256":program_sha,
                                "statuses":actual["statuses"],
                                "possible_latest_versions":actual["possible_latest_versions"],
                                "exact_known_at_utc":None,
                                "real_world_availability_authenticated":False,
                                "browser_selected_source_day":True})
                    if page.locator("body").get_attribute("data-solved")!="true":
                        raise ValueError("original native W13 playable game not solved")
                    page.screenshot(path=str(out/"world-nih-p2-live-day-level-room.png"),full_page=True)
                finally:browser.close()
        finally:
            proc.terminate()
            try:proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill();proc.communicate()
    validate_frames(frames,source,program_sha,owner_sha)
    if len(day_calls)!=5*len(CUTOFFS) or len(native_calls)<4:
        raise ValueError("not enough live browser original Python and day calls")
    after={name:digest((native/name).read_bytes()) for name in before}
    if (before!=after or prior_browser_sha!=digest((out/"game-temporal-query-events.jsonl").read_bytes())
        or len(HandoffRuntime(event_store=RuntimeJournal(native/"runtime.jsonl")).snapshot())!=12):
        raise ValueError("source-owned native journals moved during live day experiment")
    result={"schema":SCHEMA,"original_native_jobs":12,"new_native_jobs":0,
        "original_native_journal_sha256":before,
        "source_owner_receipt_sha256":owner_sha,"original_emitted_python_sha256":program_sha,
        "original_game_actions":len(plan),"actual_browser_day_selection_frames":frames,
        "original_python_executions":native_calls,
        "host_day_conditional_evaluations":day_calls,
        "host_day_model_independently_verified":True,
        "native_original_python_modified_to_support_date_model":False,
        "original_native_journals_unchanged":True,
        "historical_version_posted_day_is_source_owner_attested":True,
        "exact_historical_posted_utc_time_authenticated":False,
        "independent_actual_2019_publication_transaction_witnessed":False,
        "unknown_intervening_versions_excluded":False,
        "real_world_clinical_outcome_evaluated":False,
        "official_NIH_submission":False}
    (out/"world-nih-p2-live-day-level-room.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"schema":SCHEMA,"jobs":12,"new_jobs":0,"browser_frames":len(frames),
        "original_python_calls":len(native_calls),
        "host_date_queries":len(day_calls),"original_journals_preserved":True,
        "exact_publication_UTC_instants_verified":False},sort_keys=True))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--native",required=True)
    p.add_argument("--evidence",required=True)
    a=p.parse_args()
    run(a.native,a.evidence)
