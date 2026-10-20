"""Fresh, first-hop native-result observations for one real repo-work handoff.

This only combines already associated evidence from pinned workflow steps
with native result verification provided by the original finite/Factory
source owners. It is not a worker scheduler, branch ranking, task completion,
or proof that the operator-associated job implements its step.
"""
from __future__ import annotations

from runtime.engine import HandoffRuntime

from .workflow_idea_frontier import IdeaFrontier
from .workflow_native_results import WorkflowNativeResults

MAX_VISIBLE_EVIDENCE = 13  # current step + at most 12 first-hop related branches


def _bounded_native(row: dict) -> dict:
    """Expose only the information relevant to the same declared step."""
    return {
        "native_job_id": row["native_job_id"],
        "result_event_id": row["result_event_id"],
        "result_family": row["result_family"],
        "worker_id": row["worker_id"],
        "edition_fingerprint": row["edition_fingerprint"],
        "comparable_inputs_sha256": row["comparable_inputs_sha256"],
        "result_sha256": row["result_sha256"],
        "verdict_sequence_sha256": row["verdict_sequence_sha256"],
        "simulation_only": row["simulation_only"],
        "native_order_id": row["native_order_id"],
        "native_result_reverified_now": True,
        "native_job_reexecuted": False,
        "whole_workflow_verified": False,
        "branch_quality_verified": False,
    }


class NativeFrontierEvidence:
    def __init__(self, frontier: IdeaFrontier) -> None:
        self.frontier = frontier
        self.records = WorkflowNativeResults(frontier.repository, frontier.data_dir)

    def observe(self, *, runtime: HandoffRuntime, handoff_id: str,
                revision: str, step_id: str) -> dict:
        """Read only currently visible, exact-step, reverified native evidence.

        Reverify original native worker sources at EVERY observation. Missing
        records remain UNKNOWN; mutated records fail closed. Do not open
        unrelated branch revisions, other steps, or different ideas.
        """
        visible = self.frontier.native_handoff_frontier(
            runtime, handoff_id=handoff_id, revision=revision, step_id=step_id)
        related = [
            row for row in visible["visible_branches"]
            if row["same_step_id_present"]
        ]
        if len(related) >= MAX_VISIBLE_EVIDENCE:
            related = related[:MAX_VISIBLE_EVIDENCE - 1]
        allowed_revisions = [revision] + [row["revision"] for row in related]
        # Read the append-only ledger, but return only exact relevant
        # revision/step records to this native worker. Never return a
        # global inventory of all stored jobs.
        stored = self.records.list_records()
        allowed = {(r, step_id) for r in allowed_revisions}
        seen = {}
        for entry in stored:
            key = (entry["draft_revision"], entry["step_id"])
            if key not in allowed:
                continue
            if key in seen:
                raise ValueError("multiple native result associations for one visible step")
            seen[key] = entry

        def recheck(rev: str) -> dict:
            entry = seen.get((rev, step_id))
            if entry is None:
                return {
                    "revision": rev,
                    "step_id": step_id,
                    "status": "NO_ATTACHED_NATIVE_RESULT",
                    "quality_superiority_proven": False,
                }
            actual = self.records.inspect(entry["native"]["native_job_id"])
            if actual != entry["native"]:
                raise ValueError("source-owned native result changed after association")
            return {
                "revision": rev, "step_id": step_id,
                "status": "NATIVE_RESULT_REVERIFIED",
                "step_job_link": "USER_SELECTED_SOURCE_ASSOCIATION",
                "native": _bounded_native(actual),
                "quality_superiority_proven": False,
            }

        current = recheck(revision)
        related_evidence = []
        for edge in related:
            peer = recheck(edge["revision"])
            peer["relationship"] = edge["relationship"]
            peer["same_declared_step"] = True
            peer["comparison"] = "NOT_COMPARABLE_OR_NOT_YET_TESTED"
            if (current["status"] == "NATIVE_RESULT_REVERIFIED"
                    and peer["status"] == "NATIVE_RESULT_REVERIFIED"):
                own = current["native"]
                other = peer["native"]
                if (own["result_family"] == other["result_family"]
                        and own["comparable_inputs_sha256"] == other["comparable_inputs_sha256"]
                        and own["native_job_id"] != other["native_job_id"]
                        and (not own["simulation_only"]
                             or own["native_order_id"] != other["native_order_id"])):
                    peer["comparison"] = "SAME_OPERATION_INPUTS_REVERIFIED"
                    peer["matching_observed_result"] = (
                        own["verdict_sequence_sha256"] == other["verdict_sequence_sha256"]
                        if own["result_family"] == "finite-prefilter-v1"
                        else own["result_sha256"] == other["result_sha256"]
                    )
                    # A finite verdict match is not a proof of mathematics.
                    # A Factory simulation match is not physical production.
            related_evidence.append(peer)
        return {
            "native_handoff_id": handoff_id,
            "idea_id": visible["idea"]["idea_id"],
            "position": visible["position"],
            "current_step_native_evidence": current,
            "visible_related_step_evidence": related_evidence,
            "other_steps_not_read": True,
            "other_ideas_not_read": True,
            "operator_association_is_not_source_execution_proof": True,
            "branch_quality_ranked": False,
            "native_jobs_reexecuted": False,
        }
