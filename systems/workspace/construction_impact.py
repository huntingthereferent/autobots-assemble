"""Read-only downstream review impact for existing B9 candidate construction.

External inspirations: SolidCraft's topology/provenance separation, Jantt's
dependency graph guard and OpenHeart's incremental stale relation. This is
original A/B Python, not a port of their CAD/UML/schedule engines.

A B9 edge is ONLY a proposed dependency. Reaching a downstream node means
"consider re-observing this possibility", never "proof is invalidated",
"work completed", a verified source join, or automatic worker execution.
"""
from __future__ import annotations

from collections import deque
from hashlib import sha256
import json
from typing import Sequence

from .workstation_construction import SOURCE, WorkstationConstruction, _text

_MAX_NODES = 256
_MAX_ARCS = 2048
_MAX_CHANGES = 32


def preview_downstream_review(
    graph: WorkstationConstruction, goal_id: str, changed_candidates: Sequence[str],
) -> dict:
    """Trace potential downstream branches of explicitly named changed nodes.

    The caller must separately verify that a source/observation *did* change.
    This method does not infer change from text labels or old reports.
    Every path below is built from the CURRENT original B9 journal.
    """
    if not isinstance(graph, WorkstationConstruction):
        raise TypeError("existing B9 workstation construction required")
    runtime = graph._runtime()
    goal = graph._node(runtime, _text(goal_id, "goal ID", 120))
    if goal.metadata.get("node_kind") != "GOAL":
        raise ValueError("impact scope must name a B9 root goal")
    if not isinstance(changed_candidates, (tuple, list)) or not (
        1 <= len(changed_candidates) <= _MAX_CHANGES
    ):
        raise ValueError("explicit bounded changed candidate IDs required")
    changes = [_text(x, "changed candidate", 120) for x in changed_candidates]
    if len(set(changes)) != len(changes):
        raise ValueError("duplicate changed candidate")

    nodes = {
        h.handoff_id for h in runtime._handoffs.values()
        if h.metadata.get("source_system") == SOURCE
        and h.metadata.get("goal_id") == goal_id
    }
    if goal_id not in nodes:
        raise ValueError("original goal is not in the candidate graph")
    if len(nodes) > _MAX_NODES:
        raise ValueError("candidate graph exceeds bounded review capacity")
    for node in changes:
        if node not in nodes:
            raise ValueError("changed candidate outside original B9 goal")

    arcs = graph._arcs(runtime, goal_id)
    if len(arcs) > _MAX_ARCS:
        raise ValueError("candidate links exceed bounded review capacity")
    after = {node: set() for node in nodes}
    indegree = {node: 0 for node in nodes}
    for upstream, downstream in arcs:
        if upstream not in nodes or downstream not in nodes or upstream == downstream:
            raise ValueError("invalid source-owned construction link")
        if downstream not in after[upstream]:
            after[upstream].add(downstream)
            indegree[downstream] += 1

    # Journal edits can corrupt historical relationships, even if admission
    # initially rejected cycles. Never return a partial affected set.
    ready = deque(sorted(x for x in nodes if indegree[x] == 0))
    processed = 0
    while ready:
        here = ready.popleft()
        processed += 1
        for nxt in sorted(after[here]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
    if processed != len(nodes):
        raise ValueError("persisted candidate graph has a cycle")

    per_change = {}
    all_reachable = set()
    reach_count = {node: 0 for node in nodes}
    for changed in changes:
        # Store one deterministic shortest *example path* per downstream node,
        # not all possible routes. We retain every affected node (bounded), but
        # never imply the example route is the sole possible path.
        route = {changed: (changed,)}
        pending = deque([changed])
        while pending:
            here = pending.popleft()
            for nxt in sorted(after[here]):
                if nxt not in route:
                    route[nxt] = (*route[here], nxt)
                    pending.append(nxt)
        descendants = sorted(set(route) - {changed})
        per_change[changed] = {
            "potential_downstream_review": descendants,
            "example_paths": {x: list(route[x]) for x in descendants},
            "explanation": "proposal-link reachability, NOT proven dependence",
        }
        all_reachable.update(route)
        for node in route:
            reach_count[node] += 1

    report = {
        "goal_id": goal_id,
        "changed_candidate_ids": sorted(changes),
        "review_candidate_ids": sorted(all_reachable - set(changes)),
        "unreached_candidate_ids": sorted(nodes - all_reachable),
        "shared_review_candidate_ids": sorted(
            x for x, n in reach_count.items() if n > 1 and x not in changes
        ),
        "by_change": per_change,
        "candidate_link_count": len(arcs),
        "candidate_node_count": len(nodes),
        "state": "POSSIBLE_REVIEW_ONLY",
        "current_native_evidence_reverified": False,
        "worker_execution_authorized": False,
        "wrote_events": False,
        "interpretation": (
            "An explicit change may require fresh observation on reachable "
            "proposed branches. Unreached alternatives are not certified safe."
        ),
    }
    report["report_sha256"] = sha256(json.dumps(
        report, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    return report
