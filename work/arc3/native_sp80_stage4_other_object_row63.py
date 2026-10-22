"""Original SDK SP80 level4: source row63 response to movements on another object.

A fixed D3 lower arrangement and final upper LEFT1 movement are retained.
A right-bar re-selection control separates extra clicks from reversible
native movements; true SDK frames identify whether the other bar restored.
No row63 semantics or stage5 outcome is assumed.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_top_left_source_contrast import source_report
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

LOWER="6@46,33 3 6@24,33 2 2 2 3 3 6@34,42 3 3 3 1 1"
RIGHT_CLICK="6@46,33"
UPPER="6@34,21 3 5"
CONTROLS=(
    ("native_base",""),
    ("right_reclick_only",RIGHT_CLICK),
    ("right_left_right",RIGHT_CLICK+" 3 4"),
    ("right_up_down",RIGHT_CLICK+" 1 2"),
    ("right_right_left",RIGHT_CLICK+" 4 3"),
)

def row63(frame):
    a=frame[63]
    xs=np.flatnonzero(a==14)
    return {"first_palette14_x":int(xs.min()) if len(xs) else None,
            "source_last_row":[int(v) for v in a],
            "palette14_count":int(len(xs))}

def native_delta(a,b):
    pos=np.argwhere(a!=b)
    return {"different_pixel_count":int(len(pos)),
            "different_pixels_y0_62":int(np.count_nonzero(a[:63]!=b[:63])),
            "different_pixels_y63":int(np.count_nonzero(a[63]!=b[63])),
            "difference_bbox_xyxy":[int(pos[:,1].min()),int(pos[:,0].min()),
                int(pos[:,1].max()),int(pos[:,0].max())] if len(pos) else None,
            "changed_pixels":[{"xy":[int(x),int(y)],"source_base":int(a[y,x]),"source_other":int(b[y,x])}
                for y,x in pos[:80]],
            "truncated_changes":bool(len(pos)>80)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows=[];arrays={};kept={};roots=set()
    for label,right_word in CONTROLS:
        word=" ".join(x for x in (LOWER,right_word,UPPER) if x)
        program=parse_plan(word)
        if not program or program[-1][0]!=5 or sum(a==5 for a,_ in program)!=1:
            raise AssertionError("Expected exact original SDK terminal pour")
        for witness,entry in STAGE1_WITNESSES:
            native,raw=run_case(label,witness,entry,word)
            root=raw["entry3_34"][-1]
            before=raw["stage4_"+str(len(program)-1)][-1]
            frames=raw["stage4_"+str(len(program))]
            src=source_report(root,before,frames)
            roots.add(src["root_hash"])
            receipts=native["genuine_original_stage4_action_ledger"]
            extra=[v for v in receipts if v["real_native_click_xy"]==[46,33]]
            if (label=="native_base" and len(extra)!=1) or (label!="native_base" and len(extra)!=2):
                raise AssertionError("Unverified original right-bar re-click")
            record={"label":label,"witness":witness,"native_source_word":word,
                "native_stage4_receipts":receipts,
                "official_level":native["true_original_sdk_final_level"],
                "official_state":native["true_original_sdk_final_state"],
                "official_level5_or_WIN":native["official_original_level5_or_WIN"],
                "native_source_observation":src,
                "source_pre_pour_row63":row63(before),
                "source_final_pour_row63":row63(frames[-1]),
                "original_source_last_frame_hash":hash_frame(frames[-1])}
            rows.append(record)
            kept[(label,witness)]=(before.copy(),frames.copy())
            for key,stack in raw.items():arrays[label+"_"+witness+"_"+key]=stack
            print("ARC4_OTHER_OBJECT_CASE "+json.dumps({
                "case":label,"witness":witness,
                "official_level":record["official_level"],"official_state":record["official_state"],
                "first_row63_before":record["source_pre_pour_row63"]["first_palette14_x"],
                "first_row63_after":record["source_final_pour_row63"]["first_palette14_x"],
                "source_cups":src["source_first_full_cups"],
                "native_pre_pour_hash":src["pre_pour_hash"],
            },sort_keys=True),flush=True)
    if len(roots)!=1:raise AssertionError("Original stage4 SDK root mismatch")
    comparisons={}
    for label,_ in CONTROLS:
        pair=[r for r in rows if r["label"]==label]
        if len(pair)!=2 or {r["witness"] for r in pair}!={"A","B"}:
            raise AssertionError("Missing independent original native witness "+label)
        for k in ("official_level","official_state","native_source_observation","source_pre_pour_row63","source_final_pour_row63"):
            if pair[0][k]!=pair[1][k]:raise AssertionError("Original source witnesses disagree "+label+" "+k)
        if label=="native_base":continue
        two=[]
        for witness,_ in STAGE1_WITNESSES:
            base,base_stack=kept[("native_base",witness)]
            other,other_stack=kept[(label,witness)]
            two.append({"pre_pour":native_delta(base,other),
                "last_pour":native_delta(base_stack[-1],other_stack[-1]),
                "native_pour_frame_count":[len(base_stack),len(other_stack)],
                "first_pour_animation_difference":next((i for i in range(min(len(base_stack),len(other_stack))) if np.any(base_stack[i]!=other_stack[i])),None)})
        if two[0]!=two[1]:raise AssertionError("Original SDK paired source-frame differences disagree "+label)
        comparisons[label]=two[0]
    outcome={"kind":"ORIGINAL_SP80_STAGE4_ROW63_OTHER_OBJECT_MOVEMENT_CONTRAST",
        "real_original_sdk_resets":len(rows),
        "original_sdk_level_histogram":dict(Counter(str(r["official_level"]) for r in rows)),
        "official_level5_or_WIN_count":sum(int(r["official_level5_or_WIN"]) for r in rows),
        "prospectively_frozen_controls":CONTROLS,
        "original_native_records":rows,
        "original_native_source_differences_from_baseline":comparisons,
        "boundary":"Only genuine SDK action receipts and rendered screen pixels. An off-bar movement may change interior board state; only observed restoration supports comparison. Row63 meaning UNKNOWN."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(outcome,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ARC4_OTHER_OBJECT_SUMMARY "+json.dumps({
       "original_sdk_resets":len(rows),
       "official_levels":outcome["original_sdk_level_histogram"],
       "level5_or_win_count":outcome["official_level5_or_WIN_count"],
       "controls":{n:{"row63_pre_x":next(r["source_pre_pour_row63"]["first_palette14_x"] for r in rows if r["label"]==n),
                    "row63_after_x":next(r["source_final_pour_row63"]["first_palette14_x"] for r in rows if r["label"]==n),
                    "cup_times":next(r["native_source_observation"]["source_first_full_cups"] for r in rows if r["label"]==n),
                    "pre_difference":comparisons[n]["pre_pour"] if n in comparisons else None}
                    for n,_ in CONTROLS}},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
