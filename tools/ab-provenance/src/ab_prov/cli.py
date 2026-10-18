"""Installable A/B provenance CLI, deliberately read-only on source records."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from .model import ProvenanceError, load_document, graph_summary
from .ancestry import ancestors
from .render import render_html

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ab-prov", description="Inspect existing A/B provenance records without upgrading evidence claims")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "render", "ancestors"):
        p = commands.add_parser(command)
        p.add_argument("document", type=Path, nargs="?",
                       help="JSON envelope containing core provenance_links and traces")
        p.add_argument("--journal", type=Path,
                       help="Existing runtime/journal.py JSONL workstation events")
        if command == "inspect":
            p.add_argument("--graph", action="store_true",
                           help="Print full typed graph JSON instead of summary")
        if command in ("render", "ancestors"):
            p.add_argument("--target", type=str,
                           help="Inspect upstream ancestry of a source referent by exact ID or unambiguous label")
        if command == "render":
            p.add_argument("-o", "--output", type=Path, required=True,
                           help="Write self-contained offline HTML, without altering sources")
    args = parser.parse_args(argv)
    try:
        graph = load_document(args.document, journal=args.journal)
        if args.command == "inspect":
            print(json.dumps(graph if args.graph else graph_summary(graph),
                             indent=2, sort_keys=True))
        else:
            if args.command == "ancestors" and not args.target:
                raise ProvenanceError("ancestors requires --target")
            if args.target:
                graph = ancestors(graph, args.target)
            if args.command == "ancestors":
                print(json.dumps(graph, indent=2, sort_keys=True))
                return 0
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(render_html(graph), encoding="utf-8")
            print(json.dumps({"output": str(args.output), **graph_summary(graph)},
                             sort_keys=True))
        return 0
    except (OSError, UnicodeError, ProvenanceError) as exc:
        print("ab-prov: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
