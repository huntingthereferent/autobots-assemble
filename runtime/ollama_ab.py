"""Opt-in local generative inference inside the existing Continuity A/B evaluator.

The model selects a native source to inspect; the tool measures that source.
Inference is a proposed movement, not an admitted completion witness.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from time import perf_counter
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import json

from .handoff import EvidenceRecord


class OllamaABDriver:
    def __init__(self, repo: Path, *, model: str = "qwen3:4b-instruct",
                 endpoint: str = "http://127.0.0.1:11434", timeout: int = 90):
        self.repo = Path(repo).resolve()
        self.model = model.strip()
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        parsed = urlparse(self.endpoint)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("Ollama A/B endpoint must be local loopback HTTP")
        if not self.model:
            raise ValueError("local model identifier is required")

    def _ask(self, messages: list[dict]) -> dict:
        payload = {
            "model": self.model, "messages": messages,
            "stream": False, "format": "json",
            "options": {"temperature": 0, "num_ctx": 4096},
        }
        req = Request(
            self.endpoint + "/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=self.timeout) as response:
            answer = json.loads(response.read().decode("utf-8"))
        parsed = json.loads(answer["message"]["content"])
        if not isinstance(parsed, dict):
            raise ValueError("model must return one JSON object")
        return parsed

    def observe(self, *, referent: str,
                available: tuple[str, ...],
                task_context: tuple[dict, ...] = ()) -> tuple[dict, tuple[EvidenceRecord, ...]]:
        """One real model-directed read; no write/commit/network-shell authority."""
        safe = []
        for relative in available:
            candidate = (self.repo / relative).resolve()
            if not candidate.is_relative_to(self.repo) or not candidate.is_file():
                continue
            safe.append(relative.replace("\\", "/"))
        if not safe:
            return {"state": "UNKNOWN", "edge": "no admitted native source",
                    "model": self.model}, ()

        start = perf_counter()
        proposal = self._ask([
            {"role": "system", "content": (
                "You are the generative movement inside an existing A/B agent. "
                "Follow current referent -> surviving relations -> next edge. "
                "Choose ONE admissible repository file to read to resolve the "
                "next relation. Do not pretend a source inspection completes "
                "software work. Do not propose filesystem writes. "
                "Respond only JSON with keys state, source, direction, next_edge, reason. "
                "state must be MOVE, WALL, UNKNOWN, or PARTIAL."
            )},
            {"role": "user", "content": json.dumps({
                "referent": referent,
                "current": "native task sources exist; implementation not yet witnessed",
                "survives": ["existing A/B", "existing agent lineage", "source ownership",
                             "task evidence contracts"],
                "edge": "which native source to inspect next for real task execution?",
                "allowed_sources": safe,
                "native_tasks": task_context,
            })},
        ])
        source = str(proposal.get("source") or "").replace("\\", "/")
        state = str(proposal.get("state") or "UNKNOWN").upper()
        output = {
            "model": self.model, "proposed_state": state,
            "direction": str(proposal.get("direction") or "")[:500],
            "next_edge": str(proposal.get("next_edge") or "")[:500],
            "reason": str(proposal.get("reason") or "")[:700],
            "elapsed_ms": round((perf_counter() - start) * 1000),
            "tool": "read_native_source",
        }
        if source not in safe or state != "MOVE":
            return {**output, "state": "UNKNOWN",
                    "wall": "model did not select an admitted source for MOVE"}, ()
        path = (self.repo / source).resolve()
        if not path.is_relative_to(self.repo) or not path.is_file():
            return {**output, "state": "UNKNOWN",
                    "wall": "admitted source moved or is unavailable"}, ()
        raw = path.read_bytes()
        digest = sha256(raw).hexdigest()
        evidence = EvidenceRecord(
            condition="model-directed native source inspection", kind="source",
            source="local-ollama-tool", ref=f"repository:{source}@sha256:{digest}",
            note="Read by bounded local tool; no implementation completed",
            depth="observed",
        )
        return {
            **output, "state": "MOVE", "source": source,
            "bytes_observed": len(raw), "sha256": digest,
            "excerpt": raw[:1200].decode("utf-8", errors="replace"),
            "next": "A/B observed native source against unresolved implementation edge",
        }, (evidence,)
