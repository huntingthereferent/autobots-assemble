"""The original A/B loop is the actual evaluator of the original agent.

Unlike legacy source-only code, this is installed on AgentLineage.evaluate.
It records an honest, non-terminal A/B observation and swallow-first attempt.
The existing task agent remains READY for a future capable implementation actor.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from .ab_loop import ABAgent, ABFrame, ABLoop, ABMove
from .agent_lineage import AgentMove
from .handoff import EvidenceRecord, ExecutionResult, Handoff, HandoffState


SOURCES = {
    "finish-continuity-site": ("COMPLETE_STACK.md", "runtime/http/index.html"),
    "find-things-to-swallow": ("runtime/swallow_first.py", "runtime/external_feed.py"),
    "visual-provenance-min-max": ("runtime/http/index.html",
                                  "design/visual-provenance/registry.json"),
}


class ContinuityPoolEvaluator:
    supported_actors = frozenset({"continuity-agent-pool"})

    def __init__(self, repo: Path, *, ab_tool=None) -> None:
        self.repo = repo.resolve()
        self.service = None
        # The real A/B tool is opt-in and stays a bounded source capability.
        self.ab_tool = ab_tool

    def bind(self, service) -> None:
        if self.service is not None and self.service is not service:
            raise ValueError("evaluator already bound to a different service")
        self.service = service

    def __call__(self, agent: Handoff, state: HandoffState) -> AgentMove:
        if self.service is None:
            raise RuntimeError("A/B evaluator is not bound to the live service")
        if (agent.from_actor.casefold() not in self.supported_actors
                or agent.metadata.get("birth_reason") != "continuity_pool_task_seed"):
            raise ValueError("wrong actor or origin for native Continuity evaluator")
        links = agent.inputs.get("task_handoffs")
        if not isinstance(links, list) or len(links) != 3:
            raise ValueError("original three task handoffs not present")
        items = []
        for link in links:
            handoff = self.service.runtime.get(link["handoff_id"])
            task = next((
                task for task in self.service.personal.tasks()
                if self.service.personal.admitted_handoff_id(task.task_id) == handoff.handoff_id
            ), None)
            if task is None or task.assignee != "continuity-agent-pool":
                raise ValueError("task owner or native task evidence changed")
            seed = next((
                item.removeprefix("seed:continuity-agent:") for item in task.provenance
                if item.startswith("seed:continuity-agent:")
            ), None)
            if seed not in SOURCES or task.referent != handoff.referent:
                raise ValueError("native task seed or admission changed")
            items.append((task, seed))

        def native(frame: ABFrame) -> ABMove:
            if frame.current.get("reground"):
                return ABMove(
                    state="UNKNOWN", reached=dict(frame.current),
                    survived=frame.survives, changed=(), edge=frame.edge,
                    note="No native code-editing actor has supplied implementation evidence.",
                )
            index = frame.current["index"]
            checked = list(frame.current["checked"])
            if index == len(items):
                return ABMove(
                    state="UNKNOWN", reached={"checked": checked},
                    survived=frame.survives, changed=(),
                    edge="the original task work requires a capable executor and result witnesses",
                    note="Task requirements not completed by discovering sources.",
                )
            task, seed = items[index]
            refs = []
            for rel in SOURCES[seed]:
                path = (self.repo / rel).resolve()
                if not path.is_relative_to(self.repo) or not path.is_file():
                    return ABMove(
                        state="WALL", reached={"checked": checked, "missing": rel},
                        survived=frame.survives, changed=(),
                        edge=f"missing native source: {rel}",
                    )
                digest = sha256(path.read_bytes()).hexdigest()
                refs.append({"source": rel, "sha256": digest})
            checked.append({"title": task.title, "task_id": task.task_id,
                            "native_sources": refs, "task_complete": False})
            return ABMove(
                state="MOVE",
                reached={"index": index+1, "checked": checked},
                survived=frame.survives,
                changed=(f"native references available for {task.title}",),
                edge="compare next original task's native evidence",
                evidence=tuple(f"repository:{x['source']}@sha256:{x['sha256']}"
                               for x in refs),
                note="Native source relation verified; task not executed.",
            )

        def outward(frame: ABFrame) -> ABMove:
            # This is a genuine *bounded native source* swallow: paths already
            # inspected exist, but none supplies a software-editing worker.
            entered = frame.current.get("entered") or {}
            checked = list(entered.get("checked") or frame.current.get("checked") or ())
            return ABMove(
                state="UNKNOWN",
                reached={"searched": [
                    f"repository:{source['source']}@sha256:{source['sha256']}"
                    for item in checked for source in item["native_sources"]
                ], "still_missing": "capable implementation actor / execution witnesses"},
                survived=frame.survives, changed=(), edge=frame.edge,
                note="Swallow-first searched native references; none was a code executor.",
            )

        initial = ABFrame(
            referent=agent.referent,
            direction="Follow original tasks through witnessed native references",
            current={"index": 0, "checked": []},
            survives=("original actor", "three original tasks", "source provenance"),
            edge="compare next original task's native evidence",
            provenance=agent.provenance,
        )
        loop = ABLoop(
            (ABAgent("native-task-compare", native),),
            swallow_agent=ABAgent("native-source-swallow", outward),
            max_steps=12,
        ).run(initial)
        matched = [
            step.move.reached["checked"][-1]
            for step in loop.steps if step.move.state == "MOVE" and
            "checked" in step.move.reached
        ]
        sources = [source for item in matched for source in item["native_sources"]]
        evidence = tuple(EvidenceRecord(
            condition="source relation checked", kind="source",
            source="original-native-continuity",
            ref=f"repository:{source['source']}@sha256:{source['sha256']}",
            note="A/B source correspondence, not a task completion witness",
            depth="observed",
        ) for source in sources)
        outcome = {
            "evaluation": "original-Continuity-A/B",
            "task_source_relations": matched,
            "ab_states": [step.move.state for step in loop.steps],
            "source_relation_moves": loop.move_count,
            "swallow_attempts": loop.swallow_count,
            "stop_reason": loop.stop_reason,
            "next_unresolved_edge": loop.final_frame.edge,
            "task_results": "NOT_EXECUTED",
            "model_actor": "NOT_REGISTERED",
        }
        if self.ab_tool is not None:
            # The packaged A/B source/provenance tool participates in
            # this SAME evaluator; it is not a parallel agent or scheduler.
            # A mismatch invalidates stale source evidence.
            try:
                outcome["ab_tool_worker"] = self.ab_tool.inspect_task_sources(matched)
            except (ValueError, OSError) as exc:
                outcome["ab_tool_worker"] = {
                    "status": "UNKNOWN",
                    "wall": f"current source/provenance check failed: {type(exc).__name__}: {exc}",
                    "completion_verified": False,
                }
                evidence = ()
        return AgentMove(
            result=ExecutionResult(
                status="UNKNOWN", output=outcome, evidence=evidence,
                note="A/B ran in the existing agent; source evidence cannot complete site work.",
            ),
            observation_only=True,
        )
