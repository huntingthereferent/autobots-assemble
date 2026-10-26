"""Original ARC SP80 Level4 2-cell height holdout, only previously
native four-cup horizontal control families.

Antecedent real run #40236212016: 26 horizontal variants all had first
NEW source palette6 in y5..7, followed one native frame later by the top
border palette14 flash. Eight paired-source families had simultaneous
full-four-cup source frames. Freeze only four successful horizontal
programs, then move one or both independently SDK selectable bars two
cells vertically. Only official SDK >=5/WIN means progress.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE,read_pour
from .native_sp80_stage4_upper_strip_counterexample import see_original
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage4_upstream_junction import selected
import numpy as np

VARIANTS=(
 ("upper_up2","1 1",""),
 ("upper_down2","2 2",""),
 ("right_up2","","1 1"),
 ("right_down2","","2 2"),
 ("both_up2","1 1","1 1"),
 ("both_down2","2 2","2 2"),
)
def nativeword(upper_left,right_left,umove,rmove):
    bits=[BASE,"6@34,21"]+[str(3)]*upper_left
    if umove:bits+=umove.split()
    bits+=["6@42,33"]+[str(3)]*right_left
    if rmove:bits+=rmove.split()
    bits.append("5")
    return " ".join(bits)

FROZEN=tuple((f"upperL{u}_rightL{r}_{name}",nativeword(u,r,um,rm))
             for u in (1,2) for r in (1,2)
             for name,um,rm in VARIANTS)
assert len(FROZEN)==24==len({name for name,word in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(word)[-1][0]==5 and
           sum(a==5 for a,xy in parse_plan(word))==1 and
           len(parse_plan(word))<=35 and
           all(xy is not None for a,xy in parse_plan(word) if a==6)
           for name,word in FROZEN)

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();rows=[];arrays={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1]
            pre=raw[f"stage4_{n-1}"][-1]
            frames=raw[f"stage4_{n}"]
            source=see_original(pre,root,frames)
            cups=read_pour(root,pre,frames)
            receipts=sdk["genuine_original_stage4_action_ledger"]
            choices=[]
            for click in ([34,21],[42,33]):
                selected_click=[e for e in receipts if
                    e["genuine_original_action"]==6 and
                    e["real_native_click_xy"]==click]
                if len(selected_click)!=1 or selected_click[0]["original_source_pixel_before_click"]!=8:
                    raise AssertionError("Original source palette8 click not valid "+str(click))
                choices+=selected_click
            hit=bool(cups["same_sdk_frame_full_four_cups"]) and not source["any_new_upper_palette6"]
            record={
                "prospective_native_case":case,
                "independent_stage_entry_witness":witness,
                "original_source_action_word":word,
                "official_native_level":sdk["true_original_sdk_final_level"],
                "official_native_state":sdk["true_original_sdk_final_state"],
                "official_original_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "original_source_upper_event":source,
                "original_native_cup_frames":cups,
                "native_four_cups_without_new_palette6":hit,
                "native_pre_pour_selected_objects":selected(pre),
                "true_original_source_click_receipts":choices,
                "full_native_action_ledger":receipts
            }
            rows.append(record)
            for phase,stack in raw.items():arrays[f"{case}_{witness}_{phase}"]=stack
            print("SP80_LEVEL4_HEIGHT2_HOLDOUT_CASE "+json.dumps({
                "case":case,"witness":witness,
                "level":record["official_native_level"],
                "state":record["official_native_state"],
                "new_upper6":source["any_new_upper_palette6"],
                "first_upper6":source["first_new_original_palette6_y5_7"],
                "first_border14":source["first_original_top_palette14_border"],
                "four_full_source_frames":cups["same_sdk_frame_full_four_cups"],
                "source_both":hit},sort_keys=True),flush=True)
    if len(rows)!=48 or len(roots)!=1:
        raise AssertionError("True native source independently reset games missing")
    for case,_ in FROZEN:
        a,b=[r for r in rows if r["prospective_native_case"]==case]
        if any(a[k]!=b[k] for k in (
            "official_native_level","official_native_state",
            "original_source_upper_event","original_native_cup_frames",
            "native_four_cups_without_new_palette6","native_pre_pour_selected_objects")):
            raise AssertionError("Original independent source witnesses diverged for "+case)
    summary={
        "kind":"GENUINE_NATIVE_SP80_LEVEL4_TWO_TILE_VERTICAL_SOURCE_HOLDOUT",
        "antecedent_native_run":40236212016,
        "new_original_normal_sdk_games":len(rows),
        "native_stage4_source_root":next(iter(roots)),
        "source_four_cups_no_upper_arrival_cases":list(sorted({
            r["prospective_native_case"] for r in rows if r["native_four_cups_without_new_palette6"]})),
        "official_native_level5_or_WIN_cases":list(sorted({
            r["prospective_native_case"] for r in rows if r["official_original_level5_or_WIN"]})),
        "cases_without_any_new_upper_palette6":list(sorted({
            r["prospective_native_case"] for r in rows if not r["original_source_upper_event"]["any_new_upper_palette6"]})),
        "official_level_histogram":dict(Counter(str(r["official_native_level"]) for r in rows)),
        "official_state_histogram":dict(Counter(str(r["official_native_state"]) for r in rows)),
        "frozen_source_programs":FROZEN,
        "complete_original_sdk_evidence":rows,
        "epistemic_limit":"Frame palette is observed source only, not private goal physics. True original SDK level>=5/WIN is official success. F3-48 math and canonical agent untouched."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_LEVEL4_HEIGHT2_HOLDOUT_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("frozen_source_programs","complete_original_sdk_evidence")
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
