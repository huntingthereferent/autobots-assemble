"""Finite branch graph for a disclosed, fictional A/B word maze.

This graph contains no key references, filesystem paths, executable
transitions, or native runtime capabilities. Both exits from every node
lead to other fictional nodes. The host's bipolar presence determines
which *direction* is current; participants may explore the story graph
without steering, stopping or advancing that presence.
"""
from __future__ import annotations

from dataclasses import dataclass

GRAPH_VERSION = "ab-fictional-word-branches/v1"
START = "threshold"
PREFERENCES = frozenset({"along", "side"})
# Explicit graph, no constructed paths or accidental terminal states.
_EXITS: dict[str, tuple[str, str]] = {
    "threshold": ("hallway", "mirror"),
    "hallway": ("archive", "stair"),
    "mirror": ("fold", "gallery"),
    "archive": ("stair", "echo"),
    "stair": ("gallery", "turn"),
    "fold": ("turn", "hallway"),
    "gallery": ("echo", "passage"),
    "echo": ("passage", "threshold"),
    "turn": ("threshold", "archive"),
    "passage": ("mirror", "fold"),
}


@dataclass(frozen=True)
class BranchView:
    """A story node and its two available fictional continuations."""
    node: str
    along: str
    side: str
    movement_orientation: int


def branch_view(node: str, *, movement_orientation: int) -> BranchView:
    """Read-only graph projection aligned with the observed bipolar swing.

    Both outgoing links are fictional. The swing changes their ordering,
    not their authorization; no keys are ever consulted.
    """
    if type(node) is not str or node not in _EXITS:
        raise ValueError("unknown fictional branch")
    if type(movement_orientation) is not int or movement_orientation not in (-1, 1):
        raise ValueError("bipolar movement orientation must be observed")
    a, b = _EXITS[node]
    if movement_orientation < 0:
        a, b = b, a
    return BranchView(node=node, along=a, side=b,
                      movement_orientation=movement_orientation)


def follow(view: BranchView, preference: str) -> str:
    """Select only one of the two story links; never mutate bipolar motion."""
    if not isinstance(view, BranchView) or preference not in PREFERENCES:
        raise ValueError("use an observed fictional branch and listed exit")
    if preference == "along":
        return view.along
    return view.side


def audit_graph() -> dict:
    """Fail closed if any story link points outside the closed finite graph."""
    if not _EXITS or START not in _EXITS:
        raise AssertionError("fictional branch root missing")
    for node, exits in _EXITS.items():
        if (type(node) is not str or not node.isidentifier()
                or type(exits) is not tuple or len(exits) != 2
                or exits[0] == exits[1]
                or any(target not in _EXITS for target in exits)):
            raise AssertionError("invalid finite branch edges")
    # From any branch, repeated links can never reach an external sink;
    # every exit remains in this finite, closed component.
    reachable = {START}
    frontier = [START]
    while frontier:
        here = frontier.pop()
        for dest in _EXITS[here]:
            if dest not in reachable:
                reachable.add(dest)
                frontier.append(dest)
    if len(reachable) != len(_EXITS):
        raise AssertionError("unreachable fictional maze branches")
    return {"version": GRAPH_VERSION, "nodes": len(_EXITS),
            "directed_exits": 2 * len(_EXITS),
            "terminal_nodes": 0}
