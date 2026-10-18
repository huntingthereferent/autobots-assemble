"""Source-reverify the seven-job synthetic live temporal parent in its OWN journal.

This is not the historical owner-W13 child journal and not permission to
combine independently constructed timelines. No workers are admitted/executed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .native_receipt_projection import reverify_local
from .game_temporal_bridge import (
    JOB_ID,WORKER_ID,VERSION as RESULT_KIND,VERIFIER)
from .game_temporal_stack import VERSION as EDITION

SCHEMA="source-native-live-temporal-parent-witness/v1"
ORIGINAL_SEVEN=frozenset((
    "nih-scope-001","ontology-job","nih-reasoning-001",
    "nih-packet-001","nih-prototype-001",
    "build-game-room-v1",JOB_ID
))
SOURCE_PARENTS=("build-game-room-v1","nih-prototype-001")
OWNER_W13=("game-w13-github-001","game-native-verifier-github-001")
BROWSER_EVENT="GAME_TEMPORAL_LIVE_BROWSER_RETURNED"


def require_isolated_source_lineage(job_ids)->None:
    """A completed *separate* synthetic stack cannot stand in for owner W13."""
    if type(job_ids) not in (tuple,list,set,frozenset) or set(job_ids)!=ORIGINAL_SEVEN:
        raise ValueError("seven exact source-owned live temporal jobs required")
    if any(j in job_ids for j in OWNER_W13):
        raise ValueError("owner W13 histories cannot be joined by matching CP names")


def source_witness(*,data_dir:Path,output_dir:Path)->dict:
    data=Path(data_dir).resolve()
    output=Path(output_dir).resolve()
    journal=data/"runtime.jsonl"
    summary=output/"game-temporal-complete-stack.json"
    browser=output/"game-temporal-witness.json"
    for f in (journal,summary,browser):
        if not f.is_file() or f.is_symlink() or f.stat().st_size>4_000_000:
            raise ValueError("original local journal, stack report and browser proof required")
    result=json.loads(summary.read_text(encoding="utf8"))
    proof=json.loads(browser.read_text(encoding="utf8"))
    if (result.get("schema")!="complete-stack-live-temporal-game/v1"
            or result.get("source_owned_jobs")!=7
            or result.get("new_native_build")!=JOB_ID
            or result.get("game_temporal_browser")!="PASS"
            or result.get("source_owned_witness") is not True
            or result.get("synthetic_only") is not True
            or result.get("formally_witnessed_nih_p2_test") is not False
            or result.get("formal_cp_status")!="BLOCKED"
            or "GAME-WORKER-READY" not in result.get("formal_cp_blocked_by",())):
        raise ValueError("source-native synthetic browser/CP boundary incomplete")
    if (proof.get("kind")!="game-temporal-live-browser-witness/v1"
            or proof.get("job_id")!=JOB_ID
            or proof.get("original_game_job")!=SOURCE_PARENTS[0]
            or proof.get("original_prototype_job")!=SOURCE_PARENTS[1]
            or proof.get("game_solved") is not True
            or proof.get("future_leakage_detected") is not True
            or proof.get("synthetic_only") is not True
            or proof.get("formal_phase2_test_cp")!="BLOCKED_BY_GAME_WORKER_READY"
            or type(proof.get("live_queries")) is not int
            or proof["live_queries"]<5):
        raise ValueError("original Chromium browser-to-Python live source evidence missing")

    runtime=HandoffRuntime(event_store=RuntimeJournal(journal))
    require_isolated_source_lineage(tuple(runtime.snapshot()))
    handoff=runtime.get(JOB_ID)
    md=handoff.metadata
    if (handoff.dependencies!=SOURCE_PARENTS
            or md.get("source_system")!="process-workstation"
            or md.get("worker_id")!=WORKER_ID
            or md.get("worker_version")!=EDITION
            or md.get("native_evidence_verifier")!=VERIFIER
            or runtime.state(JOB_ID).status!="COMPLETE"):
        raise ValueError("live source parent edition, dependencies or completion changed")

    # Separately reverify all three actual source-owned native parents.
    receipts={}
    for job in (*SOURCE_PARENTS,JOB_ID):
        rec=reverify_local(data,job)
        results=[x for x in rec["events"] if
                 x["type"]=="RESULT" and x["result_status"]=="COMPLETE"]
        if (rec["recorded_status"]!="COMPLETE"
                or rec["verification"]!="FRESH_NATIVE_REVERIFICATION_LOCAL"
                or len(results)!=1):
            raise ValueError("one original native parent lost its independently verified RESULT")
        receipts[job]=rec

    events=[e for e in runtime.event_store.for_handoff(JOB_ID)
            if e.event_type==BROWSER_EVENT]
    # The browser report adds new_journal_event only when written to disk;
    # the original native journal event contains the actual browser proof.
    actual={k:v for k,v in proof.items() if k!="new_journal_event"}
    if len(events)!=1 or events[0].data!=actual:
        raise ValueError("browser return is not in the original native event lineage")
    if receipts[JOB_ID]["source_fingerprint"]!=md.get("edition_fingerprint"):
        raise ValueError("fresh source fingerprint differs from original live handoff")

    events_result=[x for x in receipts[JOB_ID]["events"] if x["type"]=="RESULT"]
    return {
        "schema":SCHEMA,
        "relation":"SEPARATE_SYNTHETIC_LIVE_TEMPORAL_PARENT_NATIVE_WITNESSED",
        "native_job_id":JOB_ID,
        "native_result_event_id":events_result[0]["event_id"],
        "browser_event_id":events[0].event_id,
        "native_worker_id":WORKER_ID,
        "native_worker_version":EDITION,
        "native_source_fingerprint":receipts[JOB_ID]["source_fingerprint"],
        "parent_jobs":list(SOURCE_PARENTS),
        "source_owned_jobs":7,
        "browser_game_solved":True,
        "browser_live_queries":proof["live_queries"],
        "native_parents_freshly_reverified":True,
        "ready_owner_w13_join_proven":False,
        "owner_w13_parent_or_child_replayed_here":False,
        "owner_w13_child_journal_present":False,
        "game_worker_ready_witnessed":False,
        "official_nih_phase2_or_external_claim":False,
        "synthetic_only":True,
        "no_native_job_executed_by_witness":True,
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir",required=True,type=Path)
    parser.add_argument("--output-dir",required=True,type=Path)
    a=parser.parse_args(argv)
    receipt=source_witness(data_dir=a.data_dir,output_dir=a.output_dir)
    (a.output_dir/"live-temporal-parent-native-receipt.json").write_text(
        json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps(receipt,sort_keys=True))


if __name__=="__main__":
    main()
