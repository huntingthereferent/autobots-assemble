"""One-factor native SP80 stage4 lower-L placement contrast.

The original SDK entrance, right/middle positions, lower-L source click,
and final upper LEFT1→ACTION5 are held fixed. Only one real ACTION1..4
while the lower-L is currently selected is varied before the upper click.
Native levels_completed/state are the only progression predicate.
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

# Original frozen D3L2 / L3U2 source arrangement. The final object is
# the genuine selected L-shaped bar at x23..28,y35..40.
LOWER = "6@46,33 3 6@24,33 2 2 2 3 3 6@34,42 3 3 3 1 1"
UPPER_POUR = "6@34,21 3 5"
FROZEN = (
    ("lower_original", ""),
    ("lower_up1", "1"),
    ("lower_down1", "2"),
    ("lower_left1", "3"),
    ("lower_right1", "4"),
)
LEFT_MEASURED = (slice(2,62),slice(2,5))
LEFT_COMPLETE = (slice(0,64),slice(0,6))

def selected_bbox(frame):
    ys,xs=np.nonzero(frame==9)
    return [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None

def border_observation(pre,frames,area):
    if pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Original native 64x64 source required")
    before=pre[area]
    result={"first_change":None,"first_1_to_14":None,"max_changed":0,
       "last_changed":0,"first_change_positions":[]}
    for i,f in enumerate(frames):
        changed=(before!=f[area])
        count=int(np.count_nonzero(changed))
        result["max_changed"]=max(result["max_changed"],count)
        result["last_changed"]=count
        if count and result["first_change"] is None:
            result["first_change"]=i
            ys,xs=np.nonzero(changed)
            result["first_change_positions"]=[
               [int(x+area[1].start),int(y+area[0].start),
                int(pre[y+area[0].start,x+area[1].start]),
                int(f[y+area[0].start,x+area[1].start])]
               for y,x in zip(ys[:120],xs[:120])]
        if result["first_1_to_14"] is None and bool(np.any(
              (before==1)&(f[area]==14))):
            result["first_1_to_14"]=i
    return result

def count_diff(a,b):
    ys,xs=np.nonzero(a!=b)
    return {"pixels":int(len(xs)),
      "bbox_xyxy":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]
                     if len(xs) else None,
      "inside_y0_62":int(np.count_nonzero(a[:63]!=b[:63])),
      "bottom_y63":int(np.count_nonzero(a[63]!=b[63]))}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    opts=p.parse_args()
    baseline_n=len(parse_plan(LOWER))
    records=[];stack_dict={};images={};roots=set()
    for condition,one_move in FROZEN:
        word=" ".join(x for x in (LOWER,one_move,UPPER_POUR) if x)
        actions=parse_plan(word)
        assert actions[-1][0]==5 and sum(a==5 for a,xy in actions)==1
        assert len(actions)==baseline_n+len(parse_plan(one_move))+3
        for witness,entry in STAGE1_WITNESSES:
            native,raw=run_case(condition,witness,entry,word)
            root=raw["entry3_34"][-1]
            pre=raw["stage4_"+str(len(actions)-1)][-1]
            frames=raw["stage4_"+str(len(actions))]
            before_move=raw["stage4_"+str(baseline_n)][-1]
            selected=raw["stage4_"+str(baseline_n+len(parse_plan(one_move)))][-1]
            if selected_bbox(before_move)!=[23,35,28,40]:
                raise AssertionError("Frozen lower L source selection not genuine")
            roots.add(hash_frame(root))
            source=source_report(root,pre,frames)
            actual_move_made=(selected_bbox(selected)!=[23,35,28,40])
            report={
                "condition":condition,"witness":witness,
                "original_source_word":word,
                "authentic_lower_L_before_bbox":selected_bbox(before_move),
                "authentic_lower_L_after_bbox":selected_bbox(selected),
                "lower_L_move_changed_selected_bbox":actual_move_made,
                "source_after_lower_L_hash":hash_frame(selected),
                "true_original_sdk_level":native["true_original_sdk_final_level"],
                "true_original_sdk_state":native["true_original_sdk_final_state"],
                "official_level5_or_WIN":bool(native["official_original_level5_or_WIN"]),
                "source_cup_measurements":source,
                "left_measured_source_border":border_observation(pre,frames,LEFT_MEASURED),
                "left_complete_screen_strip":border_observation(pre,frames,LEFT_COMPLETE),
                "original_native_action_receipts":native["genuine_original_stage4_action_ledger"],
            }
            records.append(report)
            images[(condition,witness)]=(pre.copy(),frames[-1].copy())
            for key,stack in raw.items():stack_dict[condition+"_"+witness+"_"+key]=stack
            print("ARC4_L_PLACEMENT_NATIVE "+json.dumps({
                "condition":condition,"witness":witness,
                "official_level":report["true_original_sdk_level"],
                "sdk_state":report["true_original_sdk_state"],
                "original_L_after_bbox":report["authentic_lower_L_after_bbox"],
                "changed_native_L":report["lower_L_move_changed_selected_bbox"],
                "first_four_cup_frame":source["source_first_four_simultaneous"],
                "left_original_border_first":report["left_measured_source_border"]["first_change"],
                "left_full_source_strip_first":report["left_complete_screen_strip"]["first_change"]
            },sort_keys=True),flush=True)
    if len(roots)!=1 or len(records)!=len(FROZEN)*2:
        raise AssertionError("Different original SDK stage4 source roots")
    differ={}
    for condition,_ in FROZEN:
        both=[r for r in records if r["condition"]==condition]
        if len(both)!=2 or {r["witness"] for r in both}!={"A","B"}:
            raise AssertionError("Two independent native entrance witnesses missing")
        for k in ("authentic_lower_L_before_bbox","authentic_lower_L_after_bbox",
                  "lower_L_move_changed_selected_bbox","true_original_sdk_level",
                  "true_original_sdk_state","source_cup_measurements",
                  "left_measured_source_border","left_complete_screen_strip"):
            if both[0][k]!=both[1][k]:
                raise AssertionError("Original SDK A/B disagreement: "+condition+" "+k)
        if condition=="lower_original":continue
        comparisons=[]
        for witness,_ in STAGE1_WITNESSES:
            prev,final=images[("lower_original",witness)]
            curr,currfinal=images[(condition,witness)]
            comparisons.append({"pre":count_diff(prev,curr),"final":count_diff(final,currfinal)})
        if comparisons[0]!=comparisons[1]:
            raise AssertionError("Original SDK native frame contrast A/B disagrees")
        differ[condition]=comparisons[0]
    doc={"kind":"ORIGINAL_SP80_STAGE4_LOWER_L_ONE_FACTOR_POSITION_AUDIT",
         "native_sdk_reset_count":len(records),
         "original_sdk_levels_histogram":dict(Counter(str(r["true_original_sdk_level"]) for r in records)),
         "official_level5_or_WIN_count":sum(int(r["official_level5_or_WIN"]) for r in records),
         "frozen_lower_L_interventions":FROZEN,
         "native_original_records":records,
         "source_frame_contrasts_against_control":differ,
         "limit":"A visible left-border event is only a source observation. A moved object does not establish a win mechanic. Stage5/WIN requires original SDK status."}
    opts.out.parent.mkdir(parents=True,exist_ok=True)
    opts.out.write_text(json.dumps(doc,indent=2)+"\n")
    np.savez_compressed(opts.out.with_suffix(".npz"),**stack_dict)
    print("ARC4_L_PLACEMENT_SUMMARY "+json.dumps({
        "native_sdk_reset_count":len(records),
        "original_sdk_levels_histogram":doc["original_sdk_levels_histogram"],
        "official_level5_or_WIN_count":doc["official_level5_or_WIN_count"],
        "conditions":{name:{"native_L_bbox":next(r["authentic_lower_L_after_bbox"] for r in records if r["condition"]==name),
             "movement_source_observed":next(r["lower_L_move_changed_selected_bbox"] for r in records if r["condition"]==name),
             "cup_first_full":next(r["source_cup_measurements"]["source_first_full_cups"] for r in records if r["condition"]==name),
             "four_cups_frame":next(r["source_cup_measurements"]["source_first_four_simultaneous"] for r in records if r["condition"]==name),
             "left_border_frame":next(r["left_measured_source_border"]["first_change"] for r in records if r["condition"]==name),
             "left_strip_frame":next(r["left_complete_screen_strip"]["first_change"] for r in records if r["condition"]==name),
             "source_contrast":differ.get(name)} for name,_ in FROZEN}
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
