"""Preserve original WORLD15 moving disc/fixed-square source as finite A/B evidence.

Only the original WORLD source and separate native geometry witness test contact
physics. This adapter transports chronological, source-attributed state and
declared shape support into neutral A/B ledgers. It does not select material laws.
"""
from __future__ import annotations

from copy import deepcopy
from math import isfinite
from typing import Any
import argparse
import json
from pathlib import Path

from work.ab_world.construction import PLAN, digest, load_json, run_plan
from work.ab_world.verify_construction import verify_receipt

PIN = "65339494abaccac3c4dd20aa89439af057ec3035"
SOURCE = "world-ab-body-support-construction/v1"
SCHEMA = "ab-world-trial15-body-support-handoff/v1"
BODIES = ("disc", "fixed-square")
ANGLES = (0., 7.5, 12.25, 20.)


def require(ok: bool, description: str) -> None:
    if not ok:
        raise ValueError("WORLD15 handoff: " + description)


def number(x: Any) -> bool:
    return type(x) in (int, float) and isfinite(x)


def pair(x: Any) -> bool:
    return type(x) is list and len(x) == 2 and all(number(y) for y in x)


def source_case(case: dict, body: str, angle: float) -> None:
    require(type(case) is dict and case.get("schema") == SOURCE and
            case.get("body") == body and case.get("source_angle") == angle and
            case.get("source_anchor") == [12., 1.5],
            "source case grid/control changed")
    require(case.get("status") == "TWO_MODELED_CONTACTS" and
            case.get("selected_physical_outcome") is False and
            case.get("measured_earth_material") is False and
            case.get("target_receiver_shape_provided") is False and
            case.get("actual_hardware_contact_witnessed") is False and
            case.get("new_physical_law_inferred") is False,
            "unsupported physical claim or missing modeled continuation")
    require(number(case.get("half_extent")) and case["half_extent"] > 0 and
            pair(case.get("initial_center")) and
            pair(case.get("initial_velocity")),
            "moving virtual body inputs missing")
    require(case.get("body_support") ==
            ("disc radius" if body == "disc" else
             "axis-aligned square support, orientation fixed by constraint"),
            "original shape support or rotation constraint changed")
    require(case.get("square_rotation_prevented_by_constraint") is
            (body == "fixed-square"), "constrained square rotation mutated")
    source = case.get("source")
    receiver = case.get("receiver")
    require(type(source) is dict and source.get("id") == "original-test-source" and
            pair(source.get("anchor")) and pair(source.get("normal")) and
            type(source.get("endpoints")) is list and
            len(source["endpoints"]) == 2 and
            all(pair(p) for p in source["endpoints"]),
            "original finite source geometry missing")
    require(type(receiver) is dict and
            receiver.get("id") == "movement-derived-receiver" and
            pair(receiver.get("anchor")) and pair(receiver.get("normal")) and
            type(receiver.get("endpoints")) is list and
            len(receiver["endpoints"]) == 2 and
            all(pair(p) for p in receiver["endpoints"]) and
            receiver.get("caused_by_contact_index") == 0 and
            receiver.get("constructed_from") == "recorded-model-outgoing-velocity",
            "derived receiver lineage or geometry missing")
    contacts = case.get("contacts")
    require(type(contacts) is list and len(contacts) == 2 and
            all(type(c) is dict and number(c.get("time")) and
                pair(c.get("center")) and pair(c.get("before")) and
                pair(c.get("after")) for c in contacts),
            "original two modeled contacts absent")
    first, second = contacts
    require(first["source_id"] == source["id"] and
            second["source_id"] == receiver["id"] and
            0 < first["time"] < second["time"] and
            abs(receiver["activated_at"] - first["time"]) < 1e-8 and
            first["after"] == second["before"],
            "invalid modeled motion ancestry or receiver activated too early")
    frames = case.get("frames")
    require(type(frames) is list and len(frames) >= 12 and
            frames[0].get("time") == 0 and
            frames[-1].get("time", -1) >= second["time"] - 1e-9,
            "original motion frames missing")
    prior = -1.
    for frame in frames:
        require(type(frame) is dict and number(frame.get("time")) and
                frame["time"] > prior and pair(frame.get("center")) and
                pair(frame.get("velocity")),
                "nonchronological or invalid virtual motion frame")
        prior = frame["time"]


