"""Admission gate for a single source-owned SP80 level-4 intervention.

No contact, object, or action can be manufactured from a color heuristic.
A plan is admitted only if both original SDK witnesses agree on an actual
first source-palette-6 arrival outside the cups, and the proposed click
coordinate was already present in the returned native action receipts.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

KIND = "ARC4_SOURCE_OWNED_EVENT_ORDER_AUDIT"
ROWS = {"row5", "row8"}

def make_plan(audit: dict, proposal: dict) -> dict:
    if audit.get("kind") != KIND:
        raise ValueError("Missing original source-owned event-order audit")
    case = proposal.get("case")
    contrast_case = proposal.get("contrast_case")
    row = proposal.get("source_contact_row")
    action = proposal.get("native_action")
    click = proposal.get("source_click_xy")
    x = proposal.get("contact_x")
    frame = proposal.get("contact_frame")
    if not isinstance(case, str) or not case or row not in ROWS:
        raise ValueError("Unknown case/contact row")
    if type(action) is not int or action not in (1, 2, 3, 4):
        raise ValueError("A native movement must be one of ACTION1..4")
    if not isinstance(click, list) or len(click) != 2 or any(type(v) is not int or v < 0 or v > 63 for v in click):
        raise ValueError("Native selected-object click must be an exact 64x64 source coordinate")
    if type(x) is not int or type(frame) is not int:
        raise ValueError("Original source contact needs an exact frame and x coordinate")
    if not isinstance(contrast_case, str) or not contrast_case or contrast_case == case:
        raise ValueError("A distinct matched source-negative control is required")
    if case.rsplit("_", 1)[0] != contrast_case.rsplit("_", 1)[0]:
        raise ValueError("Positive and negative must share the frozen lower arrangement")
    rows = [r for r in audit.get("original_native_records", []) if r.get("case") == case]
    controls = [r for r in audit.get("original_native_records", []) if r.get("case") == contrast_case]
    if len(controls) != 2 or {r.get("native_witness") for r in controls} != {"A", "B"}:
        raise ValueError("Matched source-negative control needs two independent witnesses")
    if controls[0].get("source_observations") != controls[1].get("source_observations"):
        raise ValueError("Original source-negative control witnesses disagree")
    if len(rows) != 2 or {r.get("native_witness") for r in rows} != {"A", "B"}:
        raise ValueError("Two different genuine original SDK entry witnesses are required")
    before = rows[0]
    if before.get("source_observations") != rows[1].get("source_observations"):
        raise ValueError("Original source witnesses disagree")
    if before.get("original_native_action_word") != rows[1].get("original_native_action_word"):
        raise ValueError("Original native words disagree")
    observed = before["source_observations"]["first_new6_outside_cups"].get(row)
    if not observed or observed.get("frame") != frame or x not in observed.get("x", []):
        raise ValueError("Proposed first source contact was not observed")
    if before["source_observations"].get("first_four_simultaneously_full") is None:
        raise ValueError("Selected source-positive case did not show four simultaneous cup windows")
    if controls[0]["source_observations"].get("first_four_simultaneously_full") is not None:
        raise ValueError("Matched source-negative control also has four simultaneous cup windows")
    other = controls[0]["source_observations"]["first_new6_outside_cups"].get(row)
    if not other or (other.get("frame"), other.get("x")) == (observed.get("frame"), observed.get("x")):
        raise ValueError("First-arrival event does not discriminate the positive/negative source cases")
    for record in rows:
        clicks = [
            v for v in record.get("original_sdk_action_receipts", [])
            if v.get("genuine_original_action") == 6 and v.get("real_native_click_xy") == click
        ]
        if not clicks or any(v.get("original_source_pixel_before_click") is None for v in clicks):
            raise ValueError("Proposed selectable source click lacks a native receipt")
    original_word = before["original_native_action_word"]
    pieces = original_word.strip().split()
    if not pieces or pieces[-1] != "5" or pieces.count("5") != 1:
        raise ValueError("Original word needs exactly one terminal native ACTION5")
    new_word = " ".join(pieces[:-1] + ["6@" + str(click[0]) + "," + str(click[1]), str(action), "5"])
    return {
        "kind": "ARC4_SOURCE_PINNED_INTERVENTION_PLAN",
        "source_audit_kind": KIND,
        "case": case, "contrasting_original_case": contrast_case,
        "source_negative_first_arrival": other,
        "source_contact_row": row, "contact_x": x, "contact_frame": frame,
        "verified_native_click_xy_from_receipts": click,
        "new_native_action": action,
        "original_native_action_word": original_word,
        "intervention_native_action_word": new_word,
        "paired_original_sdk_witnesses": ["A", "B"],
        "limits": "Click is receipt-attested in the frozen source word, but the proposed movement and any effect are untested. Native SDK run required; pixels do not imply success.",
    }

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--audit", required=True, type=Path)
    p.add_argument("--proposal", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    plan = make_plan(json.loads(args.audit.read_text()), json.loads(args.proposal.read_text()))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(plan, indent=2) + "\n")
    print("ARC4_INTERVENTION_ADMITTED " + json.dumps({
        "case": plan["case"], "source_contact_row": plan["source_contact_row"],
        "contact_frame": plan["contact_frame"], "contact_x": plan["contact_x"],
        "native_action": plan["new_native_action"]}, sort_keys=True))

if __name__ == "__main__":
    main()
