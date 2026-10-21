"""Original SP80 level4: select and MOVE the native L-shaped lower piece.

Direct inspection of authentic original SDK source artifact #12355888555
(produced in native run #39624132483) identified palette15, 27px
L-shaped source region with bbox x32..37,y41..46 in the official
level4 entry image. The previous inventory clicked (34,42), and the
original SDK changed ALL 27 pixels to selection palette9. But it
immediately poured, never testing a genuine ACTION1..4 movement of
that distinct selected lower L-shaped component.

Prior stage4 runs #39625230030 and #39627719334 preserved three
visually full upper cup regions with original right-middle bar LEFT1;
the left lateral cup [5,35,10,43] remained unfilled despite several
upper/middle horizontal and height tests.

This finite original-source SDK experiment holds that observed three-
cup upper configuration and prospectively varies only the true native
lower L-shaped selection movement: LEFT1..8, RIGHT1..3, UP1..3,
DOWN1..3, and a handful of coupled moves. Measure actual selected
piece bboxes after each actual SDK step, per-cup original animation
frames, source contact, and official levels. No guessed hidden physics
and no independent implementation. Only levels_completed>=5 / WIN.
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

UPPER_THREE="6@46,33 3" # genuine SDK native three-upper-cup response
LOWER_L="6@34,42"
CUPS={
    "left_lateral":(5,35,10,43),
    "upper_left":(17,5,25,10),
    "upper_middle":(35,5,43,10),
    "upper_right":(47,5,55,10),
}
ROWS=(17,20,23,26,29,32,35,38,41,44,47,50,53,56)

def program(word,upper=UPPER_THREE):
    return " ".join((upper,LOWER_L,word,"5")).strip()

FROZEN=(
    ("L_click_only"," ".join((UPPER_THREE,LOWER_L,"5"))),
    *((f"L_left{k}",program(" ".join(["3"]*k))) for k in range(1,9)),
    *((f"L_right{k}",program(" ".join(["4"]*k))) for k in range(1,4)),
    *((f"L_up{k}",program(" ".join(["1"]*k))) for k in range(1,4)),
    *((f"L_down{k}",program(" ".join(["2"]*k))) for k in range(1,4)),
    ("L_left3_up1",program("3 3 3 1")),
    ("L_left3_down1",program("3 3 3 2")),
    ("L_left5_up1",program("3 3 3 3 3 1")),
    ("L_left5_down1",program("3 3 3 3 3 2")),
    ("L_up1_left5",program("1 3 3 3 3 3")),
    ("L_down1_left5",program("2 3 3 3 3 3")),
)
assert len(FROZEN)==24==len({x for x,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(word)[-1][0]==5 and sum(a==5 for a,xy in parse_plan(word))==1
    and len(parse_plan(word))<=18
    and all(xy is not None for a,xy in parse_plan(word) if a==6)
    for name,word in FROZEN
)

def selected_mask_readout(frame):
    return [{"palette":c["palette"],"bbox":c["bbox"],"pixels":c["pixels"]}
            for c in color_components(frame)
            if c["palette"] in (9,15) and 18<=c["bbox"][1]<=58]

def source_visual(root,pre,frames):
    if root.shape!=(64,64) or pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Actual original SDK source frame stack required")
    original_cup_counts={
        name:int(np.count_nonzero(root[y0:y1+1,x0:x1+1]==11))
        for name,(x0,y0,x1,y1) in CUPS.items()
    }
    if any(value!=45 for value in original_cup_counts.values()):
        raise AssertionError("Genuine stage4 source root cup pixels changed")
    first_full={k:None for k in CUPS}
    max13={k:0 for k in CUPS}
    new6_side={str(y):None for y in ROWS}
    new6_in_cup=None
    for t,frame in enumerate(frames):
        new6=(pre!=6)&(frame==6)
        for y in ROWS:
            xs=np.flatnonzero(new6[y,2:20])+2
            if xs.size and new6_side[str(y)] is None:
                new6_side[str(y)]={"original_frame":t,"original_native_palette6_new_x":list(map(int,xs))}
        if new6_in_cup is None and new6[35:44,5:11].any():
            ys,xs=np.nonzero(new6[35:44,5:11])
            new6_in_cup={"original_frame":t,"original_native_new6_yx":[[int(y+35),int(x+5)] for y,x in zip(ys,xs)]}
        for name,(x0,y0,x1,y1) in CUPS.items():
            count=int(np.count_nonzero(
                (root[y0:y1+1,x0:x1+1]==11)
                &(frame[y0:y1+1,x0:x1+1]==13)
            ))
            max13[name]=max(max13[name],count)
            if count==45 and first_full[name] is None:first_full[name]=t
    return {
        "native_original_prepour_source_blake2b16":hash_frame(pre),
        "native_original_pour_final_source_blake2b16":hash_frame(frames[-1]),
        "native_original_source_frame_count":len(frames),
        "real_original_cup_first_full_frames":first_full,
        "real_original_cup_max_color13_pixels":max13,
        "original_source_lateral_cup_first_new_color6":new6_in_cup,
        "original_source_new_color6_near_left_by_y":new6_side,
        "source_prepour_selected_regions":selected_mask_readout(pre),
        "scope":"Source pixels are measured original SDK frames, not a proven fluid model or native level objective.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    records=[];arrays={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,stage1_word in STAGE1_WITNESSES:
            sdk,stacks=run_case(case,witness,stage1_word,word)
            root=stacks["entry3_34"][-1]
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            pour=stacks["stage4_"+str(n)]
            pre=stacks.get("stage4_"+str(n-1),stacks["entry3_34"])[-1]
            measured=source_visual(root,pre,pour)
            step_records=[
                {"original_sdk_step":ev["index"],
                 "actual_original_action":ev["genuine_original_action"],
                 "real_original_click_xy":ev["real_native_click_xy"],
                 "true_native_pixel_at_click":ev["original_source_pixel_before_click"],
                 "real_source_before_hash":ev["source_frame_before_blake2b16"],
                 "real_source_after_hash":ev["source_frame_after_blake2b16"],
                 "native_actual_selected_regions":selected_mask_readout(stacks["stage4_"+str(ev["index"])][-1]),
                }
                for ev in sdk["genuine_original_stage4_action_ledger"]
                if ev["genuine_original_action"] in (1,2,3,4,6)
            ]
            if not any(z["real_original_click_xy"]==[34,42] and z["true_native_pixel_at_click"]==15 for z in step_records):
                raise AssertionError("Did not actually click original lower palette15 L-shaped piece")
            row={
                "precommitted_original_source_case":case,
                "independent_original_native_witness":witness,
                "real_original_sdk_level4_word":word,
                "official_original_sdk_final_level":sdk["true_original_sdk_final_level"],
                "official_original_sdk_final_state":sdk["true_original_sdk_final_state"],
                "native_official_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "native_original_L_selection_motion":step_records,
                "original_returned_source_visuals":measured,
                "actual_original_source_action_receipts":sdk["genuine_original_stage4_action_ledger"],
            }
            records.append(row)
            for k,a in stacks.items():arrays[f"{case}_{witness}_{k}"]=a
            print("ORIGINAL_SP80_LOWER_L_SHAPED_CASE "+json.dumps({
                "case":case,"witness":witness,
                "official_level":row["official_original_sdk_final_level"],
                "official_state":row["official_original_sdk_final_state"],
                "selection_motion":step_records,
                "source":measured
            },sort_keys=True),flush=True)
    if len(records)!=48 or len(roots)!=1:
        raise AssertionError("True original level4 independent resets missing")
    for case,_ in FROZEN:
        pair=[x for x in records if x["precommitted_original_source_case"]==case]
        if len(pair)!=2 or (
            pair[0]["official_original_sdk_final_level"]!=pair[1]["official_original_sdk_final_level"]
            or pair[0]["official_original_sdk_final_state"]!=pair[1]["official_original_sdk_final_state"]
            or pair[0]["native_original_L_selection_motion"]!=pair[1]["native_original_L_selection_motion"]
            or pair[0]["original_returned_source_visuals"]!=pair[1]["original_returned_source_visuals"]
        ): raise AssertionError("Independent genuine original SDK witness disagreement "+case)
    successes=[
        {"case":r["precommitted_original_source_case"],"witness":r["independent_original_native_witness"],
         "real_word":r["real_original_sdk_level4_word"],"official_level":r["official_original_sdk_final_level"],
         "official_state":r["official_original_sdk_final_state"]}
        for r in records if r["native_official_level5_or_WIN"]
    ]
    lateral=[
        {"case":r["precommitted_original_source_case"],"witness":r["independent_original_native_witness"],
         "color13_pixels":r["original_returned_source_visuals"]["real_original_cup_max_color13_pixels"]["left_lateral"]}
        for r in records if r["original_returned_source_visuals"]["real_original_cup_max_color13_pixels"]["left_lateral"]>0
    ]
    result={
        "kind":"TRUE_ORIGINAL_SP80_LEVEL4_LOWER_L_SHAPED_SOURCE_SELECTION_MOVEMENT",
        "authentic_original_antecedent_run":39624132483,
        "original_native_fresh_sdk_resets":len(records),
        "prospectively_frozen_genuine_stage4_words":FROZEN,
        "true_original_sdk_level4_root_blake2b16":next(iter(roots)),
        "official_native_level5_or_WIN_count":len(successes),
        "original_official_level5_cases":successes,
        "original_lateral_left_cup_any_source_color13":lateral,
        "native_original_level_histogram":dict(Counter(str(x["official_original_sdk_final_level"]) for x in records)),
        "native_original_state_histogram":dict(Counter(str(x["official_original_sdk_final_state"]) for x in records)),
        "complete_source_native_evidence":records,
        "limitations":"Native returned frame/selection observations only; no presumed hidden physics, no visual WIN substitutes. Full source actions and pixels preserved.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_LOWER_L_SHAPED_SUMMARY "+json.dumps({
        k:v for k,v in result.items()
        if k not in ("prospectively_frozen_genuine_stage4_words","complete_source_native_evidence")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
