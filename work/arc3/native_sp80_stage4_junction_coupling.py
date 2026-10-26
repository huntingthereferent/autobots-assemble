"""Native SP80 Level4 lower-junction paired test, following SDK run 40174413932.

Shift the observed left-middle branch UP1 or DOWN1, then reselect and nudge
the nearby lower L-shaped native object. Upper bars remain fixed. Original
SDK frame stacks and official progress signals are retained.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_upstream_junction import inspect, selected
from .native_sp80_multi_select import parse_plan

RIGHT="6@46,33 3"
PARENTS=(
 ("A","6@24,33 2 2 2 3 3","6@34,42 3 3 3 1 1",(18,42),(27,36),44),
 ("B","6@24,33 2 2 2 2 3 3","6@34,42 3 3 3 3 1 1",(18,45),(24,36),47),
)
MIDDLE=(("up1","1",-3),("down1","2",3))
LOWER=(("hold",""),("up1","1"),("down1","2"),
       ("left1","3"),("right1","4"),("up2","1 1"),("down2","2 2"))

def trial(parent,mid,L,mid_xy,L_xy,row,mid_name,mid_action,delta,L_name,L_action):
    parts=[RIGHT,mid,L,f"6@{mid_xy[0]},{mid_xy[1]}",mid_action]
    if L_action:parts.extend((f"6@{L_xy[0]},{L_xy[1]}",L_action))
    parts.append("5")
    return (f"{parent}_{mid_name}_{L_name}"," ".join(parts),row+delta,mid_xy,L_xy)

FROZEN=tuple(trial(*parent,mid_name,mid_action,delta,L_name,L_action)
    for parent in PARENTS
    for mid_name,mid_action,delta in MIDDLE
    for L_name,L_action in LOWER)
assert len(FROZEN)==28
assert len(STAGE1_WITNESSES)==2
assert all(len(parse_plan(word))<=25 and
    sum(a==5 for a,xy in parse_plan(word))==1 and
    parse_plan(word)[-1][0]==5 and
    all(xy is not None for a,xy in parse_plan(word) if a==6)
    for _,word,_,_,_ in FROZEN)

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();records=[];arrays={};roots=set()
    for case,word,branch_y,mid_xy,L_xy in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            before=raw["stage4_"+str(n-1)][-1]
            poured=raw["stage4_"+str(n)]
            observed=inspect(raw["entry3_34"][-1],before,poured,branch_y)
            receipts=sdk["genuine_original_stage4_action_ledger"]
            moves=[{
                "step":e["index"],"native_action":e["genuine_original_action"],
                "click":e["real_native_click_xy"],
                "native_pixel_at_click":e["original_source_pixel_before_click"],
                "native_selected_after":selected(raw["stage4_"+str(e["index"])][-1]),
                "source_hash_after":e["source_frame_after_blake2b16"]}
                for e in receipts if e["genuine_original_action"] in (1,2,3,4,6)]
            if not any(m["click"]==list(mid_xy) and m["native_pixel_at_click"]==8
                       for m in moves):
                raise AssertionError("Relocated original middle bar was not selected")
            if not case.endswith("_hold") and not any(
                    m["click"]==list(L_xy) and m["native_pixel_at_click"]==15
                    for m in moves):
                raise AssertionError("Real original lower L was not selected")
            row={
                "case":case,"witness":witness,"original_stage4_word":word,
                "original_native_final_level":sdk["true_original_sdk_final_level"],
                "original_native_final_state":sdk["true_original_sdk_final_state"],
                "official_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "observed_actual_sdk":observed,
                "true_native_selections":moves,
                "complete_original_sdk_receipts":receipts,
            }
            records.append(row)
            for k,v in raw.items():arrays[f"{case}_{witness}_{k}"]=v
            print("LEVEL4_LOWER_JUNCTION_CASE "+json.dumps({
                "case":case,"witness":witness,
                "level":row["original_native_final_level"],
                "state":row["original_native_final_state"],
                "arrivals":observed["three_cell_first_arrivals"],
                "cups":observed["original_cup_max_source_color13_pixels"],
                "left_boundary":observed["native_first_left_border_change"],
            },sort_keys=True),flush=True)
    if len(records)!=56 or len(roots)!=1:
        raise AssertionError("Original SDK paired runs or native root missing")
    for case,*_ in FROZEN:
        pair=[r for r in records if r["case"]==case]
        if len(pair)!=2 or any(pair[0][key]!=pair[1][key] for key in
            ("original_native_final_level","original_native_final_state",
             "observed_actual_sdk","true_native_selections")):
            raise AssertionError("Independent original SDK discrepancy: "+case)
    wins=[{"case":r["case"],"witness":r["witness"]}
          for r in records if r["official_level5_or_WIN"]]
    summary={
        "kind":"TRUE_ORIGINAL_SP80_LEVEL4_LOWER_JUNCTION_COUPLED_CONTACT",
        "source_antecedent_run":40174413932,
        "true_original_sdk_games":len(records),
        "original_stage4_root_blake2b16":next(iter(roots)),
        "official_level5_or_WIN":wins,
        "official_level_histogram":dict(Counter(str(r["original_native_final_level"]) for r in records)),
        "official_state_histogram":dict(Counter(str(r["original_native_final_state"]) for r in records)),
        "frozen_original_words":FROZEN,
        "complete_original_sdk_evidence":records,
        "scope":"Native source pixels are observations; only official level>=5 or WIN advances. Original F3-48 math unchanged."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("LEVEL4_LOWER_JUNCTION_SUMMARY "+json.dumps({k:v for k,v in summary.items()
          if k not in ("complete_original_sdk_evidence","frozen_original_words")},sort_keys=True),flush=True)
if __name__=="__main__":main()
