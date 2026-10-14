"""Isolated, source-preserving working copies of process implementations.

This is a local version workstation, not an AI agent, build executor, or
claim of verified capability. Source trees and checkpoint evidence stay native.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
from tempfile import mkdtemp
from typing import Any

_ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,79}\Z")
_MANIFEST = "_worker_version.json"
_SKIP_DIRS = {"__pycache__", ".git", ".pytest_cache", ".mypy_cache"}
_FORBIDDEN = {".env", ".env.local", "id_rsa", "id_ed25519", ".secrets"}
_MAX_FILES = 2000
_MAX_BYTES = 50_000_000


def _safe_id(value: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value) or value in {".", ".."}:
        raise ValueError("worker and version IDs must be safe simple names")
    return value


def _hash_tree(root: Path) -> dict[str, str]:
    """Inventory regular source files, refusing unsafe/special file entries."""
    if not root.is_dir() or root.is_symlink():
        raise ValueError("source must be an ordinary existing directory")
    hashes: dict[str, str] = {}
    total = 0
    for base, dirs, files in os.walk(root, followlinks=False):
        keep = []
        for d in dirs:
            entry = Path(base) / d
            if entry.is_symlink():
                raise ValueError("source tree must not contain symlink directories")
            if d not in _SKIP_DIRS:
                if d in _FORBIDDEN:
                    raise ValueError("source tree contains a forbidden directory")
                keep.append(d)
        dirs[:] = keep
        for filename in files:
            path = Path(base) / filename
            if path.is_symlink() or not path.is_file():
                raise ValueError("source tree must contain ordinary files only")
            if filename in _FORBIDDEN or filename == _MANIFEST:
                raise ValueError("source tree contains a forbidden or reserved filename")
            data = path.read_bytes()
            total += len(data)
            if total > _MAX_BYTES or len(hashes) >= _MAX_FILES:
                raise ValueError("source exceeds workstation copy budget")
            rel = path.relative_to(root).as_posix()
            hashes[rel] = sha256(data).hexdigest()
    if not hashes:
        raise ValueError("source has no copyable files")
    return dict(sorted(hashes.items()))


def _tree_fingerprint(files: dict[str, str]) -> str:
    return sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class ProcessWorkstation:
    """Copies code into private editions and records ancestry; never runs it."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def _edition(self, worker_id: str, version_id: str) -> Path:
        return self.root / _safe_id(worker_id) / _safe_id(version_id)

    def _read(self, worker_id: str, version_id: str) -> tuple[Path, dict[str, Any]]:
        folder = self._edition(worker_id, version_id)
        if folder.is_symlink() or not folder.is_dir():
            raise KeyError("unknown worker edition")
        try:
            row = json.loads((folder / _MANIFEST).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ValueError("edition provenance manifest missing or invalid") from exc
        expected = {"schema_version", "worker_id", "version_id", "parent_version", "source_locator", "source_fingerprint", "baseline"}
        if not isinstance(row, dict) or set(row) != expected or row["schema_version"] != 1 or row["worker_id"] != worker_id or row["version_id"] != version_id:
            raise ValueError("edition provenance manifest identity mismatch")
        if not isinstance(row["baseline"], dict) or row["source_fingerprint"] != _tree_fingerprint(row["baseline"]):
            raise ValueError("edition provenance manifest fingerprint mismatch")
        return folder, row

    def _fork(self, *, source: Path, worker_id: str, version_id: str, parent_version: str | None, source_locator: str) -> dict[str, Any]:
        destination = self._edition(worker_id, version_id)
        source = Path(source).resolve(strict=True)
        if self.root == source or self.root.is_relative_to(source) or source.is_relative_to(self.root):
            # Branching from an already recorded edition is handled separately.
            if parent_version is None or not source.is_relative_to(self.root):
                raise ValueError("source and private workstation must not overlap")
        if destination.exists():
            raise FileExistsError("worker version already exists; editions are never overwritten")
        baseline = _hash_tree(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        tmp = Path(mkdtemp(prefix=".candidate-", dir=destination.parent))
        try:
            for rel in baseline:
                target = tmp / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / rel, target)
            if _hash_tree(tmp) != baseline:
                raise ValueError("copied source content changed while being captured")
            record = {"schema_version": 1, "worker_id": worker_id, "version_id": version_id,
                      "parent_version": parent_version, "source_locator": source_locator,
                      "source_fingerprint": _tree_fingerprint(baseline), "baseline": baseline}
            (tmp / _MANIFEST).write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            # Reject concurrent version creation; only one process may write an
            # edition. This prototype does not supply multi-process locking.
            if destination.exists():
                raise FileExistsError("worker version concurrently created")
            tmp.rename(destination)
            return {"path": str(destination), "worker_id": worker_id, "version_id": version_id,
                    "parent_version": parent_version, "file_count": len(baseline),
                    "source_fingerprint": record["source_fingerprint"]}
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def copy_source(self, source: str | Path, *, worker_id: str, version_id: str,
                    source_locator: str | None = None) -> dict[str, Any]:
        """Copy a chosen tree; optional stable provenance locator, never execution."""
        locator = str(Path(source).resolve()) if source_locator is None else source_locator
        if not isinstance(locator, str) or not locator.strip() or any(x in locator for x in "\r\n"):
            raise ValueError("source locator must be nonempty single-line text")
        return self._fork(source=Path(source), worker_id=worker_id, version_id=version_id,
                          parent_version=None, source_locator=locator)

    def branch(self, *, worker_id: str, parent_version: str, version_id: str) -> dict[str, Any]:
        """Fork the current files of an earlier private edition into a new one."""
        parent, record = self._read(worker_id, parent_version)
        # _hash_tree rejects the metadata file; capture the source without it.
        return self._fork_from_edition(parent, record, version_id=version_id)

    def _fork_from_edition(self, parent: Path, record: dict[str, Any], *, version_id: str) -> dict[str, Any]:
        worker_id = record["worker_id"]
        dest = self._edition(worker_id, version_id)
        if dest.exists():
            raise FileExistsError("worker version already exists")
        inventory = self._inventory_edition(parent)
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = Path(mkdtemp(prefix=".candidate-", dir=dest.parent))
        try:
            for rel in inventory:
                p = tmp / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(parent / rel, p)
            if _hash_tree(tmp) != inventory:
                raise ValueError("branch source changed during copying")
            item = {"schema_version": 1, "worker_id": worker_id, "version_id": version_id,
                    "parent_version": record["version_id"], "source_locator": record["source_locator"],
                    "source_fingerprint": _tree_fingerprint(inventory), "baseline": inventory}
            (tmp / _MANIFEST).write_text(json.dumps(item, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            if dest.exists():
                raise FileExistsError("concurrent version already exists")
            tmp.rename(dest)
            return {"path": str(dest), "worker_id": worker_id, "version_id": version_id,
                    "parent_version": record["version_id"], "file_count": len(inventory),
                    "source_fingerprint": item["source_fingerprint"]}
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    @staticmethod
    def _inventory_edition(folder: Path) -> dict[str, str]:
        # Inventory only the user-modifiable source, excluding reserved record.
        entries: dict[str, str] = {}
        count = total = 0
        for base, dirs, files in os.walk(folder, followlinks=False):
            for d in dirs:
                if (Path(base) / d).is_symlink() or d in _FORBIDDEN:
                    raise ValueError("unsafe branch directory")
            dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
            for filename in files:
                p = Path(base) / filename
                if p.is_symlink() or not p.is_file():
                    raise ValueError("unsafe branch file")
                if filename == _MANIFEST and p.parent == folder:
                    continue
                if filename in _FORBIDDEN:
                    raise ValueError("unsafe branch file name")
                content = p.read_bytes()
                total += len(content)
                count += 1
                if count > _MAX_FILES or total > _MAX_BYTES:
                    raise ValueError("worker branch exceeds copy budget")
                entries[p.relative_to(folder).as_posix()] = sha256(content).hexdigest()
        if not entries:
            raise ValueError("worker branch has no source files")
        return dict(sorted(entries.items()))

    def inspect(self, *, worker_id: str, version_id: str) -> dict[str, Any]:
        """Read-only source diff against the edition's original snapshot."""
        folder, record = self._read(worker_id, version_id)
        now = self._inventory_edition(folder)
        old = record["baseline"]
        return {"worker_id": worker_id, "version_id": version_id,
                "parent_version": record["parent_version"],
                "path": str(folder), "baseline_fingerprint": record["source_fingerprint"],
                "current_fingerprint": _tree_fingerprint(now),
                "modified": sorted(k for k in now.keys() & old.keys() if now[k] != old[k]),
                "added": sorted(now.keys() - old.keys()),
                "deleted": sorted(old.keys() - now.keys()),
                "executed": False, "verified": False}
