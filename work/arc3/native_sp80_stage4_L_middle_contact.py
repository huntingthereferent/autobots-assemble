"""Original SP80 SDK level4: adjacent middle-bar contact with four-cup L pose.

Authentic original run #39629422793 showed genuine source L-shaped
selected component LEFT5/UP1 at x17..22,y38..43 fills four cup
color11->13 windows, but original x2..4 left border source flashes
palette1->14 starting ACTION5 animation frame12. Native SDK stayed
level4. Raising the L one further step or shifting it left makes at
least one cup visibly unfilled and suppresses that border event.

This is a different actual native source intervention: HOLD the L
four-cup pose, and vary the adjacent separate left-middle red
27-pixel piece (original bbox x20..28,y32..34). That piece is
selectable by genuine ACTION6 at x24,y33. Test small upper/side
contact changes both BEFORE and AFTER moving the L; all selected
source changes are measured, never inferred object identity.
Only genuine original SDK level>=5 or WIN is progress.
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

RIGHT="6@46,33 3"
L="6@34,42 3 3 3 3 3 1"
MID_CLICK="6@24,33"
CUPS={
    "lateral_left":(5,35,10,43),
    "upper_left":(17,5,25,10),
    "upper_middle":(35,5,43,10),
    "upper_right":(47,5,55,10),
}
BORDERS={
    "left":(slice(2,62),slice(2,5)),
    "right":(slice(2,62),slice(59,62)),
    "top":(slice(2,5),slice(2,62)),
    "bottom":(slice(59,62),slice(2,62)),
}
def word(before=None,after=None,right=RIGHT,upper=""):
    def select(moves):
        return " ".join(x for x in (MID_CLICK,moves) if x is not None and x!="")
    parts=[right]
    if before is not None:parts.append(select(before))
    parts.append(L)
    if after is not None:parts.append(select(after))
    if upper:parts.append(upper)
    parts.append("5")
    return " ".join(parts)

PRE=(
    ("middle_pre_left1","3"),
    ("middle_pre_left2","3 3"),
    ("middle_pre_left3","3 3 3"),
    ("middle_pre_right1","4"),
    ("middle_pre_right2","4 4"),
    ("middle_pre_up1","1"),
    ("middle_pre_up2","1 1"),
    ("middle_pre_down1","2"),
    ("middle_pre_down2","2 2"),
    ("middle_pre_up1_left1","1 3"),
    ("middle_pre_up1_left2","1 3 3"),
    ("middle_pre_down1_left1","2 3"),
    ("middle_pre_down1_left2","2 3 3"),
    ("middle_pre_left2_up1","3 3 1"),
    ("middle_pre_left2_down1","3 3 2"),
)
POST=(
    ("middle_post_left1","3"),
    ("middle_post_left2","3 3"),
    ("middle_post_right1","4"),
    ("middle_post_up1","1"),
    ("middle_post_down1","2"),
)
FROZEN=(
    ("four_cup_L_control",word()),
    ("middle_click_before_L",word(before="")),
    *((name,word(before=moves)) for name,moves in PRE),
    *((name,word(after=moves)) for name,moves in POST),
    ("middle_pre_left1_upper_left1",word(before="3",upper="6@34,21 3")),
    ("middle_pre_up1_upper_left1",word(before="1",upper="6@34,21 3")),
    ("middle_pre_left1_rightbar_left2",word(before="3",right="6@46,33 3 3")),
)
assert len(FROZEN)==25==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(w)[-1][0]==5 and
           sum(a==5 for a,xy in parse_plan(w))==1 and
           len(parse_plan(w))<=21 and
           all(xy is not None for a,xy in parse_plan(w) if a==6)
           for n,w in FROZEN)

def regions(frame):
    return [
        {"bbox":x["bbox"],"pixels":x["pixels"],"palette":x["palette"]}
        for x in color_components(frame)
        if x["palette"] in (9,15) and 16<=x["bbox"][1]<=53
    ]
def measure(root,pre,frames):
    if (root.shape!=(64,64) or pre.shape!=(64,64) or
        frames.ndim!=3 or frames.shape[1:]!=(64,64)):
        raise AssertionError("Only authentic original SDK 64x64 frames")
    first={k:None for k in CUPS}
    max_fill={k:0 for k in CUPS}
    boundary_first={k:None for k in BORDERS}
    boundary_episodes={k:[] for k in BORDERS}
    active_previous={k:False for k in BORDERS}
    first_lateral_new6=None
    for t,f in enumerate(frames):
        blue=(pre!=6)&(f==6)
        if first_lateral_new6 is None and blue[35:44,5:11].any():
            ys,xs=np.nonzero(blue[35:44,5:11])
            first_lateral_new6={"frame":t,"native_source_yx":[[int(y+35),int(x+5)] for y,x in zip(ys,xs)]}
        for k,(x0,y0,x1,y1) in CUPS.items():
            original=(root[y0:y1+1,x0:x1+1]==11)
            n=int(np.count_nonzero(original&(f[y0:y1+1,x0:x1+1]==13)))
            if int(original.sum())!=45:raise AssertionError("Original stage4 cup changed")
            max_fill[k]=max(max_fill[k],n)
            if n==45 and first[k] is None:first[k]=t
        for k,(ys,xs) in BORDERS.items():
            mask=pre[ys,xs]!=f[ys,xs]
            active=bool(mask.any())
            if active and not active_previous[k]:boundary_episodes[k].append(t)
            active_previous[k]=active
            if active and boundary_first[k] is None:
                prev=pre[ys,xs][mask]
                now=f[ys,xs][mask]
                pairs,num=np.unique(np.stack((prev,now),axis=1),axis=0,return_counts=True)
                boundary_first[k]={
                    "frame":t,"changed_source_pixels":int(mask.sum()),
                    "native_palette_transitions":[[int(v[0]),int(v[1]),int(c)] for v,c in zip(pairs,num)]
                }
    return {
        "original_sdk_prepour_blake2b16":hash_frame(pre),
        "original_sdk_pour_final_blake2b16":hash_frame(frames[-1]),
        "native_returned_pour_frame_count":len(frames),
        "real_original_source_first_cup_full_frames":first,
        "real_original_source_max_cup_pixels_to13":max_fill,
        "real_original_left_lateral_new_palette6":first_lateral_new6,
        "original_first_source_boundary_change":boundary_first,
        "original_border_change_episode_frames":boundary_episodes,
        "original_prepour_selected_components":regions(pre),
        "limits":"These are original source pixel observations, not decoded engine physics or independent success flags.",
    }
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    rows=[];native_stacks={};roots=set()
    for case,program in FROZEN:
        parts=parse_plan(program)
        for witness,entry in STAGE1_WITNESSES:
            result,frames=run_case(case,witness,entry,program)
            roots.add(result["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=frames["entry3_34"][-1]
            prior=frames.get("stage4_"+str(len(parts)-1),frames["entry3_34"])[-1]
            original_returned=frames["stage4_"+str(len(parts))]
            obs=measure(root,prior,original_returned)
            selection_steps=[
                {
                    "index":event["index"],
                    "actual_native_action":event["genuine_original_action"],
                    "actual_original_click":event["real_native_click_xy"],
                    "real_source_click_pixel":event["original_source_pixel_before_click"],
                    "real_source_frame_sha":event["source_frame_after_blake2b16"],
                    "source_returned_selected_regions":regions(frames["stage4_"+str(event["index"])][-1]),
                }
                for event in result["genuine_original_stage4_action_ledger"]
                if event["genuine_original_action"] in (1,2,3,4,6)
            ]
            if case!="four_cup_L_control" and not any(
                x["actual_original_click"]==[24,33] for x in selection_steps
            ):
                raise AssertionError("Original independent middle bar never clicked")
            row={
                "precommitted_native_stage4_case":case,
                "true_source_independent_entry_witness":witness,
                "actual_original_sdk_stage4_word":program,
                "original_sdk_official_final_level":result["true_original_sdk_final_level"],
                "original_sdk_official_final_state":result["true_original_sdk_final_state"],
                "official_native_level5_or_WIN":result["official_original_level5_or_WIN"],
                "actual_original_stage4_source_metrics":obs,
                "actual_native_source_selected_bar_steps":selection_steps,
                "genuine_original_native_action_receipts":result["genuine_original_stage4_action_ledger"],
            }
            rows.append(row)
            for phase,stack in frames.items():
                native_stacks[f"{case}_{witness}_{phase}"]=stack
            print("ORIGINAL_SP80_L_MIDDLE_CONTACT_CASE "+json.dumps({
                "case":case,"witness":witness,"level":row["original_sdk_official_final_level"],
                "state":row["original_sdk_official_final_state"],
                "observed":obs,
                "actual_native_selected_move":selection_steps,
            },sort_keys=True),flush=True)
    if len(rows)!=50 or len(roots)!=1:
        raise AssertionError("Missing original SDK independent level4 entries")
    for case,_ in FROZEN:
        same=[x for x in rows if x["precommitted_native_stage4_case"]==case]
        if len(same)!=2 or (
            same[0]["original_sdk_official_final_level"]!=same[1]["original_sdk_official_final_level"]
            or same[0]["original_sdk_official_final_state"]!=same[1]["original_sdk_official_final_state"]
            or same[0]["actual_original_stage4_source_metrics"]!=same[1]["actual_original_stage4_source_metrics"]
            or same[0]["actual_native_source_selected_bar_steps"]!=same[1]["actual_native_source_selected_bar_steps"]
        ):
            raise AssertionError("Genuine independent SDK source difference "+case)
    advances=[
        {"case":r["precommitted_native_stage4_case"],
         "witness":r["true_source_independent_entry_witness"],
         "original_word":r["actual_original_sdk_stage4_word"],
         "official_level":r["original_sdk_official_final_level"],
         "official_state":r["original_sdk_official_final_state"]}
        for r in rows if r["official_native_level5_or_WIN"]
    ]
    fours=[
        {"case":r["precommitted_native_stage4_case"],
         "witness":r["true_source_independent_entry_witness"],
         "left_border":r["actual_original_stage4_source_metrics"]["original_first_source_boundary_change"]["left"]}
        for r in rows if all(v==45 for v in r["actual_original_stage4_source_metrics"]["real_original_source_max_cup_pixels_to13"].values())
    ]
    summary={
        "kind":"GENUINE_SP80_STAGE4_L_SHAPED_FOUR_CUP_ADJACENT_MIDDLE_BAR_CONTACT",
        "antecedent_original_native_run":39629422793,
        "genuine_original_independent_sdk_games":len(rows),
        "precommitted_original_stage4_words":FROZEN,
        "original_native_stage4_entry_blake2b16":next(iter(roots)),
        "true_original_sdk_level5_or_WIN_count":len(advances),
        "real_sdk_original_level5_witnesses":advances,
        "observed_four_visual_source_cups":fours,
        "official_original_level_histogram":dict(Counter(str(r["original_sdk_official_final_level"]) for r in rows)),
        "official_original_state_histogram":dict(Counter(str(r["original_sdk_official_final_state"]) for r in rows)),
        "original_sdk_all_action_and_frame_receipts":rows,
        "limitations":"Only genuine SDK level>=5 or WIN proves progress. No physical engine conjecture or proxy cup test. Native source arrays preserved in NPZ.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**native_stacks)
    print("ORIGINAL_SP80_L_MIDDLE_CONTACT_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("precommitted_original_stage4_words","original_sdk_all_action_and_frame_receipts")
    },sort_keys=True),flush=True)
if __name__=="__main__":
    main()
