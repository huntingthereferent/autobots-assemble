"""Original SP80 SDK: discriminate ACTION4 count from actual source bar position.

The original stage0 4/5-only source holdout predicted 36/36 official
level0->1 outcomes after three earlier ACTION4s. Its input domain
did not contain native ACTION3 left-cancellations or ACTION1/2 vertical
moves. This separately frozen intervention tests those controls, with
authentic original Arcade.NORMAL resets and ALL returned frames.

Do not presume inverse actions or matching hidden state: measure actual
pre-ACTION5 selected color9 pixels, complete source preaction image,
exact SDK level and terminal. A counterexample must be retained.
"""
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from .native_sp80_stage0_progress_animation import stage0_original_trial
from .native_sp80_legal_pairs import hash_frame

WORDS=(
 ("baseline_three","4445"),
 ("three_then_one_left","44435"),
 ("three_then_two_left","444335"),
 ("three_then_three_left","4443335"),
 ("one_left_then_three","34445"),
 ("two_right_left_one_right","44345"),
 ("right_left_two_right","43445"),
 ("three_then_up","44415"),
 ("three_then_down","44425"),
 ("up_then_three","14445"),
 ("down_then_three","24445"),
 ("up_down_then_three","124445"),
 ("down_up_then_three","214445"),
 ("up_then_three_down","144425"),
 ("three_up_down","444125"),
 ("three_down_up","444215"),
 ("four_right_then_left","444435"),
 ("two_right_left_two_right","443445"),
 ("four_right_then_two_left","4444335"),
 ("five_right_then_two_left","44444335"),
 ("two_right_then_left","4435"),
 ("two_right_then_up","4415"),
)
RESETS=2
assert len(WORDS)==len({n for n,_ in WORDS})==22
assert RESETS==2
assert all(w.endswith("5") and set(w)<={"1","2","3","4","5"} for n,w in WORDS)

def bbox_selected(frame):
    p=np.argwhere(frame==9)
    return [int(p[:,1].min()),int(p[:,0].min()),
            int(p[:,1].max()),int(p[:,0].max())] if len(p) else None

def action5_rows(trial,source):
    word=trial["frozen_original_word"]
    rows=[]
    for event in trial["genuine_source_action_records"]:
        if event.get("native_action")!=5 or "actual_SDK_frame_sequence" not in event:
            continue
        step=event["original_word_step"]
        previous=(source["reset"][-1] if step==1 else source["action_"+str(step-1)][-1])
        after=source["action_"+str(step)][-1]
        rows.append({
            "sdk_action_step":step,
            "true_preaction_prior_A4_count":word[:step-1].count("4"),
            "prior_native_A3_count":word[:step-1].count("3"),
            "prior_native_A1_count":word[:step-1].count("1"),
            "prior_native_A2_count":word[:step-1].count("2"),
            "preaction_original_full_hash":hash_frame(previous),
            "preaction_native_selected_bar_bbox":bbox_selected(previous),
            "original_after_bar_bbox":bbox_selected(after),
            "native_full_returned_frames":event["actual_SDK_frame_sequence"]["true_original_returned_frames"],
            "actual_official_level_advance":bool(event["native_SDK_level_increase"]),
            "native_SDK_level_before":event["pre_SDK_level"],
            "native_SDK_level_after":event["post_SDK_level"],
            "sdk_game_state_after":event["post_SDK_state"],
        })
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    trial_records,raw={},{}
    trials=[]
    for name,word in WORDS:
        for rep in range(RESETS):
            observed,source=stage0_original_trial(name,word,rep)
            observed["observed_original_ACTION5"]=action5_rows(observed,source)
            trials.append(observed)
            for phase,frames in source.items():
                raw[f"{name}_reset{rep}_{phase}"]=frames
    all5=[e for r in trials for e in r["observed_original_ACTION5"]]
    comparable=defaultdict(list)
    for r in trials:
        for event in r["observed_original_ACTION5"]:
            comparable[tuple(event["preaction_native_selected_bar_bbox"] or [])].append({
                "word":r["name"],"repeat":r["replicate"],
                "prior_A4":event["true_preaction_prior_A4_count"],
                "prior_A3":event["prior_native_A3_count"],
                "frame_len":event["native_full_returned_frames"],
                "advanced":event["actual_official_level_advance"],
                "full_preimage":event["preaction_original_full_hash"],
            })
    out={
        "kind":"ORIGINAL_SP80_STAGE0_ACTION4_ORDINAL_VS_NATIVE_BAR_POSITION",
        "prospectively_fixed_native_action_sequences":WORDS,
        "independent_resets_per_sequence":RESETS,
        "genuine_original_SDK_games":len(trials),
        "genuine_SDK_action_responses":sum(r["actual_SDK_action_count"] for r in trials),
        "real_stage0_ACTION5_events":len(all5),
        "true_SDK_level0_to1_advances":sum(bool(r["genuine_level0_to_level1_or_higher"]) for r in trials),
        "observed_native_ACTION5_by_A4_and_preaction_bbox":[{
            "native_source_bbox":list(k),
            "real_SDK_examples":v,
        } for k,v in comparable.items()],
        "actual_source_game_dispositions":dict(Counter(r["source_disposition"] for r in trials)),
        "complete_original_SDK_native_evidence":trials,
        "limits":"Original actual Arcade.NORMAL SP80 SDK. Source bar geometry is observed independently; equal selected-color9 bbox is not proven equal hidden state. Progress only genuine SDK counter/state. All original returned animation frames retained, no F3 mathematical law mapping.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_STAGE0_POSITION_ORDINAL "+json.dumps({
      k:v for k,v in out.items() if k not in ("complete_original_SDK_native_evidence","observed_native_ACTION5_by_A4_and_preaction_bbox")
    },sort_keys=True))
    if len(trials)!=len(WORDS)*RESETS:raise AssertionError("Missing source resets")

if __name__=="__main__":main()
