"""Run existing NIH temporal bounded workers alongside playable game BUILD in Complete Stack.

The two lanes share the ORIGINAL Process Workstation RuntimeJournal and the
original CP coordinator index. Distinct source-owned verifiers are preserved.
Their planned Phase-2 test join remains blocked pending its real dependencies.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .workstation import ProcessWorkstation
from .controls import run_job, reverify_job
from .game_build_stack import construct, JOB_ID as GAME_JOB
from .game_build_native import WORKER_ID as GAME_WORKER
from .nih_scope_bridge import NIHScopeBridge, copy_scope_source, WORKER_ID as SCOPE_WORKER
from .nih_ontology_bridge import NIHOntologyBridge, copy_ontology_source, WORKER_ID as ONTO_WORKER
from .nih_reasoning_bridge import NIHReasoningBridge, copy_reasoning_source, WORKER_ID as REASON_WORKER
from .nih_packet_bridge import NIHPacketBridge, copy_packet_source, WORKER_ID as PACKET_WORKER
from .coordinator_window import (CoordinatorIndex, from_existing_workstation,
                                 freshly_reverify_linked_jobs, run_exact_linked_job)
from .cp_motion import admit_research, one_cp_handoff, workstation_cp_view

ROOT = Path(__file__).resolve().parents[2]
INPUTS = ROOT / "network/tests/fixtures"
WINDOW = "complete-stack"
SOURCES = (
    ("NIH-P1-SCOPE", SCOPE_WORKER, "scope-v1", "nih-scope-001",
     "nih_scope_example.json", copy_scope_source, NIHScopeBridge),
    ("NIH-P1-ONTOLOGY", ONTO_WORKER, "ontology-v1", "ontology-job",
     "nih_ontology_example.json", copy_ontology_source, NIHOntologyBridge),
    ("NIH-P1-REASONING", REASON_WORKER, "reasoning-v1", "nih-reasoning-001",
     "nih_reasoning_example.json", copy_reasoning_source, NIHReasoningBridge),
)


PACKET_SPEC = (
    "NIH-P1-PACKET", PACKET_WORKER, "packet-v1", "nih-packet-001",
    "nih_packet_example.json", copy_packet_source, NIHPacketBridge,
)


def _current(data):
    return HandoffRuntime(event_store=RuntimeJournal(data / "runtime.jsonl"))


def _slot(index, lane, slot):
    _, links = index.definition(WINDOW)
    return next((item for item in links.get(lane, ()) if item["slot"] == slot), None)


def _native_temporal_job(data, index, cp, worker, version, job, fixture, copier, adapter):
    """Copy source -> exact admission/binding -> authorized worker -> fresh verifier."""
    path = INPUTS / fixture
    payload = json.loads(path.read_text(encoding="utf8"))
    desk = ProcessWorkstation(data / "workstation")
    try:
        desk.inspect(worker_id=worker, version_id=version)
    except KeyError:
        copier(data, version_id=version, allow_copy=True)
    runtime = _current(data)
    if job not in runtime.snapshot():
        adapter(runtime=runtime, workstation=desk).admit(
            version_id=version, inputs=payload, from_actor="complete-stack-temporal-world",
            job_id=job)
    else:
        handoff = runtime.get(job)
        if handoff.metadata.get("worker_id") != worker or handoff.metadata.get("worker_version") != version:
            raise ValueError("existing NIH temporal job identity differs")
    slot = "cp-" + cp.lower()
    existing = _slot(index, "nih", slot)
    if existing["source_kind"] == "planned":
        index.bind_planned(WINDOW, "nih", slot=slot, job_id=job,
                           worker_id=worker, version_id=version)
    elif (existing.get("source_kind"), existing.get("job_id"),
          existing.get("worker_id"), existing.get("version_id")) != (
          "runtime-job", job, worker, version):
        raise ValueError("NIH CP slot bound to another source worker")
    view = from_existing_workstation(data)
    moved = run_exact_linked_job(
        index, WINDOW, "nih", slot, job, view,
        lambda job_id, confirm: run_job(
            data_dir=data, job_id=job_id, confirm_execute=confirm))
    if moved["status"] != "COMPLETE" or reverify_job(data_dir=data, job_id=job)["status"] != "COMPLETE":
        raise ValueError("native temporal worker has not returned independently checked evidence")
    return job


def _game_member(index, data, output, world):
    game = construct(data_dir=data, world=world, output_dir=output)
    current = _slot(index, "game", "game-build-playable-world")
    if current is None:
        index.link_runtime(WINDOW, "game", slot="game-build-playable-world",
                           job_id=GAME_JOB, worker_id=GAME_WORKER, version_id="source-v1")
    elif (current.get("source_kind"), current.get("job_id"),
          current.get("worker_id"), current.get("version_id")) != (
          "runtime-job", GAME_JOB, GAME_WORKER, "source-v1"):
        raise ValueError("existing game BUILD link changed")
    return game


def join(*, data_dir: Path, output_dir: Path, browser_witness: bool = False, packet_build: bool = False):
    data, output = Path(data_dir), Path(output_dir)
    data.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    index = CoordinatorIndex(data / "coordinator-windows.jsonl")
    admit_research(index)
    completed = []
    for spec in SOURCES:
        completed.append(_native_temporal_job(data, index, *spec))
    packet_artifact = None
    if packet_build:
        # The source-owned bounded worker writes the new research packet;
        # the coordinator only publishes its native-reverified artifact.
        packet_job = _native_temporal_job(data, index, *PACKET_SPEC)
        completed.append(packet_job)
        built = _current(data).state(packet_job).output["packet"]
        packet_artifact = output / "nih-phase1-temporal-design-packet.md"
        if packet_artifact.exists() and packet_artifact.read_text(encoding="utf8") != built["markdown"]:
            raise ValueError("published packet differs from native worker's artifact")
        packet_artifact.write_text(built["markdown"], encoding="utf8")
        (output / "nih-phase1-packet-summary.json").write_text(
            json.dumps(built["summary"], sort_keys=True, indent=2) + "\n", encoding="utf8")
    world = json.loads((INPUTS / "game_build_world_next.json").read_text(encoding="utf8"))
    game = _game_member(index, data, output, world)
    if browser_witness:
        # WITNESS plays the actual emitted HTML, then appends its verdict to the
        # same game's original handoff—not an invented CP PASS.
        from .game_build_browser_witness import witness
        browser = witness(data_dir=data, output_dir=output)
        if not browser["solved"] or not browser["native_journal_browser_return_recorded"]:
            raise ValueError("game browser evidence did not return to original job")
    else:
        browser = None
    # CP provenance belongs to the immutable submitted handoff, not a
    # successful result or a generic UI snapshot.
    view = workstation_cp_view(data)
    verified = freshly_reverify_linked_jobs(
        index, WINDOW, view, lambda job_id: reverify_job(data_dir=data, job_id=job_id))
    packet = one_cp_handoff(index, WINDOW, verified, reverified=True)
    graph = packet["cp_automation"]
    required = {"NIH-P1-SCOPE", "NIH-P1-ONTOLOGY", "NIH-P1-REASONING"}
    if not required.issubset(set(graph["witnessed"])):
        raise ValueError("real temporal scope->ontology->reasoning did not advance in CP graph")
    if packet_build:
        if "NIH-P1-PACKET" not in graph["witnessed"]:
            raise ValueError("bounded packet BUILD did not advance its actual CP")
        if "NIH-P2-PROTOTYPE" not in graph["frontier"]:
            raise ValueError("prototype should be next admissible research build")
    elif "NIH-P1-PACKET" not in graph["frontier"]:
        raise ValueError("temporal Phase 1 packet should become admissible after reasoning")
    forbidden = {"NIH-P2-PROTOTYPE", "NIH-P2-TEST",
                 "GAME-W13-WORLDS", "GAME-WORKER-READY", "NIH-P1-AWARD"}
    if not packet_build:
        forbidden.add("NIH-P1-PACKET")
    if forbidden.intersection(graph["witnessed"]):
        raise ValueError("synthetic tests incorrectly promoted unperformed work")
    if len(_current(data).snapshot()) != (5 if packet_build else 4):
        raise ValueError("NIH and game did not share one native runtime")
    report = {
        "schema": "nih-temporal-game-complete-stack/v1",
        "coordinator": WINDOW,
        "native_journal": "runtime.jsonl",
        "exact_nih_jobs": completed,
        "native_game_build_job": GAME_JOB,
        "witnessed_nih_phase_1": sorted(required),
        "next_phase_1": "NIH-P1-SUBMISSION-EXTERNAL" if packet_build else "NIH-P1-PACKET",
        "game_world": game["world_id"],
        "game_native_build": game["BUILD_native_execution"],
        "game_native_witness": game["WITNESS_native_w12"],
        "game_browser_witness": "PASS" if browser is not None else "NOT_RUN",
        "phase_2_test": next(x["state"] for x in graph["checkpoints"]
                             if x["checkpoint"] == "NIH-P2-TEST"),
        "phase_2_test_blocked_by": next(x["blocked_by"] for x in graph["checkpoints"]
                                        if x["checkpoint"] == "NIH-P2-TEST"),
        "nih_official_award": False,
        "synthetic_only": True,
        "one_native_workstation": True,
        "separate_native_source_verifiers": True,
    }
    if packet_build:
        report["packet_worker"] = PACKET_WORKER
        report["packet_job"] = "nih-packet-001"
        report["packet_artifact"] = packet_artifact.name
        report["packet_native_witness"] = "PASS"
        report["official_submission"] = False
        report["next_prototype"] = "NIH-P2-PROTOTYPE"
    (output / "complete-stack-temporal-game.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf8")
    (output / "temporal-cp-frontier.json").write_text(
        json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf8")
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--browser-witness", action="store_true")
    p.add_argument("--build-packet", action="store_true")
    a = p.parse_args(argv)
    print(json.dumps(join(data_dir=a.data_dir, output_dir=a.output_dir,
                          browser_witness=a.browser_witness, packet_build=a.build_packet), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
