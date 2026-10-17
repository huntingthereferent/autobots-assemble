"""Game/temporal live WITNESS: actual browser actions call actual built Python."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import subprocess,sys
from urllib.request import urlopen

from runtime.engine import HandoffRuntime
from runtime.handoff import HandoffEvent
from runtime.journal import RuntimeJournal
from .controls import reverify_job
from .game_temporal_bridge import JOB_ID, LiveJoinBridge
from .workstation import ProcessWorkstation

EVENT="GAME_TEMPORAL_LIVE_BROWSER_RETURNED"

def witness(*,data_dir:Path,output_dir:Path):
    from playwright.sync_api import sync_playwright
    data,root=Path(data_dir),Path(output_dir)
    reverify_job(data_dir=data,job_id=JOB_ID)
    runtime=HandoffRuntime(event_store=RuntimeJournal(data/"runtime.jsonl"))
    handoff=runtime.get(JOB_ID)
    built=runtime.state(JOB_ID).output["bundle"]
    if handoff.metadata.get("worker_id")!="game-temporal-live-join":
        raise ValueError("not exact bounded game temporal job")
    manifest={
        "temporal-game.html":built["html"],
        "temporal_bridge_server.py":built["server_source"],
        "temporal_query.py":built["temporal_source"],
        "temporal_dataset.json":built["temporal_dataset"],
        "game-temporal-config.json":json.dumps(built["config"],sort_keys=True,indent=2)+"\n",
    }
    for name,content in manifest.items():
        p=root/name
        if p.exists() and p.read_text(encoding="utf8")!=content:
            raise ValueError("published source-owned live test bundle changed")
        p.write_text(content,encoding="utf8")
    server=subprocess.Popen([sys.executable,"-I",str(root/"temporal_bridge_server.py"),str(root),"0"],
                            cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        portline=server.stdout.readline().strip()
        if not portline.isdecimal():
            raise ValueError("native temporal loopback did not start")
        base=f"http://127.0.0.1:{int(portline)}/"
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            try:
                page=browser.new_page()
                page.goto(base)
                plan=runtime.state("build-game-room-v1").output["build"]["plan"]
                cut=built["config"]["cutover_turn"]
                before=built["config"]["known_at_before"]
                after=built["config"]["known_at_after"]
                page.wait_for_function("document.querySelector('#temporal-panel')?.dataset.known === '"+before+"'",timeout=12000)
                if page.locator("#temporal-panel").get_attribute("data-leakage")!="delayed-result":
                    raise ValueError("game did not show withheld future synthetic record at start")
                for i,action in enumerate(plan,1):
                    page.locator("#"+action).click()
                    expected=after if i>=cut else before
                    page.wait_for_function(
                        "document.querySelector('#temporal-panel')?.dataset.turn === '"+str(i)+"' && "+
                        "document.querySelector('#temporal-panel')?.dataset.known === '"+expected+"'",
                        timeout=12000)
                    if i>=cut and page.locator("#temporal-panel").get_attribute("data-leakage")!="":
                        raise ValueError("actual CLI kept later-known result withheld after game turn")
                if page.locator("body").get_attribute("data-solved")!="true":
                    raise ValueError("original built room did not complete")
                if "delayed-result" not in (page.locator("#temporal-panel").get_attribute("data-visible") or ""):
                    raise ValueError("temporal program failed to reveal formerly withheld result")
                sha=page.locator("#temporal-panel").get_attribute("data-query-sha")
                if sha!=sha256(built["temporal_source"].encode()).hexdigest():
                    raise ValueError("browser did not call original source-owned temporal program")
                page.screenshot(path=str(root/"game-temporal-browser-witness.png"),full_page=True)
            finally:
                browser.close()
    finally:
        server.terminate()
        try:server.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill();server.communicate()
    logs=(root/"game-temporal-query-events.jsonl").read_text().splitlines()
    events=[json.loads(l) for l in logs]
    if (len(events)<len(plan)+1 or
            not any(e["result"]["future_leakage_ids"]==["delayed-result"] for e in events) or
            not any(e["turn"]>=cut and e["result"]["temporal_ids"]==["delayed-result","prior-note"]
                    for e in events)):
        raise ValueError("live GAME->actual-Python-query transition not witnessed")
    proof={"job_id":JOB_ID,
           "kind":"game-temporal-live-browser-witness/v1",
           "original_game_job":"build-game-room-v1",
           "original_prototype_job":"nih-prototype-001",
           "live_queries":len(events),
           "game_actions":len(plan),
           "game_solved":True,
           "future_leakage_detected":True,
           "future_became_knowable_after_turn":cut,
           "temporal_cli_sha256":sha256(built["temporal_source"].encode()).hexdigest(),
           "formal_phase2_test_cp":"BLOCKED_BY_GAME_WORKER_READY",
           "synthetic_only":True}
    prior=[e for e in runtime.event_store.for_handoff(JOB_ID) if e.event_type==EVENT]
    if prior:
        if len(prior)!=1 or prior[0].data!=proof:
            raise ValueError("conflicting witness for original native job")
        new=False
    else:
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=JOB_ID,event_type=EVENT,actor_id="independent-live-chromium-witness",
            data=proof,parents=(runtime.state(JOB_ID).last_event_id,)))
        new=True
    (root/"game-temporal-witness.json").write_text(
        json.dumps({**proof,"new_journal_event":new},sort_keys=True,indent=2)+"\n")
    return {**proof,"new_journal_event":new}
