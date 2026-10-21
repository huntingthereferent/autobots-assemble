"""Original SP80 level4: what survives a failed pour and can a second pour advance?

The verified original level4 source SDK run #39628603248 produced a
complete visual four-cup response with L LEFT5/UP1, but native SDK
remained at level4 NOT_FINISHED. Its actual final ACTION5 frame
returns cup11 colors and removes fluid6 while changing selected/
bar geometry from the pre-pour frame.

This prospectively frozen experiment is not another static movement
sweep. It submits genuine *second* and *third* ACTION5 inputs in the
SAME original SDK game after the first failed pour and records the
actual official state, legal actions, source frame resets and possible
carryover. It also compares first three-cup then four-cup intervention,
and failed four-cup then a new selected-object movement.

Only SDK levels_completed >=5 or WIN establishes progress. No
substitute simulator, inferred fluid dynamics or image-only win.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame
from .native_sp80_stage2_source_map import color_components

RIGHT="6@46,33 3"
L="6@34,42 3 3 3 3 3 1"
MID_CLEAN="6@24,33 2 2 2 3 3"
FOUR=RIGHT+" "+L
CLEAN=RIGHT+" "+MID_CLEAN+" "+L
CUP={"lateral":(5,35,10,43),"upper_left":(17,5,25,10),
     "upper_middle":(35,5,43,10),"upper_right":(47,5,55,10)}
FROZEN=(
    ("untouched_double_pour","5 5"),
    ("three_upper_double_pour",RIGHT+" 5 5"),
    ("four_cups_double_pour",FOUR+" 5 5"),
    ("four_cups_triple_pour",FOUR+" 5 5 5"),
    ("clean_three_double_pour",CLEAN+" 5 5"),
    ("four_then_one_native_left",FOUR+" 5 3 5"),
    ("four_then_one_native_up",FOUR+" 5 1 5"),
    ("four_then_click_L",FOUR+" 5 6@34,42 3 5"),
    ("four_then_click_right",FOUR+" 5 6@46,33 3 5"),
    ("four_then_click_middle",FOUR+" 5 6@24,33 1 5"),
    ("three_then_attempt_four",RIGHT+" 5 "+L+" 5"),
    ("four_then_repeat_four",FOUR+" 5 "+FOUR+" 5"),
)
assert len(FROZEN)==12==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(sum(a==5 for a,xy in parse_plan(w)) in (2,3) and
           parse_plan(w)[-1][0]==5 and
           all(xy is not None for a,xy in parse_plan(w) if a==6)
           and len(parse_plan(w))<=32
           for n,w in FROZEN)

def selected(frame):
    return [
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(frame)
        if c["palette"] in (9,15) and 16<=c["bbox"][1]<=55
    ]

def native_pour_readout(root,pre,frames):
    if (root.shape!=(64,64) or pre.shape!=(64,64)
        or frames.ndim!=3 or frames.shape[1:]!=(64,64)):
        raise AssertionError("Require actual original SDK 64x64 source frames")
    first={k:None for k in CUP}
    last=frames[-1]
    max13={k:0 for k in CUP}
    first_left_border=None
    for t,f in enumerate(frames):
        for name,(x0,y0,x1,y1) in CUP.items():
            mask=root[y0:y1+1,x0:x1+1]==11
            if int(mask.sum())!=45:
                raise AssertionError("Original SDK cup root changed")
            count=int(np.count_nonzero(mask & (f[y0:y1+1,x0:x1+1]==13)))
            max13[name]=max(max13[name],count)
            if count==45 and first[name] is None:first[name]=t
        diff=(pre[2:62,2:5]!=f[2:62,2:5])
        if diff.any() and first_left_border is None:
            first_left_border={
                "source_frame":t,
                "changed_native_left_border_pixels":int(diff.sum()),
                "native_new_palette14_from1":int(np.count_nonzero(
                    (pre[2:62,2:5]==1)&(f[2:62,2:5]==14)
                )),
            }
    return {
        "real_sdk_pour_animation_frames":len(frames),
        "original_source_pre_pour_sha":hash_frame(pre),
        "original_source_after_pour_sha":hash_frame(last),
        "original_source_root_sha":hash_frame(root),
        "actual_final_frame_matches_prepour":bool(np.array_equal(pre,last)),
        "actual_final_frame_matches_entry_root":bool(np.array_equal(root,last)),
        "original_source_final_frame_diff_from_prepour":int(np.count_nonzero(last!=pre)),
        "original_source_final_frame_diff_from_entry":int(np.count_nonzero(last!=root)),
        "original_source_final_color6_pixel_count":int(np.count_nonzero(last==6)),
        "original_source_prepour_color6_pixel_count":int(np.count_nonzero(pre==6)),
        "original_source_prepour_selection":selected(pre),
        "original_source_after_pour_selection":selected(last),
        "original_cup_first_full_native_source_frames":first,
        "original_cup_max_palette13_pixels":max13,
        "first_original_source_left_boundary_transition":first_left_border,
        "scope":"Original SDK pixel observation only, NOT success predicate or inferred reset/flow mechanics.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows=[];arrays={};roots=set()
    for case,word in FROZEN:
        native_word=parse_plan(word)
        indices=[i for i,(a,xy) in enumerate(native_word,1) if a==5]
        for witness,entry in STAGE1_WITNESSES:
            actual,frames=run_case(case,witness,entry,word)
            roots.add(actual["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=frames["entry3_34"][-1]
            recorded=[]
            for i in indices:
                # Official SDK can terminate on an actual WIN, in which
                # case future pre-frozen actions were not executed.
                key="stage4_"+str(i)
                if key not in frames:break
                prior=frames["stage4_"+str(i-1)][-1] if i>1 else root
                poured=frames[key]
                event=next(x for x in actual["genuine_original_stage4_action_ledger"]
                           if x["index"]==i)
                recorded.append({
                    "actual_native_step_index":i,
                    "actual_original_sdk_level_before":event["original_sdk_level_before"],
                    "actual_original_sdk_level_after":event["original_sdk_level_after"],
                    "original_native_state_before":event["original_sdk_state_before"],
                    "original_native_state_after":event["original_sdk_state_after"],
                    "real_original_legal_actions_after":event["original_legal_actions_after"],
                    "source_observations":native_pour_readout(root,prior,poured),
                })
            if not recorded:raise AssertionError("No actual original SDK pour")
            record={
                "predeclared_native_trial":case,
                "independent_original_source_witness":witness,
                "genuine_original_sdk_stage4_word":word,
                "planned_native_pour_count":len(indices),
                "actually_returned_native_pour_count":len(recorded),
                "official_source_final_level":actual["true_original_sdk_final_level"],
                "official_source_final_state":actual["true_original_sdk_final_state"],
                "official_level5_or_WIN":actual["official_original_level5_or_WIN"],
                "true_original_sdk_pour_sequence":recorded,
                "original_sdk_genuine_action_receipts":actual["genuine_original_stage4_action_ledger"],
            }
            rows.append(record)
            for name,stack in frames.items():
                arrays[f"{case}_{witness}_{name}"]=stack
            print("ORIGINAL_SP80_SECOND_POUR_CASE "+json.dumps({
                "case":case,"witness":witness,
                "level":record["official_source_final_level"],
                "state":record["official_source_final_state"],
                "actual_pours":record["actually_returned_native_pour_count"],
                "pour_observations":recorded,
            },sort_keys=True),flush=True)
    if len(rows)!=24 or len(roots)!=1:
        raise AssertionError("Missing independently reset original source histories")
    for case,_ in FROZEN:
        pair=[x for x in rows if x["predeclared_native_trial"]==case]
        if len(pair)!=2 or (
            pair[0]["official_source_final_level"]!=pair[1]["official_source_final_level"]
            or pair[0]["official_source_final_state"]!=pair[1]["official_source_final_state"]
            or pair[0]["true_original_sdk_pour_sequence"]!=pair[1]["true_original_sdk_pour_sequence"]
        ):raise AssertionError("Independent original source mismatch "+case)
    advances=[{
        "case":r["predeclared_native_trial"],
        "witness":r["independent_original_source_witness"],
        "real_stage4_word":r["genuine_original_sdk_stage4_word"],
        "native_level":r["official_source_final_level"],
        "native_state":r["official_source_final_state"]}
        for r in rows if r["official_level5_or_WIN"]
    ]
    out={
        "kind":"TRUE_ORIGINAL_SP80_STAGE4_SECOND_POUR_NATIVE_STATE",
        "authentic_original_level4_entrance_run":39624132483,
        "source_first_full_four_cups_run":39628603248,
        "true_independently_reset_original_games":len(rows),
        "prospectively_frozen_native_words":FROZEN,
        "actual_native_level4_root_hash":next(iter(roots)),
        "original_official_level5_or_WIN_count":len(advances),
        "native_actual_stage5_progress_witnesses":advances,
        "original_sdk_level_histogram":dict(Counter(str(x["official_source_final_level"]) for x in rows)),
        "original_sdk_state_histogram":dict(Counter(str(x["official_source_final_state"]) for x in rows)),
        "complete_original_sdk_pour_and_action_receipts":rows,
        "limits":"Only original SDK official levels_completed>=5/WIN proves advancement. Returned source image resets are observations, not inferred hidden state or physics. No other research lanes/licensing modified.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_SECOND_POUR_SUMMARY "+json.dumps({
        k:v for k,v in out.items()
        if k not in ("prospectively_frozen_native_words","complete_original_sdk_pour_and_action_receipts")
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
