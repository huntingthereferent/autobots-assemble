from __future__ import annotations

"""Duplicate-safe seed tasks for Continuity's autonomous agent pool."""

from pathlib import Path
import argparse
import json

from .model import TaskRecord
from .store import PersonalOperationsStore


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED = (
    Path(__file__).resolve().parent
    / "task_seeds"
    / "continuity_agent_tasks.json"
)


def ensure_continuity_agent_tasks(
    store: PersonalOperationsStore,
    *,
    seed_path: str | Path = DEFAULT_SEED,
) -> tuple[TaskRecord, ...]:
    payload = json.loads(Path(seed_path).read_text(encoding="utf-8"))
    ensured: list[TaskRecord] = []

    existing_by_seed: dict[str, TaskRecord] = {}
    for task in store.tasks():
        for item in task.provenance:
            if item.startswith("seed:continuity-agent:"):
                existing_by_seed[item.removeprefix("seed:continuity-agent:")] = task

    for row in payload.get("tasks", ()):
        seed_id = str(row["seed_id"])
        existing = existing_by_seed.get(seed_id)
        if existing is not None:
            ensured.append(existing)
            continue

        admissible = {
            str(key): tuple(str(value) for value in values)
            for key, values in dict(
                row.get("admissible_evidence") or {}
            ).items()
        }
        task = TaskRecord.create(
            str(row["title"]),
            referent=str(row["referent"]),
            assignee=str(row["assignee"]),
            required_relation=str(row["required_relation"]),
            inputs=dict(row.get("inputs") or {}),
            expected_output=dict(row.get("expected_output") or {}),
            required_witnesses=tuple(
                str(value)
                for value in row.get("required_witnesses") or ()
            ),
            admissible_evidence=admissible,
            boundaries=tuple(
                str(value)
                for value in row.get("boundaries") or ()
            ),
            provenance=(
                f"seed:continuity-agent:{seed_id}",
                "source:systems/personal_operations/task_seeds/continuity_agent_tasks.json",
            ),
            notes=str(row.get("notes") or ""),
        )
        store.add_task(task)
        ensured.append(task)

    return tuple(ensured)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        default=str(ROOT / "runtime" / "data"),
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    store = PersonalOperationsStore(
        data_dir / "personal_operations.jsonl"
    )
    tasks = ensure_continuity_agent_tasks(store)

    for task in tasks:
        print(
            f"{task.task_id}\t{task.assignee}\t{task.title}\t"
            f"{task.required_relation}"
        )


if __name__ == "__main__":
    main()
