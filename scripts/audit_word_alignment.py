#!/usr/bin/env python3
"""Read-only vocabulary audit of both checked-out GitHub repositories.

This is a lexical and reference inventory, not a semantic proof or a runtime test.
Historical source records are scanned and reported, not silently rewritten.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

CURRENT_TRACEWORK = {
    "README.md", "AGENTS.md", "ENTRY.md", "TRACEWORK.md",
    "LANGUAGE_REFERENT.md", "LANGUAGE_REFERENT_CONTRACT.md",
    "language/SHAPE_CONTRACT.md", "foundation/PROGRAM_FOUNDATION.md",
    "protocols/ai/session.md", "language/README.md",
    "language/REGROUNDING.md", "language/HUMAN_DRIFT.md",
}
CURRENT_PROFILE = {"README.md", "RESEARCH.md", "ABILITY.md"}
TERMS = {
    "EXPERIENCE_AS_ASSERTION": re.compile(
        r"(?:James (?:describes|models|asserts) (?:their |his )?continuity|"
        r"James(?:'s)? (?:current )?geometric description|"
        r"I describe continuity as)", re.I
    ),
    "LEGACY_NAME_IN_TEXT": re.compile(r"\bTraceworks\b"),
    "UNCONDITIONAL_CLOSURE": re.compile(
        r"(?:decoded output is valid input|"
        r"output (?:always |automatically )?(?:remains|is) (?:a )?valid input|"
        r"proves? (?:universal |absolute )?truth)", re.I
    ),
    "WITHDRAWN_LINK_OR_TOOL": re.compile(
        r"(?:tree/main/writing|tools/generate_work_views\.py|"
        r"tools/generate_ab_views\.py|Human Drift chronology)", re.I
    ),
    "ABSOLUTE_CLAIM_REVIEW": re.compile(
        r"\b(?:universally proven|guarantees? continuity|drift.free|"
        r"only possible model|safety mechanism for truth)\b", re.I
    ),
}
MD_LINK = re.compile(r"\]\(([^)\s]+)(?:\s+['\"][^)]*)?\)")
INTERNAL_GITHUB = re.compile(
    r"https://github\.com/huntingthereferent/(autobots-assemble|huntingthereferent)"
    r"/(?:blob|tree)/main/([^\s)]+)"
)
CHECK_REQUIRED = {
    "profile": {
        "README.md": (
            "I feel continuity as **toroidal movement**",
            "mathematical witness",
            "recursion test",
        )
    },
    "tracework": {
        "LANGUAGE_REFERENT.md": (
            "James feels continuity as **toroidal movement**",
            "**Finite witness.**",
            "**Recursion test.**",
        ),
        "LANGUAGE_REFERENT_CONTRACT.md": (
            "James feels continuity as **toroidal movement**",
            "A finite toroidal model is a **witness**",
            "**Outputs are checked for re-entry.**",
        ),
        "language/SHAPE_CONTRACT.md": (
            "James feels continuity as **toroidal movement**",
            "The **recursion test** checks",
        ),
    },
}


def tracked(root: Path) -> list[Path]:
    raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    return [Path(x.decode("utf-8")) for x in raw.split(b"\0") if x]


def classification(alias: str, path: str) -> str:
    current = CURRENT_PROFILE if alias == "profile" else CURRENT_TRACEWORK
    if path in current:
        return "current-guidance"
    if re.search(r"(?:^|/)(?:archive|runs|checkpoints|history|snapshots)/", path, re.I) \
            or re.search(r"20[0-9]{2}[-_][01][0-9][-_][0-3][0-9]", path) \
            or path.startswith(("research/", "work/")):
        return "historical-or-study"
    return "other-source"


def run(roots: dict[str, Path]) -> dict:
    entries: list[dict] = []
    all_paths: dict[str, set[str]] = {}
    stats: dict[str, dict] = {}
    loaded: dict[str, dict[str, str]] = {}
    for alias, root in roots.items():
        paths = tracked(root)
        names = {p.as_posix() for p in paths}
        all_paths[alias] = names
        stats[alias] = {
            "tracked": len(paths), "text_read": 0, "binary_skipped": 0,
            "decode_failed": 0, "markdown_read": 0, "bytes_read": 0,
        }
        loaded[alias] = {}
        for rel in paths:
            full = root / rel
            try:
                data = full.read_bytes()
            except (OSError, ValueError):
                stats[alias]["decode_failed"] += 1
                continue
            if b"\0" in data:
                stats[alias]["binary_skipped"] += 1
                continue
            try:
                content = data.decode("utf-8")
            except UnicodeDecodeError:
                stats[alias]["decode_failed"] += 1
                continue
            path = rel.as_posix()
            loaded[alias][path] = content
            stats[alias]["text_read"] += 1
            stats[alias]["bytes_read"] += len(data)
            if path.lower().endswith((".md", ".mdx", ".rst", ".txt")):
                stats[alias]["markdown_read"] += 1
            kind = classification(alias, path)
            if path == "scripts/audit_word_alignment.py":
                continue
            for number, line in enumerate(content.splitlines(), 1):
                for code, regex in TERMS.items():
                    if regex.search(line):
                        entries.append({
                            "repo": alias, "path": path, "line": number,
                            "kind": kind, "code": code, "text": line.strip()[:260],
                            "severity": "review",
                        })
            if path.lower().endswith((".md", ".mdx")):
                for number, line in enumerate(content.splitlines(), 1):
                    for link in MD_LINK.findall(line):
                        raw = unquote(link.split("#")[0].split("?")[0])
                        if not raw or raw.startswith(("http:", "https:", "mailto:", "data:", "#")):
                            continue
                        dest = (rel.parent / raw).as_posix()
                        while "/../" in dest:
                            dest = re.sub(r"[^/]+/\.\./", "", dest, count=1)
                        dest = re.sub(r"^\./", "", dest)
                        dest_dir = root / dest
                        if dest not in names and not dest_dir.is_dir():
                            entries.append({
                                "repo": alias, "path": path, "line": number,
                                "kind": kind, "code": "MISSING_RELATIVE_TARGET",
                                "text": f"{raw} -> {dest}", "severity": "review",
                            })
    # Cross-repository and same-repository GitHub main links.
    for alias, files in loaded.items():
        for path, content in files.items():
            if not path.lower().endswith((".md", ".mdx")):
                continue
            for number, line in enumerate(content.splitlines(), 1):
                for repo_name, tail in INTERNAL_GITHUB.findall(line):
                    other = "profile" if repo_name == "huntingthereferent" else "tracework"
                    rel = unquote(tail.split("#")[0].split("?")[0])
                    root = roots[other]
                    if rel not in all_paths[other] and not (root / rel).is_dir():
                        entries.append({
                            "repo": alias, "path": path, "line": number,
                            "kind": classification(alias, path),
                            "code": "MISSING_GITHUB_MAIN_TARGET",
                            "text": f"{repo_name}/{rel}", "severity": "review",
                        })
    for alias, requirements in CHECK_REQUIRED.items():
        for path, phrases in requirements.items():
            content = loaded[alias].get(path, "")
            for phrase in phrases:
                if phrase.casefold() not in content.casefold():
                    entries.append({
                        "repo": alias, "path": path, "line": 0,
                        "kind": "current-guidance", "code": "CANONICAL_MISSING",
                        "text": phrase, "severity": "error",
                    })
    profile = loaded["profile"].get("README.md", "")
    for ban in (r"\bflow\b", r"\bI describe continuity as\b"):
        if re.search(ban, profile, re.I):
            entries.append({
                "repo": "profile", "path": "README.md", "line": 0,
                "kind": "current-guidance", "code": "PROFILE_REJECTED_WORDING",
                "text": ban, "severity": "error",
            })
    return {"stats": stats, "counts": dict(Counter(x["code"] for x in entries)),
            "findings": entries, "errors": sum(x["severity"] == "error" for x in entries)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracework", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--json", type=Path, default=Path("word-alignment-report.json"))
    args = parser.parse_args()
    result = run({"tracework": args.tracework.resolve(), "profile": args.profile.resolve()})
    args.json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for alias, stat in result["stats"].items():
        print(
            f"{alias}: {stat['tracked']} tracked, {stat['text_read']} UTF-8 text read, "
            f"{stat['markdown_read']} prose documents, "
            f"{stat['binary_skipped']} binary skipped, "
            f"{stat['decode_failed']} unreadable"
        )
    print("Review findings by category:")
    for category, amount in sorted(result["counts"].items()):
        print(f"  {category}: {amount}")
    print(f"Canonical wording failures: {result['errors']}")
    for finding in result["findings"]:
        print(
            f"[{finding['severity']}] {finding['repo']}/{finding['path']}:"
            f"{finding['line']} [{finding['code']}] {finding['text']}"
        )
    print(f"Structured findings: {args.json}")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
