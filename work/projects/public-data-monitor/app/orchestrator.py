from collections.abc import Callable

from .platform import SourceObservation
from .source_runs import fail_source_run, finish_source_run, start_source_run


def run_source(
    source: str,
    fetch: Callable[[], list[SourceObservation]],
    *,
    task_id: str | None = None,
) -> list[SourceObservation]:
    run_id = start_source_run(source, task_id=task_id)
    try:
        observations = fetch()
    except Exception as exc:
        fail_source_run(run_id, exc)
        raise

    finish_source_run(run_id, items_seen=len(observations))
    return observations
