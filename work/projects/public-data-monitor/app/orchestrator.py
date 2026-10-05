from collections.abc import Callable
from time import perf_counter

from .metrics import SOURCE_ITEMS, SOURCE_RUN_DURATION, SOURCE_RUNS
from .lifecycle_store import persist_complete_snapshot
from .platform import SourceObservation
from .source_runs import fail_source_run, finish_source_run, start_source_run


def run_source(
    source: str,
    fetch: Callable[[], list[SourceObservation]],
    *,
    task_id: str | None = None,
    commit: Callable[[list[SourceObservation]], None] | None = None,
) -> list[SourceObservation]:
    """Run one source as a single operational unit.

    A run is only marked successful after both acquisition and the optional
    durable commit step complete. Any exception in either phase is persisted as
    a failed source run and exposed through metrics.
    """
    run_id = start_source_run(source, task_id=task_id)
    started = perf_counter()

    try:
        observations = fetch()
        if commit is not None:
            commit(observations)
    except Exception as exc:
        fail_source_run(run_id, exc)
        SOURCE_RUNS.labels(source=source, status="failed").inc()
        SOURCE_RUN_DURATION.labels(source=source).observe(perf_counter() - started)
        raise

    finish_source_run(run_id, items_seen=len(observations))
    SOURCE_RUNS.labels(source=source, status="success").inc()
    SOURCE_ITEMS.labels(source=source).inc(len(observations))
    SOURCE_RUN_DURATION.labels(source=source).observe(perf_counter() - started)
    return observations


def run_source_persisted(
    source: str,
    fetch: Callable[[], list[SourceObservation]],
    *,
    task_id: str | None = None,
) -> list[SourceObservation]:
    """Acquire a source and append its observations to durable history.

    Fetch failures cannot mutate observation history because commit is not
    entered until acquisition returns successfully.
    """

    def commit(observations: list[SourceObservation]) -> None:
        persist_complete_snapshot(source, observations)

    return run_source(source, fetch, task_id=task_id, commit=commit)
