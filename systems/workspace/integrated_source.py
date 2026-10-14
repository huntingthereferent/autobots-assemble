"""Preserve a reconstructed historical CP20–CP30 source as an isolated edition.

This is SOURCE admission only: no native capability or historical evidence is
transferred to worker execution; no handoffs, tests, or job status are created.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from .workstation import ProcessWorkstation, _safe_id, _tree_fingerprint

WORKER_ID = "finite-correspondence-integrated"
MANIFEST_REL = Path("work/arc_like_maze/chatbot/research/integrated/MANIFEST.json")


def verify_archive_source(repo_root: str | Path, stage: int = 30) -> dict:
    """Independently check ALL source bytes before selecting a checkpoint."""
    if type(stage) is not int or not 20 <= stage <= 30:
        raise ValueError("CP stage must be 20..30")
    root = Path(repo_root).resolve()
    integrated = (root / MANIFEST_REL).parent
    manifest = json.loads((integrated / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("original_file_count") != 281:
        raise ValueError("unexpected historical source manifest")
    stages = manifest.get("stages")
    if not isinstance(stages, list) or [s.get("cumulative_file_count") for s in stages] != [201 + 8 * i for i in range(11)]:
        raise ValueError("historical checkpoint accounting changed")
    files = manifest.get("files")
    if not isinstance(files, dict) or len(files) != 281:
        raise ValueError("historical source file count changed")
    selected = {}
    for name, meta in files.items():
        if not isinstance(name, str) or not name or Path(name).name != name or "\\" in name:
            raise ValueError("unsafe historical filename")
        if not isinstance(meta, dict) or type(meta.get("stage")) is not int or not 20 <= meta["stage"] <= 30:
            raise ValueError("invalid historical stage metadata")
        source = meta.get("path")
        if not isinstance(source, str):
            raise ValueError("invalid historical source locator")
        unresolved = integrated / source
        if unresolved.is_symlink():
            raise ValueError("historical source symlinks are not permitted")
        path = unresolved.resolve(strict=True)
        if integrated not in path.parents or path.is_symlink() or not path.is_file():
            raise ValueError("historical source escapes the integrated directory")
        payload = path.read_bytes()
        digest = sha256(payload).hexdigest()
        if digest != meta.get("sha256") or len(payload) != meta.get("size"):
            raise ValueError(f"historical file integrity failure: {name}")
        if meta["stage"] <= stage:
            selected[name] = (payload, digest)
    if len(selected) != 201 + 8 * (stage - 20):
        raise ValueError("selected checkpoint source is incomplete")
    return {"stage": stage, "files": selected,
            "fingerprint": _tree_fingerprint({n: x[1] for n, x in selected.items()})}


def copy_integrated_source(*, repo_root: str | Path, data_dir: str | Path,
                           stage: int, version_id: str, allow_copy: bool = False) -> dict:
    """Opt-in private SOURCE copy; refuses version overwrite; never runs it."""
    if not allow_copy:
        raise PermissionError("copying historical source requires explicit --copy")
    _safe_id(version_id)
    source = verify_archive_source(repo_root, stage)
    data = Path(data_dir).resolve()
    repo = Path(repo_root).resolve()
    if data == repo or repo.is_relative_to(data):
        raise ValueError("private data folder must not contain repository")
    desk = ProcessWorkstation(data / "workstation")
    with TemporaryDirectory(prefix="cp-reconstruction-", dir=data if data.exists() else _make_data(data)) as scratch:
        staged = Path(scratch) / "selected"
        staged.mkdir()
        for filename, (payload, _) in source["files"].items():
            (staged / filename).write_bytes(payload)
        copied = desk.copy_source(staged, worker_id=WORKER_ID, version_id=version_id,
                                  source_locator=f"repo:{MANIFEST_REL.as_posix()}#CP-{stage}")
    if copied["source_fingerprint"] != source["fingerprint"]:
        raise ValueError("integrated edition fingerprint differs from verified historical bytes")
    return {"worker_id": WORKER_ID, "version_id": version_id,
            "stage": stage, "file_count": copied["file_count"],
            "source_fingerprint": source["fingerprint"],
            "source_verified": True, "capability_verified": False,
            "executed": False, "job_admitted": False,
            "note": "Source bytes verified and copied only; no owner-backed job or evidence was transferred."}


def _make_data(data: Path) -> Path:
    data.mkdir(parents=True, exist_ok=True)
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reconstruct checked historical CP source as a private workstation edition")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--stage", type=int, choices=range(20, 31), default=30)
    parser.add_argument("--version", required=True)
    parser.add_argument("--copy", action="store_true", help="Affirm creating an isolated source copy")
    opts = parser.parse_args(argv)
    result = copy_integrated_source(repo_root=opts.repo_root, data_dir=opts.data_dir,
                                    stage=opts.stage, version_id=opts.version, allow_copy=opts.copy)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
