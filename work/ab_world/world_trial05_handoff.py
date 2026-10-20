"""Carry actual WORLD Trial 05 native output into the general A/B construction ledger.

The source branch independently owns contact rules and verification. This
module only records supplied native outputs and contrasts source baselines
with constructed two-face outputs; it cannot authenticate the supplied bytes.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import re
from pathlib import Path
from typing import Any

from work.ab_world.construction import PLAN, digest, load_json, run_plan
from work.ab_world.verify_construction import verify_receipt

SCHEMA = "ab-world-trial05-source-handoff/v1"
NATIVE_SCHEMA = "world-ab-connected-receiver-routing/v1"


def contrast(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "first_contact": row["source_first_contact"],
        "outgoing_velocity": deepcopy(row["outgoing_velocity"]),
    }


def carry(native: dict[str, Any], source_commit: str) -> dict[str, Any]:
    if type(source_commit) is not str or re.fullmatch(r"[0-9a-f]{40}", source_commit) is None:
        raise ValueError("pinned original source commit SHA is required")
    if type(native) is not dict or native.get("schema") != NATIVE_SCHEMA:
        raise ValueError("not the original WORLD Trial05 source schema")
    geometry = native["geometry"]
    faces = geometry["surfaces"]
    levels = native["probe_y_levels"]
    baseline = native["baseline_first_face_only"]
    assembled = native["assembled_two_faces"]
    if (type(faces) is not list or len(faces) != 2
            or any(type(face) is not dict or type(face.get("id")) is not str for face in faces)
            or faces[0]["id"] == faces[1]["id"]):
        raise ValueError("original finite receiver faces missing or ambiguous")
    if (type(levels) is not list or not 1 <= len(levels) <= 100
            or type(baseline) is not list or type(assembled) is not list
            or len(baseline) != len(levels) or len(assembled) != len(levels)):
        raise ValueError("source probe rows do not align")
    if len(set(map(str, levels))) != len(levels):
        raise ValueError("probe levels must have distinct recorded identities")
    source = {"kind": "source-execution",
              "source": "WORLD Trial05 native source at commit " + source_commit}
    baseline_basis = {"kind": "declared",
                      "source": "WORLD Trial05 original single-receiver control at " + source_commit}
    steps = [
        {"op": "introduce", "id": "source-face-0", "state": deepcopy(faces[0]), "basis": source},
        {"op": "introduce", "id": "source-face-1", "state": deepcopy(faces[1]), "basis": source},
        {"op": "connect", "id": "source-junction", "from": "source-face-0",
         "to": "source-face-1", "label": "source-reported-finite-intersection",
         "state": {"junction": deepcopy(geometry["junction"]),
                   "topology": deepcopy(geometry["topology"])}, "basis": source},
    ]
    changed = []
    for i, (level, old, new) in enumerate(zip(levels, baseline, assembled), 1):
        if type(old) is not dict or type(new) is not dict:
            raise ValueError("source result must be a record")
        if old["initial"] != new["initial"]:
            raise ValueError("original and assembled probes must share the initial state")
        prior = contrast(old)
        observed = contrast(new)
        if prior != observed:
            changed.append(level)
        ident = f"source-probe-{i:03d}"
        obs = f"source-observation-{i:03d}"
        steps.extend([
            {"op": "introduce", "id": ident, "state": {
                "level": level, "baseline": deepcopy(old)}, "basis": baseline_basis},
            {"op": "revise", "entity": "object", "id": ident, "after": {
                "level": level, "baseline": deepcopy(old),
                "assembled": deepcopy(new)}, "basis": source},
            {"op": "observe", "id": obs, "entity": "object", "subject": ident,
             "reading": observed, "basis": source},
            {"op": "compare", "id": f"baseline-contrast-{i:03d}",
             "observation": obs, "expected": prior, "basis": baseline_basis},
        ])
    if changed != native["route_changed_probe_levels"]:
        raise ValueError("source reported changed routes disagree with its own rows")
    plan = {
        "schema": PLAN,
        "referent": "WORLD Trial05 native first-contact routing / original source",
        "limits": {"objects": 2 + len(levels), "relations": 1, "steps": len(steps)},
        "steps": steps,
    }
    receipt = run_plan(plan)
    witness = verify_receipt(receipt)
    return {
        "schema": SCHEMA,
        "source_commit": source_commit,
        "reported_native_content_sha256": digest(native),
        "original_source_verification": "requires separate native test execution",
        "difference_levels": changed,
        "world_receipt": receipt,
        "ledger_witness": witness,
        "source_authenticated_by_this_adapter": False,
        "physical_measurement_verified": False,
        "multicontact_physics_verified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    result = carry(load_json(args.native), args.source_commit)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
