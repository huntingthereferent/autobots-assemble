"""Carry original WORLD15 body-support movement and source misses into A/B.

Source dynamics, body support and the independent geometry oracle belong to
the immutable WORLD15 source. This adapter records reported finite motion and
causal receiver introduction. It never solves unconstrained square rotation,
finite-segment endpoint contact, or measured physical collision mechanics.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from math import isfinite
from pathlib import Path
import re
from typing import Any

from work.ab_world.construction import PLAN, digest, load_json, run_plan
from work.ab_world.verify_construction import verify_receipt

SCHEMA = "ab-world-trial15-body-support-causal-handoff/v1"
SOURCE = "world-ab-body-support-construction/v1"
BODIES = ("disc", "fixed-square")
ANGLES = (0., 7.5, 12.25, 20.)
SUCCESS = "TWO_MODELED_CONTACTS"
REFUSAL = "NO_ADMITTED_INTERIOR_CONTACT"


def demand(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError("WORLD15 A/B: " + msg)


def num(v: Any) -> bool:
    return type(v) in (float, int) and isfinite(v)


def xy(v: Any) -> bool:
    return type(v) is list and len(v) == 2 and all(num(x) for x in v)


def check_base(case: dict[str, Any]) -> None:
    demand(type(case) is dict and case.get("schema") == SOURCE,
           "original body-support schema changed")
    body = case.get("body")
    demand(body in BODIES, "source body no longer bounded")
    demand(case.get("body_support") ==
           ("disc radius" if body == "disc" else
            "axis-aligned square support, orientation fixed by constraint"),
           "body support model or square constraint changed")
    demand(case.get("selected_physical_outcome") is False and
           case.get("measured_earth_material") is False and
           case.get("target_receiver_shape_provided") is False,
           "model geometry promoted to material observation")
    demand(num(case.get("half_extent")) and case["half_extent"] > 0 and
           xy(case.get("source_anchor")) and xy(case.get("initial_center")) and
           xy(case.get("initial_velocity")) and
           num(case.get("source_angle")) and
           abs(case["source_angle"]) <= 40,
           "bounded source controls missing")
    source = case.get("source")
    demand(type(source) is dict and
           source.get("id") == "original-test-source" and
           xy(source.get("anchor")) and xy(source.get("normal")) and
           type(source.get("endpoints")) is list and
           len(source["endpoints"]) == 2 and
           all(xy(p) for p in source["endpoints"]),
           "original finite input segment missing")


def carry(native: dict[str, Any], source_commit: str, refused: dict[str, Any]) -> dict[str, Any]:
    demand(type(source_commit) is str and
           re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None,
           "exact pinned original source commit required")
    demand(type(native) is dict and native.get("schema") == SOURCE and
           native.get("source_trial14") ==
           "world-ab-relation-derived-free-orientation/v1" and
           native.get("source_trial04b_reused") is True and
           native.get("body_types") == list(BODIES) and
           native.get("angles") == list(ANGLES) and
           native.get("shape_independent_contact_law") ==
           "frictionless translational normal reflection" and
           native.get("no_new_world_or_renderer") is True and
           native.get("real_material_behavior_observed") is False,
           "original constrained source lineage changed")
    cases = native.get("cases")
    demand(type(cases) is list and len(cases) == 8,
           "eight predeclared disc and fixed-square movements required")
    owner = {"kind": "source-execution",
             "source": "pinned native WORLD15 @" + source_commit}
    model = {"kind": "declared",
             "source": "finite translational normal reflection, constrained square"}
    pages = []
    sample_count = 0
    for i, (body, angle) in enumerate((b, a) for b in BODIES for a in ANGLES):
        case = cases[i]
        check_base(case)
        demand(case.get("body") == body and case.get("source_angle") == angle and
               case.get("source_anchor") == [12., 1.5],
               "predeclared body support and angle case reordered")
        demand(case.get("status") == SUCCESS and
               case.get("actual_hardware_contact_witnessed") is False and
               case.get("new_physical_law_inferred") is False and
               case.get("finite_face_endpoints_matter") is True and
               case.get("square_rotation_prevented_by_constraint") ==
               (body == "fixed-square"),
               "two-contact trial/rotation boundary altered")
        src = case["source"]
        rec = case.get("receiver")
        contacts = case.get("contacts")
        demand(type(rec) is dict and rec.get("id") == "movement-derived-receiver" and
               rec.get("constructed_from") == "recorded-model-outgoing-velocity" and
               rec.get("caused_by_contact_index") == 0 and
               xy(rec.get("normal")) and xy(rec.get("anchor")) and
               type(rec.get("endpoints")) is list and
               len(rec["endpoints"]) == 2 and all(xy(p) for p in rec["endpoints"]),
               "derived receiver ancestry or finite face missing")
        demand(type(contacts) is list and len(contacts) == 2 and
               all(type(c) is dict and num(c.get("time")) and
                   xy(c.get("center")) and xy(c.get("before")) and
                   xy(c.get("after")) for c in contacts),
               "original modeled contacts missing")
        first, second = contacts
        t1, t2 = first["time"], second["time"]
        demand(t1 > 0 and t2 > t1 and
               first.get("source_id") == src["id"] and
               second.get("source_id") == rec["id"] and
               num(rec.get("activated_at")) and
               abs(rec["activated_at"]-t1) < 2e-9 and
               first["after"] == second["before"],
               "receiver backdated or separated from first movement")
        frames = case.get("frames")
        demand(type(frames) is list and len(frames) >= 12,
               "original finite motion frames missing")
        steps = [
            {"op": "introduce", "id": "original-finite-input",
             "state": deepcopy(src), "basis": owner},
            {"op": "introduce", "id": "controlled-moving-body",
             "state": {"body": body, "center": deepcopy(case["initial_center"]),
                       "velocity": deepcopy(case["initial_velocity"]),
                       "time": 0., "virtual_only": True,
                       "square_rotation_fixed": body == "fixed-square"},
             "basis": model},
            {"op": "connect", "id": "original-source-approach",
             "from": "original-finite-input", "to": "controlled-moving-body",
             "label": "original-bounded-support-test",
             "state": {"body_support": case["body_support"], "source_angle": angle},
             "basis": model},
        ]
        first_seen = False
        second_seen = False
        prior = -1.
        for frame in frames:
            demand(type(frame) is dict and num(frame.get("time")) and
                   frame["time"] > prior and xy(frame.get("center")) and
                   xy(frame.get("velocity")),
                   "source body motion time/position/velocity out of order")
            current = frame["time"]
            prior = current
            if current >= t1 and not first_seen:
                steps.extend([
                    {"op": "observe", "id": "first-source-model-contact",
                     "entity": "object", "subject": "original-finite-input",
                     "reading": {"modeled_contact": deepcopy(first),
                                 "measured_hardware": False}, "basis": owner},
                    {"op": "introduce", "id": "derived-receiver",
                     "state": deepcopy(rec), "basis": model},
                    {"op": "connect", "id": "movement-created-geometry",
                     "from": "controlled-moving-body", "to": "derived-receiver",
                     "label": "constructed-from-first-outgoing-velocity",
                     "state": {"activated_at": t1,
                               "receiver_existed_before_first_contact": False},
                     "basis": model},
                ])
                first_seen = True
            if current >= t2 and not second_seen:
                demand(first_seen, "receiver contact before creation")
                steps.append({
                    "op": "observe", "id": "second-receiver-model-contact",
                    "entity": "object", "subject": "derived-receiver",
                    "reading": {"modeled_contact": deepcopy(second),
                                "measured_hardware": False}, "basis": owner})
                second_seen = True
            steps.append({
                "op": "revise", "entity": "object", "id": "controlled-moving-body",
                "after": {"body": body, "center": deepcopy(frame["center"]),
                          "velocity": deepcopy(frame["velocity"]),
                          "time": current, "virtual_only": True,
                          "square_rotation_fixed": body == "fixed-square"},
                "basis": owner,
            })
        demand(first_seen and second_seen and frames[0]["time"] == 0. and
               frames[-1]["time"] >= t2,
               "finite motion history did not reach both modeled contacts")
        steps.append({
            "op": "observe", "id": "finite-source-horizon",
            "entity": "object", "subject": "controlled-moving-body",
            "reading": {"original_case_sha256": digest(case),
                        "model_status": SUCCESS,
                        "body": body, "square_rotation_fixed": body == "fixed-square",
                        "frames_retained": len(frames),
                        "hardware_witnessed": False}, "basis": owner})
        plan = {"schema": PLAN,
                "referent": f"WORLD15 / bounded {body} source angle {angle}",
                "limits": {"objects": 3, "relations": 2, "steps": len(steps)},
                "steps": steps}
        receipt = run_plan(plan)
        pages.append({
            "kind": "completed", "case": i, "body": body, "angle": angle,
            "frames": len(frames), "receipt": receipt,
            "witness": verify_receipt(receipt)})
        sample_count += len(frames)

    # A square that reaches only an unsupported finite endpoint has NOT been
    # shown to miss material; keep the failure-to-admit-source-model exactly.
    check_base(refused)
    demand(refused.get("body") == "fixed-square" and
           refused.get("source_angle") == 30. and
           refused.get("status") == REFUSAL and
           refused.get("receiver") is None and
           refused.get("contacts") == [] and refused.get("frames") == [],
           "unsupported endpoint converted to completed motion or physical miss")
    refusal_steps = [
        {"op": "introduce", "id": "finite-source",
         "state": deepcopy(refused["source"]), "basis": owner},
        {"op": "introduce", "id": "constrained-square",
         "state": {"body": "fixed-square", "orientation_fixed": True,
                   "initial_center": deepcopy(refused["initial_center"]),
                   "completed_motion": None}, "basis": model},
        {"op": "observe", "id": "outside-admitted-interior-contact",
         "entity": "object", "subject": "finite-source",
         "reading": {"source_status": REFUSAL, "not_an_observed_physical_miss": True,
                     "receiver": None, "source_sha256": digest(refused)},
         "basis": owner},
    ]
    refusal_plan = {
        "schema": PLAN, "referent": "WORLD15 / unsupported square endpoint contact",
        "limits": {"objects": 2, "relations": 1,
                   "steps": len(refusal_steps)}, "steps": refusal_steps,
    }
    receipt = run_plan(refusal_plan)
    pages.append({"kind": "unsupported", "case": 8,
                  "body": "fixed-square", "angle": 30., "frames": 0,
                  "receipt": receipt, "witness": verify_receipt(receipt)})
    manifest = {
        "native_report_sha256": digest(native),
        "refusal_sha256": digest(refused),
        "ordered_case_heads": [
            {"kind": p["kind"], "case": p["case"], "body": p["body"],
             "angle": p["angle"], "head_hash": p["receipt"]["head_hash"]}
            for p in pages],
    }
    witness = {
        "valid": all(p["witness"]["valid"] for p in pages),
        "pages_verified": len(pages),
        "steps_verified": sum(p["witness"]["steps_verified"] for p in pages),
        "observations_recorded": sum(
            p["witness"]["observations_recorded"] for p in pages),
    }
    return {
        "schema": SCHEMA, "source_commit": source_commit,
        "source_report_sha256": digest(native),
        "completed_source_cases": 8, "unsupported_endpoint_cases": 1,
        "preserved_motion_frames": sample_count,
        "receiver_created_after_source_contact": True,
        "free_square_rotation_solved": False,
        "actual_physical_contact_measured": False,
        "physical_endpoint_miss_established": False,
        "native_physics_verified_by_adapter": False,
        "ledger_pages": pages, "ledger_witness": witness,
        "page_manifest": manifest,
        "page_manifest_sha256": digest(manifest),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--refusal", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    print(json.dumps(carry(load_json(args.native), args.source_commit,
                           load_json(args.refusal)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
