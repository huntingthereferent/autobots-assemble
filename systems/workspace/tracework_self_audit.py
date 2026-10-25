"""Evaluate one explicitly selected finite audit; never select latest main as referent."""
import argparse
import json
from pathlib import Path
from systems.workspace.bounded_audit import assess, load

DEFAULT = Path(__file__).with_name("audits") / "tracework-self-audit-2026-10-25.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=DEFAULT)
    parser.add_argument("--out", type=Path, default=Path("tracework-self-audit.json"))
    args = parser.parse_args()
    result = assess(load(args.audit))
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["closed"]:
        raise SystemExit("Audit remains open; unresolved descendants must close against its original referent.")


if __name__ == "__main__":
    main()
