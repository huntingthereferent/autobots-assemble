"""Native SP80 Level4: test observed upper-left source offset from x26 to x23.

Actual original SDK source-success stage3->4 has palette6 near top
(x23..25,y5..7) and no top-edge palette14 response. Our genuine
Level4 visual four-cup witness has x26..28,y5..7 and all 171 upper
border source pixels blink color14, yet stays officially Level4.
Nine tiny upper-bar controls failed to affect that source arrival
(run 40228814659). Now freeze four-cup base geometry and move ONLY
already-selected native lower-L left an additional one to three cells,
with local vertical or middle-height controls. No invented physics.
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

MORE_MOVES=(
 ("parent",""),
 ("L_left1_more","3"),("L_left2_more","3 3"),("L_left3_more","3 3 3"),
 ("L_left1_up1","3 1"),("L_left1_down1","3 2"),
 ("L_left2_up1","3 3 1"),("L_left2_down1","3 3 2"),
 ("L_left1_midup","3 6@15,48 1"),("L_left1_middown","3 6@15,48 2"),
 ("L_left2_midup","3 3 6@15,48 1"),("L_left2_middown","3 3 6@15,48 2"),
)
FROZEN=tuple((name,BASE+(" "+edits if edits else "")+" 5") for name,edits in MORE_MOVES)
assert len(FROZEN)==12
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(w)[-1][0]==5 and
          sum(a==5 for a,xy in parse_plan(w))==1 and
          len(parse_plan(w))<=30 and
          all(xy is not None for a,xy in parse_plan(w) if a==6)
          for name,w in FROZEN)

REGIONS={
    "stage3_success_x23_25":(5,8,23,26),
    "stage4_overflow_x26_28":(5,8,26,29),
    "stage4_right_x56_58":(5,8,56,59),
}
def arrival(root,frames):
    out={}
    for name,(y0,y1,x0,x1) in REGIONS.items():
        times=[int(t) for t,f in enumerate(frames)
               if np.any(f[y0:y1,x0:x1]==6)]
        out[name]={"first_native_frame":times[0] if times else None,
                   "native_frames_with_palette6":times}
    border=[int(t) for t,f in enumerate(frames) if
             np.any((root[2:5,5:62]==1)&(f[2:5,5:62]==14))]
    return {"native_source_top_three_cell_arrivals":out,
            "first_top_palette14_border_frame":border[0] if border else None,
            "native_frames_with_top_border":border}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();records=[];arrays={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1]
            before=raw["stage4_"+str(n-1)][-1]
            pour=raw["stage4_"+str(n)]
            src=arrival(root,pour)
            cups=read_pour(root,before,pour)
            receipts=sdk["genuine_original_stage4_action_ledger"]
            if case.find("_mid")>=0 and not any(
               e["genuine_original_action"]==6 and
               e["real_native_click_xy"]==[15,48] and
               e["original_source_pixel_before_click"]==8
               for e in receipts):
                raise AssertionError("Genuine original middle source selection missing")
            rec={
                "predeclared_case":case,"source_witness":witness,
                "original_stage4_action_word":word,
                "true_original_sdk_level":sdk["true_original_sdk_final_level"],
                "true_original_sdk_state":sdk["true_original_sdk_final_state"],
                "native_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "source_path_region_arrivals":src,
                "source_cups_same_frame":cups,
                "actual_sdk_original_ledger":receipts,
                "actual_native_selected_prepour":selected(before)}
            records.append(rec)
            for key,stack in raw.items():arrays[f"{case}_{witness}_{key}"]=stack
            print("SP80_LEVEL4_LEFT_TOP_CORRIDOR_CASE "+json.dumps({
                "case":case,"witness":witness,
                "official_level":rec["true_original_sdk_level"],
                "official_state":rec["true_original_sdk_state"],
                "path":src,"max_cups":cups["max_original_cup_palette13"],
                "all_four_frames":cups["same_sdk_frame_full_four_cups"],
            },sort_keys=True),flush=True)
    if len(records)!=24 or len(roots)!=1:
        raise AssertionError("Original SDK paired games or authentic stage4 root missing")
    for name,_ in FROZEN:
        a,b=[r for r in records if r["predeclared_case"]==name]
        if any(a[k]!=b[k] for k in (
              "true_original_sdk_level","true_original_sdk_state",
              "source_path_region_arrivals","source_cups_same_frame",
              "actual_native_selected_prepour")):
            raise AssertionError("Independent original SDK entry disagreement "+name)
    result={
      "kind":"ORIGINAL_NATIVE_SP80_LEVEL4_TOP_LEFT_SOURCE_X23_CORRIDOR",
      "source_antecedent_native_runs":[40179237019,40228814659],
      "actual_original_sdk_independent_games":len(records),
      "true_original_stage4_root":next(iter(roots)),
      "original_sdk_official_level5_or_WIN":[r["predeclared_case"] for r in records if r["native_level5_or_WIN"]],
      "original_sdk_level_histogram":dict(Counter(str(r["true_original_sdk_level"]) for r in records)),
      "original_sdk_state_histogram":dict(Counter(str(r["true_original_sdk_state"]) for r in records)),
      "frozen_original_words":FROZEN,
      "actual_original_sdk_frame_and_action_receipts":records,
      "scope":"All outcomes from genuine SDK frames and levels. Source top branch does not prove hidden game physics or goal. Original mathematics/canonical agent untouched."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_LEVEL4_LEFT_TOP_CORRIDOR_SUMMARY "+json.dumps(
        {k:v for k,v in result.items()
         if k not in ("frozen_original_words","actual_original_sdk_frame_and_action_receipts")},
        sort_keys=True),flush=True)
if __name__=="__main__":main()
