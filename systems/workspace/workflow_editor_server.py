"""Opt-in localhost-only visual editor for proposed workflow graphs.

The original Workstation observer remains GET-only. This separate service
provides authenticated, local draft actions but NO worker execution route.
No cloud users, uploads, network access, external code, or billing.
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets

from foundation.program_kernel.manifest import load_manifest
from systems.workspace.workflow_draft import build_preview, commit_proposal
from systems.workspace.workflow_pins import WorkflowPins

ROOT = Path(__file__).resolve().parents[2]
MAX_BYTES = 131072


def handler_for(root: Path, data_dir: Path, token: str):
    root = root.resolve()
    data_dir = data_dir.resolve()

    class Handler(BaseHTTPRequestHandler):
        def _json(self, data: object, status: int = 200) -> None:
            out = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(out)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.end_headers()
            self.wfile.write(out)

        def _allowed_host(self) -> bool:
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

        def do_GET(self) -> None:
            if not self._allowed_host():
                self._json({"error": "invalid local host"}, 403)
                return
            if self.path == "/":
                template = (root / "runtime/http/workflow-editor.html").read_text(encoding="utf-8")
                page = template.replace("__EDITOR_TOKEN__", token)
                out = page.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(out)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Security-Policy",
                    "default-src 'none'; script-src 'unsafe-inline'; "
                    "style-src 'unsafe-inline'; connect-src 'self'; img-src 'self'; "
                    "base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
                self.send_header("X-Frame-Options", "DENY")
                self.end_headers()
                self.wfile.write(out)
                return
            if self.path == "/api/ideas":
                try:
                    from systems.workspace.workflow_idea_frontier import IdeaFrontier
                    self._json(IdeaFrontier(root, data_dir).ideas())
                except (ValueError, OSError) as e:
                    self._json({"error": str(e)}, 400)
                return
            if self.path == "/api/pins":
                try:
                    self._json(WorkflowPins(data_dir).list_pins())
                except ValueError as e:
                    self._json({"error": str(e)}, 400)
                return
            if self.path == "/api/ab-native-records":
                try:
                    from systems.workspace.workflow_ab_bridge import ABWorkflowSources
                    self._json(ABWorkflowSources(root, data_dir).recorded_native_pool_sources())
                except (ValueError, OSError) as e:
                    self._json({"error": str(e)}, 400)
                return
            if self.path == "/api/native-results":
                try:
                    from systems.workspace.workflow_native_results import WorkflowNativeResults
                    self._json(WorkflowNativeResults(root, data_dir).list_records())
                except (ValueError, OSError) as e:
                    self._json({"error": str(e)}, 400)
                return
            if self.path == "/api/ab-links":
                try:
                    from systems.workspace.workflow_ab_bridge import ABWorkflowSources
                    self._json(ABWorkflowSources(root, data_dir).list_records())
                except ValueError as e:
                    self._json({"error": str(e)}, 400)
                return
            if self.path == "/api/manifests":
                try:
                    catalog = []
                    for path in sorted((root / "foundation/program_examples").glob("*.json")):
                        m = load_manifest(path)
                        catalog.append({"path": path.relative_to(root).as_posix(),
                                        "label": m["referent"],
                                        "inputs": m["inputs"], "outputs": m["outputs"]})
                    self._json(catalog)
                except (ValueError, OSError, KeyError) as e:
                    self._json({"error": str(e)}, 400)
                return
            if self.path == "/api/example":
                example = json.loads((root / "examples/workstation_workflow_draft.json").read_text(encoding="utf-8"))
                self._json(example)
                return
            self._json({"error": "unknown route"}, 404)

        def do_POST(self) -> None:
            if not self._allowed_host():
                self._json({"error": "invalid local host"}, 403)
                return
            # A browser from another origin cannot obtain this per-server
            # token; no Access-Control-Allow-Origin header is ever emitted.
            origin = self.headers.get("Origin")
            expected = f"http://127.0.0.1:{self.server.server_port}"
            if origin != expected or self.headers.get("X-Workstation-Token") != token:
                self._json({"error": "local editor authorization required"}, 403)
                return
            if self.path not in ("/api/preview", "/api/diff", "/api/commit",
                                 "/api/pin", "/api/consider",
                                 "/api/ab-preview", "/api/ab-record",
                                 "/api/native-inspect", "/api/native-attach",
                                 "/api/native-compare",
                                 "/api/idea-bind", "/api/idea-branches", "/api/idea-frontier",
                                 "/api/idea-propose", "/api/idea-native-frontier",
                                 "/api/idea-native-propose"):
                self._json({"error": "unknown action"}, 404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > MAX_BYTES:
                    raise ValueError("invalid bounded request size")
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("request object required")
                if self.path.startswith("/api/idea-"):
                    from systems.workspace.workflow_idea_frontier import IdeaFrontier
                    ideas = IdeaFrontier(root, data_dir)
                    if self.path in ("/api/idea-native-frontier",
                                         "/api/idea-native-propose"):
                        from runtime.engine import HandoffRuntime
                        from runtime.journal import RuntimeJournal
                        runtime = HandoffRuntime(
                            event_store=RuntimeJournal(data_dir / "runtime.jsonl"))
                        if self.path == "/api/idea-native-frontier":
                            reply = ideas.native_handoff_frontier(
                                runtime, handoff_id=payload.get("handoff_id"),
                                revision=payload.get("revision"),
                                step_id=payload.get("step_id"))
                        else:
                            reply = ideas.propose_from_native_handoff(
                                runtime, handoff_id=payload.get("handoff_id"),
                                revision=payload.get("revision"),
                                step_id=payload.get("step_id"),
                                target_revision=payload.get("target_revision"),
                                kind=payload.get("kind"), reason=payload.get("reason"))
                    elif self.path == "/api/idea-branches":
                        reply = ideas.idea_branches_for_operator(payload.get("idea_id"))
                    elif self.path == "/api/idea-bind":
                        reply = ideas.bind(idea_id=payload.get("idea_id"),
                                           revision=payload.get("revision"),
                                           worker=payload.get("worker"),
                                           reason=payload.get("reason"))
                    elif self.path == "/api/idea-frontier":
                        reply = ideas.worker_frontier(
                            idea_id=payload.get("idea_id"),
                            revision=payload.get("revision"),
                            step_id=payload.get("step_id"),
                            worker=payload.get("worker"))
                    else:
                        reply = ideas.propose(
                            kind=payload.get("kind"),
                            idea_id=payload.get("idea_id"),
                            revision=payload.get("revision"),
                            step_id=payload.get("step_id"),
                            worker=payload.get("worker"),
                            target_revision=payload.get("target_revision"),
                            reason=payload.get("reason"))
                    self._json(reply)
                    return
                if self.path.startswith("/api/native-"):
                    from systems.workspace.workflow_native_results import WorkflowNativeResults
                    native = WorkflowNativeResults(root, data_dir)
                    if self.path == "/api/native-inspect":
                        reply = native.inspect(payload.get("job_id"))
                    elif self.path == "/api/native-attach":
                        reply = native.attach(payload.get("draft"), step_id=payload.get("step_id"),
                                              job_id=payload.get("job_id"))
                    else:
                        reply = native.compare(
                            parent_revision=payload.get("parent_revision"),
                            branch_revision=payload.get("branch_revision"),
                            parent_step_id=payload.get("parent_step_id"),
                            branch_step_id=payload.get("branch_step_id"),
                        )
                    self._json(reply)
                    return
                if not isinstance(payload.get("draft"), dict):
                    raise ValueError("draft object required")
                draft = payload["draft"]
                if self.path in ("/api/ab-preview", "/api/ab-record"):
                    from systems.workspace.workflow_ab_bridge import ABWorkflowSources
                    bridge = ABWorkflowSources(root, data_dir)
                    records = payload.get("source_records")
                    bindings = payload.get("step_bindings")
                    if self.path == "/api/ab-preview":
                        reply = bridge.inspect(draft, records, bindings)
                    else:
                        reply = bridge.record_for_pinned_branch(draft, records, bindings)
                elif self.path == "/api/preview":
                    reply = build_preview(draft, root)
                elif self.path == "/api/diff":
                    reply = WorkflowPins(data_dir).compare_branch(draft, root)
                elif self.path == "/api/commit":
                    reply = commit_proposal(draft, root, data_dir)
                elif self.path == "/api/pin":
                    reply = WorkflowPins(data_dir).pin_candidate(
                        draft, root, reason=payload.get("reason"))
                else:
                    reply = WorkflowPins(data_dir).consider_discovery(
                        draft, root, assessment=payload.get("assessment"))
                self._json(reply)
            except (ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as exc:
                self._json({"error": str(exc)}, 400)

        def log_message(self, _format: str, *args) -> None:
            return

    return Handler


def serve(*, root: Path = ROOT, data_dir: Path = Path("runtime/data"),
          port: int = 8054) -> None:
    if not 1024 <= port <= 65535:
        raise ValueError("port must be between 1024 and 65535")
    token = secrets.token_urlsafe(32)
    with ThreadingHTTPServer(("127.0.0.1", port), handler_for(root, data_dir, token)) as server:
        print(f"Local workflow editor: http://127.0.0.1:{server.server_port}/", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Start an opt-in local-only workflow draft editor")
    p.add_argument("--port", type=int, default=8054)
    p.add_argument("--repo-root", type=Path, default=ROOT)
    p.add_argument("--data-dir", type=Path, default=Path("runtime/data"))
    args = p.parse_args()
    serve(root=args.repo_root, data_dir=args.data_dir, port=args.port)
