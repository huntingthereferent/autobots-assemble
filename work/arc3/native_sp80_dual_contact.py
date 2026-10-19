"""Original SP80 level1: independently test sequential color8 contacts.

Actual Arcade.NORMAL stage1 source frames reveal TWO separate native
color8 areas at x28..39,y24..27 and x8..19,y16..19. In the previous
real-game experiments ACTION5 visibly changed native color9/color8
at one band, whereas ACTION6 was a matched negative control. NONE
of those individual tests advanced levels_completed beyond one.

This NEW native study predeclares a route from the lower contact
1115 toward the upper color8 band: five ACTION3 (left) and two
ACTION1 (up), both orders, with ACTION5/ACTION6 once there.
Also compare upper-first ACTION5, repeats and a move toward the
original source three-glyph top band at x28..39,y4..11.

These are geometric PROBES not assertions that colored pixels
represent the game's objective. SDK levels_completed and WIN are
the only positive indicators. All 1..6 actions must remain genuinely
advertised; stop at native terminal and preserve original frames.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np

from .native_sp80_legal_pairs import one
from .native_sp80_overlap_intervention import source_frame_observation

LOWER="1115"
UPPER="111113335"
L_TO_U="3333311"
U_TO_L="1133333"
WORDS=(
    "111","1115","1116",                    # old one-band controls
    "11153333311",                           # lower contact, approach upper without new action
    "111533333115","111533333116",          # lower->upper ACTION5 v ACTION6
    "111511333335","111511333336",          # same desired contact but movement order changed
    "11111333","111113335","111113336",     # upper original controls
    "1111133355","111113335345",            # repeat and nudge after upper
    "111113335445",                          # upper contact then horizontal move
    "11111333511115","11111333511116",     # upper contact then approach top row
    "111511115","111511116",                # lower contact then approach top row
)
RESETS=2
assert len(WORDS)==len(set(WORDS))==18
assert all(set(w)<={"1","3","4","5","6"} for w in WORDS)
assert "1115"+L_TO_U+"5" in WORDS
assert "1115"+L_TO_U+"6" in WORDS
assert "1115"+U_TO_L+"5" in WORDS
assert "1115"+U_TO_L+"6" in WORDS
assert RESETS==2

REGIONS={
    "upper_color8_visible_region":(8,20,16,20),
    "lower_color8_visible_region":(28,40,24,28),
    "top_score_like_source_glyphs":(12,56,4,12),
}


def direct_native_observation(frame):
    d=source_frame_observation(frame)
    for name,(x0,x1,y0,y1) in REGIONS.items():
        region=frame[y0:y1,x0:x1]
        d[name+"_native_color8_pixels"]=int(np.count_nonzero(region==8))
        d[name+"_native_color9_pixels"]=int(np.count_nonzero(region==9))
        d[name+"_native_color11_pixels"]=int(np.count_nonzero(region==11))
    return d


def run_source_trial(word,replicate):
    trial,frames=one(word,replicate)
    if len(frames)<7:
        raise AssertionError("No original native stage1 root")
    observed=[]
    root=direct_native_observation(frames[6])
    observed.append({
        "stage1_context_step":0,"actual_native_action":None,
        "official_native_levels_completed":1,
        "source_frame":root,
    })
    count=0
    for e in trial["source_effects"]:
        if not e.get("native_complete_frame"):
            observed.append({
                "stage1_context_step":e["context_step"],
                "actual_native_action":e["native_action"],
                "admission":"UNKNOWN_NATIVE_NONSTANDARD_FRAME",
                "sdk_disposition":e.get("status"),
            })
            continue
        count+=1
        if len(frames)<=6+count:
            raise AssertionError("Missing admitted original game source frame")
        pre,post=frames[5+count],frames[6+count]
        yy,xx=np.nonzero(pre!=post)
        actual=[{"xy":[int(x),int(y)],"before":int(pre[y,x]),
                 "after":int(post[y,x])} for y,x in zip(yy,xx)]
        if actual!=e["actual_original_pixel_color_changes"]:
            raise AssertionError("Original native color pairs do not match raw SDK frames")
        observed.append({
            "stage1_context_step":e["context_step"],
            "actual_native_action":e["native_action"],
            "official_native_levels_completed":e["official_after_levels_completed"],
            "official_native_state":e["official_after_state"],
            "native_changed_pixel_count":len(actual),
            "original_native_changed_colors":dict(Counter(
                str(q["before"])+"->"+str(q["after"]) for q in actual)),
            "source_frame":direct_native_observation(post),
        })
    trial["original_native_region_observations"]=observed
    trial["first_actual_native_level2_or_WIN"]=next((
        {"step":e["context_step"],
         "level":e.get("official_after_levels_completed"),
         "state":e.get("official_after_state")}
        for e in trial["source_effects"]
        if e.get("official_after_levels_completed",0)>=2
        or e.get("official_after_state")=="WIN"
    ),None)
    return trial,frames


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    samples,raw=[],{}
    for word in WORDS:
        for replicate in range(RESETS):
            trial,frames=run_source_trial(word,replicate)
            samples.append(trial)
            raw[f"word_{word}_reset{replicate}"]=frames
    grouped={}
    for word in WORDS:
        rows=[r for r in samples if r["word"]==word]
        grouped[word]={
            "genuine_native_resets":len(rows),
            "observed_source_actions":[r["actual_accepted_complete_native_action_frames"] for r in rows],
            "original_SDK_state":[r["last_reported_native_state"] for r in rows],
            "actual_level_after_word":[r["last_reported_native_level"] for r in rows],
            "real_level2_or_WIN":[r["first_actual_native_level2_or_WIN"] for r in rows],
            "native_disposition":[r["status"] for r in rows],
            "color9_final_xy":[r["original_native_region_observations"][-1].get("source_frame",{}).get("native_color9_xy_bounds") for r in rows],
            "color8_final_count":[r["original_native_region_observations"][-1].get("source_frame",{}).get("actual_native_color8_pixels") for r in rows],
            "upper_source_color8_remaining":[r["original_native_region_observations"][-1].get("source_frame",{}).get("upper_color8_visible_region_native_color8_pixels") for r in rows],
            "lower_source_color8_remaining":[r["original_native_region_observations"][-1].get("source_frame",{}).get("lower_color8_visible_region_native_color8_pixels") for r in rows],
            "score_like_source_glyph11_pixels":[r["original_native_region_observations"][-1].get("source_frame",{}).get("top_score_like_source_glyphs_native_color11_pixels") for r in rows],
        }
    payload={
        "kind":"SP80_ORIGINAL_NATIVE_DUAL_COLOR8_CONTACT_LEVEL2_TEST",
        "precommitted_original_stage1_words":WORDS,
        "native_reset_count":len(samples),
        "original_valid_context_actions":sum(r["actual_accepted_complete_native_action_frames"] for r in samples),
        "actual_SDK_level2_or_WIN":sum(int(r["first_actual_native_level2_or_WIN"] is not None) for r in samples),
        "native_dispositions":dict(Counter(r["status"] for r in samples)),
        "word_scores":grouped,
        "native_full_source_trial_records":samples,
        "limits":"Genuine Arcade.NORMAL native SP80, stage1 witnessed via real 454545. Color8 overlap and top native11 glyphs are observations not known objectives. Only actual SDK levels_completed or WIN count as progress; no clone, learned hidden model or F3 generator identity.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(payload,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_DUAL_CONTACT "+json.dumps({
        k:v for k,v in payload.items() if k!="native_full_source_trial_records"},
        sort_keys=True))
    if len(samples)!=len(WORDS)*RESETS:
        raise RuntimeError("Missing genuine independently reset native SP80 trials")


if __name__=="__main__":
    main()
