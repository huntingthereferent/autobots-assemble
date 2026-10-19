"""Read-only pairing of two independently authenticated native histories.

No event import, worker admission, execution, or readiness promotion. Private
plaintext exists only inside a TemporaryDirectory and is never uploaded.
"""
from __future__ import annotations
import base64
from contextlib import contextmanager
from hashlib import sha256
import io
import json
import os
from pathlib import Path, PurePosixPath
import tarfile
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen
import zipfile

REPO = "huntingthereferent/autobots-assemble"
REPO_ID = 1403664339
OWNER_ID = 331854748
OWNER_COMMIT = "d725ac88d710199ce4de579dddcee36533a32ef9"
CHILD_EVENT = "evt_a9ba637571d04967ab777c71a2945a64"
PUBLIC_KEY = "gAtsThg8pin0jVvB8Cvj5utgPU/SkB14zvkbUfvz63E="
SOURCES = {
    "owner": {
        "run": 39176448014, "artifact": 12154278730,
        "name": "w13-encrypted-39176448014",
        "workflow": "owner-w13-encrypted-capsule-producer",
        "commit": OWNER_COMMIT,
        "digest": "sha256:efd88c5583fe781a3e48ed3a70cda7ce35788d65c3c3af1af4c5c96df2fb4dec",
    },
    "temporal": {
        "run": 39174631878, "artifact": 12154340140,
        "name": "live-game-temporal-39174631878-1",
        "workflow": "Complete Stack actual live game-to-temporal query",
        "commit": "832acb777ee64d173ec8d5c91cbfe2c6dcdbfbad",
        "digest": "sha256:591fe04d2537d753efaae5fc69580fa5885bb8e7510614af633ba8769a00e3a0",
    },
}
MAX_ARCHIVE = 8 * 1024 * 1024
MAX_EXPANDED = 24 * 1024 * 1024


def validate_origin(kind, run, artifact):
    pin = SOURCES[kind]
    if (run.get("id") != pin["run"] or run.get("name") != pin["workflow"]
            or run.get("head_sha") != pin["commit"]
            or run.get("event") != "push" or run.get("head_branch") != "main"
            or run.get("run_attempt") != 1 or run.get("status") != "completed"
            or run.get("conclusion") != "success"
            or run.get("actor", {}).get("id") != OWNER_ID
            or run.get("actor", {}).get("login") != "huntingthereferent"
            or run.get("repository", {}).get("id") != REPO_ID
            or run.get("head_repository", {}).get("id") != REPO_ID
            or run.get("head_repository", {}).get("full_name") != REPO):
        raise ValueError("source run identity, owner or successful first attempt differs")
    binding = artifact.get("workflow_run", {})
    if (artifact.get("id") != pin["artifact"] or artifact.get("name") != pin["name"]
            or artifact.get("digest") != pin["digest"]
            or artifact.get("expired") is not False
            or binding.get("id") != pin["run"]
            or binding.get("head_sha") != pin["commit"]
            or binding.get("repository_id") != REPO_ID):
        raise ValueError("source artifact digest, retention or run binding differs")


def _safe_path(name):
    p = PurePosixPath(name)
    if (not name or not p.parts or "\\" in name or p.is_absolute() or ".." in p.parts
            or len(name) > 250):
        raise ValueError("unsafe retained evidence path")
    return p


def unpack_zip(raw, destination, expected_digest):
    if len(raw) > MAX_ARCHIVE or "sha256:" + sha256(raw).hexdigest() != expected_digest:
        raise ValueError("downloaded artifact bytes differ from authenticated digest")
    dest = Path(destination)
    dest.mkdir(mode=0o700)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        if len(entries) > 200 or sum(x.file_size for x in entries) > MAX_EXPANDED:
            raise ValueError("retained artifact exceeds bounded extraction")
        seen = set()
        for entry in entries:
            rel = _safe_path(entry.filename)
            if str(rel) in seen or (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("duplicate or linked artifact entry")
            seen.add(str(rel))
            target = dest.joinpath(*rel.parts)
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(entry))
                target.chmod(0o600)


def unpack_temporal(source, destination):
    source, dest = Path(source), Path(destination)
    archive = source / "actual-native-workstation.tar.gz"
    checksum = source / "actual-native-workstation.sha256"
    if (not archive.is_file() or archive.is_symlink() or not checksum.is_file()
            or checksum.is_symlink() or archive.stat().st_size > MAX_ARCHIVE
            or checksum.stat().st_size > 1024):
        raise ValueError("retained temporal archive and checksum required")
    recorded = checksum.read_text().split()
    if not recorded or recorded[0] != sha256(archive.read_bytes()).hexdigest():
        raise ValueError("temporal native archive checksum differs")
    dest.mkdir(mode=0o700)
    with tarfile.open(archive, "r|gz") as stream:
        seen = set()
        total = 0
        for count, entry in enumerate(stream, 1):
            total += entry.size
            if count > 200 or total > MAX_EXPANDED:
                raise ValueError("temporal native archive exceeds bound")
            rel = _safe_path(entry.name)
            if (str(rel) in seen or not (entry.isfile() or entry.isdir())
                    or rel.parts[0] not in {"runtime.jsonl", "coordinator-windows.jsonl",
                                            "workstation", "world-request.json"}
                    or (rel.parts[0] != "workstation" and len(rel.parts) != 1)):
                raise ValueError("unexpected, linked or duplicate temporal native entry")
            seen.add(str(rel))
            target = dest.joinpath(*rel.parts)
            if entry.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(stream.extractfile(entry).read())
                target.chmod(0o600)


