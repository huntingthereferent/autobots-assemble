"""Release candidate CLI from verified native A/B source and test evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from .ab_tool import ABEvidenceError
from .release import ship

def main(argv=None):
    p = argparse.ArgumentParser(prog="ab ship", description="Create a source-verified A/B release candidate")
    p.add_argument("--repo-root", type=Path, default=Path.cwd())
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--dist", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        result = ship(repo=args.repo_root, evidence=args.evidence,
                      dist=args.dist, out=args.out)
    except (OSError, ValueError, ABEvidenceError) as exc:
        print("ab ship: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0
