"""A/B tool capability for existing native workers, not a replacement agent.

Use the actual A/B package for provenance graph construction and bounded
ancestry. Recheck source evidence already recorded by a worker. Never execute
the A/B source-mutation pipeline, start jobs, or alter the original REA source.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

from ab_prov import build_graph, graph_summary, load_document
from ab_prov.ancestry import ancestors

_MAX_TASKS = 32
_MAX_SOURCES = 128
_MAX_SOURCE_BYTES = 4_000_000
_HASH = re.compile(r"[0-9a-f]{64}\Z")


class ABToolWorkerError(ValueError):
    pass


class ABToolWorkerBridge:
    """Read-only A/B tool interface that source-owning workers can reuse."""

    def __init__(self, repository: str | Path):
        self.repository = Path(repository).resolve()
        if not (self.repository / "runtime" / "pool_evaluator.py").is_file():
            raise ABToolWorkerError("expected the original native worker repository")

    def inspect_native_journal(self, journal: str | Path, *, target: str | None = None) -> dict:
        """Read existing Workstation/RuntimeJournal through the A/B package.

        A journal is an explicitly supplied local file. No worker is invoked,
        no event is written, and a source-reference graph does not verify jobs.
        """
        path = Path(journal)
        if (path.is_symlink() or not path.is_file()
                or path.stat().st_size > _MAX_SOURCE_BYTES):
            raise ABToolWorkerError("explicit local runtime journal is absent or unsafe")
        graph = load_document(journal=path)
        result = ancestors(graph, target, max_hops=32) if target is not None else graph
        return {
            "capability": "ab-tool/native-runtime-journal-v1",
            "status": "JOURNAL_PROJECTED_NOT_REVERIFIED",
            "projection": result,
            "graph_summary": graph_summary(graph),
            "native_jobs_executed": 0,
            "completion_verified": False,
            "source_edits_performed": False,
        }

    def inspect_task_sources(self, records: list[dict]) -> dict:
        if not isinstance(records, list) or not 1 <= len(records) <= _MAX_TASKS:
            raise ABToolWorkerError("a bounded list of native task records is required")
        links = []
        known_tasks = set()
        total_refs = 0
        identities = []
        ancestry_targets = {}
        for item in records:
            if not isinstance(item, dict) or not {"task_id", "native_sources"} <= set(item):
                raise ABToolWorkerError("native task identity and source records are required")
            task_id = item["task_id"]
            if not isinstance(task_id, str) or not task_id.strip() or len(task_id) > 160 or task_id in known_tasks:
                raise ABToolWorkerError("invalid or duplicate native task ID")
            known_tasks.add(task_id)
            refs = item["native_sources"]
            if not isinstance(refs, list) or not 1 <= len(refs) <= _MAX_SOURCES:
                raise ABToolWorkerError("native task requires bounded source references")
            for offset, source in enumerate(refs):
                total_refs += 1
                if total_refs > _MAX_SOURCES:
                    raise ABToolWorkerError("source relationship budget exceeded")
                if not isinstance(source, dict) or set(source) != {"source", "sha256"}:
                    raise ABToolWorkerError("exact source locator and SHA-256 required")
                rel, checksum = source["source"], source["sha256"]
                if not isinstance(rel, str) or not rel or len(rel) > 400 or not isinstance(checksum, str) or not _HASH.fullmatch(checksum):
                    raise ABToolWorkerError("invalid source locator or digest")
                path = Path(rel)
                if path.is_absolute() or ".." in path.parts or not path.parts or path.suffix == ".pyc":
                    raise ABToolWorkerError("source locator must remain inside the repository")
                location = self.repository / path
                resolved = location.resolve()
                if (not resolved.is_relative_to(self.repository) or location.is_symlink()
                        or not location.is_file() or location.stat().st_size > _MAX_SOURCE_BYTES):
                    raise ABToolWorkerError("native source absent, unsafe or outside file budget")
                actual = sha256(location.read_bytes()).hexdigest()
                if actual != checksum:
                    raise ABToolWorkerError("recorded source fingerprint disagrees with current native source")
                reference = "repository:" + rel + "@sha256:" + checksum
                identities.append(reference)
                ancestry_targets.setdefault(task_id, []).append(
                    "ref:" + json.dumps(["repository-source", reference], ensure_ascii=False))
                links.append({
                    "schema_version": 1,
                    "provenance_id": "agent-source-" + sha256(f"{task_id}\0{offset}\0{rel}".encode()).hexdigest()[:32],
                    "from": {"layer": "native-task", "ref": task_id},
                    "to": {"layer": "repository-source", "ref": reference},
                    "relation": "declared_native_task_source",
                    "evidence_refs": [reference],
                    "survived": ["exact native task ID", "recorded source digest"],
                    "invalidated": [],
                    "boundaries": [
                        "Source version rechecked, not independent task-completion evidence.",
                        "A/B provenance graph does not authenticate actors or execute workers.",
                    ],
                    "transformation": "read-only A/B tool projection from native worker source records",
                    "observed_at": "source content rechecked at invocation",
                })
        # This invokes the actual installed A/B package, not a replica
        # of the inverse-math engine or a constructed completion witness.
        graph = build_graph(links, [], [])
        scoped = {}
        for task_id, targets in sorted(ancestry_targets.items()):
            views = [ancestors(graph, target, max_hops=32) for target in targets]
            scoped[task_id] = {
                "recorded_ancestor_edges": sorted({e["id"] for v in views for e in v["edges"]}),
                "truncated": any(v["truncated"] for v in views),
            }
        return {
            "capability": "ab-tool/provenance-graph-v1",
            "scope": "read_only_native_source_relationships",
            "status": "SOURCE_REFERENCES_RECHECKED",
            "task_ids": sorted(known_tasks),
            "source_references": sorted(identities),
            "graph_summary": graph_summary(graph),
            "graph": graph,
            "task_ancestry": scoped,
            "native_jobs_executed": 0,
            "completion_verified": False,
            "source_edits_performed": False,
        }
