"""Original SP80 SDK level4: temporal repeats on source-verified four-cup parents.

Frozen native D3 middle / L3U2 lower / upper LEFT1 geometry. Right-bar
LEFT1 and LEFT2 are independently source-observed four-cup positives,
but both remain official level4. This test adds NO selected-object
movement after the initial pour: exact 1 / 2 / 3 genuine native ACTION5s
in the SAME game. No fabricated liquid simulator or private rule.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_top_left_source_contrast import source_report
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

MIDDLE="6@24,33 2 2 2 3 3"
LOWER="6@34,42 3 3 3 1 1"
UPPER="6@34,21 3"
RIGHT=(
    ("right_LEFT1","6@46,33 3"),
    ("right_LEFT2","6@46,33 3 3"),
)
FROZEN=tuple(
    (f"{name}_{pours}pours",
     " ".join((right,MIDDLE,LOWER,UPPER,*("5",)*pours)),
     pours)
    for name,right in RIGHT for pours in (1,2,3)
)
assert len(FROZEN)==6
assert len(STAGE1_WITNESSES)==2
assert all(sum(action==5 for action,xy in parse_plan(word))==count
           and parse_plan(word)[-1][0]==5 for name,word,count in FROZEN)

def terminal_delta(pre,after):
    changed=pre!=after
    ys,xs=np.nonzero(changed)
    return {
      "original_sdk_terminal_changed_pixels":int(np.count_nonzero(changed)),
      "terminal_bbox_xyxy":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None,
      "original_bottommost_row_y63_changes":int(np.count_nonzero(pre[63]!=after[63])),
      "original_visible_pixels_y0_62_changes":int(np.count_nonzero(pre[:63]!=after[:63]))}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    opts=p.parse_args()
    rows=[];full_stacks={};root_hashes=set()
    for case,word,count in FROZEN:
        actions=parse_plan(word)
        pour_indexes=[i for i,(a,xy) in enumerate(actions,1) if a==5]
        if len(pour_indexes)!=count or pour_indexes[-1]!=len(actions):
            raise AssertionError("All genuine ACTION5 ordinals must be frozen")
        for witness,entry in STAGE1_WITNESSES:
            native,source=run_case(case,witness,entry,word)
            root=source["entry3_34"][-1]
            root_hashes.add(hash_frame(root))
            receipts=native["genuine_original_stage4_action_ledger"]
            pours=[]
            if len(receipts)!=len(actions):
                raise AssertionError("Original native ACTION5s unexpectedly missing or terminated")
            for ordinal,position in enumerate(pour_indexes,1):
                receipt=receipts[position-1]
                if receipt["genuine_original_action"]!=5:
                    raise AssertionError("Authentic original native action receipt differs")
                before=source["stage4_"+str(position-1)][-1]
                animation=source["stage4_"+str(position)]
                measured=source_report(root,before,animation)
                pours.append({
                    "genuine_original_pour_ordinal":ordinal,
                    "genuine_native_stage4_action_position":position,
                    "original_sdk_level_before":receipt["original_sdk_level_before"],
                    "original_sdk_level_after":receipt["original_sdk_level_after"],
                    "original_sdk_state_before":receipt["original_sdk_state_before"],
                    "original_sdk_state_after":receipt["original_sdk_state_after"],
                    "native_action5_returned_frames":len(animation),
                    "native_real_pre_pour_source_hash":hash_frame(before),
                    "native_real_post_pour_source_hash":hash_frame(animation[-1]),
                    "native_source_cup_measurements":measured,
                    "native_terminal_screen_difference":terminal_delta(before,animation[-1]),
                    "original_native_action5_receipt":receipt,
                })
            baseline=pours[0]["native_source_cup_measurements"]
            expected=(
                {"lateral":13,"top_left":25,"top_middle":21,"top_right":21}
                if case.startswith("right_LEFT1") else
                {"lateral":13,"top_left":25,"top_middle":23,"top_right":19})
            if baseline["source_first_full_cups"]!=expected or baseline["source_first_four_simultaneous"]!=25:
                raise AssertionError("Frozen earlier original native first-pour source positive changed")
            row={
                "condition":case,
                "witness":witness,
                "exact_original_sdk_stage4_word":word,
                "source_stage4_root_hash":hash_frame(root),
                "original_sdk_pour_count":count,
                "genuine_action5_return_history":pours,
                "official_original_sdk_final_level":native["true_original_sdk_final_level"],
                "official_original_sdk_final_state":native["true_original_sdk_final_state"],
                "official_level5_or_WIN":native["official_original_level5_or_WIN"],
                "original_stage4_sdk_action_ledger":receipts,
            }
            rows.append(row)
            for key,frames in source.items():
                full_stacks[case+"_"+witness+"_"+key]=frames
            print("ARC4_REPEAT_POUR_ORIGINAL_CASE "+json.dumps({
                "case":case,"witness":witness,
                "action5_levels":[[x["original_sdk_level_before"],x["original_sdk_level_after"]] for x in pours],
                "returned_frames":[x["native_action5_returned_frames"] for x in pours],
                "first_full_cups":[x["native_source_cup_measurements"]["source_first_full_cups"] for x in pours],
                "post_source_hashes":[x["native_real_post_pour_source_hash"] for x in pours],
                "official_end":native["true_original_sdk_final_level"]
                },sort_keys=True),flush=True)
    if len(rows)!=12 or len(root_hashes)!=1:
        raise AssertionError("Original SDK native reset count or entry roots differ")
    for name,word,count in FROZEN:
        pair=[r for r in rows if r["condition"]==name]
        if len(pair)!=2 or {r["witness"] for r in pair}!={"A","B"}:
            raise AssertionError("Independent A/B original entrances absent")
        for k in ("genuine_action5_return_history","official_original_sdk_final_level",
                  "official_original_sdk_final_state","source_stage4_root_hash",
                  "original_sdk_pour_count"):
            if pair[0][k]!=pair[1][k]:
                raise AssertionError("Genuine native A/B mismatch "+name+" "+k)
    report={
      "kind":"SP80_ORIGINAL_SDK_STAGE4_SAME_GAME_REPEATED_ACTION5_FOUR_CUP",
      "original_native_independently_reset_games":len(rows),
      "frozen_native_pour_count_controls":FROZEN,
      "source_original_stage4_root":next(iter(root_hashes)),
      "official_final_level_counts":dict(Counter(str(x["official_original_sdk_final_level"]) for x in rows)),
      "official_level5_or_WIN_count":sum(int(x["official_level5_or_WIN"]) for x in rows),
      "native_genuine_sdk_replay_records":rows,
      "limit":"Additional ACTION5 is not another same-time animation frame. Exact original SDK state, returned pixels, cup source events and official status are measured after each full native action. No hidden win rule inferred."}
    opts.out.parent.mkdir(parents=True,exist_ok=True)
    opts.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(opts.out.with_suffix(".npz"),**full_stacks)
    print("ARC4_SAME_GAME_REPEATED_POURS_SUMMARY "+json.dumps({
       "actual_native_reset_games":len(rows),
       "official_levels":report["official_final_level_counts"],
       "official_level5_or_WIN_count":report["official_level5_or_WIN_count"],
       "cases":{name:{
        "verified_sdk_pours":len(next(r["genuine_action5_return_history"] for r in rows if r["condition"]==name)),
        "native_level_path":[[e["original_sdk_level_before"],e["original_sdk_level_after"]]
             for e in next(r["genuine_action5_return_history"] for r in rows if r["condition"]==name)],
        "source_animation_lengths":[e["native_action5_returned_frames"]
             for e in next(r["genuine_action5_return_history"] for r in rows if r["condition"]==name)],
        "source_first_full_by_pour":[e["native_source_cup_measurements"]["source_first_full_cups"]
             for e in next(r["genuine_action5_return_history"] for r in rows if r["condition"]==name)],
        "native_source_frame_changes_per_pour":[e["native_terminal_screen_difference"]["original_sdk_terminal_changed_pixels"]
             for e in next(r["genuine_action5_return_history"] for r in rows if r["condition"]==name)],
        } for name,word,count in FROZEN},
       "native_A_B_agreement":True
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
