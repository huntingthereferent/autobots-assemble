from __future__ import annotations

from runtime.handoff import Handoff


def james_task() -> Handoff:
    return Handoff(
        handoff_id="example-james-001",
        referent="James current day",
        from_actor="planner",
        to_actor="james",
        required_relation="move current actionable item",
        inputs={"item": "Review the current task queue"},
        expected_output={"result": "done / partial / blocked"},
        required_witnesses=("task disposition reported",),
        admissible_evidence={
            "task disposition reported": ("human_report",),
        },
        boundaries=("Do not invent a rigid hourly schedule.",),
        metadata={"title": "Review current task queue", "projection": "task"},
    )


def school_task() -> Handoff:
    return Handoff(
        handoff_id="example-school-001",
        referent="Online School / current mathematics block",
        from_actor="school-planner",
        to_actor="learner-a",
        required_relation="complete mathematics block",
        inputs={"planned_minutes": 60, "topic": "measurement"},
        expected_output={"completion": "reported", "work_evidence": "optional"},
        required_witnesses=("learning activity disposition reported",),
        admissible_evidence={
            "learning activity disposition reported": (
                "human_report",
                "work_artifact",
            ),
        },
        metadata={"title": "Mathematics", "projection": "task"},
    )


def software_job() -> Handoff:
    return Handoff(
        handoff_id="example-software-001",
        referent="software change / test run",
        from_actor="orchestrator",
        to_actor="test-runner",
        required_relation="run automated tests",
        inputs={"command": "python -m unittest discover"},
        expected_output={"exit_code": 0},
        required_witnesses=("test execution completed",),
        admissible_evidence={
            "test execution completed": ("automated_test",),
        },
        metadata={"projection": "job"},
    )


def factory_command() -> Handoff:
    return Handoff(
        handoff_id="example-factory-001",
        referent="ORDER-0001 / demo part",
        from_actor="factory-router",
        to_actor="machine-sim",
        required_relation="machine feature",
        inputs={"quantity": 10, "material_state": "received"},
        expected_output={"quantity": 10, "operation": "machined"},
        required_witnesses=("machining operation completed",),
        admissible_evidence={
            "machining operation completed": (
                "simulation",
                "machine_telemetry",
            ),
        },
        boundaries=(
            "Simulation evidence must not be upgraded to physical machining evidence.",
        ),
        metadata={"projection": "command"},
    )


def all_examples() -> tuple[Handoff, ...]:
    return james_task(), school_task(), software_job(), factory_command()
