"""True SP80 SDK upper-row arrival vs border signal: right-bar local controls.

The prior native four-cup visual parent with upper LEFT2 gave four cups
simultaneously at original returned frame21 and first upper border
palette14 at frame22, unlike upper LEFT1 (flash frame20). Observed
SOURCE-only timing candidate: top border first palette14 follows first
new palette6 near top y5..7 by one frame. Freeze all left geometry and
upper LEFT2, then change one grounded right-middle bar placement.
This is a discriminating source test, not private engine physics.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE,read_pour
from .native_sp80_stage4_upper_flash_control import top_signal
from .native_sp80_multi_select import parse_plan

UPPER_LEFT2="6@34,21 3 3"
CHOICES=(
 ("right_hold",""),
 ("right_left1","3"),
 ("right_left2","3 3"),
 ("right_right1","4"),
 ("right_right2","4 4"),
 ("right_up1","1"),
 ("right_down1","2"),
)
FROZEN=tuple((name,BASE+" "+UPPER_LEFT2+" 6@42,33"+(" "+m if m else "")+" 5")
             for name,m in CHOICES)
assert len(FROZEN)==7 and len(STAGE1_WITNESSES)==2
assert all(parse_plan(w)[-1][0]==5 and len(parse_plan(w))<=30 for _,w in FROZEN)

def top_new_source(pre,arr):
    if pre.shape!=(64,64) or arr.ndim!=3 or arr.shape[1:]!=(64,64):
        raise AssertionError("Expected original SDK source payload")
    sites={}
    for x in range(5,59,3):
        ys=slice(5,8);xs=slice(x,x+3)
        first=next((int(t) for t,f in enumerate(arr)
                    if np.any((pre[ys,xs]!=6)&(f[ys,xs]==6))),None)
        if first is not None:
            sites[str(x)+"-"+str(x+2)]=first
    return {"first_any_new_palette6_y5_7":
                 min(sites.values()) if sites else None,
            "first_new_palette6_by_x_cell":sites,
            "source_color6_root_at_y5":int(np.count_nonzero(pre[5:8,5:59]==6))}
def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();rows=[];stacks={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=raw["entry3_34"][-1];pre=raw["stage4_"+str(n-1)][-1]
            animation=raw["stage4_"+str(n)]
            source=top_new_source(pre,animation)
            borders=top_signal(root,animation)
            cups=read_pour(root,pre,animation)
            selects=[e for e in sdk["genuine_original_stage4_action_ledger"]
                     if e["genuine_original_action"]==6 and
                        e["real_native_click_xy"]==[42,33]]
            if len(selects)!=1 or selects[0]["original_source_pixel_before_click"]!=8:
                raise AssertionError("Real original right-middle source palette8 not selected")
            flash=borders["top_palette1_to14_first_frame"]
            earliest=source["first_any_new_palette6_y5_7"]
            row={"case":case,"entry_witness":witness,
                 "true_original_stage4_word":word,
                 "official_sdk_level":sdk["true_original_sdk_final_level"],
                 "official_sdk_state":sdk["true_original_sdk_final_state"],
                 "official_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                 "true_native_source_top_arrivals":source,
                 "true_native_border_signal":borders,
                 "true_native_cup_windows":cups,
                 "empirical_border_after_upper_arrival_one_frame":
                    None if earliest is None or flash is None else flash==earliest+1,
                 "grounded_original_selected_right_bar_receipt":selects,
                 "all_original_sdk_action_receipts":sdk["genuine_original_stage4_action_ledger"]}
            rows.append(row)
            for key,frames in raw.items():stacks[f"{case}_{witness}_{key}"]=frames
            print("SP80_LEVEL4_RIGHT_EDGE_TIMING_CASE "+json.dumps({
                "case":case,"witness":witness,
                "official_level":row["official_sdk_level"],
                "official_state":row["official_sdk_state"],
                "first_new_source":earliest,"new_source_cells":source["first_new_palette6_by_x_cell"],
                "top_border":flash,
                "source_full_four_frames":cups["same_sdk_frame_full_four_cups"],
                "source_cup_first":cups["first_complete_original_cups"],
                "source_timing_relation":row["empirical_border_after_upper_arrival_one_frame"],
            },sort_keys=True),flush=True)
    if len(rows)!=14 or len(roots)!=1:
        raise AssertionError("Independently reset actual SDK runs or source roots missing")
    for case,_ in FROZEN:
        a,b=[r for r in rows if r["case"]==case]
        if any(a[k]!=b[k] for k in
           ("official_sdk_level","official_sdk_state","true_native_source_top_arrivals",
            "true_native_border_signal","true_native_cup_windows",
            "grounded_original_selected_right_bar_receipt")):
            raise AssertionError("Source disagreement between original independent entries "+case)
    result={"kind":"ORIGINAL_NATIVE_SP80_LEVEL4_RIGHT_SOURCE_UPPER_BORDER_TIMING",
        "antecedent_original_native_run":40232179104,
        "actual_original_sdk_games":len(rows),
        "same_original_native_stage4_source_root":next(iter(roots)),
        "official_level5_or_WIN":[r["case"] for r in rows if r["official_level5_or_WIN"]],
        "official_level_counts":dict(Counter(str(r["official_sdk_level"]) for r in rows)),
        "official_state_counts":dict(Counter(str(r["official_sdk_state"]) for r in rows)),
        "prospectively_frozen_programs":FROZEN,
        "complete_original_sdk_evidence":rows,
        "scope":"Source frame timing is empirical only. Level>=5/WIN is original SDK progress. Original F3-48 math/canonical agent untouched."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**stacks)
    print("SP80_LEVEL4_RIGHT_EDGE_TIMING_SUMMARY "+json.dumps({
        k:v for k,v in result.items() if k not in ("prospectively_frozen_programs","complete_original_sdk_evidence")
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
