from __future__ import annotations

from pathlib import Path

from runtime import ExecutionResult, Handoff, HandoffRuntime
from runtime.activation import ActivationRegistry, run_activation


ROOT = Path(__file__).resolve().parents[2]


def make(handoff_id: str, title: str, *, assignee: str = "james") -> Handoff:
    return Handoff(
        handoff_id=handoff_id,
        referent=title,
        from_actor="ecosystem-router",
        to_actor=assignee,
        required_relation="move current task",
        metadata={"title": title},
    )


def demo():
    runtime = HandoffRuntime()
    handoffs = [
        make("day-school", "Check Online School task monitor"),
        make("day-runtime", "Review handoff-runtime trace"),
        make("day-repo", "Inspect current repo movement"),
        make("day-other", "Learner mathematics", assignee="learner-a"),
        make("day-done", "Completed setup"),
    ]

    for item in handoffs:
        runtime.submit(item)

    runtime.return_result(
        "day-done",
        actor_id="james",
        result=ExecutionResult(status="COMPLETE", output={"done": True}),
    )

    registry = ActivationRegistry.from_json(ROOT / "activations" / "registry.json")
    route = registry.resolve("ohayo", actor_id="james")
    result = run_activation(
        route,
        surface="ohayo",
        handoffs=[(item, runtime.state(item.handoff_id)) for item in handoffs],
    )

    return result


if __name__ == "__main__":
    result = demo()
    print(result.route.referent)
    for item in result.items:
        print(f"[{item['status']}] {item['title']}")
