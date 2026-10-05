from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

SOURCE_RUNS = Counter(
    "platform_source_runs_total",
    "Completed source runs by source and status.",
    ["source", "status"],
)
SOURCE_ITEMS = Counter(
    "platform_source_items_total",
    "Items observed by successful source runs.",
    ["source"],
)
SOURCE_RUN_DURATION = Histogram(
    "platform_source_run_duration_seconds",
    "Source run duration in seconds.",
    ["source"],
)
RECONCILIATIONS = Counter(
    "platform_reconciliations_total",
    "Reconciliation results by status.",
    ["status"],
)
IDENTITY_DECISIONS = Counter(
    "platform_identity_decisions_total",
    "Cross-system identity decisions by outcome.",
    ["matched"],
)


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
