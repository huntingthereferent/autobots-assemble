"""Genuine SP80 level4 paired source history: MOVE before versus after failed POUR.

Observed original first ACTION5 reselects the right bar (palette9), not a
hypothesized state. On two independently established four-cup source
parents, compare direct right position before ACTION5 with the same
right position reached only AFTER one four-cup ACTION5. Explicitly
reselect upper before second POUR, retain the complete original source
frames and compare terminal pre-pour screens before asking if animation
or official SDK level differs. Does not assume hidden-state equality.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_top_left_source_contrast import source_report
from .native_sp80_legal_pairs import hash_frame
from .native_sp80_multi_select import parse_plan

MID="6@24,33 2 2 2 3 3"
LOWER="6@34,42 3 3 3 1 1"
UPPER="6@34,21 3"
LEFT1=" ".join(("6@46,33 3",MID,LOWER,UPPER,"5"))
LEFT2=" ".join(("6@46,33 3 3",MID,LOWER,UPPER,"5"))
FROZEN=(
    ("direct_LEFT1",LEFT1, "LEFT1",False),
    ("direct_LEFT2",LEFT2, "LEFT2",False),
    ("after_LEFT1_pour_then_LEFT1", LEFT1+" 3 6@34,21 5", "LEFT2",True),
    ("after_LEFT2_pour_then_RIGHT1", LEFT2+" 4 6@34,21 5", "LEFT1",True),
)
ROOT_SEL_RIGHT={"LEFT1":[38,32,52,34],"LEFT2":[35,32,49,34]}
EXPECTED_SOURCE_FULL={
    "LEFT1":{"lateral":13,"top_left":25,"top_middle":21,"top_right":21},
    "LEFT2":{"lateral":13,"top_left":25,"top_middle":23,"top_right":19},
}

def bbox_9(frame):
    ys,xs=np.nonzero(frame==9)
    return [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None

def delta(a,b):
    assert a.shape==b.shape==(64,64)
    ys,xs=np.nonzero(a!=b)
    return {"changed_pixels":int(len(xs)),
       "changed_board_y0_62":int(np.count_nonzero(a[:63]!=b[:63])),
       "changed_bottom_y63":int(np.count_nonzero(a[63]!=b[63])),
       "changed_bbox":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None}

def stack_delta(a,b):
    if a.ndim!=3 or b.ndim!=3 or a.shape[1:]!=(64,64) or b.shape[1:]!=(64,64):
        raise AssertionError("Authentic 64x64 SDK action stacks required")
    count=min(len(a),len(b))
    diffs=np.asarray(a[:count]!=b[:count])
    return {
      "original_frames_a":len(a),"original_frames_b":len(b),
      "aligned_frame_count":count,
      "source_first_differing_frame":next((int(i) for i in range(count) if np.any(diffs[i])),None),
      "source_differing_pixels_total":int(np.count_nonzero(diffs)),
      "source_differing_pixels_visible_y0_62":int(np.count_nonzero(diffs[:,:63])),
      "source_differing_pixels_row63":int(np.count_nonzero(diffs[:,63])),
      "source_differing_color13_mask_pixels":int(sum(
        np.count_nonzero((a[i]==13)!=(b[i]==13)) for i in range(count))),
      "source_differing_color6_mask_pixels":int(sum(
        np.count_nonzero((a[i]==6)!=(b[i]==6)) for i in range(count))),
      "source_last_frame":delta(a[-1],b[-1]),
      "scope":"Frame ordinals aligned only, not physical time."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    arg=p.parse_args()
    rows=[];arrays={};roots=set();pre_map={};stack_map={}
    for name,word,target,history in FROZEN:
        actions=parse_plan(word)
        pour_at=[i for i,(a,xy) in enumerate(actions,1) if a==5]
        if history and (len(pour_at)!=2 or pour_at[-1]!=len(actions) or
                        [a for a,xy in actions[pour_at[0]:]]!=
                        [3 if target=="LEFT2" else 4,6,5]):
            raise AssertionError("Prospective post-first-pour history changed")
        if not history and (pour_at!=[len(actions)]):
            raise AssertionError("Direct source control changed")
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(name,witness,entry,word)
            root=raw["entry3_34"][-1]
            roots.add(hash_frame(root))
            final_index=pour_at[-1]
            pre=raw["stage4_"+str(final_index-1)][-1]
            stack=raw["stage4_"+str(final_index)]
            first=None
            if history:
                first_index=pour_at[0]
                first_frame=raw["stage4_"+str(first_index)][-1]
                selected_first=bbox_9(first_frame)
                expected_from="LEFT1" if target=="LEFT2" else "LEFT2"
                if selected_first!=ROOT_SEL_RIGHT[expected_from]:
                    raise AssertionError("First native failed pour did not select the authentic right source bar")
                after_step=raw["stage4_"+str(first_index+1)][-1]
                after_move=bbox_9(after_step)
                if after_move!=ROOT_SEL_RIGHT[target]:
                    raise AssertionError("Actual selected right bar did not reach the intended target after first pour")
                # Genuine upper selection must be re-established before the second pour.
                if bbox_9(pre)!=[26,20,37,22]:
                    raise AssertionError("Actual upper bar not reselected before second ACTION5")
                first={"native_first_post_pour_selected_right":selected_first,
                       "native_post_pour_move_selected_right":after_move,
                       "native_reselected_upper_bbox":bbox_9(pre),
                       "original_sdk_first_pour_receipt":sdk["genuine_original_stage4_action_ledger"][first_index-1]}
            else:
                if bbox_9(pre)!=[26,20,37,22]:
                    raise AssertionError("Direct first-pour upper bar position changed")
            observed=source_report(root,pre,stack)
            expected=EXPECTED_SOURCE_FULL[target]
            if not history and observed["source_first_full_cups"]!=expected:
                raise AssertionError("Native direct four-cup source control changed")
            last=sdk["genuine_original_stage4_action_ledger"][-1]
            row={"condition":name,"target_right_setting":target,"witness":witness,
                 "has_first_failed_pour_then_right_move":history,
                 "source_program":word,
                 "source_stage4_root_hash":hash_frame(root),
                 "native_final_pre_pour_hash":hash_frame(pre),
                 "native_final_action5_stack_hash":hash_frame(stack[-1]),
                 "original_sdk_end_level":sdk["true_original_sdk_final_level"],
                 "original_sdk_end_state":sdk["true_original_sdk_final_state"],
                 "official_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                 "original_native_final_action5_receipt":last,
                 "native_selected_object_transfer":first,
                 "source_final_pour_observation":observed,
                 "original_native_full_stage4_receipts":sdk["genuine_original_stage4_action_ledger"]}
            rows.append(row)
            pre_map[(name,witness)]=pre.copy()
            stack_map[(name,witness)]=stack.copy()
            for k,v in raw.items():arrays[name+"_"+witness+"_"+k]=v
            print("ARC4_ORDERED_ACTION_CONTRAST "+json.dumps({
                "condition":name,"witness":witness,
                "official_level":row["original_sdk_end_level"],
                "official_state":row["original_sdk_end_state"],
                "observed_first_full":observed["source_first_full_cups"],
                "four_full_at":observed["source_first_four_simultaneous"],
                "right_repositioning":first,
                "native_final_pour_frames":len(stack)},sort_keys=True),flush=True)
    if len(rows)!=8 or len(roots)!=1:
        raise AssertionError("Original independent SDK source root mismatch")
    for case,word,target,history in FROZEN:
        pair=[x for x in rows if x["condition"]==case]
        if len(pair)!=2 or {x["witness"] for x in pair}!={"A","B"}:
            raise AssertionError("Independent source SDK entrance missing")
        for field in ("native_final_pre_pour_hash","native_final_action5_stack_hash",
                      "original_sdk_end_level","original_sdk_end_state",
                      "source_final_pour_observation","native_selected_object_transfer"):
            if pair[0][field]!=pair[1][field]:
                raise AssertionError("Original native A/B mismatch: "+case+"."+field)
    comparisons={}
    for case,target in (("after_LEFT1_pour_then_LEFT1","LEFT2"),
                        ("after_LEFT2_pour_then_RIGHT1","LEFT1")):
        direct="direct_"+target
        pair=[]
        for witness,_ in STAGE1_WITNESSES:
            result={
              "witness":witness,
              "actual_prepour_source_screen":delta(pre_map[(direct,witness)],pre_map[(case,witness)]),
              "original_sdk_source_animation":stack_delta(stack_map[(direct,witness)],stack_map[(case,witness)]),
              "official_levels":[
                next(x["original_sdk_end_level"] for x in rows if x["condition"]==direct and x["witness"]==witness),
                next(x["original_sdk_end_level"] for x in rows if x["condition"]==case and x["witness"]==witness)]}
            pair.append(result)
        if {k:v for k,v in pair[0].items() if k!="witness"} != {k:v for k,v in pair[1].items() if k!="witness"}:
            raise AssertionError("Native source comparative A/B disagreement")
        comparisons[case]={"matched_direct_control":direct,"independent_native_comparison":pair}
    report={"kind":"ORIGINAL_SP80_STAGE4_PREPOUR_VS_POSTPOUR_RIGHT_REPOSITION_ORDER",
            "source_genuine_original_sdk_reset_count":len(rows),
            "frozen_source_native_arms":FROZEN,
            "same_original_sdk_root_hash":next(iter(roots)),
            "native_original_records":rows,
            "native_history_vs_direct_comparisons":comparisons,
            "original_sdk_outcome_counts":dict(Counter(str(x["original_sdk_end_level"]) for x in rows)),
            "official_stage5_or_WIN_count":sum(int(x["official_level5_or_WIN"]) for x in rows),
            "boundary":"A post-failed-pour right-bar movement followed by reselecting upper bar is an authentic alternative action history. Match only after actual source frames verify position; visible equality cannot prove private SDK state equality."}
    arg.out.parent.mkdir(parents=True,exist_ok=True)
    arg.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(arg.out.with_suffix(".npz"),**arrays)
    print("ARC4_ORDERED_POUR_SOURCE_SUMMARY "+json.dumps({
       "real_sdk_resets":len(rows),
       "official_level_count":report["original_sdk_outcome_counts"],
       "official_stage5_or_WIN_count":report["official_stage5_or_WIN_count"],
       "comparisons":{k:{
          "direct":v["matched_direct_control"],
          "native_prepour_screen":v["independent_native_comparison"][0]["actual_prepour_source_screen"],
          "source_pour_animation":v["independent_native_comparison"][0]["original_sdk_source_animation"],
          "official_levels":v["independent_native_comparison"][0]["official_levels"]}
         for k,v in comparisons.items()},
       "two_independent_original_sdk_witnesses":True},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
