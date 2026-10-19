"""Reverify actual native worker results before attaching them to workflow pins.

This adapter admits precisely two source-owned worker families: the native
finite-correspondence prefilter and Factory's *simulated* machine stage.
controls.reverify_job recreates each source-native verifier and rechecks the
real selected source edition, handoff, output and evidence without executing
another worker. No physical factory production is verified.

Native computation success is NOT overall workflow correctness or quality.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.controls import reverify_job
from systems.workspace.process_handoff import WORKER_ID, VERIFIER
from systems.workspace.factory_machine_bridge import (
    WORKER_ID as FACTORY_WORKER_ID, VERIFIER as FACTORY_VERIFIER,
)
from .workflow_draft import build_preview
from .workflow_pins import WorkflowPins

SCHEMA = "workstation-pinned-native-result/v1"
_HEX = re.compile(r"[0-9a-f]{64}\Z")
MAX_RECORDS = 4000
MAX_BYTES = 8_000_000


def _hash(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                            ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


class NativeResultBoundary(ValueError):
    pass


class WorkflowNativeResults:
    """Single-writer local append-only source-verified native result binding."""

    def __init__(self, repository: str | Path, data_dir: str | Path):
        self.repository = Path(repository).resolve()
        self.data_dir = Path(data_dir).resolve()
        self.path = self.data_dir / "workflow_native_result_links.jsonl"

    def inspect(self, job_id: str) -> dict:
        if not isinstance(job_id, str) or not 1 <= len(job_id) <= 120:
            raise NativeResultBoundary("exact native job ID required")
        runtime = HandoffRuntime(event_store=RuntimeJournal(self.data_dir / "runtime.jsonl"))
        job, state = runtime.get(job_id), runtime.state(job_id)
        # Restrict the dispatch BEFORE invoking a native source-owned
        # verifier. Factory has its own simulated machine-stage owner, not
        # the finite correspondence verifier or any physical machine.
        worker_id = job.metadata.get("worker_id")
        finite = (worker_id == WORKER_ID
                  and job.metadata.get("native_evidence_verifier") == VERIFIER
                  and job.metadata.get("source_system") == "process-workstation")
        factory = (worker_id == FACTORY_WORKER_ID
                   and job.metadata.get("native_evidence_verifier") == FACTORY_VERIFIER
                   and job.metadata.get("source_system") == "factory"
                   and job.metadata.get("workstation_worker") is True
                   and job.metadata.get("stage") == "machine"
                   and job.to_actor == "machine-sim")
        if (not (finite or factory) or state.status != "COMPLETE"
                or state.missing_witnesses):
            raise NativeResultBoundary("not a completed supported native computation/simulation")
        # Each original verifier reopens its own source edition and replays
        # its result without running the native process.
        verdict = reverify_job(data_dir=self.data_dir, job_id=job_id)
        if verdict != {"job_id": job_id, "status": "COMPLETE",
                       "reverified": True, "executed": False}:
            raise NativeResultBoundary("native source-owned verifier did not confirm COMPLETE")
        output = state.output
        if finite and (output.get("kind") != "finite-prefilter-v1"
                       or not isinstance(output.get("verdicts"), list)):
            raise NativeResultBoundary("unexpected finite source-native result shape")
        if factory and (not isinstance(output, dict)
                        or set(output) != {"part", "quantity", "part_state"}
                        or output.get("part_state") != "machined"
                        or type(output.get("quantity")) is not int):
            raise NativeResultBoundary("unexpected native Factory simulation result shape")
        if factory:
            # A Factory order identity is not a machine-operation parameter.
            # The actual source handoff must still carry the matching order ID.
            if (set(job.inputs) != {"order", "product", "material", "quantity", "material_state"}
                    or job.inputs.get("order") != job.metadata.get("order_id")):
                raise NativeResultBoundary("Factory order/source identity mismatch")
            comparable_inputs = {k: v for k, v in job.inputs.items() if k != "order"}
        else:
            comparable_inputs = job.inputs
        events = [event for event in runtime.event_store.for_handoff(job_id)
                  if event.event_type == "RESULT"]
        if len(events) != 1:
            raise NativeResultBoundary("native job must have exactly one RESULT event")
        native = {
            "native_job_id": job_id,
            "worker_id": worker_id,
            "result_family": "finite-prefilter-v1" if finite else "factory-machine-simulation-v1",
            "simulation_only": bool(factory),
            "worker_version": job.metadata["worker_version"],
            "edition_fingerprint": job.metadata["edition_fingerprint"],
            "inputs_sha256": _hash(job.inputs),
            "comparable_inputs_sha256": _hash(comparable_inputs),
            "native_order_id": job.metadata["order_id"] if factory else None,
            "result_event_id": events[0].event_id,
            "result_sha256": _hash(output),
            "evidence_sha256": _hash([vars(e) for e in state.evidence]),
            "verdict_counts": ({
                v: output["verdicts"].count(v)
                for v in ("CONTRADICTED", "NOT_CONTRADICTED", "UNDECIDED")
            } if finite else None),
            "tested_candidates": len(output["verdicts"]) if finite else None,
            "verdict_sequence_sha256": _hash(output["verdicts"]) if finite else None,
            "simulated_part_state": output["part_state"] if factory else None,
            "native_result_reverified": True,
            "native_job_reexecuted": False,
            "full_workflow_verified": False,
            "branch_quality_verified": False,
            "actor_identity_authenticated": False,
        }
        return native

    def _replay(self) -> list[dict]:
        if not self.path.exists():
            return []
        if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_size > MAX_BYTES:
            raise NativeResultBoundary("unsafe or overlarge native-result history")
        records = []
        parent = ""
        for row_num, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            if row_num > MAX_RECORDS or not line:
                raise NativeResultBoundary("native-result history malformed")
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                raise NativeResultBoundary("native-result history invalid JSON") from exc
            if (not isinstance(entry, dict) or set(entry) != {"parent", "data", "hash"}
                    or entry["parent"] != parent or not isinstance(entry["data"], dict)
                    or entry["hash"] != _hash({"parent": parent, "data": entry["data"]})):
                raise NativeResultBoundary("native-result history ancestry/content mismatch")
            data = entry["data"]
            if (data.get("schema") != SCHEMA or
                    not _HEX.fullmatch(str(data.get("draft_revision", ""))) or
                    not isinstance(data.get("step_id"), str) or
                    not isinstance(data.get("native"), dict) or
                    data["native"].get("native_result_reverified") is not True or
                    data["native"].get("branch_quality_verified") is not False):
                raise NativeResultBoundary("native-result journal contains an invalid authority claim")
            records.append(data)
            parent = entry["hash"]
        return records

    def list_records(self, draft_revision: str | None = None) -> list[dict]:
        rows = self._replay()
        if draft_revision is None:
            return rows
        if not isinstance(draft_revision, str) or not _HEX.fullmatch(draft_revision):
            raise NativeResultBoundary("exact workflow revision hash required")
        return [row for row in rows if row["draft_revision"] == draft_revision]

    def attach(self, draft: dict, *, step_id: str, job_id: str) -> dict:
        preview = build_preview(draft, self.repository)
        revision = preview["revision"]
        if step_id not in {s["id"] for s in preview["draft"]["steps"]}:
            raise NativeResultBoundary("native result must bind to an existing workflow step")
        selected = next((r for r in WorkflowPins(self.data_dir).list_pins()
                         if r["revision"] == revision), None)
        if selected is None or selected["draft"] != preview["draft"]:
            raise NativeResultBoundary("native result requires exact pinned workflow source revision")
        current = self.inspect(job_id)
        data = {"schema": SCHEMA, "draft_revision": revision, "step_id": step_id,
                "native": current,
                "relation_scope": ("NATIVE_FINITE_PREFILTER_RESULT_ONLY"
                                   if current["result_family"] == "finite-prefilter-v1"
                                   else "NATIVE_FACTORY_MACHINE_SIMULATION_ONLY"),
                "step_job_link": "USER_SELECTED_SOURCE_ASSOCIATION",
                "execution_authorized_by_pin": False}
        old = self._replay()
        if data in old:
            return {"recorded": False, "observation": data}
        if any(x["draft_revision"] == revision and x["step_id"] == step_id for x in old):
            raise NativeResultBoundary("step already has another native-result binding; branch to replace")
        if len(old) >= MAX_RECORDS:
            raise NativeResultBoundary("native-result journal full")
        parent = ""
        if self.path.exists():
            parent = json.loads(self.path.read_text(encoding="utf-8").splitlines()[-1])["hash"]
        envelope = {"parent": parent, "data": data, "hash": _hash({"parent": parent, "data": data})}
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as out:
            out.write(json.dumps(envelope, sort_keys=True, ensure_ascii=False,
                                 allow_nan=False, separators=(",", ":")) + "\n")
            out.flush()
            os.fsync(out.fileno())
        return {"recorded": True, "observation": data}

    def compare(self, *, parent_revision: str, branch_revision: str,
                parent_step_id: str, branch_step_id: str) -> dict:
        """Compare two already completed native jobs, with fresh source replay.

        This reports exact native observations; more CONTRADICTED or fewer
        UNDECIDED results is NOT automatically a better research workflow.
        """
        pins = {p["revision"]: p for p in WorkflowPins(self.data_dir).list_pins()}
        if parent_revision not in pins or branch_revision not in pins:
            raise NativeResultBoundary("both source revisions must be pinned")
        if pins[branch_revision]["parent_revision"] != parent_revision:
            raise NativeResultBoundary("branch must descend directly from selected pinned parent")
        observations = self._replay()
        def select(revision, step):
            rows = [x for x in observations if x["draft_revision"] == revision and x["step_id"] == step]
            if len(rows) != 1:
                raise NativeResultBoundary("exact native result binding missing or ambiguous")
            current = self.inspect(rows[0]["native"]["native_job_id"])
            if current != rows[0]["native"]:
                raise NativeResultBoundary("native observation changed since it was attached")
            return current
        earlier = select(parent_revision, parent_step_id)
        later = select(branch_revision, branch_step_id)
        if earlier["comparable_inputs_sha256"] != later["comparable_inputs_sha256"]:
            raise NativeResultBoundary("native worker operation inputs differ; results are not comparable")
        if (earlier["simulation_only"] and
                earlier["native_order_id"] == later["native_order_id"]):
            raise NativeResultBoundary("Factory comparison requires two distinct native orders")
        if earlier["worker_id"] != later["worker_id"]:
            raise NativeResultBoundary("native worker families differ")
        if earlier["native_job_id"] == later["native_job_id"]:
            raise NativeResultBoundary("one source job cannot independently witness two branches")
        if earlier["result_family"] != later["result_family"]:
            raise NativeResultBoundary("native result families differ")
        finite = earlier["result_family"] == "finite-prefilter-v1"
        if finite:
            differences = {name: later["verdict_counts"][name] - earlier["verdict_counts"][name]
                           for name in earlier["verdict_counts"]}
        else:
            differences = None
        return {
            "parent_revision": parent_revision, "branch_revision": branch_revision,
            "parent_job": earlier["native_job_id"], "branch_job": later["native_job_id"],
            "parent_result_sha256": earlier["result_sha256"],
            "branch_result_sha256": later["result_sha256"],
            "result_family": earlier["result_family"],
            "simulation_only": not finite,
            "verdict_count_deltas": differences,
            "identical_native_verdicts": (earlier["verdict_sequence_sha256"]
                                          == later["verdict_sequence_sha256"] if finite else None),
            "identical_native_results": earlier["result_sha256"] == later["result_sha256"],
            "source_owned_native_results_reverified_now": True,
            "native_jobs_reexecuted": False,
            "native_metric_scope": ("finite-prefilter verdict counts on identical native inputs"
                                    if finite else "simulated Factory machine operation on identical parameters, separate order IDs"),
            "workflow_quality_ranked": False,
            "physical_production_verified": False,
            "whole_workflow_verified": False,
            "automatic_pin_promotion": False,
        }
