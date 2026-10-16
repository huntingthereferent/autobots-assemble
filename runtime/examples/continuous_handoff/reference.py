"""Continuous Handoff: read-only candidate graph and observational gate.

Not a scheduler, native verifier, universal A/B model, or repository mutation.
No observation claims are trusted unless an external verifier is injected.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Callable

VERDICTS = {"SUPPORTED", "CONTRADICTED", "UNKNOWN"}
Verifier = Callable[[dict, dict], str]


def validate(data: dict) -> None:
    """Check minimal graph integrity; for production also apply sidecar.schema.json."""
    if data.get("schema_version") != 1 or not data.get("referent"):
        raise ValueError("missing schema_version=1 or referent")
    nodes = data.get("nodes", [])
    ids = [n["id"] for n in nodes]
    if len(ids) != len(set(ids)) or any(not n.get("owner") or not n.get("source_ref") for n in nodes):
        raise ValueError("duplicate or incomplete nodes")
    for end in ("source_node", "target_node"):
        if data.get(end) not in ids:
            raise ValueError("missing endpoint: " + end)
    edges = data.get("candidates", [])
    eids = [e["id"] for e in edges]
    if len(eids) != len(set(eids)):
        raise ValueError("duplicate candidate id")
    by_edge = {e["id"]: e for e in edges}
    for e in edges:
        if e["from"] not in ids or e["to"] not in ids or not e.get("relation"):
            raise ValueError("malformed candidate endpoint/relation")
        cs = e.get("required_conditions", [])
        if not cs or len(cs) != len(set(cs)):
            raise ValueError("required_conditions must be nonempty and distinct")
    oids = set()
    for o in data.get("observations", []):
        if o["id"] in oids or o["edge_id"] not in by_edge:
            raise ValueError("duplicate observation or missing candidate")
        oids.add(o["id"])
        if (o["condition"] not in by_edge[o["edge_id"]]["required_conditions"]
                or not o.get("source_ref") or not o.get("witness_ref")
                or o.get("reported_outcome") not in VERDICTS):
            raise ValueError("observation has inadmissible condition or missing locator")


def edge_verdict(edge: dict, observations: list[dict], verifier: Verifier | None = None) -> str:
    """Only an injected native verifier may determine evidence status."""
    attached = [o for o in observations if o["edge_id"] == edge["id"]]
    if not attached:
        return "PROPOSED"
    if verifier is None:
        return "UNKNOWN"
    supported = set()
    for o in attached:
        result = verifier(edge, o)  # Revalidate current native source, not JSON's claim.
        if result not in VERDICTS:
            raise ValueError("native verifier returned invalid verdict")
        if result == "CONTRADICTED":
            return "CONTRADICTED"
        if result == "SUPPORTED":
            supported.add(o["condition"])
    return "SUPPORTED" if set(edge["required_conditions"]) <= supported else "UNKNOWN"


def backward_paths(data: dict, verifier: Verifier | None = None) -> list[dict]:
    """Return all declared backward routes, including unresolved branches.

    An absent candidate route is an OPEN requirement, never an invented edge.
    """
    validate(data)
    incoming: dict[str, list[dict]] = defaultdict(list)
    for e in data["candidates"]:
        incoming[e["to"]].append(e)
    for edges in incoming.values():
        edges.sort(key=lambda e: e["id"])
    target, source = data["target_node"], data["source_node"]
    paths = []

    def walk(node: str, reverse_steps: list[dict], seen: frozenset[str]) -> None:
        if node == source:
            paths.append({"status": "REACHES_SOURCE", "steps": list(reverse_steps)})
            return
        if node in seen:
            paths.append({"status": "CYCLE", "steps": list(reverse_steps), "at": node})
            return
        options = incoming.get(node, [])
        if not options:
            paths.append({"status": "OPEN_REQUIREMENT", "steps": list(reverse_steps), "at": node})
            return
        for e in options:
            step = {"edge_id": e["id"], "from": e["from"], "to": e["to"],
                    "relation": e["relation"],
                    "observation": edge_verdict(e, data.get("observations", []), verifier)}
            walk(e["from"], reverse_steps + [step], seen | {node})

    walk(target, [], frozenset())
    return paths


# A hard-coded synthetic callback used ONLY to demonstrate the verifier interface.
# This does not authenticate real native sources or prove these operations ran.
_TOY_RECEIPTS = {
    ("P", "schema_preserved", "fixture://p-schema", "source://dataset/edition-1"),
    ("P", "source_identified", "fixture://p-source", "source://dataset/edition-1"),
    ("Q", "report_matches_input", "fixture://q-report", "candidate://parser-p/output"),
}


def toy_verifier(edge: dict, observation: dict) -> str:
    record = (edge["id"], observation["condition"], observation["witness_ref"], observation["source_ref"])
    return "SUPPORTED" if record in _TOY_RECEIPTS else "UNKNOWN"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--toy-fixture", action="store_true", help="Synthetic only; NOT a native verifier")
    args = parser.parse_args()
    data = json.loads(args.file.read_text(encoding="utf-8"))
    routes = backward_paths(data, toy_verifier if args.toy_fixture else None)
    print(json.dumps({"referent": data["referent"], "routes_back_from_target": routes,
                      "determination": "toy simulation" if args.toy_fixture else "not performed"}, indent=2))


if __name__ == "__main__":
    main()
