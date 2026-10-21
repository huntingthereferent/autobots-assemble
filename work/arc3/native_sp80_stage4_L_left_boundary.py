"""True original SP80 level4: all four visible cups versus left spill boundary.

Original SDK run #39628603248 (PR #372) discovered that the native
27-pixel selectable L-shaped component at source x32..37/y41..46,
when moved LEFT5/UP1, produces source palette11->13 full-color
transitions in ALL FOUR level4 cups (frames lateral11, upper-left21,
upper-middle23, upper-right21). Both independent source witnesses
reproduced it, but official SDK level remained4 NOT_FINISHED.

Independent direct raw source NPZ inspection located a new genuine
boundary: at original animation frame12, x2..4 along the left side
changes source palette1->14 and flashes repeatedly (frames12,26,28,30).
It starts immediately after the new lateral cup reaches visual-full
frame11. Colors are source observations, not a proven hidden loss rule.

Test specifically the L-shaped piece's neighboring original positions
LEFT4..8 / UP1..3, click/move-order controls and narrowly coupled
upper bars. Record native SDK official level5/WIN as the only success,
source four-cup frames and actual left/right/top/bottom palette14 border
events as correlated OBSERVATIONS, not engine-physics claims.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

RIGHT3C="6@46,33 3"
L_CLICK="6@34,42"
CUP_BOXES={
    "left_lateral":(5,35,10,43),
    "upper_left":(17,5,25,10),
    "upper_middle":(35,5,43,10),
    "upper_right":(47,5,55,10),
}
def word(left_count,up_count,reverse=False,right=RIGHT3C,top=""):
    moves=([1]*up_count+[3]*left_count) if reverse else ([3]*left_count+[1]*up_count)
    return " ".join(str(x) for x in [right,L_CLICK,*moves,top,"5"] if str(x).strip())

FROZEN=(
    *(
        (f"L_left{k}_up{u}",word(k,u))
        for k in (4,5,6,7,8)
        for u in (1,2,3)
    ),
    ("L_left5_held_height",word(5,0)),
    ("L_left5_down1"," ".join((RIGHT3C,L_CLICK,"3 3 3 3 3 2","5"))),
    *((f"L_up1_then_left{k}",word(k,1,True)) for k in (4,5,6)),
    ("L_left5_up1_rightbar_left2",word(5,1,right="6@46,33 3 3")),
    ("L_left6_up1_rightbar_left2",word(6,1,right="6@46,33 3 3")),
    ("L_left5_up1_topbar_left1",word(5,1,top="6@34,21 3")),
    ("L_left6_up1_topbar_left1",word(6,1,top="6@34,21 3")),
)
assert len(FROZEN)==24==len({name for name,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(w)[-1][0]==5
    and sum(a==5 for a,xy in parse_plan(w))==1
    and len(parse_plan(w))<=19
    and all(xy is not None for a,xy in parse_plan(w) if a==6)
    for _,w in FROZEN
)

def chosen(frame):
    return [{"bbox":c["bbox"],"pixels":c["pixels"]}
            for c in color_components(frame)
            if c["palette"]==9 and c["bbox"][1]>=23 and c["bbox"][1]<=56]

def source_metrics(root,pre,frames):
    if root.shape!=(64,64) or pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Real original SDK source image arrays required")
    counts={n:int(np.count_nonzero(root[y0:y1+1,x0:x1+1]==11))
            for n,(x0,y0,x1,y1) in CUP_BOXES.items()}
    if any(v!=45 for v in counts.values()):raise AssertionError("Level4 source root is not same 4 cups")
    first_full={n:None for n in CUP_BOXES}
    max_fill={n:0 for n in CUP_BOXES}
    boundary_first={n:None for n in ("left","right","top","bottom")}
    boundary_episode={n:[] for n in boundary_first}
    last_changed={n:False for n in boundary_first}
    region={
        "left":(slice(2,62),slice(2,5)),
        "right":(slice(2,62),slice(59,62)),
        "top":(slice(2,5),slice(2,62)),
        "bottom":(slice(59,62),slice(2,62)),
    }
    first_lateral_blue=None
    all_four=None
    for t,frame in enumerate(frames):
        new6=(pre!=6)&(frame==6)
        if first_lateral_blue is None and new6[35:44,5:11].any():
            ys,xs=np.nonzero(new6[35:44,5:11])
            first_lateral_blue={"frame":t,"native_yx_samples":[[int(y+35),int(x+5)] for y,x in zip(ys,xs)][:100]}
        for name,(x0,y0,x1,y1) in CUP_BOXES.items():
            amount=int(np.count_nonzero(
                (root[y0:y1+1,x0:x1+1]==11)&
                (frame[y0:y1+1,x0:x1+1]==13)
            ))
            max_fill[name]=max(max_fill[name],amount)
            if amount==45 and first_full[name] is None:first_full[name]=t
        if all_four is None and all(x is not None for x in first_full.values()):
            # Earliest all-four-ever-full is a timing upper bound only.
            all_four=t
        for name,(ys,xs) in region.items():
            changed=(pre[ys,xs]!=frame[ys,xs])
            active=bool(changed.any())
            if active and not last_changed[name]:boundary_episode[name].append(t)
            last_changed[name]=active
            if active and boundary_first[name] is None:
                pairs,num=np.unique(np.stack((pre[ys,xs][changed],frame[ys,xs][changed]),axis=1),axis=0,return_counts=True)
                boundary_first[name]={
                    "original_source_frame":t,
                    "source_changed_pixels":int(changed.sum()),
                    "actual_palette_transitions":[[int(a),int(b),int(n)] for (a,b),n in zip(pairs,num)],
                }
    return {
        "original_sdk_source_prepour_blake2b16":hash_frame(pre),
        "original_sdk_source_pour_end_blake2b16":hash_frame(frames[-1]),
        "original_sdk_returned_frames":len(frames),
        "observed_cup_first_full_frame":first_full,
        "observed_cup_max_palette11to13_pixels":max_fill,
        "first_native_frame_all_cups_ever_full":all_four,
        "first_source_color6_at_lateral_cup":first_lateral_blue,
        "original_boundary_region_first_change":boundary_first,
        "observed_boundary_region_change_episodes":boundary_episode,
        "pre_original_sdk_selected_object_bbox":chosen(pre),
        "limits":"All cup/boundary masks are observations of actual SDK pixel arrays; only SDK level>=5/WIN proves advancement.",
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows=[];arrays={};roots=set()
    for case,program in FROZEN:
        length=len(parse_plan(program))
        for witness,entry in STAGE1_WITNESSES:
            result,stacks=run_case(case,witness,entry,program)
            roots.add(result["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=stacks["entry3_34"][-1]
            prior=stacks.get("stage4_"+str(length-1),stacks["entry3_34"])[-1]
            frames=stacks["stage4_"+str(length)]
            source=source_metrics(root,prior,frames)
            row={
                "predeclared_native_source_case":case,
                "genuine_original_independent_witness":witness,
                "true_original_sdk_stage4_word":program,
                "actual_original_sdk_final_level":result["true_original_sdk_final_level"],
                "actual_original_sdk_final_state":result["true_original_sdk_final_state"],
                "official_stage5_or_WIN":result["official_original_level5_or_WIN"],
                "original_source_actual_frame_measures":source,
                "genuine_sdk_stage4_action_receipts":result["genuine_original_stage4_action_ledger"],
            }
            rows.append(row)
            for phase,st in stacks.items():arrays[f"{case}_{witness}_{phase}"]=st
            print("ORIGINAL_SP80_LEFT_BOUNDARY_CASE "+json.dumps({
                "case":case,"witness":witness,
                "native_level":row["actual_original_sdk_final_level"],
                "native_state":row["actual_original_sdk_final_state"],
                "observed_original_source":source,
            },sort_keys=True),flush=True)
    if len(rows)!=48 or len(roots)!=1:
        raise AssertionError("Original stage4 independent source replays missing")
    for case,_ in FROZEN:
        pair=[r for r in rows if r["predeclared_native_source_case"]==case]
        if len(pair)!=2 or (
            pair[0]["actual_original_sdk_final_level"]!=pair[1]["actual_original_sdk_final_level"]
            or pair[0]["actual_original_sdk_final_state"]!=pair[1]["actual_original_sdk_final_state"]
            or pair[0]["original_source_actual_frame_measures"]!=pair[1]["original_source_actual_frame_measures"]
        ):raise AssertionError("Original source A/B mismatch "+case)
    wins=[
        {"case":r["predeclared_native_source_case"],
         "witness":r["genuine_original_independent_witness"],
         "actual_word":r["true_original_sdk_stage4_word"],
         "official_level":r["actual_original_sdk_final_level"],
         "official_state":r["actual_original_sdk_final_state"]}
        for r in rows if r["official_stage5_or_WIN"]
    ]
    visually_four=[
        {"case":r["predeclared_native_source_case"],"witness":r["genuine_original_independent_witness"],
         "first_boundary_changes":r["original_source_actual_frame_measures"]["original_boundary_region_first_change"]}
        for r in rows if all(v==45 for v in r["original_source_actual_frame_measures"]["observed_cup_max_palette11to13_pixels"].values())
    ]
    summary={
        "kind":"GENUINE_SP80_LEVEL4_L_SHAPED_PIECE_LEFT_BOUNDARY_VERSUS_ALL_CUPS",
        "original_native_antecedent_run":39628603248,
        "true_original_sdk_reset_games":len(rows),
        "prospectively_frozen_source_words":FROZEN,
        "genuine_source_level4_entry_blake2b16":next(iter(roots)),
        "native_original_level5_or_WIN_count":len(wins),
        "native_official_progress_witnesses":wins,
        "four_source_visually_full_cups_with_boundary_signals":visually_four,
        "original_sdk_final_level_counts":dict(Counter(str(r["actual_original_sdk_final_level"]) for r in rows)),
        "original_sdk_final_state_counts":dict(Counter(str(r["actual_original_sdk_final_state"]) for r in rows)),
        "complete_true_original_sdk_source_records":rows,
        "scope":"No engine physics/model, no image-only win. Only genuine original SDK official level>=5/WIN qualifies, with native frame/action evidence.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_LEFT_BOUNDARY_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("prospectively_frozen_source_words","complete_true_original_sdk_source_records")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
