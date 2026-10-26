"""Official SDK SP80 Level4: source top-border flash controls around four-cup witness.

The genuine original SDK frame archive #12593288221 showed source
palette1->14 top-border flashing from frame20 for ALL 32 frozen
frame-8 fork configurations. The sole full-four-source-cup visual
witness still ended level4 NOT_FINISHED. By contrast, preceding
independently original level3->4 success had no top-edge flash.
This is a source association, not a diagnosed game win rule.

Freeze the proven lower four-cup geometry. Intervene ONLY on the
original root upper source object x29..40,y20..22, selected at x34,y21.
Original official level>=5/WIN is the only progression criterion.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE,read_pour
from .native_sp80_stage4_upstream_junction import selected
from .native_sp80_multi_select import parse_plan
UPPER=(34,21)
MOVES=(
 ("reselect_hold",""),
 ("up1","1"),("down1","2"),("left1","3"),("right1","4"),
 ("up1_left1","1 3"),("up1_right1","1 4"),
 ("down1_left1","2 3"),("down1_right1","2 4"),
)
FROZEN=tuple((name,BASE+" 6@34,21"+(" "+actions if actions else "")+" 5")
             for name,actions in MOVES)
assert len(FROZEN)==9
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(word)[-1][0]==5 and
           len(parse_plan(word))<=28 and
           all(xy is not None for a,xy in parse_plan(word) if a==6)
           for _,word in FROZEN)

def top_signal(root,frames):
    earlier=(root[2:5,5:62]==1)
    first=None;max_flash=0;frames_flash=[]
    for t,frame in enumerate(frames):
        amount=int(np.count_nonzero(earlier&(frame[2:5,5:62]==14)))
        max_flash=max(max_flash,amount)
        if amount and first is None:first=t
        if amount:frames_flash.append(t)
    return {"top_palette1_to14_first_frame":first,
            "max_new_top_border_14_pixels_of_171":max_flash,
            "original_returned_frames_with_top_flash":frames_flash}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    receipts=[];stacks={};roots=set()
    for name,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(name,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1]
            prepour=raw["stage4_"+str(n-1)][-1]
            poured=raw["stage4_"+str(n)]
            pixels=read_pour(root,prepour,poured)
            top=top_signal(root,poured)
            native=sdk["genuine_original_stage4_action_ledger"]
            upper_click=[r for r in native
                if r["genuine_original_action"]==6 and
                    r["real_native_click_xy"]==[34,21]]
            if len(upper_click)!=1 or upper_click[0]["original_source_pixel_before_click"]!=8:
                raise AssertionError("True original SDK upper bar x34,y21 was not selected")
            row={
                "frozen_original_case":name,"independent_source_entry":witness,
                "original_native_stage4_word":word,
                "real_sdk_official_level":sdk["true_original_sdk_final_level"],
                "real_sdk_official_state":sdk["true_original_sdk_final_state"],
                "real_sdk_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "real_native_top_border_observation":top,
                "real_native_cup_observation":pixels,
                "real_sdk_selected_upper_source":upper_click,
                "original_sdk_action_receipts":native,
            }
            receipts.append(row)
            for key,array in raw.items():
                stacks[f"{name}_{witness}_{key}"]=array
            print("SP80_LEVEL4_UPPER_FLASH_CASE "+json.dumps({
                "case":name,"witness":witness,
                "sdk_level":row["real_sdk_official_level"],
                "sdk_state":row["real_sdk_official_state"],
                "top":top,
                "max_cups":pixels["max_original_cup_palette13"],
                "full_four_source_frames":pixels["same_sdk_frame_full_four_cups"],
            },sort_keys=True),flush=True)
    if len(receipts)!=18 or len(roots)!=1:
        raise AssertionError("Original native independent resets or source roots missing")
    for name,_ in FROZEN:
        pair=[r for r in receipts if r["frozen_original_case"]==name]
        if len(pair)!=2 or any(pair[0][field]!=pair[1][field] for field in (
            "real_sdk_official_level","real_sdk_official_state",
            "real_native_top_border_observation","real_native_cup_observation",
            "real_sdk_selected_upper_source")):
            raise AssertionError("Different genuine source entry witnesses: "+name)
    results={
        "kind":"GENUINE_ORIGINAL_SP80_LEVEL4_FOURCUP_TOP_FLASH_CONTROL",
        "antecedent_original_sdk_runs":[40179237019,40179623943],
        "independently_reset_original_sdk_games":len(receipts),
        "original_stage4_root_digest":next(iter(roots)),
        "official_sdk_level5_or_WIN":[{"case":r["frozen_original_case"],"witness":r["independent_source_entry"]}
            for r in receipts if r["real_sdk_level5_or_WIN"]],
        "genuine_original_level_histogram":dict(Counter(str(r["real_sdk_official_level"]) for r in receipts)),
        "genuine_original_state_histogram":dict(Counter(str(r["real_sdk_official_state"]) for r in receipts)),
        "prospectively_frozen_original_programs":FROZEN,
        "full_original_sdk_evidence":receipts,
        "source_limits":"Palette14 top flash is a sourced observation only. Never infer private game physics or award official advance without SDK level>=5/WIN. F3 math and canonical agent unchanged.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(results,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**stacks)
    print("SP80_LEVEL4_UPPER_FLASH_SUMMARY "+json.dumps({k:v for k,v in results.items() if
          k not in ("prospectively_frozen_original_programs","full_original_sdk_evidence")},
          sort_keys=True),flush=True)
if __name__=="__main__":main()
