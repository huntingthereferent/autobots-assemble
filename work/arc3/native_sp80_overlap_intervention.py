"""Genuine SP80 original-native color8/color9 overlap interventions.

Read-only source-frame discovery found native stage1 color9 region
x20..39, y36..39. Three consecutive ACTION1 move it to y24..27,
where source original color8 visible count drops 96->48, indicating
a screen-color overlap; no target semantics or win was established.
Predeclare ACTION5 versus ACTION6 before and after this visible event,
and control for two ACTION4 shifts before/after the ACTION1 movement.

Re-use original SDK-traced real stage1 `454545` native prefix from
native_sp80_legal_pairs.one(). Two independently reset original games
per word. Check true native level progress / WIN / GAME_OVER and legal
actions at EACH step. Preserve actual original NPZ, frame hashes and
native color-pixel differences, not inferred hidden state.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from .native_sp80_legal_pairs import one

WORDS=(
    "111",       # original screen overlap observation, no intervention
    "115","116",# native interaction prior to original color8 overlap
    "1115","1116",# native interaction on observed source color8 overlap
    "44111",     # shifted geometry without interaction
    "441115","441116", # shifted first, overlap then candidate interaction
    "111445","111446", # shift after overlap, candidate interaction
    "11154","11164",# attempt horizontal movement after interaction
)
RESETS=2
assert len(WORDS)==len(set(WORDS))==12
assert all(set(w)<={"1","4","5","6"} for w in WORDS)
assert RESETS==2


def source_frame_observation(a):
    points=np.argwhere(a==9)
    bbox=([int(points[:,1].min()),int(points[:,0].min()),
           int(points[:,1].max()),int(points[:,0].max())]
          if len(points) else None)
    return {
        "actual_native_color8_pixels":int(np.count_nonzero(a==8)),
        "actual_native_color9_pixels":int(np.count_nonzero(a==9)),
        "native_color9_xy_bounds":bbox,
        "actual_native_color8_cells_in_y24_to27":int(np.count_nonzero(a[24:28]==8)),
        "actual_native_color9_cells_in_y24_to27":int(np.count_nonzero(a[24:28]==9)),
        "bottom_row63_cleared_cells":int(np.count_nonzero(a[63]==0)),
    }


def native_trial(word,replicate):
    trial,frames=one(word,replicate)
    if len(frames)<7:raise RuntimeError("Real witnessed native stage1 root missing")
    snapshots=[{"context_step":0,"prior_native_action":None,
                "real_native_observation":source_frame_observation(frames[6])}]
    accepted=0
    for event in trial["source_effects"]:
        if not event.get("native_complete_frame"):
            continue
        accepted+=1
        if len(frames)<=6+accepted:
            raise AssertionError("Native frame unavailable for accepted action")
        snapshots.append({
            "context_step":event["context_step"],
            "prior_native_action":event["native_action"],
            "sdk_state":event["official_after_state"],
            "sdk_levels_completed":event["official_after_levels_completed"],
            "real_native_observation":source_frame_observation(frames[6+accepted]),
        })
    original8=snapshots[0]["real_native_observation"]["actual_native_color8_pixels"]
    first_changed=[s["context_step"] for s in snapshots[1:]
                   if s["real_native_observation"]["actual_native_color8_pixels"]<original8]
    trial["genuine_stage1_source_frame_observations"]=snapshots
    trial["first_native_original_color8_count_decrease_step"]=first_changed[0] if first_changed else None
    trial["genuine_original_root_color8_count"]=original8
    trial["native_overlap_candidate_happened"]=bool(first_changed)
    return trial,frames


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    records,source_frames=[],{}
    for word in WORDS:
        for reset in range(RESETS):
            record,frames=native_trial(word,reset)
            records.append(record)
            source_frames[f"{word}_{reset}"]=frames
    byword={}
    for word in WORDS:
        pair=[r for r in records if r["word"]==word]
        byword[word]={
            "replicates":RESETS,
            "complete_native_actions":[r["actual_accepted_complete_native_action_frames"] for r in pair],
            "state":[r["last_reported_native_state"] for r in pair],
            "levels":[r["last_reported_native_level"] for r in pair],
            "WIN_or_level2":[r["progress_to_level2_or_native_WIN"] for r in pair],
            "first_color8_reduction_step":[r["first_native_original_color8_count_decrease_step"] for r in pair],
            "last_native_color8_count":[r["genuine_stage1_source_frame_observations"][-1]["real_native_observation"]["actual_native_color8_pixels"] for r in pair],
            "last_native_color9_xy_bbox":[r["genuine_stage1_source_frame_observations"][-1]["real_native_observation"]["native_color9_xy_bounds"] for r in pair],
            "last_native_bottom_row_cleared":[r["genuine_stage1_source_frame_observations"][-1]["real_native_observation"]["bottom_row63_cleared_cells"] for r in pair],
            "disposition":[r["status"] for r in pair],
        }
    out={
        "kind":"SP80_ORIGINAL_NATIVE_COLOR8_COLOR9_STAGE1_OVERLAP_INTERVENTION",
        "frozen_preexisting_witness":"111 produces visible native color9 overlap at y24..27 with original native color8 region, not proven target",
        "frozen_new_words":WORDS,
        "resets_per_original_stage1_word":RESETS,
        "original_native_resets":len(records),
        "valid_original_context_action_frames":sum(r["actual_accepted_complete_native_action_frames"] for r in records),
        "official_native_level2_or_WIN_count":sum(int(r["progress_to_level2_or_native_WIN"]) for r in records),
        "real_native_dispositions":dict(Counter(r["status"] for r in records)),
        "by_native_word":byword,
        "actual_original_source_trial_evidence":records,
        "limits":"Original public Arcade.NORMAL native actions, real stage1 rooted frames and SDK level/WIN statuses. Color8/9 pixel overlap is ONLY a visible event, not a known goal, hidden mechanism, F3 mathematical generator mapping or solved-game proof.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**source_frames)
    print("SP80_OVERLAP_NATIVE "+json.dumps({
        k:v for k,v in out.items() if k!="actual_original_source_trial_evidence"
    },sort_keys=True))
    if len(records)!=len(WORDS)*RESETS:raise RuntimeError("Missing native resets")


if __name__=="__main__":
    main()
