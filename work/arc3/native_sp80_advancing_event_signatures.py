"""Original SP80: compare genuine SDK advancing/nonadvancing ACTION5 events.

No known stage1 game goal is assumed. Prior real stage0 progress:
source level0->1 when selected bar reached x24..43 in tested cases;
stage1 selected-bar alignment/staggered placements all failed to advance.
Study *actual returned images* at the phase transition, not just their
last images or animated frame count.

Freeze six stage0 and six stage1 source programs before game execution,
two fresh native SDK resets each. Save EVERY obs.frame in original NPZ
and exact per-image changed XY/colors via the original source runners.
Catalog color6/9/11/13/14 in the entire image and measured row bands.
The class label is ONLY original SDK levels_completed / WIN.
These are comparisons across different source levels, NOT mechanism,
hidden state identity, decoded HUD, or a level2 solver.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import numpy as np
from .native_sp80_stage0_progress_animation import stage0_original_trial
from .native_sp80_action5_frame_stacks import one
from .native_sp80_legal_pairs import hash_frame
from .native_sp80_multi_select import parse_plan

STAGE0=(
  ("advancing_three_right","4445"),
  ("advancing_with_left_cancel","444435"),
  ("advancing_vertical_up","14445"),
  ("negative_two_right","445"),
  ("negative_three_right_one_left","44435"),
  ("negative_four_right","44445"),
)
STAGE1=(
  ("unmoved","5"),
  ("three_right","4 4 4 5"),
  ("click_lower_right_three","6@32,25 4 4 4 5"),
  ("click_upper_right_three","6@12,17 4 4 4 5"),
  ("click_first_up_right","6@24,37 1 4 5"),
  ("click_two_bars_442","6@12,17 6@32,25 4 4 2 5"),
)
RESETS=2
PALETTE=(6,9,11,13,14)
BANDS=(("upper",0,13),("upper_bar",13,24),
       ("middle_bar",24,36),("lower_bar",36,48),
       ("bottom",48,64))
assert len(STAGE0)==len(STAGE1)==6 and RESETS==2
assert len({n for n,_ in STAGE0})==len(STAGE0)
assert len({n for n,_ in STAGE1})==len(STAGE1)
assert all(set(w)<={"1","2","3","4","5"} and "5" in w
           for _,w in STAGE0)
assert all(parse_plan(w)[-1][0]==5 and
           all(a!=6 or xy is not None for a,xy in parse_plan(w))
           for _,w in STAGE1)


def bbox(a,color):
    y,x=np.nonzero(a==color)
    return ([int(x.min()),int(y.min()),int(x.max()),int(y.max())]
            if len(x) else None)


def image_observation(frame):
    """Count actual source SDK colors in fixed observable pixel rows."""
    result={
        "source_full_original_color_counts":{
          str(c):int(np.count_nonzero(frame==c)) for c in PALETTE},
        "original_native_selected_color9_bbox":bbox(frame,9),
        "source_region_counts":{},
        "top_color6_x_columns":sorted(int(v) for v in
            np.unique(np.nonzero(frame[:13]==6)[1])),
    }
    for name,lower,upper in BANDS:
        region=frame[lower:upper]
        result["source_region_counts"][name]={
            str(c):int(np.count_nonzero(region==c)) for c in PALETTE}
    return result


def stage0_event(trial,raw):
    result=[]
    for action in trial["genuine_source_action_records"]:
        if action.get("native_action")!=5 or "actual_SDK_frame_sequence" not in action:
            continue
        idx=action["original_word_step"]
        stack=raw["action_"+str(idx)]
        before=raw["reset"][-1] if idx==1 else raw["action_"+str(idx-1)][-1]
        assert len(stack)==action["actual_SDK_frame_sequence"]["true_original_returned_frames"]
        result.append({
            "native_phase":"SOURCE_STAGE0",
            "original_action_word_step":idx,
            "native_prelevel":action["pre_SDK_level"],
            "native_postlevel":action["post_SDK_level"],
            "official_native_progress":bool(action["native_SDK_level_increase"] or action["native_SDK_WIN"]),
            "source_state_after":action["post_SDK_state"],
            "actual_returned_source_frames":len(stack),
            "source_preimage_sha256":hash_frame(before),
            "source_preimage_snapshot":image_observation(before),
            "observed_returned_frames":[image_observation(frame) for frame in stack],
            "source_last_image_snapshot":image_observation(stack[-1]),
            "actual_source_frame_ledger":action["actual_SDK_frame_sequence"],
        })
    return result


def stage1_event(trial,raw):
    result=[]
    for action in trial["real_sdk_observation_ledger"]:
        if (action["phase"]!="context" or action["native_action_id"]!=5 or
                "source_animation" not in action):
            continue
        idx=action["phase_action_number"]
        stack=raw["context_"+str(idx)]
        before=raw["entry_6"][-1] if idx==1 else raw["context_"+str(idx-1)][-1]
        assert len(stack)==action["source_animation"]["true_original_returned_frames"]
        result.append({
            "native_phase":"SOURCE_STAGE1",
            "original_action_word_step":idx,
            "native_prelevel":1,
            "native_postlevel":action["original_source_level_after"],
            "official_native_progress":bool(action["original_source_level_after"]>=2 or
                                            action["original_source_state_after"]=="WIN"),
            "source_state_after":action["original_source_state_after"],
            "actual_returned_source_frames":len(stack),
            "source_preimage_sha256":hash_frame(before),
            "source_preimage_snapshot":image_observation(before),
            "observed_returned_frames":[image_observation(frame) for frame in stack],
            "source_last_image_snapshot":image_observation(stack[-1]),
            "actual_source_frame_ledger":action["source_animation"],
        })
    return result


def event_summary(ev):
    frames=ev["observed_returned_frames"]
    return {
      "phase":ev["native_phase"],
      "native_level_progress":ev["official_native_progress"],
      "real_SDK_frames":ev["actual_returned_source_frames"],
      "source_preselected_bar_bbox":ev["source_preimage_snapshot"]["original_native_selected_color9_bbox"],
      "source_postselected_bar_bbox":ev["source_last_image_snapshot"]["original_native_selected_color9_bbox"],
      "source_color6_top_x_columns":sorted({x for fr in frames for x in fr["top_color6_x_columns"]}),
      "source_color6_top_frame_count":sum(bool(fr["top_color6_x_columns"]) for fr in frames),
      "source_color13_upper_counts":[fr["source_region_counts"]["upper"]["13"] for fr in frames],
      "source_color11_upper_counts":[fr["source_region_counts"]["upper"]["11"] for fr in frames],
      "source_color6_full_counts":[fr["source_full_original_color_counts"]["6"] for fr in frames],
      "source_color9_full_counts":[fr["source_full_original_color_counts"]["9"] for fr in frames],
      "source_final_selected_color9_count":ev["source_last_image_snapshot"]["source_full_original_color_counts"]["9"],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    records,arrays=[],{}
    for stage,programs in (("stage0",STAGE0),("stage1",STAGE1)):
        for name,word in programs:
            for replicate in range(RESETS):
                if stage=="stage0":
                    trial,raw=stage0_original_trial(name,word,replicate)
                    events=stage0_event(trial,raw)
                else:
                    trial,raw=one(name,word,replicate)
                    events=stage1_event(trial,raw)
                for key,frame_stack in raw.items():
                    arrays[f"{stage}_{name}_rep{replicate}_{key}"]=frame_stack
                records.append({
                   "source_stage":stage,
                   "frozen_word_name":name,
                   "precommitted_source_word":word,
                   "replicate":replicate,
                   "native_sdk_action_count":(
                     trial["actual_SDK_action_count"] if stage=="stage0"
                     else trial["actual_native_calls"]),
                   "native_last_level":(
                     trial["SDK_native_level_at_end"] if stage=="stage0"
                     else trial["original_last_source_level"]),
                   "native_last_state":(
                     trial["SDK_native_state_at_end"] if stage=="stage0"
                     else trial["original_last_source_state"]),
                   "actual_source_ACTION5_events":events,
                   "complete_native_source_trial":trial,
                })
    all_ev=[e for r in records for e in r["actual_source_ACTION5_events"]]
    grouped=defaultdict(list)
    for r in records:
      for e in r["actual_source_ACTION5_events"]:
        grouped[(e["native_phase"],e["official_native_progress"])].append({
            "name":r["frozen_word_name"],
            "replicate":r["replicate"],
            **event_summary(e),
        })
    out={
      "kind":"ORIGINAL_SP80_REAL_LEVEL_ADVANCING_VS_NONADVANCING_FULL_FRAME_EVENTS",
      "original_native_precommitted_stage0_words":STAGE0,
      "original_native_precommitted_stage1_words":STAGE1,
      "independent_source_game_resets_per_word":RESETS,
      "actual_source_game_resets":len(records),
      "true_original_sdk_action_responses":sum(r["native_sdk_action_count"] for r in records),
      "native_action5_returned_responses":len(all_ev),
      "native_returned_action5_frame_count":sum(e["actual_returned_source_frames"] for e in all_ev),
      "sdk_true_stage0_to1_events":sum(int(e["official_native_progress"])
          for e in all_ev if e["native_phase"]=="SOURCE_STAGE0"),
      "sdk_true_stage1_to2_or_WIN":sum(int(e["official_native_progress"])
          for e in all_ev if e["native_phase"]=="SOURCE_STAGE1"),
      "actual_source_comparisons":[{
          "native_phase":stage,"official_sdk_progress":progress,
          "observed_native_action5_events":len(rows),
          "real_native_returned_frame_lengths":dict(Counter(str(r["real_SDK_frames"]) for r in rows)),
          "individual_original_sdk_event_summaries":rows,
      } for (stage,progress),rows in sorted(grouped.items())],
      "genuine_original_native_source_trials":records,
      "limits":"These are actual source SDK-returned color events, not inferred game mechanics, targets, rays, score or hidden state. Comparing across stages does not isolate causation. Native SDK levels_completed and WIN alone label progress. Keep original full SDK NPZ frames and source ledgers.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_SOURCE_ADVANCEMENT_EVENTS "+json.dumps({
       k:v for k,v in out.items() if k!="genuine_original_native_source_trials"
    },sort_keys=True))
    if len(records)!=(len(STAGE0)+len(STAGE1))*RESETS:
        raise AssertionError("Native original source trial count incomplete")

if __name__=="__main__":
    main()