def _api_request(route, token):
    req = Request(f"https://api.github.com/repos/{REPO}/{route}", headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "owner-temporal-handoff"})
    # The GitHub API authenticates the first request. Its signed storage
    # redirect authenticates itself and must not receive the GitHub token.
    req.add_unredirected_header("Authorization", "Bearer " + token)
    return req


def _get(route, token, *, binary=False):
    req = _api_request(route, token)
    with urlopen(req, timeout=30) as response:
        raw = response.read(MAX_ARCHIVE + 1)
    if len(raw) > MAX_ARCHIVE:
        raise ValueError("source API response exceeded bound")
    return raw if binary else json.loads(raw)


def witness_pair(*, owner_dir, temporal_dir, temporal_artifacts):
    """Reverify BOTH histories locally; retain their distinct event identities."""
    from .owner_native_evidence_vault import _witness
    from .live_temporal_parent_evidence import source_witness
    from runtime.engine import HandoffRuntime
    from runtime.journal import RuntimeJournal
    owner, temporal = Path(owner_dir), Path(temporal_dir)
    if owner.resolve() == temporal.resolve():
        raise ValueError("two distinct native source histories required")
    paths = [root / name for root in (owner, temporal)
             for name in ("runtime.jsonl", "coordinator-windows.jsonl")]
    before = {str(p): sha256(p.read_bytes()).hexdigest() for p in paths}
    owner_jobs = HandoffRuntime(event_store=RuntimeJournal(owner/"runtime.jsonl")).snapshot()
    if "live-game-temporal-001" in owner_jobs:
        raise ValueError("separate temporal source must not impersonate owner history")
    original = _witness(owner)
    if original["child_event"] != CHILD_EVENT:
        raise ValueError("retained owner child RESULT differs")
    live = source_witness(data_dir=temporal, output_dir=Path(temporal_artifacts))
    if before != {str(p): sha256(p.read_bytes()).hexdigest() for p in paths}:
        raise ValueError("read-only verification changed a native journal")
    if (live["ready_owner_w13_join_proven"] is not False
            or live["game_worker_ready_witnessed"] is not False):
        raise ValueError("source receipt promoted an unwitnessed checkpoint")
    return {
        "schema": "owner-temporal-source-pair/v1",
        "state": "BOTH_NATIVE_HISTORIES_FRESHLY_REVERIFIED_SEPARATELY",
        "owner_parent_event": original["parent_event"],
        "owner_child_event": original["child_event"],
        "temporal_result_event": live["native_result_event_id"],
        "temporal_browser_event": live["browser_event_id"],
        "temporal_source_fingerprint": live["native_source_fingerprint"],
        "temporal_live_queries": live["browser_live_queries"],
        "source_artifacts": SOURCES,
        "journal_hashes_unchanged": True,
        "owner_runtime_contains_temporal_source": False,
        "native_dependency_join_witnessed": False,
        "game_worker_ready_witnessed": False,
        "new_worker_executed": False,
        "private_journal_published": False,
    }


@contextmanager
def authenticated_sources(*, token, private):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    from .owner_native_evidence_vault import restore_verified
    public = X25519PrivateKey.from_private_bytes(private).public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    if public != base64.b64decode(PUBLIC_KEY, validate=True):
        raise ValueError("configured recipient differs from pinned source")
    with TemporaryDirectory(prefix="owner-temporal-private-") as scratch:
        root = Path(scratch)
        for kind, pin in SOURCES.items():
            run = _get(f"actions/runs/{pin['run']}", token)
            artifact = _get(f"actions/artifacts/{pin['artifact']}", token)
            validate_origin(kind, run, artifact)
            raw = _get(f"actions/artifacts/{pin['artifact']}/zip", token, binary=True)
            unpack_zip(raw, root/kind, pin["digest"])
            (root/(kind+".zip")).write_bytes(raw)
        owner = root/"owner"
        receipt = json.loads((owner/"receipt.json").read_text())
        sealed = receipt["encrypted_retention"]
        capsule = owner/"continuation.enc"
        if (receipt["owner_authorization_commit"] != OWNER_COMMIT
                or receipt["child_result_event_id"] != CHILD_EVENT
                or sealed["owner_execution_commit"] != OWNER_COMMIT
                or sealed["child_event"] != CHILD_EVENT
                or sealed["sealed_sha256"] != sha256(capsule.read_bytes()).hexdigest()):
            raise ValueError("owner capsule receipt binding differs")
        restore_verified(encrypted=capsule, private_key_raw=private,
            destination=root/"owner-native", expected_owner_execution_commit=OWNER_COMMIT,
            expected_child_event=CHILD_EVENT)
        unpack_temporal(root/"temporal", root/"temporal-native")
        yield root


def main():
    private = base64.b64decode(os.environ["PRIVATE_KEY_B64"], validate=True)
    with authenticated_sources(token=os.environ["GH_TOKEN"], private=private) as root:
        result = witness_pair(owner_dir=root/"owner-native", temporal_dir=root/"temporal-native",
                              temporal_artifacts=root/"temporal")
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
