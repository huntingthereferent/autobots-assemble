"""Native original SP80 level4: raise left bar, move farther left, then lower.

Original run #39626005057 proved left-middle 27px bar horizontal
movement saturates at x14..22/y32..34 after TWO left moves, but
UP1 then LEFT4 gets the genuine source selected component to
x8..16/y29..31. That elevated pose left the lateral cup
bbox x5..10/y35..43 untouched, in all 44 source-native games.

New falsifiable original-source relationship: return that real
left-middle bar DOWN one, two, three, four native movements *after*
it has achieved the further-left x8..16 position. Measure both actual
SDK per-step selected bboxes AND original returned ACTION5 cup/stream
evidence, not presumed geometry or a fabricated fluid engine.

Original level4 is entered from the exact verified native stage3
winning action word through both independent original source histories.
Only actual SDK levels_completed>=5 or WIN is official progress.
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

RIGHT="6@46,33 3"  # empirically filled three upper source cups
LEFT="6@24,33 "
CUP_BOXES={
    "lateral_left":(5,35,10,43),
    "upper_left":(17,5,25,10),
    "upper_middle":(35,5,43,10),
    "upper_right":(47,5,55,10),
}
def candidate(left_word,right=RIGHT,upper=""):
    return " ".join(x for x in (right,LEFT+left_word,upper,"5") if x)

FROZEN=(
    ("left2_initial_saturation",candidate("3 3")),
    ("up1_left4_elevated_control",candidate("1 3 3 3 3")),
    ("up2_left4_elevated_control",candidate("1 1 3 3 3 3")),
    *(
        (f"up1_left4_down{d}",candidate(" ".join(["1"]+["3"]*4+["2"]*d)))
        for d in (1,2,3,4)
    ),
    *(
        (f"up2_left4_down{d}",candidate(" ".join(["1"]*2+["3"]*4+["2"]*d)))
        for d in (1,2,3,4)
    ),
    *(
        (f"up1_left3_down{d}",candidate(" ".join(["1"]+["3"]*3+["2"]*d)))
        for d in (1,2,3)
    ),
    *(
        (f"left2_up1_left2_down{d}",candidate(" ".join(["3"]*2+["1"]+["3"]*2+["2"]*d)))
        for d in (1,2,3)
    ),
    ("up1_left4_down2_left1",candidate("1 3 3 3 3 2 2 3")),
    ("up1_left4_down2_right1",candidate("1 3 3 3 3 2 2 4")),
    ("up1_left4_down3_left1",candidate("1 3 3 3 3 2 2 2 3")),
    ("up2_left4_down3_left1",candidate("1 1 3 3 3 3 2 2 2 3")),
    ("up1_left4_down2_upper_left1",candidate("1 3 3 3 3 2 2",upper="6@34,21 3")),
    ("up1_left4_down2_rightbar_left2",candidate("1 3 3 3 3 2 2",right="6@46,33 3 3")),
)
assert len(FROZEN)==23==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(word)[-1][0]==5
    and sum(a==5 for a,xy in parse_plan(word))==1
    and len(parse_plan(word))<=17
    and all(xy is not None for a,xy in parse_plan(word) if a==6)
    for _,word in FROZEN
)

def chosen_bar_components(frame):
    return [
        {"bbox":c["bbox"],"pixels":c["pixels"],"palette":c["palette"]}
        for c in color_components(frame)
        if c["palette"]==9 and 18<=c["bbox"][1]<=47
    ]

def source_observations(root,pre,frames):
    if root.shape!=(64,64) or pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Real original SDK 64x64 frames required")
    initial={n:int(np.count_nonzero(root[y0:y1+1,x0:x1+1]==11))
             for n,(x0,y0,x1,y1) in CUP_BOXES.items()}
    if any(v!=45 for v in initial.values()):
        raise AssertionError("Actual level4 source cup geometry changed")
    first_full={n:None for n in CUP_BOXES}
    maximum={n:0 for n in CUP_BOXES}
    source_left_side_first={str(y):None for y in range(23,53,3)}
    earliest_side_blue=None
    for t,frame in enumerate(frames):
        newblue=(pre!=6)&(frame==6)
        for y in range(23,53,3):
            xs=np.flatnonzero(newblue[y,2:19])+2
            if xs.size and source_left_side_first[str(y)] is None:
                source_left_side_first[str(y)]={"frame":t,"source_x":list(map(int,xs))}
        if earliest_side_blue is None and newblue[35:44,5:11].any():
            ys,xs=np.nonzero(newblue[35:44,5:11])
            earliest_side_blue={"frame":t,"source_yx":[[int(y+35),int(x+5)] for y,x in zip(ys,xs)]}
        for name,(x0,y0,x1,y1) in CUP_BOXES.items():
            count=int(np.count_nonzero(
                (root[y0:y1+1,x0:x1+1]==11)&(frame[y0:y1+1,x0:x1+1]==13)
            ))
            maximum[name]=max(maximum[name],count)
            if count==45 and first_full[name] is None:first_full[name]=t
    return {
        "actual_original_sdk_source_prepour_blake2b16":hash_frame(pre),
        "actual_original_sdk_pour_end_blake2b16":hash_frame(frames[-1]),
        "original_sdk_returned_pour_frames":len(frames),
        "native_original_cup_full_visual_frames":first_full,
        "original_max_source_cup_pixels_changed_to13":maximum,
        "left_side_cup_first_new_source_color6":earliest_side_blue,
        "actual_new_palette6_near_left_by_row":source_left_side_first,
        "genuine_source_prepour_selected_components":chosen_bar_components(pre),
        "source_only":"Official SDK level>=5/WIN alone establishes progress. Pixel observations do not prove game physics or goal.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows=[];arrays={};roots=set()
    for name,program in FROZEN:
        steps=parse_plan(program)
        for witness,entry in STAGE1_WITNESSES:
            result,frames=run_case(name,witness,entry,program)
            roots.add(result["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=frames["entry3_34"][-1]
            poured=frames["stage4_"+str(len(steps))]
            pre=frames.get("stage4_"+str(len(steps)-1),frames["entry3_34"])[-1]
            metrics=source_observations(root,pre,poured)
            movements=[
                {
                    "original_sdk_action_index":event["index"],
                    "actual_native_action":event["genuine_original_action"],
                    "actual_native_original_click_xy":event["real_native_click_xy"],
                    "before":event["source_frame_before_blake2b16"],
                    "after":event["source_frame_after_blake2b16"],
                    "original_frame_selected_bboxes":chosen_bar_components(
                        frames["stage4_"+str(event["index"])][-1]
                    ),
                }
                for event in result["genuine_original_stage4_action_ledger"]
                if event["genuine_original_action"] in (1,2,3,4,6)
            ]
            r={
                "prospectively_frozen_case":name,
                "original_native_independent_witness":witness,
                "actual_native_stage4_word":program,
                "official_original_sdk_final_level":result["true_original_sdk_final_level"],
                "official_original_sdk_final_state":result["true_original_sdk_final_state"],
                "original_sdk_advanced_to_level5_or_WIN":result["official_original_level5_or_WIN"],
                "original_sdk_selected_bar_step_movements":movements,
                "genuine_native_source_frame_metrics":metrics,
                "true_stage4_action_receipts":result["genuine_original_stage4_action_ledger"],
            }
            rows.append(r)
            for phase,stack in frames.items():arrays[f"{name}_{witness}_{phase}"]=stack
            print("ORIGINAL_SP80_RAISE_LEFT_RETURN_CASE "+json.dumps({
                "case":name,"witness":witness,
                "native_level":r["official_original_sdk_final_level"],
                "native_state":r["official_original_sdk_final_state"],
                "source":metrics,
                "observed_step_components":movements,
            },sort_keys=True),flush=True)
    if len(rows)!=46 or len(roots)!=1:raise AssertionError("Missing original SDK independent level4 source witness")
    for name,_ in FROZEN:
        pair=[r for r in rows if r["prospectively_frozen_case"]==name]
        if len(pair)!=2 or (
            pair[0]["official_original_sdk_final_level"]!=pair[1]["official_original_sdk_final_level"]
            or pair[0]["official_original_sdk_final_state"]!=pair[1]["official_original_sdk_final_state"]
            or pair[0]["genuine_native_source_frame_metrics"]!=pair[1]["genuine_native_source_frame_metrics"]
            or pair[0]["original_sdk_selected_bar_step_movements"]!=pair[1]["original_sdk_selected_bar_step_movements"]
        ):raise AssertionError("Independent actual original SDK witness mismatch: "+name)
    advances=[
        {"case":r["prospectively_frozen_case"],"witness":r["original_native_independent_witness"],
         "native_stage4_word":r["actual_native_stage4_word"],
         "official_level":r["official_original_sdk_final_level"],
         "official_state":r["official_original_sdk_final_state"]}
        for r in rows if r["original_sdk_advanced_to_level5_or_WIN"]
    ]
    visible_lateral=[
        {"case":r["prospectively_frozen_case"],"witness":r["original_native_independent_witness"],
         "native_lateral_source_color13_pixels":r["genuine_native_source_frame_metrics"]["original_max_source_cup_pixels_changed_to13"]["lateral_left"]}
        for r in rows
        if r["genuine_native_source_frame_metrics"]["original_max_source_cup_pixels_changed_to13"]["lateral_left"]>0
    ]
    summary={
        "kind":"TRUE_ORIGINAL_SP80_STAGE4_RAISED_LEFT_THEN_RETURN_DOWN",
        "antecedent_original_native_run":39626005057,
        "authentic_original_sdk_independent_reset_games":len(rows),
        "prospectively_frozen_stage4_original_sdk_words":FROZEN,
        "original_stage4_native_entry_blake2b16":next(iter(roots)),
        "official_source_level5_or_WIN_count":len(advances),
        "genuine_original_level5_witnesses":advances,
        "source_lateral_cup_any_visual_color_change":visible_lateral,
        "official_original_level_histogram":dict(Counter(str(r["official_original_sdk_final_level"]) for r in rows)),
        "official_original_state_histogram":dict(Counter(str(r["official_original_sdk_final_state"]) for r in rows)),
        "genuine_original_source_receipts":rows,
        "limits":"No private physics speculation, no substitute simulator. Only source SDK levels_completed>=5/WIN proves progression. Full original 64x64 SDK return arrays archived.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_RAISE_LEFT_RETURN_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("prospectively_frozen_stage4_original_sdk_words","genuine_original_source_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
