"""Original SP80 SDK: timed four-cup visual completion versus top-edge flash.

Measured original native run #40228814659:
four-cup parent last cup filled frame23, top-border first palette14 frame20.
UPPER LEFT1 advances the last cup to frame21 (but remains level4).
Prospectively test UPPER LEFT2..LEFT4 as *timing* displacements, not as
inferred hidden physics or the earlier non-grounded x23 corridor claim.
Keep all other source geometry fixed and retain two independent actual
original SDK entry histories. Only SDK levels_completed>=5/WIN advances.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE,read_pour
from .native_sp80_stage4_upper_flash_control import top_signal
from .native_sp80_multi_select import parse_plan

FROZEN=(
 ("control_upper_left1","6@34,21 3"),
 ("upper_left2","6@34,21 3 3"),
 ("upper_left3","6@34,21 3 3 3"),
 ("upper_left4","6@34,21 3 3 3 3"),
 ("upper_left2_up1","6@34,21 3 3 1"),
 ("upper_left2_down1","6@34,21 3 3 2"),
 ("upper_left3_up1","6@34,21 3 3 3 1"),
)
assert len(FROZEN)==7 and len(STAGE1_WITNESSES)==2
assert all(parse_plan(BASE+" "+movement+" 5")[-1][0]==5 and
           sum(a==5 for a,xy in parse_plan(BASE+" "+movement+" 5"))==1
           for _,movement in FROZEN)

def measure_root_new6(root,pre,frames):
    cells={}
    for label,(y0,y1,x0,x1) in {
        "leftupper_x14_16":(5,8,14,17),
        "leftupper_x20_22":(5,8,20,23),
        "leftupper_x23_25":(5,8,23,26),
        "leftupper_x26_28":(5,8,26,29),
        "rightupper_x44_46":(5,8,44,47),
        "rightupper_x56_58":(5,8,56,59),
    }.items():
        source=pre[y0:y1,x0:x1]
        times=[int(t) for t,frame in enumerate(frames)
               if np.any((source!=6)&(frame[y0:y1,x0:x1]==6))]
        cells[label]={"first_new_actual_source_frame":times[0] if times else None,
                      "pre_pour_palette6_pixels":int(np.count_nonzero(source==6))}
    return cells

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();rows=[];native_arrays={};roots=set()
    for case,movement in FROZEN:
        word=BASE+" "+movement+" 5"
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1]
            before=raw["stage4_"+str(n-1)][-1]
            frames=raw["stage4_"+str(n)]
            cups=read_pour(root,before,frames)
            border=top_signal(root,frames)
            arrivals=measure_root_new6(root,before,frames)
            upper=[e for e in sdk["genuine_original_stage4_action_ledger"]
                   if e["genuine_original_action"]==6 and e["real_native_click_xy"]==[34,21]]
            if len(upper)!=1 or upper[0]["original_source_pixel_before_click"]!=8:
                raise AssertionError("Original SDK root upper palette8 source not selected")
            full=cups["same_sdk_frame_full_four_cups"]
            first_flash=border["top_palette1_to14_first_frame"]
            rec={
                "frozen_case":case,"independent_original_entry":witness,
                "original_stage4_word":word,
                "true_original_sdk_level":sdk["true_original_sdk_final_level"],
                "true_original_sdk_state":sdk["true_original_sdk_final_state"],
                "official_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "source_cup_observations":cups,"source_border_observations":border,
                "source_root_palette6_arrival_observations":arrivals,
                "full_four_cup_first_frame":full[0] if full else None,
                "visual_full_four_before_first_border_flash":bool(full and (
                    first_flash is None or full[0]<first_flash)),
                "genuine_source_upper_click":upper,
                "all_real_original_sdk_action_receipts":sdk["genuine_original_stage4_action_ledger"]
            }
            rows.append(rec)
            for phase,stack in raw.items():native_arrays[f"{case}_{witness}_{phase}"]=stack
            print("SP80_LEVEL4_TIMING_CONTROL_CASE "+json.dumps({
                "case":case,"witness":witness,
                "official_level":rec["true_original_sdk_level"],
                "official_state":rec["true_original_sdk_state"],
                "full_four_first":rec["full_four_cup_first_frame"],
                "full_before_flash":rec["visual_full_four_before_first_border_flash"],
                "flash_first":first_flash,
                "cup_first":cups["first_complete_original_cups"],
                "new_source_cells":arrivals,
            },sort_keys=True),flush=True)
    if len(rows)!=14 or len(roots)!=1:
        raise AssertionError("Independent original SDK native witness pair incomplete")
    for case,_ in FROZEN:
        a,b=[r for r in rows if r["frozen_case"]==case]
        if any(a[k]!=b[k] for k in (
             "true_original_sdk_level","true_original_sdk_state",
             "source_cup_observations","source_border_observations",
             "source_root_palette6_arrival_observations",
             "genuine_source_upper_click")):
            raise AssertionError("Original SDK independent source mismatch: "+case)
    report={
        "kind":"ACTUAL_NATIVE_SP80_LEVEL4_FOUR_CUP_TIMING_VS_TOP_BOUNDARY",
        "native_original_antecedent_run":40228814659,
        "true_original_independent_games":len(rows),
        "same_original_stage4_source_root":next(iter(roots)),
        "official_level5_or_WIN":[{"case":r["frozen_case"],"entry":r["independent_original_entry"]}
                                   for r in rows if r["official_level5_or_WIN"]],
        "official_level_counts":dict(Counter(str(r["true_original_sdk_level"]) for r in rows)),
        "official_state_counts":dict(Counter(str(r["true_original_sdk_state"]) for r in rows)),
        "frozen_original_sdk_words":FROZEN,
        "full_true_native_sdk_frame_action_receipts":rows,
        "limitation":"No hidden objective interpretation; source occupancy versus SDK progress kept separate. Original F3 mathematics and canonical agent unchanged.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**native_arrays)
    print("SP80_LEVEL4_TIMING_CONTROL_SUMMARY "+json.dumps({
       k:v for k,v in report.items()
       if k not in ("frozen_original_sdk_words","full_true_native_sdk_frame_action_receipts")},
       sort_keys=True),flush=True)
if __name__=="__main__":main()