def carry(native: dict, refusal: dict, source_commit: str = PIN) -> dict:
    require(source_commit == PIN, "source commit not pinned")
    require(type(native) is dict and native.get("schema") == SOURCE and
            native.get("body_types") == list(BODIES) and
            native.get("angles") == list(ANGLES) and
            native.get("no_new_world_or_renderer") is True and
            native.get("real_material_behavior_observed") is False and
            native.get("shape_independent_contact_law") ==
            "frictionless translational normal reflection",
            "original source experiment identity changed")
    cases = native.get("cases")
    require(type(cases) is list and len(cases) == 8,
            "all original body/angle cases required")
    owner = {"kind": "source-execution",
             "source": "original WORLD15 @" + source_commit}
    derived = {"kind": "declared", "source": "modeled outgoing movement"}
    pages = []
    total_frames = 0
    for index, (body, angle) in enumerate(
            (b, a) for b in BODIES for a in ANGLES):
        case = cases[index]
        source_case(case, body, angle)
        first, second = case["contacts"]
        t1, t2 = first["time"], second["time"]
        steps = [
            {"op": "introduce", "id": "finite-input-source",
             "state": deepcopy(case["source"]), "basis": owner},
            {"op": "introduce", "id": "moving-body",
             "state": {"body": body, "support": case["body_support"],
                       "position": deepcopy(case["initial_center"]),
                       "velocity": deepcopy(case["initial_velocity"]),
                       "time": 0., "virtual_body": True},
             "basis": owner},
            {"op": "connect", "id": "declared-test",
             "from": "finite-input-source", "to": "moving-body",
             "label": "declared-source-contact-test",
             "state": {"angle": angle, "geometry": body}, "basis": derived},
        ]
        introduced = False
        second_seen = False
        for frame in case["frames"]:
            t = frame["time"]
            if t >= t1 - 1e-9 and not introduced:
                steps.extend([
                    {"op": "observe", "id": "first-modeled-contact",
                     "entity": "object", "subject": "finite-input-source",
                     "reading": {"contact": deepcopy(first),
                                 "hardware_measured": False}, "basis": owner},
                    {"op": "introduce", "id": "movement-derived-receiver",
                     "state": deepcopy(case["receiver"]), "basis": derived},
                    {"op": "connect", "id": "receiver-ancestry",
                     "from": "moving-body", "to": "movement-derived-receiver",
                     "label": "constructed-after-source-contact",
                     "state": {"activated_at": t1,
                               "source_contact_index": 0}, "basis": derived},
                ])
                introduced = True
            if t >= t2 - 1e-9 and not second_seen:
                require(introduced, "second modeled contact before first")
                steps.append({
                    "op": "observe", "id": "second-modeled-contact",
                    "entity": "object", "subject": "movement-derived-receiver",
                    "reading": {"contact": deepcopy(second),
                                "hardware_measured": False}, "basis": owner})
                second_seen = True
            steps.append({
                "op": "revise", "entity": "object", "id": "moving-body",
                "after": {"body": body, "support": case["body_support"],
                          "position": deepcopy(frame["center"]),
                          "velocity": deepcopy(frame["velocity"]),
                          "time": t, "virtual_body": True},
                "basis": owner})
        require(introduced and second_seen,
                "source frames never reached both modeled contacts")
        steps.append({
            "op": "observe", "id": "modeled-completion",
            "entity": "object", "subject": "moving-body",
            "reading": {"status": case["status"], "source_sha256": digest(case),
                        "frames_carried": len(case["frames"]),
                        "square_rotation_constrained": body == "fixed-square",
                        "hardware_measured": False}, "basis": owner})
        plan = {"schema": PLAN,
                "referent": "WORLD15 / " + body + " / angle " + str(angle),
                "limits": {"objects": 3, "relations": 2,
                           "steps": len(steps)}, "steps": steps}
        receipt = run_plan(plan)
        pages.append({"kind": "modeled", "index": index, "body": body,
                      "angle": angle, "frames": len(case["frames"]),
                      "receipt": receipt, "witness": verify_receipt(receipt)})
        total_frames += len(case["frames"])

    # The original source refuses to infer an interior square contact at 30°.
    require(type(refusal) is dict and refusal.get("schema") == SOURCE and
            refusal.get("body") == "fixed-square" and
            refusal.get("source_angle") == 30. and
            refusal.get("status") == "NO_ADMITTED_INTERIOR_CONTACT" and
            refusal.get("receiver") is None and
            refusal.get("contacts") == [] and refusal.get("frames") == [] and
            refusal.get("measured_earth_material") is False,
            "unsupported endpoint candidate promoted to a contact")
    declined_plan = {
        "schema": PLAN, "referent": "WORLD15 / square endpoint ambiguity",
        "limits": {"objects": 2, "relations": 0, "steps": 3},
        "steps": [
            {"op": "introduce", "id": "finite-input-source",
             "state": deepcopy(refusal["source"]), "basis": owner},
            {"op": "introduce", "id": "initial-body",
             "state": {"shape": "fixed-square", "virtual_body": True},
             "basis": owner},
            {"op": "observe", "id": "unadmitted-interior-contact",
             "entity": "object", "subject": "finite-input-source",
             "reading": {"status": refusal["status"],
                         "source_sha256": digest(refusal),
                         "derived_receiver": None,
                         "physical_contact_selected": False},
             "basis": owner},
        ]}
    declined = run_plan(declined_plan)
    pages.append({"kind": "unadmitted", "index": 8, "body": "fixed-square",
                  "angle": 30., "frames": 0, "receipt": declined,
                  "witness": verify_receipt(declined)})
    manifest = {
        "native_source_sha256": digest(native),
        "unadmitted_source_sha256": digest(refusal),
        "ordered_pages": [
            {"index": p["index"], "kind": p["kind"],
             "head_hash": p["receipt"]["head_hash"]} for p in pages],
    }
    verdict = {
        "valid": all(p["witness"]["valid"] for p in pages),
        "pages_verified": len(pages),
        "steps_verified": sum(p["witness"]["steps_verified"] for p in pages),
        "observations_recorded": sum(
            p["witness"]["observations_recorded"] for p in pages),
    }
    return {
        "schema": SCHEMA, "source_commit": source_commit,
        "modeled_movements": 8, "unadmitted_endpoint_cases": 1,
        "disc_cases": 4, "constrained_square_cases": 4,
        "frames_carried": total_frames,
        "ledger_pages": pages, "ledger_witness": verdict,
        "manifest": manifest, "manifest_sha256": digest(manifest),
        "real_material_measurements": 0, "contact_law_generalized": False,
        "free_square_rotation_solved": False,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--native", type=Path, required=True)
    p.add_argument("--refusal", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(carry(load_json(args.native), load_json(args.refusal)),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
