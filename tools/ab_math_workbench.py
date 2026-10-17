"""Read-only A/B finite-math workbench with an optional REA evidence boundary.

REA (https://github.com/morluto/rea) supplies source-analysis Evidence; it
does not certify the mathematical relationships in this module. The actual
mathematical owner is work.arc_like_maze.window_family.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
from xml.sax.saxutils import escape

from work.arc_like_maze.window_family import (
    ClassifiedWindow,
    certify_family,
    classify_pair,
    family,
    scalar_invariant,
)

SCHEMA = "ab-math-workbench/v1"
MATHEMATICAL_OWNER = "work.arc_like_maze.window_family"
REA_SOURCE = "https://github.com/morluto/rea"


def _world_id(world: ClassifiedWindow) -> str:
    return f"k{world.support}c{world.coefficient}"


def survey() -> dict:
    """Exhaust the currently declared 12-world family, not all A/B laws."""
    members = family()
    certificate = certify_family()
    if certificate.status != "CERTIFIED":
        # Report the actual certificate rather than silently assuming success.
        certification_status = certificate.status
    else:
        certification_status = "CERTIFIED"
    worlds = [
        {
            "id": _world_id(w),
            "support": w.support,
            "coefficient": w.coefficient,
            "fixed_B_depth_3": scalar_invariant(3, w.support),
        }
        for w in members
    ]
    movements = []
    walls = []
    for w in members:
        movements.append({
            "from": _world_id(w),
            "to": _world_id(w.shear_next()),
            "operation": "shear_next",
            "relation": "same declared full-state conjugacy class",
        })
        nxt = w.support_next()
        if nxt is None:
            walls.append({
                "from": _world_id(w),
                "operation": "support_next",
                "reason": "support=3 is the declared family boundary",
            })
        else:
            movements.append({
                "from": _world_id(w),
                "to": _world_id(nxt),
                "operation": "support_next",
                "relation": "different fixed-B invariant; not a conjugacy",
            })
    comparisons = []
    for i, left in enumerate(members):
        for right in members[i + 1:]:
            pair = classify_pair(left, right)
            comparisons.append({
                "left": _world_id(left),
                "right": _world_id(right),
                "status": pair.status,
                "witness_shear": pair.witness_shear,
                "left_fixed_B": pair.source_B_fixed,
                "right_fixed_B": pair.target_B_fixed,
                "obstruction_depth": pair.obstruction_depth,
            })
    return {
        "schema": SCHEMA,
        "kind": "declared-finite-family",
        "owner": MATHEMATICAL_OWNER,
        "scope": "12 constructed WindowProcess worlds over F_3; no general A/B theorem",
        "certificate": asdict(certificate),
        "certificate_status": certification_status,
        "worlds": worlds,
        "movements": movements,
        "walls": walls,
        "unordered_pair_comparisons": comparisons,
    }


def compare(left: ClassifiedWindow, right: ClassifiedWindow) -> dict:
    pair = classify_pair(left, right)
    return {
        "schema": SCHEMA,
        "kind": "finite-pair-comparison",
        "owner": MATHEMATICAL_OWNER,
        "scope": "specified 12-world family and its published proof obligations",
        "left": _world_id(left),
        "right": _world_id(right),
        "status": pair.status,
        "witness_shear": pair.witness_shear,
        "left_fixed_B_depth_3": pair.source_B_fixed,
        "right_fixed_B_depth_3": pair.target_B_fixed,
        "obstruction_depth": pair.obstruction_depth,
    }


def trace(world: ClassifiedWindow, actions: str, depth: int) -> dict:
    if depth < 3 or depth > 8:
        raise ValueError("depth must be 3..8")
    if len(actions) > 128 or any(ch not in "AB" for ch in actions):
        raise ValueError("actions must contain at most 128 A/B letters")
    state = (0,) * depth
    steps = []
    for index, action in enumerate(actions):
        before = state
        after = world.step(before, action)
        inverse = world.inverse(after, action)
        steps.append({
            "index": index + 1,
            "action": action,
            "before": before,
            "after": after,
            "inverse_recovers_before": inverse == before,
        })
        state = after
    return {
        "schema": SCHEMA,
        "kind": "finite-word-trace",
        "owner": MATHEMATICAL_OWNER,
        "world": _world_id(world),
        "depth": depth,
        "actions": actions,
        "origin": (0,) * depth,
        "final": state,
        "steps": steps,
        "all_steps_reversible": all(x["inverse_recovers_before"] for x in steps),
        "scope": "one constructed finite-state trace, not an observed application",
    }


def inspect_rea_evidence(path: Path) -> dict:
    """Index the real REA envelope without inventing mathematical correspondences.

    The original Evidence file remains authoritative. A digest binds this small
    projection to the exact bytes, including omitted or unknown fields.
    """
    raw = path.read_bytes()
    if len(raw) > 128 * 1024 * 1024:
        raise ValueError("REA Evidence input exceeds 128 MiB local intake limit")
    document = json.loads(raw)
    if not isinstance(document, dict) or not isinstance(document.get("evidence_id"), str) or "normalized_result" not in document:
        raise ValueError("expected a REA Evidence envelope with evidence_id and normalized_result")
    result = document["normalized_result"]
    if not isinstance(result, dict):
        raise ValueError("REA normalized_result is not a JSON object")
    return {
        "schema": SCHEMA,
        "kind": "rea-evidence-reference",
        "upstream": REA_SOURCE,
        "evidence_path": str(path.resolve()),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "evidence_id": document["evidence_id"],
        "operation": document.get("operation"),
        "analysis_profile": document.get("analysis_profile"),
        "result_top_level_fields": sorted(result),
        "coverage": result.get("coverage"),
        "limitations": result.get("limitations"),
        "unknowns": result.get("unknowns"),
        "status": "IMPORTED_NOT_MATH_WITNESSED",
        "reason": "REA static/runtime/source Evidence is not a proof of mathematical conjugacy",
        "next_boundary": "Select a specific REA relation, its authority, source and witness before mapping it to a mathematical question",
    }


def render_svg(survey_record: dict) -> str:
    """Self-contained GitHub-renderable diagram of actual declared movements."""
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="745" viewBox="0 0 960 745">',
        '<rect width="960" height="745" fill="#101825"/>',
        '<text x="44" y="53" fill="#f3f6fc" font-family="system-ui,sans-serif" font-size="27" font-weight="bold">A/B | Finite Mathematical Workbench</text>',
        '<text x="44" y="80" fill="#aab8ca" font-family="system-ui,sans-serif" font-size="14">Existing 12-world F3 family · movement, conjugacy, obstruction, walls</text>',
        '<g font-family="system-ui,sans-serif" font-size="14" text-anchor="middle">',
    ]
    for c in range(3):
        x = 235 + c * 270
        parts.append(f'<text x="{x}" y="120" fill="#c4cfde">shear chart c={c}</text>')
    for k in range(4):
        y = 180 + k * 145
        parts.append(f'<text x="65" y="{y + 4}" fill="#b7c8dd" text-anchor="start">support k={k}</text>')
        for c in range(3):
            x = 235 + c * 270
            if k < 3:
                parts.append(f'<path d="M{x} {y + 37} V{y + 106}" stroke="#f5ad69" stroke-width="2" stroke-dasharray="6 6"/>')
            if c < 2:
                parts.append(f'<path d="M{x + 72} {y} H{x + 198}" stroke="#76bdff" stroke-width="2"/>')
            parts.append(f'<rect x="{x - 72}" y="{y - 35}" width="144" height="70" rx="12" fill="#1c2b3d" stroke="#6a849f"/>')
            parts.append(f'<text x="{x}" y="{y - 5}" fill="#f2f6ff" font-weight="bold">k{k} c{c}</text>')
            parts.append(f'<text x="{x}" y="{y + 19}" fill="#afcbe6">fixed B: {(3-k)*3}</text>')
            if k == 3:
                parts.append(f'<text x="{x}" y="{y + 58}" fill="#ffad9f">WALL ↓</text>')
        parts.append(f'<path d="M{235 + 2*270 + 72} {y-9} h24 v18 h-24" fill="none" stroke="#76bdff" stroke-width="2"/>')
    parts.extend([
        '</g>',
        '<path d="M44 694 h28" stroke="#76bdff" stroke-width="3"/>',
        '<text x="82" y="700" fill="#d3e0ef" font-family="system-ui,sans-serif" font-size="13">shear: same class (third step returns to start)</text>',
        '<path d="M484 694 h28" stroke="#f5ad69" stroke-width="3" stroke-dasharray="6 6"/>',
        '<text x="522" y="700" fill="#d3e0ef" font-family="system-ui,sans-serif" font-size="13">support: class changes; last row is a wall</text>',
        '<text x="44" y="728" fill="#94a3b8" font-family="system-ui,sans-serif" font-size="12">Source: work.arc_like_maze.window_family · diagram does not claim universal A/B closure</text>',
        '</svg>',
    ])
    # All dynamic numeric coordinates are locally generated, not remote HTML.
    return "\n".join(parts) + "\n"


def _save_or_print(record: dict, output: str | None) -> None:
    data = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(data, encoding="utf-8")
        print(output)
    else:
        sys.stdout.write(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect actual finite A/B models and bind REA evidence without upgrading its claims")
    commands = parser.add_subparsers(dest="command", required=True)
    family_parser = commands.add_parser("survey", help="emit 12-world movements, walls, comparisons and certificate")
    family_parser.add_argument("--output")
    family_parser.add_argument("--svg")
    pair = commands.add_parser("compare", help="compare two declared family members")
    pair.add_argument("--left", nargs=2, metavar=("K", "C"), type=int, required=True)
    pair.add_argument("--right", nargs=2, metavar=("K", "C"), type=int, required=True)
    pair.add_argument("--output")
    word = commands.add_parser("trace", help="run A/B words through actual finite transitions and inverses")
    word.add_argument("--world", nargs=2, metavar=("K", "C"), type=int, required=True)
    word.add_argument("--actions", required=True)
    word.add_argument("--depth", type=int, default=3)
    word.add_argument("--output")
    rea = commands.add_parser("rea-evidence", help="read a saved REA JSON envelope; no mathematical proof inferred")
    rea.add_argument("path", type=Path)
    rea.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        if args.command == "survey":
            report = survey()
            if args.svg:
                Path(args.svg).write_text(render_svg(report), encoding="utf-8")
        elif args.command == "compare":
            report = compare(ClassifiedWindow(*args.left), ClassifiedWindow(*args.right))
        elif args.command == "trace":
            report = trace(ClassifiedWindow(*args.world), args.actions, args.depth)
        else:
            report = inspect_rea_evidence(args.path)
        _save_or_print(report, args.output)
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"WALL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
