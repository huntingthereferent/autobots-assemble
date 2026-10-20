from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .compose import CompositionError
from .runtime import ExecutionRecord, execute


class GraphError(ValueError):
    pass


@dataclass(frozen=True)
class GraphNode:
    manifest: dict[str, Any]
    inputs: dict[str, Any] = field(default_factory=dict)
    initial_state: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphLink:
    source_node: str
    source_output: str
    target_node: str
    target_input: str


@dataclass(frozen=True)
class GraphExecution:
    order: list[str]
    records: dict[str, ExecutionRecord]


def _compatible(source: dict[str, Any], target: dict[str, Any]) -> bool:
    a = source["type"]
    b = target["type"]
    return a == b or a == "any" or b == "any"


def _validate_links(
    nodes: dict[str, GraphNode],
    links: list[GraphLink],
    *,
    allow_missing: bool = False,
) -> tuple[dict[str, set[str]], dict[str, int]]:
    adjacency = {name: set() for name in nodes}
    indegree = {name: 0 for name in nodes}
    claimed_inputs: set[tuple[str, str]] = set()

    for link in links:
        if link.source_node not in nodes:
            raise GraphError(f"unknown source node: {link.source_node}")
        if link.target_node not in nodes:
            raise GraphError(f"unknown target node: {link.target_node}")

        source_manifest = nodes[link.source_node].manifest
        target_manifest = nodes[link.target_node].manifest

        if link.source_output not in source_manifest.get("outputs", {}):
            raise GraphError(
                f"{link.source_node}.{link.source_output} is not a declared output"
            )
        if link.target_input not in target_manifest.get("inputs", {}):
            raise GraphError(
                f"{link.target_node}.{link.target_input} is not a declared input"
            )

        source_contract = source_manifest["outputs"][link.source_output]
        target_contract = target_manifest["inputs"][link.target_input]
        if not _compatible(source_contract, target_contract):
            raise GraphError(
                f"incompatible link {link.source_node}.{link.source_output} "
                f"-> {link.target_node}.{link.target_input}"
            )

        claim = (link.target_node, link.target_input)
        if claim in claimed_inputs:
            raise GraphError(
                f"multiple links claim {link.target_node}.{link.target_input}"
            )
        if link.target_input in nodes[link.target_node].inputs:
            raise GraphError(
                f"{link.target_node}.{link.target_input} is both linked and external"
            )
        claimed_inputs.add(claim)

        if link.target_node not in adjacency[link.source_node]:
            adjacency[link.source_node].add(link.target_node)
            indegree[link.target_node] += 1

    for node_name, node in nodes.items():
        supplied = set(node.inputs)
        linked = {
            link.target_input
            for link in links
            if link.target_node == node_name
        }
        for input_name, contract in node.manifest.get("inputs", {}).items():
            if not allow_missing and contract.get("required", True) and input_name not in supplied | linked:
                raise GraphError(
                    f"{node_name} missing required input relation: {input_name}"
                )

    return adjacency, indegree


def _topological_order(
    nodes: dict[str, GraphNode],
    adjacency: dict[str, set[str]],
    indegree: dict[str, int],
) -> list[str]:
    ready = sorted(name for name, degree in indegree.items() if degree == 0)
    order: list[str] = []

    while ready:
        current = ready.pop(0)
        order.append(current)
        for target in sorted(adjacency[current]):
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
                ready.sort()

    if len(order) != len(nodes):
        raise GraphError(
            "graph contains a cycle; explicit state/time recursion is not defined"
        )
    return order



def validate_graph(
    nodes: dict[str, GraphNode],
    links: list[GraphLink],
    *,
    allow_missing: bool = False,
) -> list[str]:
    """Check graph contracts and cycles without executing ANY implementation.

    Construction-time editing may allow missing inputs as unresolved openings;
    native execution keeps its original strict required-input validation.
    """
    if not nodes:
        raise GraphError("graph must contain at least one node")
    adjacency, indegree = _validate_links(nodes, links, allow_missing=allow_missing)
    return _topological_order(nodes, adjacency, indegree)


def execute_graph(
    nodes: dict[str, GraphNode],
    links: list[GraphLink],
) -> GraphExecution:
    if not nodes:
        raise GraphError("graph must contain at least one node")

    adjacency, indegree = _validate_links(nodes, links)
    order = _topological_order(nodes, adjacency, indegree)
    records: dict[str, ExecutionRecord] = {}

    incoming = {name: [] for name in nodes}
    for link in links:
        incoming[link.target_node].append(link)

    for node_name in order:
        node = nodes[node_name]
        inputs = dict(node.inputs)
        input_provenance: dict[str, dict[str, Any]] = {}
        parents: list[str] = []

        for link in incoming[node_name]:
            source_record = records[link.source_node]
            inputs[link.target_input] = source_record.values[link.source_output]
            parents.append(source_record.execution_id)
            input_provenance[link.target_input] = {
                "kind": "graph_link",
                "source_node": link.source_node,
                "source_execution_id": source_record.execution_id,
                "source_manifest_id": source_record.manifest_id,
                "source_output": link.source_output,
            }

        records[node_name] = execute(
            node.manifest,
            inputs,
            initial_state=node.initial_state,
            input_provenance=input_provenance,
            parent_executions=parents,
        )

    return GraphExecution(order=order, records=records)
