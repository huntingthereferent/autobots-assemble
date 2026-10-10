"""Inventory and safely stage historical Continuity research ZIPs.

No network, Git actions, or overwrites. Deliberately opt in to extraction:
  python -m research.continuity_archive_import --source ZIP_FOLDER --destination REPO --stage

Each archive member is placed under a per-archive provenance directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

NAMESPACE = Path("research/continuity_engine/collected/archive_sources")
SKIPPED = {".pyc", ".pyo", ".DS_Store"}


def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def safe_path(name: str) -> PurePosixPath:
    if not name or "\\" in name or "\x00" in name:
        raise ValueError(f"unsafe archive member: {name!r}")
    parts = PurePosixPath(name).parts
    if (name.startswith("/") or not parts or any(part in (".", "..") for part in parts)
            or ":" in parts[0]):
        raise ValueError(f"unsafe archive member: {name!r}")
    return PurePosixPath(*parts)


def inventory(source: Path) -> tuple[list[dict], list[tuple[str, bytes]]]:
    records = []
    contents = []
    seen_archive_names = set()
    for archive in sorted(source.glob("*.zip"), key=lambda p: p.name.lower()):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+\.zip", archive.name, flags=re.IGNORECASE):
            raise ValueError(f"unsafe archive filename: {archive.name}")
        slug = archive.stem
        if slug.casefold() in seen_archive_names:
            raise ValueError("case-insensitive archive basename collision")
        seen_archive_names.add(slug.casefold())
        with zipfile.ZipFile(archive) as z:
            seen_paths = set()
            for entry in z.infolist():
                if entry.is_dir():
                    continue
                p = safe_path(entry.filename)
                if p.as_posix().casefold() in seen_paths:
                    raise ValueError(f"duplicate member: {archive.name} / {p}")
                seen_paths.add(p.as_posix().casefold())
                if "__pycache__" in p.parts or p.suffix in SKIPPED:
                    continue
                filetype = (entry.external_attr >> 16) & 0o170000
                if filetype not in (0, 0o100000):
                    raise ValueError("unsafe special-file member")
                blob = z.read(entry)
                target = (NAMESPACE / slug / Path(*p.parts)).as_posix()
                records.append({"archive": archive.name, "member": p.as_posix(),
                                "target": target, "bytes": len(blob), "sha256": digest(blob)})
                contents.append((target, blob))
    return records, contents


def run(source: Path, destination: Path, *, stage: bool = False) -> dict:
    if not source.is_dir() or not destination.is_dir():
        raise ValueError("existing ZIP folder and checkout directory are required")
    records, blobs = inventory(source)
    output = {"schema": 1, "archive_count": len(set(x["archive"] for x in records)),
              "member_count": len(records),
              "distinct_sha256_count": len(set(x["sha256"] for x in records)),
              "contents": records}
    root = destination.resolve()
    pending = []
    for rel, blob in blobs:
        p = (root / rel).resolve()
        if root not in p.parents:
            raise ValueError("staging path escaped destination")
        if p.exists():
            if not p.is_file() or p.read_bytes() != blob:
                raise FileExistsError(f"conflicting existing file: {p}")
        else:
            pending.append((p, blob))
    if stage:
        for p, blob in pending:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(blob)
            if p.read_bytes() != blob:
                raise IOError(f"write verification failed: {p}")
    output["pending_files"] = len(pending)
    output["staged"] = stage
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--stage", action="store_true",
                        help="copy missing members under archive_sources")
    parser.add_argument("--manifest", type=Path, help="optional JSON inventory output")
    a = parser.parse_args()
    report = run(a.source, a.destination, stage=a.stage)
    if a.manifest:
        a.manifest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "contents"}, indent=2))


if __name__ == "__main__":
    main()
