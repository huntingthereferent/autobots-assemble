"""Explicit local workstation control entrance, separate from the GET-only viewer.

No hidden scheduler, no listening control API, no automatic execution. Only
source-pinned finite prefilter jobs and already-emitted Factory machine-stage
simulation handoffs can be acted upon. Running selected Python is NOT sandboxed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .workstation import ProcessWorkstation, _safe_id
from .finite_verifier import validate_inputs
from .promotion import PreferredEditions, compare_editions, preference_view
from .process_handoff import (CorrespondenceWorkBridge, WORKER_ID as FINITE_ID)
from .factory_machine_bridge import (FactoryMachineSimulationBridge,
                                     WORKER_ID as FACTORY_ID)
from .integrated_source import WORKER_ID as INTEGRATED_ID
from .integrated_attestation_bridge import IntegratedCP30Bridge
from .integrated_attestation_verifier import validate_request
from .integrated_route_bridge import IntegratedRouteBridge, VERIFIER as ROUTE_VERIFIER
from .integrated_route_verifier import validate_route_request

KNOWN_WORKERS = frozenset((FINITE_ID, FACTORY_ID))
FINITE_FILES = frozenset(("finite_goal_priority.py", "finite_required_edge_guard.py"))
EXECUTABLE_WORKERS = KNOWN_WORKERS | {INTEGRATED_ID}


def _data_root(path: str | Path) -> Path:
    root = Path(path).resolve()
    # Runtime data must be a separate directory, never the repository itself.
    repo = Path(__file__).resolve().parents[2]
    if root == repo or repo.is_relative_to(root):
        raise ValueError("data directory cannot contain the source repository")
    return root


def _runtime(root: Path) -> HandoffRuntime:
    return HandoffRuntime(event_store=RuntimeJournal(root / "runtime.jsonl"))


def _inputs(path: str | Path) -> dict:
    file = Path(path)
    if not file.is_file() or file.stat().st_size > 16384:
        raise ValueError("finite inputs must be an existing JSON file of at most 16 KiB")
    return validate_inputs(json.loads(file.read_text(encoding="utf-8")))



def _cp30_inputs(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_file() or p.stat().st_size > 18000:
        raise ValueError("CP30 verifier inputs must be existing JSON <=18 KiB")
    return validate_request(json.loads(p.read_text(encoding="utf-8")))


def prepare(*, data_dir: str | Path, worker_id: str, version_id: str,
            inputs_file: str | Path | None = None) -> dict[str, Any]:
    """Read-only validation and selected-edition report; no journal or subprocess."""
    if worker_id not in EXECUTABLE_WORKERS:
        raise ValueError("unsupported workstation process")
    _safe_id(version_id)
    root = _data_root(data_dir)
    desk = ProcessWorkstation(root / "workstation")
    info = desk.inspect(worker_id=worker_id, version_id=version_id)
    if worker_id == FINITE_ID:
        if inputs_file is None:
            raise ValueError("finite job preparation requires --inputs-file")
        required = FINITE_FILES
        payload = _inputs(inputs_file)
    elif worker_id == INTEGRATED_ID:
        if inputs_file is None:
            raise ValueError("CP30 signature verification requires --inputs-file")
        required = frozenset(("finite_process_attestation.py",))
        payload = _cp30_inputs(inputs_file)
    else:
        if inputs_file is not None:
            raise ValueError("Factory admission comes from FactorySystem, not arbitrary JSON")
        required = frozenset(("factory_machine_worker.py",))
        payload = None
    files = desk._inventory_edition(Path(info["path"]))
    if not required.issubset(files):
        raise ValueError("edition missing required source modules")
    return {"worker_id": worker_id, "version_id": version_id,
            "fingerprint": info["current_fingerprint"],
            "source_modified_from_copy": bool(info["modified"] or info["added"] or info["deleted"]),
            "operation": "finite-required-edge-prefilter" if worker_id == FINITE_ID
                         else "integrated-cp30-ed25519-verification" if worker_id == INTEGRATED_ID
                         else "existing-factory-machine-simulation",
            "inputs": payload,
            "admitted": False, "executed": False,
            "note": "Preparation is read-only. Inspect trusted edition source before local execution."}


def admit_finite(*, data_dir: str | Path, version_id: str,
                 inputs_file: str | Path, job_id: str, confirm_admit: str,
                 from_actor: str, lane_id: str = "") -> dict[str, Any]:
    """Explicit and version-pinned admission; never runs the selected source."""
    _safe_id(job_id)
    if confirm_admit != job_id:
        raise PermissionError("--confirm-admit must match the exact new job ID")
    if not isinstance(from_actor, str) or not from_actor.strip():
        raise ValueError("from-actor required")
    report = prepare(data_dir=data_dir, worker_id=FINITE_ID,
                     version_id=version_id, inputs_file=inputs_file)
    root = _data_root(data_dir)
    runtime = _runtime(root)
    bridge = CorrespondenceWorkBridge(runtime=runtime,
                                     workstation=ProcessWorkstation(root / "workstation"))
    h = bridge.admit(version_id=version_id, inputs=report["inputs"],
                     from_actor=from_actor, lane_id=lane_id, job_id=job_id)
    return {"job_id": h.handoff_id, "worker_id": FINITE_ID,
            "version_id": version_id, "status": runtime.state(job_id).status,
            "source_fingerprint": h.metadata["edition_fingerprint"],
            "executed": False}



def admit_integrated(*, data_dir: str | Path, version_id: str,
                     inputs_file: str | Path, job_id: str, confirm_admit: str,
                     from_actor: str, lane_id: str = "") -> dict[str, Any]:
    """Explicit CP30 signature-check admission; never runs the copied code."""
    _safe_id(job_id)
    if confirm_admit != job_id:
        raise PermissionError("--confirm-admit must match the exact CP30 job ID")
    report = prepare(data_dir=data_dir, worker_id=INTEGRATED_ID,
                     version_id=version_id, inputs_file=inputs_file)
    root = _data_root(data_dir)
    runtime = _runtime(root)
    bridge = IntegratedCP30Bridge(runtime=runtime,
                                  workstation=ProcessWorkstation(root / "workstation"))
    h = bridge.admit(version_id=version_id, inputs=report["inputs"],
                     from_actor=from_actor, job_id=job_id, lane_id=lane_id)
    return {"job_id": job_id, "worker_id": INTEGRATED_ID, "version_id": version_id,
            "status": runtime.state(job_id).status, "executed": False,
            "source_fingerprint": h.metadata["edition_fingerprint"]}


def prepare_integrated_route(*, data_dir: str | Path, version_id: str,
                             inputs_file: str | Path) -> dict[str, Any]:
    """Read-only check of one CP30 synthetic exact-task request."""
    file=Path(inputs_file)
    if not file.is_file() or file.stat().st_size > 4096:
        raise ValueError("CP30 synthetic route request must be JSON <=4 KiB")
    inputs=validate_route_request(json.loads(file.read_text(encoding="utf-8")))
    root=_data_root(data_dir)
    desk=ProcessWorkstation(root / "workstation")
    info=desk.inspect(worker_id=INTEGRATED_ID,version_id=version_id)
    _, provenance=desk._read(INTEGRATED_ID,version_id)
    if provenance["source_locator"] != "repo:work/arc_like_maze/chatbot/research/integrated/MANIFEST.json#CP-30":
        raise ValueError("CP30 integrated original edition required")
    return {"worker_id":INTEGRATED_ID,"version_id":version_id,
            "source_fingerprint":info["current_fingerprint"],"inputs":inputs,
            "operation":"cp30-synthetic-selected-route-audit", "admitted":False,
            "executed":False,"real_world_owners":False}


def admit_integrated_route(*, data_dir: str | Path, version_id: str,
                           inputs_file: str | Path, job_id: str, confirm_admit: str,
                           from_actor: str, lane_id: str = "") -> dict[str, Any]:
    """Explicitly admit one exact CP30 synthetic owner/pin fixture job."""
    _safe_id(job_id)
    if confirm_admit != job_id:
        raise PermissionError("--confirm-admit must match the exact CP30 route job ID")
    report=prepare_integrated_route(data_dir=data_dir,version_id=version_id,
                                    inputs_file=inputs_file)
    root=_data_root(data_dir)
    runtime=_runtime(root)
    bridge=IntegratedRouteBridge(runtime=runtime,
                                 workstation=ProcessWorkstation(root/"workstation"))
    h=bridge.admit(version_id=version_id,inputs=report["inputs"],
                   job_id=job_id,from_actor=from_actor,lane_id=lane_id)
    return {"job_id":h.handoff_id,"version_id":version_id,"worker_id":INTEGRATED_ID,
            "status":runtime.state(job_id).status,"executed":False,
            "source_fingerprint":h.metadata["edition_fingerprint"]}


def _bridge(runtime: HandoffRuntime, root: Path, worker_id: str,
            verifier: str | None = None):
    desk = ProcessWorkstation(root / "workstation")
    if worker_id == FINITE_ID:
        return CorrespondenceWorkBridge(runtime=runtime, workstation=desk)
    if worker_id == FACTORY_ID:
        return FactoryMachineSimulationBridge(runtime=runtime, workstation=desk)
    if worker_id == INTEGRATED_ID:
        if verifier == ROUTE_VERIFIER:
            return IntegratedRouteBridge(runtime=runtime,workstation=desk)
        if verifier == "integrated-cp30-three-scope-attestation-v1":
            return IntegratedCP30Bridge(runtime=runtime, workstation=desk)
        raise ValueError("unsupported integrated CP30 verifier")
    raise ValueError("job does not belong to a supported workstation worker")


def job_view(*, data_dir: str | Path, job_id: str) -> dict[str, Any]:
    """Read-only exact-job view. Does not reverify previously recorded sources."""
    root = _data_root(data_dir)
    runtime = _runtime(root)
    h = runtime.get(job_id)
    worker = h.metadata.get("worker_id")
    if worker not in EXECUTABLE_WORKERS or not (
        h.metadata.get("source_system") == "process-workstation" or
        h.metadata.get("workstation_worker") is True
    ):
        raise ValueError("job is not a registered workstation handoff")
    from .monitor import workstation_snapshot
    snapshot = workstation_snapshot(root=root / "workstation", runtime=runtime)
    for job in snapshot["jobs"]:
        if job["job_id"] == job_id:
            return job
    raise ValueError("admitted job not visible in workstation")


def run_job(*, data_dir: str | Path, job_id: str,
            confirm_execute: str) -> dict[str, Any]:
    """Explicit, exact-ID execution or replay-safe recovery, no bulk activation."""
    if confirm_execute != job_id:
        raise PermissionError("--confirm-execute must match the exact job ID")
    root = _data_root(data_dir)
    runtime = _runtime(root)
    handoff = runtime.get(job_id)
    worker = handoff.metadata.get("worker_id")
    if worker not in EXECUTABLE_WORKERS:
        raise ValueError("not a supported workstation job")
    bridge = _bridge(runtime, root, worker, handoff.metadata.get("native_evidence_verifier"))
    state = runtime.state(job_id)
    if worker in (FINITE_ID, INTEGRATED_ID):
        if handoff.metadata.get("source_system") != "process-workstation":
            raise ValueError("selected local worker job source does not match")
        if state.status == "READY":
            bridge.execute(job_id, allow_local_execution=True)
        elif state.status != "COMPLETE":
            raise ValueError("unresolved finite job requires a separate recovery decision")
        bridge.reverify(job_id)
    else:
        if handoff.metadata.get("source_system") != "factory" or handoff.metadata.get("workstation_worker") is not True:
            raise ValueError("not a workstation Factory stage")
        # Factory owns the order state: recover result and reconcile at most once.
        from systems.factory.system import FactorySystem
        factory_path = root / "factory_orders.jsonl"
        if not factory_path.is_file():
            raise ValueError("Factory local order journal is missing")
        factory = FactorySystem(factory_path)
        order_id = handoff.metadata.get("order_id")
        order = factory.order(order_id)
        if state.status == "READY":
            if order.pending_handoff_id != job_id or order.stage_index != 1:
                raise ValueError("Factory machine job is not the pending source-owned stage")
            bridge.execute(job_id, allow_local_execution=True)
        elif state.status != "COMPLETE":
            raise ValueError("unresolved Factory stage requires separate recovery")
        bridge.reverify(job_id)
        order = factory.order(order_id)
        if order.pending_handoff_id == job_id and order.stage_index == 1:
            factory.reconcile(order_id, handoff=factory.pending_handoff(order_id),
                              state=runtime.state(job_id))
        elif order.stage_index < 2:
            raise ValueError("Factory local stage is not aligned with recorded result")
    return {"job_id": job_id, "worker_id": worker,
            "status": runtime.state(job_id).status,
            "reverified": True,
            "note": "Completed jobs reverify without another subprocess execution."}


def reverify_job(*, data_dir: str | Path, job_id: str) -> dict[str, Any]:
    root = _data_root(data_dir)
    runtime = _runtime(root)
    h = runtime.get(job_id)
    bridge = _bridge(runtime, root, h.metadata.get("worker_id"),
                     h.metadata.get("native_evidence_verifier"))
    bridge.reverify(job_id)
    return {"job_id": job_id, "status": runtime.state(job_id).status,
            "reverified": True, "executed": False}




def compare_versions(*, data_dir: str | Path, worker_id: str,
                     left_version: str, right_version: str) -> dict[str, Any]:
    """Read-only source comparison; never inherits results from either copy."""
    return compare_editions(ProcessWorkstation(_data_root(data_dir) / "workstation"),
                            worker_id=worker_id, left_version=left_version,
                            right_version=right_version)


def preferred_versions(*, data_dir: str | Path) -> list[dict]:
    """Read-only selections, retaining stale source warnings."""
    root = _data_root(data_dir)
    return preference_view(PreferredEditions(root / "preferred_editions.jsonl"),
                           ProcessWorkstation(root / "workstation"))


def promote_edition(*, data_dir: str | Path, worker_id: str, version_id: str,
                    supporting_job_id: str, confirm_version: str,
                    confirm_fingerprint: str, actor_id: str) -> dict:
    """Choose edition for FUTURE explicit work, only after exact native job replay.

    The selected edition is not deployed or automatically admitted; the job's
    native verifier proves only its declared operation, not general capability.
    """
    if worker_id not in KNOWN_WORKERS:
        raise ValueError("unsupported process selection")
    _safe_id(version_id)
    _safe_id(supporting_job_id)
    _safe_id(actor_id)
    if confirm_version != version_id:
        raise PermissionError("--confirm-version must equal the exact chosen version")
    root = _data_root(data_dir)
    desk = ProcessWorkstation(root / "workstation")
    before = desk.inspect(worker_id=worker_id, version_id=version_id)
    fingerprint = before["current_fingerprint"]
    if confirm_fingerprint != fingerprint:
        raise PermissionError("--confirm-fingerprint must equal full current source hash")
    runtime = _runtime(root)
    handoff = runtime.get(supporting_job_id)
    state = runtime.state(supporting_job_id)
    md = handoff.metadata
    if (state.status != "COMPLETE" or md.get("worker_id") != worker_id or
            md.get("worker_version") != version_id or
            md.get("edition_fingerprint") != fingerprint or
            md.get("native_evidence_verifier") not in (
                "finite-correspondence-prefilter-v1", "workstation.factory.machine.simulation.v1") or
            not (md.get("source_system") == "process-workstation" or
                 md.get("workstation_worker") is True)):
        raise ValueError("completed native job on this exact worker edition required")
    # Reverify using the original native process-specific verifier; no worker run.
    _bridge(runtime, root, worker_id).reverify(supporting_job_id)
    after = desk.inspect(worker_id=worker_id, version_id=version_id)
    if after["current_fingerprint"] != fingerprint:
        raise ValueError("selected edition source changed during revalidation")
    return PreferredEditions(root / "preferred_editions.jsonl").select(
        worker_id=worker_id, version_id=version_id,
        source_fingerprint=fingerprint, supporting_job_id=supporting_job_id,
        required_relation=handoff.required_relation,
        native_verifier=md["native_evidence_verifier"], actor_id=actor_id)

def prepare_preferred(*, data_dir: str | Path, worker_id: str,
                      inputs_file: str | Path | None = None) -> dict:
    """Read-only supporting-job recheck and current edition preparation."""
    from .selected_admission import checked_selection
    root = _data_root(data_dir)
    row = checked_selection(data_dir=root, worker_id=worker_id)
    report = prepare(data_dir=root, worker_id=worker_id,
                     version_id=row['version_id'], inputs_file=inputs_file)
    return {**report, **row}


def admit_selected_finite(*, data_dir: str | Path, inputs_file: str | Path,
                          job_id: str, confirm_admit: str,
                          confirm_selection: str, from_actor: str,
                          lane_id: str = '') -> dict:
    from .selected_admission import admit_preferred_finite
    root = _data_root(data_dir)
    return admit_preferred_finite(data_dir=root, inputs=_inputs(inputs_file),
               job_id=job_id, confirm_admit=confirm_admit,
               confirm_selection=confirm_selection,
               from_actor=from_actor, lane_id=lane_id)


def admit_selected_factory(*, data_dir: str | Path, order_id: str,
                           confirm_handoff: str, confirm_selection: str) -> dict:
    from .selected_admission import admit_preferred_factory
    return admit_preferred_factory(data_dir=_data_root(data_dir), order_id=order_id,
                                  confirm_handoff=confirm_handoff,
                                  confirm_selection=confirm_selection)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local explicit Process Workstation controls")
    parser.add_argument("--data-dir", type=Path, required=True)
    modes = parser.add_subparsers(dest="action", required=True)
    p = modes.add_parser("prepare", help="Read-only edition/inputs check")
    p.add_argument("--worker", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--inputs-file", type=Path)
    p = modes.add_parser("admit-finite", help="Only explicit finite prefilter admission")
    p.add_argument("--version", required=True)
    p.add_argument("--inputs-file", type=Path, required=True)
    p.add_argument("--job-id", required=True)
    p.add_argument("--confirm-admit", required=True)
    p.add_argument("--from-actor", required=True)
    p.add_argument("--lane", default="")
    p = modes.add_parser("admit-integrated", help="Admit one CP30 Ed25519 check, no execution")
    p.add_argument("--version", required=True)
    p.add_argument("--inputs-file", type=Path, required=True)
    p.add_argument("--job-id", required=True)
    p.add_argument("--confirm-admit", required=True)
    p.add_argument("--from-actor", required=True)
    p.add_argument("--lane", default="")
    p = modes.add_parser("prepare-cp30-route", help="Read-only synthetic route task check")
    p.add_argument("--version", required=True)
    p.add_argument("--inputs-file", type=Path, required=True)
    p = modes.add_parser("admit-cp30-route", help="Admit exactly one CP30 synthetic route task")
    p.add_argument("--version", required=True)
    p.add_argument("--inputs-file", type=Path, required=True)
    p.add_argument("--job-id", required=True)
    p.add_argument("--confirm-admit", required=True)
    p.add_argument("--from-actor", required=True)
    p.add_argument("--lane", default="")
    p = modes.add_parser("inspect", help="Read-only recorded job")
    p.add_argument("--job-id", required=True)
    p = modes.add_parser("execute", help="Explicitly run selected ready job")
    p.add_argument("--job-id", required=True)
    p.add_argument("--confirm-execute", required=True)
    p = modes.add_parser("reverify", help="Replay native verifier, no execution")
    p.add_argument("--job-id", required=True)
    p = modes.add_parser("compare", help="Read-only current-source edition diff")
    p.add_argument("--worker", required=True)
    p.add_argument("--left-version", required=True)
    p.add_argument("--right-version", required=True)
    modes.add_parser("preferred", help="Read-only selected editions with stale warnings")
    p = modes.add_parser("promote", help="Explicit evidence-gated preferred edition selection")
    p.add_argument("--worker", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--supporting-job", required=True)
    p.add_argument("--confirm-version", required=True)
    p.add_argument("--confirm-fingerprint", required=True)
    p.add_argument("--actor", required=True)
    p = modes.add_parser("prepare-preferred", help="Read-only selected-source and supporting-job check")
    p.add_argument("--worker", required=True)
    p.add_argument("--inputs-file", type=Path)
    p = modes.add_parser("admit-preferred-finite", help="Admit one new job on selected finite edition")
    p.add_argument("--inputs-file", type=Path, required=True)
    p.add_argument("--job-id", required=True)
    p.add_argument("--confirm-admit", required=True)
    p.add_argument("--confirm-selection", required=True)
    p.add_argument("--from-actor", required=True)
    p.add_argument("--lane", default="")
    p = modes.add_parser("admit-preferred-factory", help="Bind an existing pending Factory machine stage")
    p.add_argument("--order-id", required=True)
    p.add_argument("--confirm-handoff", required=True)
    p.add_argument("--confirm-selection", required=True)
    args = parser.parse_args(argv)
    opts = vars(args)
    data = opts.pop("data_dir")
    action = opts.pop("action")
    if action == "prepare":
        result = prepare(data_dir=data, worker_id=opts["worker"],
                         version_id=opts["version"], inputs_file=opts["inputs_file"])
    elif action == "admit-finite":
        result = admit_finite(data_dir=data, version_id=opts["version"],
                    inputs_file=opts["inputs_file"], job_id=opts["job_id"],
                    confirm_admit=opts["confirm_admit"],
                    from_actor=opts["from_actor"], lane_id=opts["lane"])
    elif action == "admit-integrated":
        result = admit_integrated(data_dir=data, version_id=opts["version"],
                   inputs_file=opts["inputs_file"], job_id=opts["job_id"],
                   confirm_admit=opts["confirm_admit"],
                   from_actor=opts["from_actor"], lane_id=opts["lane"])
    elif action == "prepare-cp30-route":
        result = prepare_integrated_route(data_dir=data,version_id=opts["version"],
                                          inputs_file=opts["inputs_file"])
    elif action == "admit-cp30-route":
        result = admit_integrated_route(data_dir=data,version_id=opts["version"],
                 inputs_file=opts["inputs_file"],job_id=opts["job_id"],
                 confirm_admit=opts["confirm_admit"],from_actor=opts["from_actor"],
                 lane_id=opts["lane"])
    elif action == "prepare-preferred":
        result = prepare_preferred(data_dir=data, worker_id=opts["worker"],
                                   inputs_file=opts["inputs_file"])
    elif action == "admit-preferred-finite":
        result = admit_selected_finite(data_dir=data, inputs_file=opts["inputs_file"],
                         job_id=opts["job_id"], confirm_admit=opts["confirm_admit"],
                         confirm_selection=opts["confirm_selection"],
                         from_actor=opts["from_actor"], lane_id=opts["lane"])
    elif action == "admit-preferred-factory":
        result = admit_selected_factory(data_dir=data, order_id=opts["order_id"],
                    confirm_handoff=opts["confirm_handoff"],
                    confirm_selection=opts["confirm_selection"])
    elif action == "inspect":
        result = job_view(data_dir=data, job_id=opts["job_id"])
    elif action == "execute":
        result = run_job(data_dir=data, job_id=opts["job_id"],
                         confirm_execute=opts["confirm_execute"])
    elif action == "reverify":
        result = reverify_job(data_dir=data, job_id=opts["job_id"])
    elif action == "compare":
        result = compare_versions(data_dir=data, worker_id=opts["worker"],
                 left_version=opts["left_version"], right_version=opts["right_version"])
    elif action == "preferred":
        result = preferred_versions(data_dir=data)
    else:
        result = promote_edition(data_dir=data, worker_id=opts["worker"],
                 version_id=opts["version"], supporting_job_id=opts["supporting_job"],
                 confirm_version=opts["confirm_version"],
                 confirm_fingerprint=opts["confirm_fingerprint"], actor_id=opts["actor"])
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
