"""Original SP80: deliberately place source-selected bars at other visible bar bands.

The genuine SP80 native SDK stage1 frame shows three actual horizontal
colored bar regions:
  selected native color9 x20..39,y36..39 (20 x 4)
  upper native color8 x8..19,y16..19 (12 x 4)
  lower native color8 x28..39,y24..27 (12 x 4).

Prior independent actual original SDK source studies established
coordinate ACTION6 changes highlighted bar and ACTION1/2/3/4 move the
highlighted bar in 4-pixel grid increments in tested contexts.
Neither bars nor HUD colors are PROVEN level objectives.

These programs prospectively move source-selected bars to concrete
other observed bar coordinates in BOTH route orders, test different
selected target sequences, and retain negative unchanged-order controls.
A coordinate may hit a different actual color after movement; always
record real source clicked pixel before applying action.

Each action uses original SDK real native legal controls. Every ACTION6
must carry native coordinates. Preserve ALL native returned obs.frame
images as independent original source evidence. Only levels_completed
>=2 or WIN constitute genuine game progress. No autonomous solver,
substitute physics, F3 mathematical mapping or hidden-state claims.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from .native_sp80_action5_frame_stacks import one
from .native_sp80_multi_select import parse_plan

PROGRAMS=(
 ("no_click_prior_lower_control","1 1 1 5"),
 ("lower_to_upper_left_first","6@32,25 3 3 3 3 3 1 1 5"),
 ("lower_to_upper_up_first","6@32,25 1 1 3 3 3 3 3 5"),
 ("upper_to_lower_right_first","6@12,17 4 4 4 4 4 2 2 5"),
 ("upper_to_lower_down_first","6@12,17 2 2 4 4 4 4 4 5"),
 ("first_to_upper_left_first","6@24,37 3 3 3 1 1 1 1 1 5"),
 ("first_to_upper_up_first","6@24,37 1 1 1 1 1 3 3 3 5"),
 ("first_to_lower_up_first","6@24,37 1 1 1 4 4 5"),
 ("upper_to_first_right_first","6@12,17 4 4 4 2 2 2 2 2 5"),
 ("lower_to_first_left_first","6@32,25 3 3 2 2 2 5"),
 ("two_bars_at_lower_y","6@12,17 2 2 6@24,37 1 1 1 5"),
 ("two_bars_at_upper_y","6@24,37 1 1 1 1 1 6@32,25 1 1 5"),
 ("select_upper_lower_no_move","6@12,17 6@32,25 5"),
 ("select_lower_upper_no_move","6@32,25 6@12,17 5"),
 ("first_near_top_source_glyphs","6@24,37 1 1 1 1 1 1 1 5"),
 ("upper_below_lower_same_x","6@12,17 4 4 4 4 4 2 2 2 5"),
)
RESETS=2
assert len(PROGRAMS)==len(set(n for n,_ in PROGRAMS))==16
assert RESETS==2
assert all(parse_plan(w)[-1][0]==5 and
       all(n!=6 or xy is not None for n,xy in parse_plan(w))
       for _,w in PROGRAMS)

SOURCE_BANDS={
 "upper_original_native_band":(8,20,16,20),
 "lower_original_native_band":(28,40,24,28),
 "initial_selected_native_band":(20,40,36,40),
 "source_top_glyph_region":(12,56,4,12),
}


def source_placement_snapshot(img):
    p=np.argwhere(img==9)
    result={
      "actual_color9_cells":int(len(p)),
      "native_color9_xy_bbox":([int(p[:,1].min()),int(p[:,0].min()),
         int(p[:,1].max()),int(p[:,0].max())] if len(p) else None),
      "actual_color8_cells":int(np.count_nonzero(img==8)),
      "actual_color11_cells":int(np.count_nonzero(img==11)),
    }
    for name,(x0,x1,y0,y1) in SOURCE_BANDS.items():
        region=img[y0:y1,x0:x1]
        result[name+"_color9_count"]=int(np.count_nonzero(region==9))
        result[name+"_color8_count"]=int(np.count_nonzero(region==8))
        result[name+"_color11_count"]=int(np.count_nonzero(region==11))
    return result


def inspect_source_game(t,stacks):
    placements=[]
    for event in t["real_sdk_observation_ledger"]:
        if event["phase"]!="context":
            continue
        k="context_"+str(event["phase_action_number"])
        if k not in stacks or "source_animation" not in event:
            placements.append({
                "context_action":event["phase_action_number"],
                "source_disposition":"UNKNOWN_OR_NO_COMPLETE_NATIVE_FRAME",
                "source_level":event["original_source_level_after"],
                "source_state":event["original_source_state_after"],
            })
            continue
        arr=stacks[k]
        placements.append({
            "context_action":event["phase_action_number"],
            "original_native_action_id":event["native_action_id"],
            "source_click_xy":event["native_click_xy"],
            "source_preclick_actual_pixel_color":event["actual_native_pre_click_pixel"],
            "source_SDK_returned_frame_count":len(arr),
            "source_final_image_placement":source_placement_snapshot(arr[-1]),
            "official_native_level_after":event["original_source_level_after"],
            "official_native_state_after":event["original_source_state_after"],
        })
    return placements


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    actual,all_arrays=[],{}
    for name,word in PROGRAMS:
        for replicate in range(RESETS):
            trial,frames=one(name,word,replicate)
            trial["genuine_actual_source_object_arrangements"]=inspect_source_game(trial,frames)
            actual.append(trial)
            for phase,arr in frames.items():
                all_arrays[f"{name}_reset{replicate}_{phase}"]=arr
    byword={}
    for name,word in PROGRAMS:
        rows=[r for r in actual if r["name"]==name]
        byword[name]={
          "precommitted_original_actions":word,
          "source_independent_resets":len(rows),
          "source_real_SDK_levels_completed":[r["original_last_source_level"] for r in rows],
          "source_real_SDK_state":[r["original_last_source_state"] for r in rows],
          "native_level2_or_WIN":[r["native_level2_or_win"] for r in rows],
          "source_dispositions":[r["actual_source_disposition"] for r in rows],
          "valid_original_SDK_action_calls":[r["actual_native_calls"] for r in rows],
          "final_observed_source_placement":[
            r["genuine_actual_source_object_arrangements"][-1].get("source_final_image_placement")
            if r["genuine_actual_source_object_arrangements"] else None for r in rows
          ],
          "proper_original_click_observations":[[
            {"source_click_xy":s["source_click_xy"],
             "real_original_preclick_pixel":s["source_preclick_actual_pixel_color"]}
            for s in r["genuine_actual_source_object_arrangements"]
            if s.get("original_native_action_id")==6] for r in rows],
        }
    result={
      "kind":"ORIGINAL_SP80_NATIVE_SELECTED_BAR_SPATIAL_PLACEMENTS_LEVEL2",
      "fixed_actual_original_native_programs":PROGRAMS,
      "independent_resets_per_program":RESETS,
      "actual_independent_original_sdk_games":len(actual),
      "genuine_source_action_calls":sum(r["actual_native_calls"] for r in actual),
      "sdk_native_level2_or_WIN":sum(int(r["native_level2_or_win"]) for r in actual),
      "original_game_dispositions":dict(Counter(r["actual_source_disposition"] for r in actual)),
      "original_game_program_outcomes":byword,
      "native_full_source_trial_evidence":actual,
      "limits":"Actual public original ARC3 SP80 SDK, not inferred goal geometry. Selecting bar at coordinate requires real data x,y. A move can change click target under precommitted location; pre-click pixel is preserved. All complete returned source frames in NPZ, original WIN/level counters govern success. Source F3-48 mathematics and agent untouched.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**all_arrays)
    print("SP80_BAR_PLACEMENT "+json.dumps({
      k:v for k,v in result.items() if k!="native_full_source_trial_evidence"
    },sort_keys=True))
    if len(actual)!=len(PROGRAMS)*RESETS:
        raise RuntimeError("Missing genuine source original SP80 resets")

if __name__=="__main__":
    main()
