"""Trial14: carry source-derived geometry in the order movement constructs it.

Original WORLD Trial14 mathematical contact code and independent native oracle
own the geometry and dynamics. A/B records declared source geometry, a moving
body and the receiver introduced *only after* the source contact. A miss
constructs no receiver and no completed motion. Nothing is a hardware reading.
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

SCHEMA = "ab-world-trial14-causal-receiver-handoff/v1"
SOURCE = "world-ab-relation-derived-free-orientation/v1"
ANGLES = (0., 7.5, 12.25, 20.)
FRICTIONS = (0., 0.4)
COMPLETED = "TWO_CONTACTS_IN_DECLARED_MODEL"
MISS = "NO_FINITE_SEGMENT_CONTACT"


def demand(ok: bool, explanation: str) -> None:
    if not ok:
        raise ValueError("Trial14 A/B: " + explanation)


def finite(v: Any) -> bool:
    return type(v) in (int, float) and isfinite(v)


def pair(v: Any) -> bool:
    return type(v) is list and len(v) == 2 and all(finite(x) for x in v)


def check_base(c: dict[str, Any]) -> None:
    demand(type(c) is dict and c.get("schema") == SOURCE,
           "original model schema changed")
    demand(c.get("source_collision_is_a_declared_model") is True and
           c.get("measured_physical_material") is False and
           c.get("target_shape_supplied") is False,
           "unobserved material or supplied target promoted")
    demand(finite(c.get("input_source_angle_degrees")) and
           abs(c["input_source_angle_degrees"]) <= 40 and
           pair(c.get("input_source_anchor")) and
           7 <= c["input_source_anchor"][0] <= 16 and
           0.75 <= c["input_source_anchor"][1] <= 5.25 and
           finite(c.get("friction")) and 0 <= c["friction"] <= .4,
           "bounded source controls missing")
    demand(pair(c.get("input_origin")) and pair(c.get("input_velocity")) and
           finite(c.get("disc_radius")) and c["disc_radius"] > 0 and
           finite(c.get("disc_inertia")) and c["disc_inertia"] > 0,
           "declared finite moving body missing")
    source = c.get("source")
    demand(type(source) is dict and
           source.get("id") == "finite-input-source" and
           pair(source.get("normal")) and pair(source.get("anchor")) and
           type(source.get("endpoints")) is list and
           len(source["endpoints"]) == 2 and
           all(pair(p) for p in source["endpoints"]),
           "original source finite segment missing")


def carry(native: dict[str, Any], source_commit: str,
          miss: dict[str, Any]) -> dict[str, Any]:
    demand(type(source_commit) is str and
           re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None,
           "pin exact original source commit")
    demand(type(native) is dict and native.get("schema") == SOURCE and
           native.get("source_angle_grid") == list(ANGLES) and
           native.get("friction_grid") == list(FRICTIONS),
           "original eight-case model controls changed")
    demand(native.get("new_receiver_shape_is_source_derived") is True and
           native.get("real_earth_physics_verified") is False and
           native.get("physical_motor_or_nih_blueprint_tested") is False,
           "virtual movement promoted to physical blueprint")
    cases = native.get("cases")
    demand(type(cases) is list and len(cases) == 8,
           "all eight source movement cases required")
    owner = {"kind": "source-execution",
             "source": "original WORLD Trial14 @" + source_commit}
    derived = {"kind": "declared",
               "source": "model receiver from first outgoing source movement"}
    pages = []
    total_frames = 0
    for index, (angle, friction) in enumerate(
            (a, mu) for a in ANGLES for mu in FRICTIONS):
        c = cases[index]
        check_base(c)
        demand(c.get("input_source_angle_degrees") == angle and
               c.get("friction") == friction and
               c.get("input_source_anchor") == [12.0, 1.5],
               "original source angle/friction/anchor control changed")
        demand(c.get("status") == COMPLETED and
               c.get("source_model_04B_unchanged") is True and
               c.get("world48_and_nih_unmodified") is True and
               c.get("all_physical_interactions_solved") is False,
               "source lineage or two-contact model status changed")
        receiver = c.get("receiver")
        contacts = c.get("contacts")
        demand(type(receiver) is dict and
               receiver.get("id") == "movement-derived-receiver" and
               receiver.get("constructed_from") == "first-outgoing-velocity" and
               receiver.get("source_contact_index") == 0 and
               pair(receiver.get("normal")) and pair(receiver.get("anchor")) and
               type(receiver.get("endpoints")) is list and
               len(receiver["endpoints"]) == 2 and
               all(pair(p) for p in receiver["endpoints"]),
               "receiver ancestry or finite geometry lost")
        demand(type(contacts) is list and len(contacts) == 2 and
               all(type(contact) is dict and finite(contact.get("time")) and
                   pair(contact.get("center")) and
                   pair(contact.get("incoming_velocity")) and
                   pair(contact.get("outgoing_velocity")) and
                   finite(contact.get("outgoing_spin")) and
                   type(contact.get("impulse")) is dict
                   for contact in contacts),
               "two original finite modeled contacts missing")
        first, second = contacts
        t1, t2 = first["time"], second["time"]
        demand(0 < t1 < t2 and
               first.get("source_id") == c["source"]["id"] and
               second.get("source_id") == receiver["id"] and
               abs(receiver.get("activated_at", -1) - t1) < 2e-9 and
               first["outgoing_velocity"] == second["incoming_velocity"],
               "receiver existed before causal contact or motion lineage changed")
        frames = c.get("frames")
        demand(type(frames) is list and len(frames) >= 5,
               "missing original time-sampled movement history")
        steps = [
            {"op": "introduce", "id": "finite-source-face",
             "state": deepcopy(c["source"]), "basis": owner},
            {"op": "introduce", "id": "moving-disc",
             "state": {"position": deepcopy(c["input_origin"]),
                       "velocity": deepcopy(c["input_velocity"]), "spin": 0.,
                       "virtual_body": True, "time": 0.}, "basis": owner},
            {"op": "connect", "id": "declared-source-disc",
             "from": "finite-source-face", "to": "moving-disc",
             "label": "declared-source-contact-test",
             "state": {"source_angle": angle, "friction": friction},
             "basis": derived},
        ]
        first_recorded = False
        second_recorded = False
        prior_time = -1.
        for frame in frames:
            demand(type(frame) is dict and finite(frame.get("time")) and
                   frame["time"] > prior_time and
                   pair(frame.get("position")) and
                   pair(frame.get("velocity")) and
                   finite(frame.get("spin")),
                   "source frames missing or out of chronological order")
            prior_time = frame["time"]
            phase = frame.get("phase")
            expected_phase = ("before-source-contact" if frame["time"] < t1
                              else "source-contact-to-receiver" if frame["time"] < t2
                              else "after-derived-contact")
            demand(phase == expected_phase,
                   "source frame misclassified relative to causal contacts")
            if frame["time"] >= t1 and not first_recorded:
                steps.extend([
                    {"op": "observe", "id": "first-modeled-contact",
                     "entity": "object", "subject": "finite-source-face",
                     "reading": {"source_contact": deepcopy(first),
                                 "hardware_observation": False}, "basis": owner},
                    {"op": "introduce", "id": "derived-receiver-face",
                     "state": deepcopy(receiver), "basis": derived},
                    {"op": "connect", "id": "movement-created-receiver",
                     "from": "moving-disc", "to": "derived-receiver-face",
                     "label": "constructed-after-first-modeled-contact",
                     "state": {"activated_at": t1,
                               "from": "first-outgoing-velocity",
                               "precontact_receiver_existed": False},
                     "basis": derived},
                ])
                first_recorded = True
            if frame["time"] >= t2 and not second_recorded:
                demand(first_recorded, "second contact before source contact")
                steps.append({
                    "op": "observe", "id": "second-modeled-contact",
                    "entity": "object", "subject": "derived-receiver-face",
                    "reading": {"receiver_contact": deepcopy(second),
                                "hardware_observation": False}, "basis": owner})
                second_recorded = True
            steps.append({
                "op": "revise", "entity": "object", "id": "moving-disc",
                "after": {"position": deepcopy(frame["position"]),
                          "velocity": deepcopy(frame["velocity"]),
                          "spin": frame["spin"],
                          "virtual_body": True, "time": frame["time"],
                          "phase": phase},
                "basis": owner,
            })
        demand(first_recorded and second_recorded and
               frames[0]["time"] == 0 and frames[-1]["time"] >= t2,
               "source history never reached both constructed contacts")
        steps.append({
            "op": "observe", "id": "original-source-completion",
            "entity": "object", "subject": "moving-disc",
            "reading": {"model_status": COMPLETED,
                        "source_sha256": digest(c),
                        "frames_carried": len(frames),
                        "receiver_was_derived_after_first_contact": True,
                        "real_material_measurement": False}, "basis": owner,
        })
        plan = {"schema": PLAN,
                "referent": f"WORLD Trial14 / orientation {angle}, friction {friction}",
                "limits": {"objects": 3, "relations": 2,
                           "steps": len(steps)}, "steps": steps}
        receipt = run_plan(plan)
        pages.append({"kind": "completed", "index": index,
                      "angle": angle, "friction": friction,
                      "frames": len(frames), "receipt": receipt,
                      "witness": verify_receipt(receipt)})
        total_frames += len(frames)

    # Independent source miss is itself evidence, not an invitation to
    # manufacture a receiver/continuation on a path that never touched.
    check_base(miss)
    demand(miss.get("input_source_angle_degrees") == 0. and
           miss.get("input_source_anchor") == [12., 4.] and
           miss.get("friction") == .4 and
           miss.get("status") == MISS and
           miss.get("receiver") is None and
           miss.get("contacts") == [] and miss.get("frames") == [],
           "source miss converted into a constructed contact")
    failed_steps = [
        {"op": "introduce", "id": "finite-source-face",
         "state": deepcopy(miss["source"]), "basis": owner},
        {"op": "introduce", "id": "initial-moving-disc",
         "state": {"position": deepcopy(miss["input_origin"]),
                   "velocity": deepcopy(miss["input_velocity"]),
                   "virtual": True}, "basis": owner},
        {"op": "observe", "id": "source-miss-no-receiver",
         "entity": "object", "subject": "finite-source-face",
         "reading": {"source_status": MISS,
                     "source_sha256": digest(miss),
                     "derived_receiver": None, "constructed_path": False},
         "basis": owner},
    ]
    failed_plan = {"schema": PLAN,
                   "referent": "WORLD Trial14 / independently recorded finite source miss",
                   "limits": {"objects": 2, "relations": 1,
                              "steps": len(failed_steps)}, "steps": failed_steps}
    missing_receipt = run_plan(failed_plan)
    pages.append({"kind": "miss", "index": 8,
                  "angle": 0., "friction": .4,
                  "frames": 0, "receipt": missing_receipt,
                  "witness": verify_receipt(missing_receipt)})
    manifest = {"native_report_sha256": digest(native),
                "source_miss_sha256": digest(miss),
                "ordered_pages": [
                    {"kind": p["kind"], "index": p["index"],
                     "head_hash": p["receipt"]["head_hash"]}
                    for p in pages]}
    witness = {"valid": all(p["witness"]["valid"] for p in pages),
               "pages_verified": len(pages),
               "steps_verified": sum(p["witness"]["steps_verified"] for p in pages),
               "observations_recorded":
                   sum(p["witness"]["observations_recorded"] for p in pages)}
    return {"schema": SCHEMA, "source_commit": source_commit,
            "native_report_sha256": digest(native),
            "completed_causal_movements": 8, "source_misses": 1,
            "source_frames_carried": total_frames,
            "receivers_constructed_only_after_source_contact": True,
            "physical_material_measurements": 0,
            "real_material_construction_verified": False,
            "original_frictional_multicontact_solved": False,
            "source_physics_verified_by_adapter": False,
            "ledger_pages": pages, "ledger_witness": witness,
            "page_manifest": manifest, "page_manifest_sha256": digest(manifest)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--miss", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    print(json.dumps(carry(load_json(args.native), args.source_commit,
                           load_json(args.miss)), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
