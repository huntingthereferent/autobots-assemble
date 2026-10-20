"""Frozen finite screen-path contrast against authentic original SP80 stage2.

Source stage2 screen mapped independently in run #39461857154.
Finite path proxy is a PROPOSAL derived from screen geometry, not an
engine implementation, validated game law, or source predicate.
Results are always scored by original Arcade.NORMAL SDK levels/WIN.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage2_click_inventory import trial as source_trial
from .native_sp80_stage2_fourbar_pairwise import (
    original_word,source_stage2_commit,BARS
)

# Native verified original SDK frame (SHA256 b23d0e...):
# 4px cells, source apparent emitters at x-cells 1/9/14,
# top U-shaped source shapes centered at x-cells 2/7/13;
# four original movable palette8/9 bands x=2,10,2,9.
# These are measurements of screen positions ONLY. The proxy deliberately
# does NOT know actual contact, cup, spill, simultaneous ray semantics.
ROOT=(2,10,2,9)
WIDTHS=(4,5,6,6)
Y=(5,7,8,10)
SOURCE_X=(1,9,14)
TOP_NOTCH_X=(2,7,13)
# Prospective candidates from bounded 18,876 horizontal placement proxy,
# plus four original-source controls. All source trials NEW resets.
FROZEN=(
    ("proxy_a",(3,8,3,7)),
    ("proxy_b",(3,8,4,7)),
    ("proxy_c",(3,8,7,7)),
    ("proxy_d",(3,7,7,7)),
    ("proxy_e",(3,8,5,5)),
    ("proxy_f",(3,8,6,6)),
    ("proxy_g",(3,8,4,4)),
    ("proxy_h",(3,8,3,6)),
    ("proxy_i",(3,8,0,10)),
    ("proxy_j",(3,8,4,10)),
    ("proxy_k",(3,7,0,7)),
    ("proxy_l",(3,8,0,7)),
    ("control_root",(2,10,2,9)),
    ("control_inward",(4,8,4,7)),
    ("control_shifted",(3,9,7,7)),
    ("control_reverse",(2,11,2,10)),
)
def finite_screen_proxy(positions):
    # Pure declared finite graph: each upward projected ray that intersects
    # a horizontal segment branches at its endpoints. This is a candidate
    # topology rank only, NOT actual liquid physics or native SDK observation.
    waves=[(x,14) for x in SOURCE_X]
    ends=[]
    bars=sorted(zip(Y,positions,WIDTHS),reverse=True)
    for _ in range(12):
        if not waves:break
        next_w=[]
        for x,cy in waves:
            hit=[(y,a,w) for y,a,w in bars if y<cy and a<=x<a+w]
            if not hit:
                ends.append(x);continue
            y,a,w=max(hit)
            next_w.extend(((a-1,y),(a+w,y)))
        waves=next_w
    ends.extend(x for x,_ in waves)
    return {
        "unverified_proxy_terminals":sorted(ends),
        "source_top_notch_columns_reached_by_proxy":sorted(set(ends)&set(TOP_NOTCH_X)),
        "unverified_proxy_unmatched_rays":sum(x not in TOP_NOTCH_X for x in ends),
    }
PROGRAMS=tuple((name, tuple(p[i]-ROOT[i] for i in range(4)),
                original_word(tuple(p[i]-ROOT[i] for i in range(4))),p)
               for name,p in FROZEN)
assert len(PROGRAMS)==len(set(x[0] for x in PROGRAMS))==16
assert len(STAGE1_WITNESSES)==2
assert all(all(0<=p<=16-w for p,w in zip(pos,WIDTHS))
           for _,_,_,pos in PROGRAMS)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    original_rows=[];arrays={}
    for name,delta,word,positions in PROGRAMS:
        for witness,original_entry in STAGE1_WITNESSES:
            row,raw=source_trial(witness,original_entry,name,word,0)
            if row["source_genuine_level2_entry"]["source_original_level"]!=2:
                raise RuntimeError("Source did not witness genuine original level2")
            row["declared_screen_geometry"]=dict(zip(BARS,positions))
            row["frozen_native_horizontal_offsets"]=dict(zip(BARS,delta))
            row["candidate_proxy_not_source_physics"]=finite_screen_proxy(positions)
            observed=source_stage2_commit(row,raw)
            row["actual_source_original_pour"]=observed
            boxes=observed.get("actual_source_pre_ACTION5_bar_positions")
            row["native_precommit_displacement_matches"]=(
                None if not boxes else
                all(boxes[b]["actual_native_bbox"]==[
                    positions[k]*4, Y[k]*4,
                    positions[k]*4+WIDTHS[k]*4-1,Y[k]*4+3
                ] for k,b in enumerate(BARS))
            )
            original_rows.append(row)
            for phase,frame in raw.items():
                arrays["%s_%s_%s"%(name,witness,phase)]=frame
    summary={
        "kind":"ORIGINAL_SP80_STAGE2_FINITE_SCREEN_PATH_PROPOSAL_AND_NATIVE_FALSIFICATION",
        "immutable_screen_source":"Original native SDK run #39461857154, observed level2 source root SHA256 b23d0e2243bc716d36e8602c7d30758a687250f142263510d2bc36432b5f35b4",
        "source_frame_cell_size":4,
        "source_observed_initial_x_cells":ROOT,
        "source_observed_top_notch_x_cells":TOP_NOTCH_X,
        "source_observed_emitters_x_cells":SOURCE_X,
        "frozen_candidate_plan":PROGRAMS,
        "genuine_original_SDK_game_resets":len(original_rows),
        "source_original_official_level3_or_WIN":sum(int(r["source_level3_or_WIN"]) for r in original_rows),
        "source_dispositions":dict(Counter(r["source_stage2_control_disposition"] for r in original_rows)),
        "authentic_native_geometry_match":sum(int(r["native_precommit_displacement_matches"] is True) for r in original_rows),
        "source_successes":[{"candidate":r["frozen_level2_control"],"witness":r["witness"],
                             "level":r["original_source_final_level"],"state":r["original_source_final_state"]}
                            for r in original_rows if r["source_level3_or_WIN"]],
        "original_source_per_game_rows":original_rows,
        "limits":"Finite screen path proxy has NOT been independently established as genuine original fluid mechanics. Native screens/actions/clicks/full returned SDK frames are source; source level>=3 or WIN alone is progress. No F3 source mapping or six-level WIN claimed.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_FINITE_SOURCE_CONTRAST "+json.dumps({
       k:v for k,v in summary.items()
       if k not in ("original_source_per_game_rows","frozen_candidate_plan")
    },sort_keys=True))
    for r in original_rows:
        if r["source_level3_or_WIN"]:
            print("GENUINE_ORIGINAL_SDK_LEVEL3_ADVANCE "+json.dumps({
              "candidate":r["frozen_level2_control"],
              "native_word":r["frozen_level2_action_word"],
              "source_level":r["original_source_final_level"],
              "witness":r["witness"]
            },sort_keys=True))
if __name__=="__main__":main()
