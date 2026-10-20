"""Trial07 original source evidence: admit a simultaneous contact without solving it.

The native WORLD source and its independent verifier own junction geometry and
dynamics. This adapter creates A/B objects, records and source attribution only.
No A/B operation manufactures a simultaneous impulse or a completed trajectory.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from math import isfinite
import json
from pathlib import Path
import re
from typing import Any

from work.ab_world.construction import PLAN, digest, load_json, run_plan
from work.ab_world.verify_construction import verify_receipt

SCHEMA = "ab-world-trial07-ambiguous-contact-handoff/v1"
NATIVE_SCHEMA = "world-ab-junction-arrival-tie/v1"
ORIGINAL_OFFSETS = (-.01, -.0001, -.000001, -.00000001, 0.,
                    .00000001, .000001, .0001, .01)


def demand(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("Trial07 A/B handoff: " + message)


def finite(value: Any) -> bool:
    return type(value) in (int, float) and isfinite(value)


def carry(native: dict[str, Any], source_commit: str) -> dict[str, Any]:
    demand(type(source_commit) is str and
           re.fullmatch("[0-9a-f]{40}", source_commit) is not None,
           "pin an exact original source commit")
    demand(type(native) is dict and native.get("schema") == NATIVE_SCHEMA,
           "wrong original WORLD source record")
    demand(native.get("simultaneous_contact_solver") is False,
           "simultaneous contact cannot be promoted to solved")
    demand(native.get("unresolved_contacts_remain_unresolved") is True,
           "unresolved-source evidence cannot be erased")
    demand(native.get("earth_material_equivalence") is False and
           native.get("full_original_blueprint_generated") is False,
           "unsupported physical claim")
    demand(native.get("source_04B_branches_simultaneously_generated") is False,
           "source branch geometry is separately generated")
    geometry = native.get("source_geometry")
    demand(type(geometry) is dict and type(geometry.get("surfaces")) is list and
           len(geometry["surfaces"]) == 2, "missing original two surfaces")
    surfaces = geometry["surfaces"]
    ids = [s.get("id") if type(s) is dict else None for s in surfaces]
    demand(all(type(s) is str and s.strip() for s in ids) and
           ids[0] != ids[1], "invalid original surface identities")
    candidate = native.get("junction_contact")
    demand(type(candidate) is dict and candidate.get("source_ids") == ids,
           "source contact does not match original surfaces")
    demand(candidate.get("features") == ["interior", "interior"],
           "original contact features changed")
    demand(finite(candidate.get("entry_y")) and
           finite(candidate.get("contact_time")) and
           finite(candidate.get("candidate_gap")) and
           abs(candidate["candidate_gap"]) <= 2e-9,
           "invalid native near-simultaneous arrival")
    bracket = native.get("bracket")
    demand(type(bracket) is list and len(bracket) == 2 and
           all(finite(v) for v in bracket) and
           bracket[0] < candidate["entry_y"] < bracket[1],
           "unbracketed source junction")
    probes = native.get("probes")
    demand(type(probes) is list and len(probes) == len(ORIGINAL_OFFSETS),
           "missing original nearby control probes")
    for i, (offset, probe) in enumerate(zip(ORIGINAL_OFFSETS, probes)):
        demand(type(probe) is dict and probe.get("offset") == offset and
               finite(probe.get("entry_y")) and
               abs(probe["entry_y"] - candidate["entry_y"] - offset) <= 2e-10,
               "source probe roster/order mismatch at " + str(i))
        demand(probe.get("surface_order_independent") is True,
               "probe requires unsupported surface ordering")
        demand(type(probe.get("status")) is str and
               type(probe.get("observed_contacts")) is int and
               probe["observed_contacts"] >= 0,
               "missing source status or contact count")
    middle = probes[len(probes) // 2]
    demand(middle["status"] == "unresolved-multiple-contacts" and
           middle["observed_contacts"] == 0,
           "tie silently resolved or emitted fictional impulse")
    unresolved = middle.get("unresolved")
    demand(type(unresolved) is dict and
           type(unresolved.get("surfaces")) is list and
           set(unresolved["surfaces"]) == set(ids),
           "unresolved original source pair missing")

    source = {"kind": "source-execution",
              "source": "WORLD Trial07 native source @" + source_commit}
    steps = [
        {"op": "introduce", "id": "original-face-0",
         "state": deepcopy(surfaces[0]), "basis": source},
        {"op": "introduce", "id": "original-face-1",
         "state": deepcopy(surfaces[1]), "basis": source},
        {"op": "connect", "id": "declared-candidate-junction",
         "from": "original-face-0", "to": "original-face-1",
         "label": "source-reported-finite-junction",
         "state": {"geometry": deepcopy(geometry.get("junction")),
                   "candidate-only": True}, "basis": source},
        {"op": "introduce", "id": "source-simultaneous-arrival",
         "state": {"candidate": deepcopy(candidate), "resolution": "UNRESOLVED",
                   "outgoing_impulse": None}, "basis": source},
        {"op": "observe", "id": "source-tie-witness",
         "entity": "object", "subject": "source-simultaneous-arrival",
         "reading": {"candidate": deepcopy(candidate), "resolution": "UNRESOLVED",
                     "outgoing_impulse": None}, "basis": source},
    ]
    for i, probe in enumerate(probes, 1):
        ident = "control-probe-" + str(i).zfill(2)
        steps.extend([
            {"op": "introduce", "id": ident,
             "state": {"entry_y": probe["entry_y"], "offset": probe["offset"],
                       "status": "UNOBSERVED"}, "basis": source},
            {"op": "revise", "entity": "object", "id": ident,
             "after": {"entry_y": probe["entry_y"], "offset": probe["offset"],
                       "status": probe["status"], "source_unresolved":
                       deepcopy(probe.get("unresolved"))}, "basis": source},
            {"op": "observe", "id": "source-control-" + str(i).zfill(2),
             "entity": "object", "subject": ident,
             "reading": {"original_probe": deepcopy(probe)}, "basis": source},
        ])
    plan = {
        "schema": PLAN,
        "referent": "WORLD Trial07 / native finite-junction simultaneous arrival",
        "limits": {"objects": 3 + len(probes), "relations": 1,
                   "steps": len(steps)},
        "steps": steps,
    }
    receipt = run_plan(plan)
    witness = verify_receipt(receipt)
    return {
        "schema": SCHEMA,
        "source_commit": source_commit,
        "native_report_sha256": digest(native),
        "control_probes_recorded": len(probes),
        "source_tie_entry_y": candidate["entry_y"],
        "native_tie_status": middle["status"],
        "native_tie_contacts": middle["observed_contacts"],
        "outgoing_impulse_decided": False,
        "source_authenticated_by_adapter": False,
        "native_physics_verified_by_adapter": False,
        "material_world_verified": False,
        "world_receipt": receipt,
        "ledger_witness": witness,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    print(json.dumps(carry(load_json(args.native), args.source_commit),
                     indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
