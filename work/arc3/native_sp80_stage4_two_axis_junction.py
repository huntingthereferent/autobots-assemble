"""Genuine native SP80 Level4: two-axis lower-L junction, both move orders.

Built from actual original SDK native run #40177191960. Source-only:
some 1-cell lower-L lateral changes switch top-left/lateral visual cups,
but never official level>=5. Freeze adjacent horizontal+vertical changes
in both native action orders while preserving the upper bars. Retain raw
original frames and official level. No private fluid-engine assumptions.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_upstream_junction import inspect,selected
from .native_sp80_multi_select import parse_plan

RIGHT="6@46,33 3"
PARENTS=(
 ("A","6@24,33 2 2 2 3 3","6@34,42 3 3 3 1 1",(18,42),(27,36),44),
 ("B","6@24,33 2 2 2 2 3 3","6@34,42 3 3 3 3 1 1",(18,45),(24,36),47),
)
CUPS={"lateral":(5,35,10,43),"top_left":(17,5,25,10),
      "top_middle":(35,5,43,10),"top_right":(47,5,55,10)}
FROZEN=tuple(
 (f"{name}_mid{mid_label}_L{h_label}_{v_label}_{order}",
  " ".join((RIGHT,mid,L,
            f"6@{midxy[0]},{midxy[1]}",midmove,
            f"6@{Lxy[0]},{Lxy[1]}",
            " ".join((hmove,vmove) if order=="HV" else (vmove,hmove)),
            "5")),row+(-3 if midmove=="1" else 3),midxy,Lxy)
 for name,mid,L,midxy,Lxy,row in PARENTS
 for mid_label,midmove in (("up1","1"),("down1","2"))
 for h_label,hmove in (("left1","3"),("right1","4"))
 for v_label,vmove in (("up1","1"),("down1","2"))
 for order in ("HV","VH"))
assert len(FROZEN)==32==len({r[0] for r in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(sum(a==5 for a,xy in parse_plan(w))==1 and
           parse_plan(w)[-1][0]==5 and len(parse_plan(w))<=25 and
           all(xy is not None for a,xy in parse_plan(w) if a==6)
           for name,w,*_ in FROZEN)

def simultaneous(root,pour):
    first_two,first_four=None,None
    max_simul_two=0
    for t,frame in enumerate(pour):
        counts={}
        for name,(x0,y0,x1,y1) in CUPS.items():
            original=(root[y0:y1+1,x0:x1+1]==11)
            if int(original.sum())!=45:raise AssertionError("Original source cup changed")
            counts[name]=int(np.count_nonzero(original & (frame[y0:y1+1,x0:x1+1]==13)))
        max_simul_two=max(max_simul_two,counts["lateral"]+counts["top_left"])
        if first_two is None and counts["lateral"]==counts["top_left"]==45:
            first_two=t
        if first_four is None and all(v==45 for v in counts.values()):
            first_four=t
    return {"first_both_left_cups_full_same_original_sdk_frame":first_two,
            "first_all_four_cups_full_same_original_sdk_frame":first_four,
            "max_simultaneous_left_cups_sum_of_90":max_simul_two}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args(); rows=[];arrays={};roots=set()
    for case,word,row_y,midxy,Lxy in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,stacks=run_case(case,witness,entry,word)
            root=stacks["entry3_34"][-1]
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            pre=stacks["stage4_"+str(n-1)][-1]
            pour=stacks["stage4_"+str(n)]
            observed=inspect(root,pre,pour,row_y)
            simult=simultaneous(root,pour)
            ledger=sdk["genuine_original_stage4_action_ledger"]
            movements=[{
                "index":e["index"],"action":e["genuine_original_action"],
                "genuine_click":e["real_native_click_xy"],
                "actual_clicked_source_palette":e["original_source_pixel_before_click"],
                "selected_after":selected(stacks["stage4_"+str(e["index"])][-1]),
                "source_after_hash":e["source_frame_after_blake2b16"]}
                for e in ledger if e["genuine_original_action"] in (1,2,3,4,6)]
            if not any(x["genuine_click"]==list(midxy) and x["actual_clicked_source_palette"]==8
                       for x in movements):raise AssertionError("Native relocated middle selection missing")
            if not any(x["genuine_click"]==list(Lxy) and x["actual_clicked_source_palette"]==15
                       for x in movements):raise AssertionError("Native relocated L selection missing")
            record={
                "case":case,"witness":witness,"original_native_word":word,
                "official_sdk_level":sdk["true_original_sdk_final_level"],
                "official_sdk_state":sdk["true_original_sdk_final_state"],
                "official_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "native_cup_same_frame_readout":simult,
                "genuine_original_frame_observations":observed,
                "genuine_original_selected_receipts":movements,
                "complete_original_sdk_action_ledger":ledger}
            rows.append(record)
            for k,v in stacks.items():arrays[f"{case}_{witness}_{k}"]=v
            print("SP80_LEVEL4_TWO_AXIS_CASE "+json.dumps({
                "case":case,"witness":witness,"level":record["official_sdk_level"],
                "state":record["official_sdk_state"],"simultaneous":simult,
                "cup_max":observed["original_cup_max_source_color13_pixels"],
                "left_border":observed["native_first_left_border_change"]},sort_keys=True),flush=True)
    if len(rows)!=64 or len(roots)!=1:raise AssertionError("Native original independent resets missing")
    for case,*_ in FROZEN:
        a,b=[r for r in rows if r["case"]==case]
        if any(a[k]!=b[k] for k in ("official_sdk_level","official_sdk_state",
              "native_cup_same_frame_readout","genuine_original_frame_observations",
              "genuine_original_selected_receipts")):
            raise AssertionError("Original A/B witness discrepancy "+case)
    advances=[{"case":r["case"],"witness":r["witness"]} for r in rows if r["official_level5_or_WIN"]]
    summary={
        "kind":"TRUE_ORIGINAL_SP80_LEVEL4_LOWER_L_TWO_AXIS_INTERVENTION",
        "native_source_antecedent_run":40177191960,
        "genuine_original_sdk_games":len(rows),
        "true_original_level4_root":next(iter(roots)),
        "official_level5_or_WIN_cases":advances,
        "official_original_level_counts":dict(Counter(str(r["official_sdk_level"]) for r in rows)),
        "official_original_state_counts":dict(Counter(str(r["official_sdk_state"]) for r in rows)),
        "frozen_words":FROZEN,"authentic_original_action_frame_receipts":rows,
        "limits":"Only actual SDK level>=5/WIN is native progress. Source pixels are not decoded engine physics."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_LEVEL4_TWO_AXIS_SUMMARY "+json.dumps({k:v for k,v in summary.items()
       if k not in ("frozen_words","authentic_original_action_frame_receipts")},sort_keys=True),flush=True)
if __name__=="__main__":main()
