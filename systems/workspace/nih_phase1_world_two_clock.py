"""Exercise both independent temporal axes inside the ORIGINAL playable W13 world.

This is a bounded, read-only *follow-on experiment* using the original twelve
native jobs and the separately verified Phase 1 world frontier. Playwright's
exposed binding invokes the ORIGINAL emitted temporal_query.py for selected
valid-time targets on real button clicks; the independent host recomputes from
the ORIGINAL Phase 1 scope. No native source edits, thirteenth job, NIH CP,
clinical inference, or authenticated historical publication time.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .nih_phase1_world_frontier import (
    run_world, digest, check_frame,
    PROTOTYPE_JOB, GAME_JOB,
)
from .nih_prototype_native import oracle, invoke
from .nih_scope_native import validate_scope

SCHEMA = "nih-phase1-original-w13-world-two-clock/v1"
TARGETS = ("2026-01-02", "2026-01-04", "2026-01-11")

# Additional bounded presentation only: the source-owned original game and
# its original /api/query local server are NOT patched or replaced.
# Playwright binding invokes the unchanged original Python program for each
# independently selected validity target. The saved HTML is an inspection
# artifact and requires Playwright's host binding for interactive probes.
OVERLAY = r"""
<script id="phase1-world-two-clock">
(() => {
  if (!document.querySelector("#temporal-panel") ||
      !document.querySelector("#phase1-frontier")) {
    throw Error("the already-witnessed original game world is missing");
  }
  const targets = ["2026-01-02", "2026-01-04", "2026-01-11"];
  const panel = document.createElement("section");
  panel.id = "phase1-axis";
  panel.setAttribute("aria-label", "Phase 1 independent knowledge and validity-time queries");
  panel.style.cssText = "background:#14262a;border:1px solid #8aa4a8;color:#eff2f0;padding:12px;margin:12px 0;font-family:monospace;line-height:1.6";
  const title=document.createElement("h2");
  title.textContent="Phase 1 / two temporal axes";
  title.style.cssText="font-size:16px;margin:0 0 6px";
  panel.appendChild(title);
  const choices=document.createElement("div");
  choices.id="phase1-target-choices";
  for(const date of targets) {
    const b=document.createElement("button");
    b.textContent="Valid at "+date;
    b.dataset.target=date;
    b.style.cssText="margin:3px;padding:5px 7px";
    choices.appendChild(b);
  }
  panel.appendChild(choices);
  const view=document.createElement("p");
  view.id="phase1-axis-observed";
  view.textContent="Reading original Python source for the first target...";
  panel.appendChild(view);
  const note=document.createElement("p");
  note.textContent="Synthetic scope only. Playwright-bound local original-Python queries; not registry source history or clinical evidence.";
  panel.appendChild(note);
  document.querySelector("#phase1-frontier").insertAdjacentElement("afterend", panel);
  let target=targets[0], generation=0;
  async function refresh() {
    const turn=Number(document.querySelector("#turns").textContent.replace(/[^0-9]/g,""));
    const ticket=++generation;
    const result=await window.phase1OriginalPythonProbe({turn,target});
    if(ticket!==generation)return;
    if(result.kind!=="synthetic-bitemporal-query/v1" ||
       result.clinical_verdict!=="NOT_EVALUATED" ||
       result.target_at!==target)throw Error("source response boundary changed");
    panel.dataset.turn=String(turn);
    panel.dataset.known=result.known_at;
    panel.dataset.target=result.target_at;
    panel.dataset.visible=result.temporal_ids.join(",");
    panel.dataset.withheld=result.future_leakage_ids.join(",");
    panel.dataset.static=result.static_snapshot_ids.join(",");
    panel.dataset.querySha=result.source_program_sha256;
    panel.dataset.clinical=result.clinical_verdict;
    panel.dataset.completed=String(ticket);
    view.textContent="Game turn "+turn+" | K="+result.known_at+" | V="+result.target_at+
      " | T: "+(result.temporal_ids.join(",")||"none")+
      " | S: "+(result.static_snapshot_ids.join(",")||"none")+
      " | L: "+(result.future_leakage_ids.join(",")||"none");
  }
  for(const b of choices.querySelectorAll("button")) {
    b.addEventListener("click",()=>{
      target=b.dataset.target;
      refresh().catch(e=>{panel.dataset.error=e.message;});
    });
  }
  for(const name of ["up","down","left","right","interact","reset"]) {
    document.querySelector("#"+name).addEventListener("click",()=>{
      refresh().catch(e=>{panel.dataset.error=e.message;});
    });
  }
  document.addEventListener("keyup",()=>{
    refresh().catch(e=>{panel.dataset.error=e.message;});
  });
  refresh().catch(e=>{panel.dataset.error=e.message;});
})();
</script>
"""


def extend_world_html(html):
    if (type(html) is not str or html.count("</body>") != 1 or
            html.count('id="phase1-world-frontier-source"') != 1 or
            html.count('id="native-temporal-client"') != 1 or
            "phase1-world-two-clock" in html):
        raise ValueError("two-clock experiment requires exact original played world")
    return html.replace("</body>", OVERLAY + "</body>")


def check_axes(frames, *, plan_length, cutover, targets=TARGETS):
    """No fixture/prose result substitutes for actual observed browser frames."""
    if not (type(plan_length) is int and 2 <= plan_length <= 30 and
            type(cutover) is int and 1 <= cutover <= plan_length):
        raise ValueError("actual game path and source cutover required")
    if (type(frames) is not list or
            len(frames) != (plan_length+1)*len(targets)):
        raise ValueError("all independent validity targets must be clicked on every game turn")
    indexed = {}
    for row in frames:
        if type(row) is not dict or set(row) != {
                "turn","known_at","target_at","visible_ids",
                "future_withheld_ids","static_ids","outside_validity_ids",
                "source_program_sha256","independent_scope_agreement"}:
            raise ValueError("frame missing original program source or evidence axes")
        key=(row["turn"],row["target_at"])
        if key in indexed or key[1] not in targets or not 0 <= key[0] <= plan_length:
            raise ValueError("duplicate, invalid or unrelated world axis observation")
        if row["independent_scope_agreement"] is not True:
            raise ValueError("independent oracle must agree")
        v,w,s=(row[n] for n in ("visible_ids","future_withheld_ids","static_ids"))
        if any(type(x) is not list or len(x) != len(set(x)) for x in (v,w,s)):
            raise ValueError("invalid or duplicated frame source identifiers")
        if set(v) & set(w) or set(v) | set(w) != set(s):
            raise ValueError("missing or wrongly leaked source evidence")
        indexed[key]=row
    if {(turn,target) for turn in range(plan_length+1) for target in targets} != set(indexed):
        raise ValueError("original world did not observe every turn and valid-time target")
    whole=set(indexed[0,"2026-01-04"]["static_ids"]) | set(
        indexed[0,"2026-01-04"]["outside_validity_ids"])
    if len(whole) < 2:
        raise ValueError("insufficient original source observations for two clocks")
    for row in frames:
        outside=row["outside_validity_ids"]
        if (type(outside) is not list or len(outside)!=len(set(outside)) or
                set(outside) & set(row["static_ids"]) or
                set(outside) | set(row["static_ids"]) != whole):
            raise ValueError("valid and outside-validity sets must partition original source")
    knowledge_by_turn=[]
    for turn in range(plan_length+1):
        times={indexed[turn,target]["known_at"] for target in targets}
        if len(times)!=1:
            raise ValueError("independent valid-time selection changed game knowledge clock")
        knowledge_by_turn.append(next(iter(times)))
    if (knowledge_by_turn[0] >= knowledge_by_turn[cutover] or
            len(set(knowledge_by_turn[:cutover]))!=1 or
            len(set(knowledge_by_turn[cutover:]))!=1):
        raise ValueError("world known-time axis differs from original cutover")
    for target in targets:
        prev=None
        for turn in range(plan_length+1):
            row=indexed[turn,target]
            if prev:
                if row["known_at"] < prev["known_at"]:
                    raise ValueError("source knowledge time regressed")
                if not set(prev["visible_ids"]).issubset(row["visible_ids"]):
                    raise ValueError("visible evidence regressed without source replacement")
                if row["static_ids"] != prev["static_ids"]:
                    raise ValueError("fixed-validity original dataset changed across game turns")
                if row["source_program_sha256"] != prev["source_program_sha256"]:
                    raise ValueError("changed original generated temporal executable")
            prev=row
    before=indexed[cutover-1,"2026-01-04"]
    after=indexed[cutover,"2026-01-04"]
    if ("delayed-result" not in before["future_withheld_ids"] or
            "delayed-result" in before["visible_ids"] or
            "delayed-result" in after["future_withheld_ids"] or
            "delayed-result" not in after["visible_ids"]):
        raise ValueError("observed original known-time cutover failed")
    if any(indexed[t,"2026-01-11"]["static_ids"] for t in range(plan_length+1)):
        raise ValueError("expired facts remain visible beyond validity end")
    if any("delayed-result" in indexed[t,"2026-01-02"]["static_ids"]
           for t in range(plan_length+1)):
        raise ValueError("not-yet-valid result appears at earlier valid time")
    return True


def run_two_clock(*, data_dir, output_dir, parent=run_world):
    from playwright.sync_api import sync_playwright

    data,out=Path(data_dir),Path(output_dir)
    data.mkdir(parents=True,exist_ok=True)
    out.mkdir(parents=True,exist_ok=True)
    witnessed=parent(data_dir=data,output_dir=out)
    if (witnessed.get("schema")!="nih-phase1-original-w13-world-frontier/v1" or
            witnessed.get("original_native_jobs") != 12 or
            witnessed.get("independent_scope_oracle_agreed") is not True or
            witnessed.get("browser_world_solved") is not True or
            witnessed.get("new_native_job_created") is not False):
        raise ValueError("original source-owned twelve-job browser frontier must pass first")
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    if len(runtime.snapshot()) != 12:
        raise ValueError("two-clock experiment would invent a native worker")
    scope=validate_scope(runtime.get("nih-scope-001").inputs)
    emitted=runtime.state(PROTOTYPE_JOB).output["prototype"]
    program=emitted["python_source"]
    fingerprint=digest(program)
    plan=runtime.state(GAME_JOB).output["build"]["plan"]
    config=json.loads((out/"game-temporal-config.json").read_text())
    if (not isinstance(plan,list) or not 2<=len(plan)<=30 or
            config.get("synthetic") is not True or
            config.get("cutover_turn") not in range(1,len(plan)+1) or
            config.get("known_at_before") >= config.get("known_at_after")):
        raise ValueError("source-owned game time configuration malformed")
    if (out/"temporal_query.py").read_text()!=program:
        raise ValueError("original temporal executable changed")
    dataset=json.loads((out/"temporal_dataset.json").read_text())
    if dataset["observations"] != scope["observations"]:
        raise ValueError("original scope is not exact game source")
    preserved={name:(data/name).read_bytes() for name in
               ("runtime.jsonl","coordinator-windows.jsonl")}
    parent_browser_log=(out/"game-temporal-query-events.jsonl").read_bytes()
    base_html=(out/"nih-phase1-frontier-world.html").read_text(encoding="utf8")
    html=extend_world_html(base_html)
    frames=[]
    calls=[]
    with TemporaryDirectory(prefix="nih-phase1-two-clock-") as td:
        root=Path(td)
        for name in ("temporal_bridge_server.py","temporal_query.py",
                     "temporal_dataset.json","game-temporal-config.json"):
            (root/name).write_bytes((out/name).read_bytes())
        (root/"temporal-game.html").write_text(html,encoding="utf8")
        source=root/"temporal_query.py"
        ds=root/"temporal_dataset.json"
        def source_call(payload):
            if (type(payload) is not dict or
                    set(payload)!={"turn","target"} or
                    type(payload["turn"]) is not int or
                    not 0<=payload["turn"]<=len(plan) or
                    payload["target"] not in TARGETS):
                raise ValueError("only actual bounded world turn and validity target allowed")
            turn,target=payload["turn"],payload["target"]
            known=(config["known_at_after"] if turn>=config["cutover_turn"]
                   else config["known_at_before"])
            req={"known_at":known,"target_at":target}
            observed=invoke(source,ds,req)
            expected=oracle(scope,dataset["functional_predicates"],
                            known=known,target=target)
            if observed!=expected or observed["clinical_verdict"]!="NOT_EVALUATED":
                raise ValueError("original generated Python contradicted independent Phase 1 scope")
            calls.append({"turn":turn,"request":req,"source_program_sha256":fingerprint,
                          "observed_response_sha256":digest(
                              json.dumps(observed,sort_keys=True,separators=(",",":")))})
            return {**observed,"source_program_sha256":fingerprint}
        import subprocess,sys
        server=subprocess.Popen([sys.executable,"-I",
              str(root/"temporal_bridge_server.py"),str(root),"0"],
              cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            port=server.stdout.readline().strip()
            if not port.isdecimal():
                raise ValueError("original game loopback server failed")
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True)
                try:
                    page=browser.new_page()
                    page.expose_binding("phase1OriginalPythonProbe",
                                        lambda _source,payload: source_call(payload))
                    page.goto(f"http://127.0.0.1:{int(port)}/")
                    def snapshot(turn,target):
                        known=(config["known_at_after"] if turn>=config["cutover_turn"]
                               else config["known_at_before"])
                        page.wait_for_function(
                            "(p) => document.querySelector('#phase1-axis')?.dataset.turn===String(p.turn) && "
                            "document.querySelector('#phase1-axis')?.dataset.target===p.target && "
                            "document.querySelector('#phase1-axis')?.dataset.known===p.known",
                            arg={"turn":turn,"target":target,"known":known},timeout=15000)
                        expected=oracle(scope,dataset["functional_predicates"],
                                        known=known,target=target)
                        # Inspect the actual selected target widget, not the original
                        # fixed-target frontier panel.
                        selected=page.locator("#phase1-axis")
                        observation={
                            "turn":selected.get_attribute("data-turn"),
                            "known":selected.get_attribute("data-known"),
                            "target":selected.get_attribute("data-target"),
                            "visible":selected.get_attribute("data-visible"),
                            "withheld":selected.get_attribute("data-withheld"),
                            "static":selected.get_attribute("data-static"),
                            "query_sha":selected.get_attribute("data-query-sha"),
                            "clinical":selected.get_attribute("data-clinical"),
                        }
                        frame=check_frame(observation,turn=turn,known=known,
                                          target=target,source_sha=fingerprint,
                                          expected=expected)
                        if not any(e["turn"]==turn and
                                   e["request"]=={"known_at":known,"target_at":target}
                                   for e in calls):
                            raise ValueError("clicked target did not execute original Python")
                        frames.append({**frame,"outside_validity_ids":
                                       expected["outside_validity_ids"]})
                    for turn in range(len(plan)+1):
                        if turn:
                            act=plan[turn-1]
                            if act not in ("up","down","left","right","interact"):
                                raise ValueError("unexpected original played game action")
                            page.locator("#"+act).click()
                            page.wait_for_function(
                                "(t) => document.querySelector('#temporal-panel')?.dataset.turn===String(t)",
                                arg=turn,timeout=15000)
                        # Every distinct validity target is clicked by the browser,
                        # including one before, within, and after stated source validity.
                        for target in TARGETS:
                            previous=page.locator("#phase1-axis").get_attribute("data-completed")
                            previous_number=int(previous) if previous is not None else 0
                            page.locator(f'#phase1-target-choices button[data-target="{target}"]').click()
                            page.wait_for_function(
                                "(n) => Number(document.querySelector('#phase1-axis')?.dataset.completed || 0)>n",
                                arg=previous_number,timeout=15000)
                            snapshot(turn,target)
                    if page.locator("body").get_attribute("data-solved")!="true":
                        raise ValueError("real original world did not complete")
                    page.screenshot(path=str(out/"nih-phase1-two-clock-live-world.png"),
                                    full_page=True)
                finally:
                    browser.close()
        finally:
            server.terminate()
            try:server.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.communicate()
    check_axes(frames,plan_length=len(plan),cutover=config["cutover_turn"])
    if ({name:(data/name).read_bytes() for name in preserved}!=preserved or
            (out/"game-temporal-query-events.jsonl").read_bytes()!=parent_browser_log):
        raise ValueError("additional world experiment changed original native source receipts")
    (out/"nih-phase1-two-clock-world.html").write_text(html,encoding="utf8")
    report={
        "schema":SCHEMA,"original_native_jobs":12,
        "original_phase1_world_witnessed":True,
        "original_game_solved":True,
        "source_program_sha256":fingerprint,
        "original_runtime_journal_sha256":digest(preserved["runtime.jsonl"]),
        "original_game_browser_log_sha256":digest(parent_browser_log),
        "world_actions":len(plan),"knowledge_cutover_turn":config["cutover_turn"],
        "targets":list(TARGETS),"browser_target_query_frames":frames,
        "actual_original_python_probe_calls":len(calls),
        "probe_source_receipts":calls,
        "both_clock_dimensions_observed":True,
        "independent_source_oracle_agreed":True,
        "preserved_original_native_ancestry":True,
        "native_worker_created":False,"new_cp_witnessed":False,
        "historical_publication_time_authenticated":False,
        "synthetic_only":True,"clinical_verdict":"NOT_EVALUATED",
        "official_NIH_submission":False,
    }
    (out/"nih-phase1-two-clock-world-report.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
    return report


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args(argv)
    report=run_two_clock(data_dir=a.data_dir,output_dir=a.output_dir)
    print(json.dumps({"schema":report["schema"],
        "original_native_jobs":report["original_native_jobs"],
        "world_actions":report["world_actions"],
        "target_frames":len(report["browser_target_query_frames"]),
        "python_probe_calls":report["actual_original_python_probe_calls"],
        "real_registry_evidence_authenticated":False},sort_keys=True))


if __name__=="__main__":
    raise SystemExit(main())
