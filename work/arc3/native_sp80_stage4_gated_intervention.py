"""Run a *previously admitted* ARC4 intervention on the original SDK.

Requires a source-pinned plan created by arc4_intervention_gate. No generated
plan is committed here and no native result is claimed in advance.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    if plan.get("kind") != "ARC4_SOURCE_PINNED_INTERVENTION_PLAN":
        raise ValueError("Native run requires a source-owned admitted plan")
    word = plan.get("intervention_native_action_word", "")
    parts = parse_plan(word)
    if not parts or parts[-1][0] != 5 or sum(a == 5 for a, _ in parts) != 1:
        raise ValueError("Exactly one terminal native pour required")
    case = plan["case"] + "_source_pinned_intervention"
    records, retained = [], {}
    for witness, entry in STAGE1_WITNESSES:
        native, raw = run_case(case, witness, entry, word)
        record = {
            "case": case, "native_witness": witness,
            "actual_original_sdk_level": native["true_original_sdk_final_level"],
            "actual_original_sdk_state": native["true_original_sdk_final_state"],
            "official_level5_or_WIN": native["official_original_level5_or_WIN"],
            "original_sdk_action_receipts": native["genuine_original_stage4_action_ledger"],
        }
        records.append(record)
        for key, stack in raw.items():
            retained[witness + "_" + key] = stack
        print("ARC4_NATIVE_INTERVENTION_RESULT " + json.dumps({
            "witness": witness, "level": record["actual_original_sdk_level"],
            "state": record["actual_original_sdk_state"],
        }, sort_keys=True), flush=True)
    if records[0]["actual_original_sdk_level"] != records[1]["actual_original_sdk_level"] or records[0]["actual_original_sdk_state"] != records[1]["actual_original_sdk_state"]:
        raise AssertionError("Independent original SDK witnesses disagree")
    output = {
        "kind": "ARC4_GATED_ORIGINAL_SDK_INTERVENTION",
        "source_pinned_plan": plan,
        "native_records": records,
        "official_progress": any(bool(v["official_level5_or_WIN"]) for v in records),
        "boundary": "Observed native result only, not inferred game mechanics.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + "\n")
    np.savez_compressed(args.out.with_suffix(".npz"), **retained)

if __name__ == "__main__":
    main()
