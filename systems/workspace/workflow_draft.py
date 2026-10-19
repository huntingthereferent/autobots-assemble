"""Workflow draft construction: editable declared graphs, never silent execution.

A draft reads native Program Foundation manifests, resolves only unambiguous
name-and-type matches, checks graph contracts and cycles without running code,
and optionally commits PROPOSED candidate paths to the existing B9 journal.

This is not a native-workflow importer, source-owner verifier, scheduler,
sandbox, executable job admission, or hosted service.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any

from foundation.program_kernel.graph import GraphError, GraphLink, GraphNode, validate_graph
from foundation.program_kernel.manifest import load_manifest
from systems.workspace.workstation_construction import WorkstationConstruction

SCHEMA = "workstation-workflow-draft/v1"
_ID = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{0,63}\Z")
_MAX_STEPS = 64
_MAX_LINKS = 256


def _name(value: object, field: str, *, id_style: bool = False) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ValueError(f"{field} must be a non-empty bounded string")
    value = value.strip()
    if id_style and not _ID.fullmatch(value):
        raise ValueError(f"{field} must be an alphanumeric, hyphen or underscore identifier")
    return value


def _manifest(root: Path, ref: object) -> tuple[str, dict]:
    relative = _name(ref, "manifest")
    candidate = Path(relative)
    if candidate.is_absolute() or candidate.suffix != ".json" or ".." in candidate.parts:
        raise ValueError("manifest must be a relative JSON source path within the repository")
    root = root.resolve()
    resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file() or resolved.stat().st_size > 1_000_000:
        raise ValueError("manifest must be an existing small repository-local JSON file")
    return resolved.relative_to(root).as_posix(), load_manifest(resolved)


def _contract_types_match(left: dict, right: dict) -> bool:
    a, b = left["type"], right["type"]
    return a == b or a == "any" or b == "any"


def build_preview(spec: dict, repo_root: str | Path) -> dict:
    """Pure read-only validation/projection. No B9 writes or implementation calls."""
    if not isinstance(spec, dict) or spec.get("schema") != SCHEMA:
        raise ValueError("unrecognized workflow draft schema")
    title = _name(spec.get("title"), "title")
    provenance = _name(spec.get("provenance"), "provenance")
    parent_revision = spec.get("parent_revision", "")
    if parent_revision:
        if not isinstance(parent_revision, str) or not re.fullmatch(r"[0-9a-f]{64}", parent_revision):
            raise ValueError("parent_revision must be a SHA-256 hex digest")
    if type(spec.get("auto_connect", False)) is not bool:
        raise ValueError("auto_connect must be boolean")
    auto_connect = spec.get("auto_connect", False)
    raw_steps = spec.get("steps")
    raw_links = spec.get("links", [])
    if not isinstance(raw_steps, list) or not 1 <= len(raw_steps) <= _MAX_STEPS:
        raise ValueError("steps must be a non-empty bounded list")
    if not isinstance(raw_links, list) or len(raw_links) > _MAX_LINKS:
        raise ValueError("too many or invalid links")

    steps = []
    graph_nodes: dict[str, GraphNode] = {}
    for item in raw_steps:
        if not isinstance(item, dict):
            raise ValueError("invalid workflow step")
        sid = _name(item.get("id"), "step id", id_style=True)
        if sid in graph_nodes:
            raise ValueError("duplicate step ID")
        label = _name(item.get("label"), f"{sid}.label")
        role = item.get("path_role", "REQUIRED")
        if role not in ("REQUIRED", "ALTERNATIVE"):
            raise ValueError("path_role must be REQUIRED or ALTERNATIVE")
        ref, manifest = _manifest(Path(repo_root), item.get("manifest"))
        inputs = item.get("inputs", {})
        if not isinstance(inputs, dict) or any(k not in manifest["inputs"] for k in inputs):
            raise ValueError(f"{sid} contains undeclared external inputs")
        graph_nodes[sid] = GraphNode(manifest=manifest, inputs=inputs)
        manifest_sha256 = sha256(json.dumps(manifest, ensure_ascii=False, allow_nan=False,
                                           sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        steps.append({"id": sid, "label": label, "manifest": ref,
                      "manifest_sha256": manifest_sha256,
                      "path_role": role, "inputs": inputs})

    links = []
    claimed: set[tuple[str, str]] = set()
    for row in raw_links:
        if not isinstance(row, dict):
            raise ValueError("invalid link")
        a = _name(row.get("from"), "source step", id_style=True)
        b = _name(row.get("to"), "target step", id_style=True)
        output = _name(row.get("output"), "source output")
        target_input = _name(row.get("input"), "target input")
        if a == b:
            raise ValueError("self-link is not a supported declared workflow")
        claim = (b, target_input)
        if claim in claimed:
            raise ValueError("multiple links claim one input")
        claimed.add(claim)
        links.append(GraphLink(a, output, b, target_input))

    generated = []
    ambiguous = []
    if auto_connect:
        for target_id, node in graph_nodes.items():
            for port, contract in node.manifest["inputs"].items():
                if not contract.get("required", True) or port in node.inputs or (target_id, port) in claimed:
                    continue
                # Generation is deliberately conservative: match both the port
                # name and declared type, and only if there is exactly one source.
                matches = [
                    source_id for source_id, source in graph_nodes.items()
                    if source_id != target_id and port in source.manifest["outputs"]
                    and _contract_types_match(source.manifest["outputs"][port], contract)
                ]
                if len(matches) == 1:
                    link = GraphLink(matches[0], port, target_id, port)
                    links.append(link)
                    generated.append({"from": matches[0], "output": port,
                                      "to": target_id, "input": port})
                    claimed.add((target_id, port))
                elif len(matches) > 1:
                    ambiguous.append({"to": target_id, "input": port,
                                      "possible_sources": sorted(matches)})

    # No code is executed. This is the SAME structural contract checker as
    # the Program Foundation executor, but incomplete proposals are allowed.
    order = validate_graph(graph_nodes, links, allow_missing=True)
    missing = []
    for sid, node in graph_nodes.items():
        for port, contract in node.manifest["inputs"].items():
            if contract.get("required", True) and port not in node.inputs and (sid, port) not in claimed:
                missing.append({"step": sid, "input": port, "state": "OPEN_NOT_LINKED"})
    links_json = [{"from": l.source_node, "output": l.source_output,
                   "to": l.target_node, "input": l.target_input} for l in links]
    normalized = {"schema": SCHEMA, "title": title, "provenance": provenance,
                  "parent_revision": parent_revision, "auto_connect": auto_connect,
                  "steps": steps, "links": links_json}
    digest = sha256(json.dumps(normalized, ensure_ascii=False, allow_nan=False,
                               sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {"draft": normalized, "revision": digest, "order": order,
            "generated_links": generated, "ambiguous_links": ambiguous,
            "unresolved_inputs": missing, "contract_check": "STRUCTURAL_ONLY",
            "proposal_state": "PROPOSED_NOT_OBSERVED",
            "execution_authorized": False}


def commit_proposal(spec: dict, repo_root: str | Path, data_dir: str | Path) -> dict:
    """Append an immutable, source-linked proposal to B9, not a runnable job."""
    preview = build_preview(spec, repo_root)  # validate all before journal writes
    draft = preview["draft"]
    rev = preview["revision"]
    graph = WorkstationConstruction(data_dir)
    goal_id = graph.goal(draft["title"], provenance=f"workflow-draft:{rev}:{draft['provenance']}")
    ids = {}
    for step in draft["steps"]:
        ids[step["id"]] = graph.candidate(
            goal_id, step["label"], provenance=f"workflow-draft:{rev}:step:{step['id']}",
            path_role=step["path_role"], capability_hint=step["manifest"],
            input_contract="declared Program Foundation manifest; execution NOT admitted",
        )
    for link in draft["links"]:
        graph.propose_connection(ids[link["from"]], ids[link["to"]],
                                 reason=f"proposed port relation {link['from']}.{link['output']} -> {link['to']}.{link['input']} (draft {rev})")
    for step in draft["steps"]:
        graph.suggest_source(ids[step["id"]], worker_id="program-foundation-draft",
                             edition_ref=rev, source_locator=step["manifest"],
                             reason="Existing manifest is a construction hint; source fit and execution unverified")
    return {"revision": rev, "goal_id": goal_id, "candidate_ids": ids,
            "projection": graph.inspect(goal_id),
            "unresolved_inputs": preview["unresolved_inputs"],
            "generated_links": preview["generated_links"],
            "execution_started": False, "native_verification": False}


def main() -> None:
    parser = argparse.ArgumentParser(description="Review or record a non-executing workflow draft")
    parser.add_argument("action", choices=("preview", "commit"))
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--data-dir", type=Path, default=Path("runtime/data"))
    args = parser.parse_args()
    draft = json.loads(args.draft.read_text(encoding="utf-8"))
    answer = (build_preview(draft, args.repo_root) if args.action == "preview"
              else commit_proposal(draft, args.repo_root, args.data_dir))
    print(json.dumps(answer, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
