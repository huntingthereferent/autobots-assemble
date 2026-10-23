"""Bounded independent ESM static-import extraction for REA trial 01."""
from pathlib import Path
import json
import re
import sys

IMPORT = re.compile(r'(?m)^[ \t]*import[ \t]+(?:[^;\n]*?[ \t]+from[ \t]+)?[\'\"]([^\'\"\n]+)[\'\"][ \t]*;?')


def inspect(root: Path) -> dict:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("directory required")
    files = sorted(p for p in root.rglob("*.js") if p.is_file())
    modules = [p.relative_to(root).as_posix() for p in files]
    edges = []
    for file in files:
        relative = file.relative_to(root).as_posix()
        for match in IMPORT.finditer(file.read_text(encoding="utf-8")):
            specifier = match.group(1)
            if not specifier.startswith("."):
                continue
            target = (file.parent / specifier).resolve()
            try:
                target_rel = target.relative_to(root).as_posix()
            except ValueError:
                continue
            edges.append({"from": relative, "to": target_rel, "specifier": specifier})
    return {"modules": modules, "edges": edges,
            "scope": "simple static relative ESM imports; not a full JS parser"}


if __name__ == "__main__":
    print(json.dumps(inspect(Path(sys.argv[1])), indent=2, sort_keys=True))
