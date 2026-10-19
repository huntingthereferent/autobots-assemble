"""Genuine original SP80 stage1: are three top white glyph regions clickable?

Source-observed original native stage1 post-454545 upper white/color11:
  glyph1 x12..23,y4..11, glyph2 x28..39,y4..11,
  glyph3 x44..55,y4..11. Their centers x18/34/50 at y5 are color11.
Original ACTION5 animation can temporarily make the same upper
regions color13, including all 240 pixels with NO native level2.
That is NOT proof that white glyphs are targets, controls or goals.

Prospectively compare genuine coordinate ACTION6 clicks at these
three white native source pixels, a hollow interior negative, a remote
background pixel, and authentic selectable color8/9 bar controls,
alone and in combinations with proper bar clicks.
Preserve EVERY official SDK-returned 64x64 native frame, genuine
clicked pixel color, highlighted bar position, legal controls and
native levels_completed/WIN/GAME_OVER. No source modifications.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_action5_frame_stacks import one
from .native_sp80_multi_select import parse_plan

FROZEN_COORDINATES={
 "top_white_A":(14,5,11),
 "top_white_B":(30,5,11),
 "top_white_C":(46,5,11),
 "top_hole_background":(18,9,None),
 "remote_background":(60,30,None),
 "upper_color8":(12,17,8),
 "lower_color8":(32,25,8),
 "selected_color9":(24,37,9),
}
PLANS=(
 ("top_white_A_commit","6@14,5 5"),
 ("top_white_B_commit","6@30,5 5"),
 ("top_white_C_commit","6@46,5 5"),
 ("all_three_white_commit","6@14,5 6@30,5 6@46,5 5"),
 ("reverse_three_white_commit","6@46,5 6@30,5 6@14,5 5"),
 ("white_hole_control","6@18,9 5"),
 ("background_control","6@60,30 5"),
 ("upper_real_bar_control","6@12,17 5"),
 ("lower_real_bar_control","6@32,25 5"),
 ("already_selected_real_bar_control","6@24,37 5"),
 ("upper_bar_then_white_mid","6@12,17 6@30,5 5"),
 ("lower_bar_then_white_right","6@32,25 6@46,5 5"),
 ("white_left_then_lower_bar","6@14,5 6@32,25 5"),
 ("white_middle_then_move_right","6@30,5 4 4 5"),
 ("white_right_then_real_bar","6@46,5 6@12,17 4 5"),
)
RESETS=2
assert len(PLANS)==len({name for name,_ in PLANS})==15
assert RESETS==2
assert all(parse_plan(word)[-1][0]==5 and
   all(a!=6 or xy is not None for a,xy in parse_plan(word))
   for _,word in PLANS)


def bbox(frame,color):
    y,x=np.nonzero(frame==color)
    return [int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None


def native_observation(trial,raw):
    out=[]
    for ev in trial["real_sdk_observation_ledger"]:
        if ev["phase"]!="context":continue
        index=ev["phase_action_number"]
        stack=raw.get("context_"+str(index))
        if stack is None or "source_animation" not in ev:
            out.append({"source_action_step":index,
                "source_admission":"UNKNOWN_SDK_FRAME",
                "native_sdk_level":ev["original_source_level_after"],
                "native_sdk_state":ev["original_source_state_after"]})
            continue
        before=(raw["entry_6"][-1] if index==1
               else raw["context_"+str(index-1)][-1])
        after=stack[-1]
        coord=ev["native_click_xy"]
        out.append({
            "original_context_step":index,
            "real_original_native_action":ev["native_action_id"],
            "source_click_xy":coord,
            "actual_original_clicked_preimage_pixel_color":ev["actual_native_pre_click_pixel"],
            "actual_source_click_preimage_color11":int(np.count_nonzero(before[:13]==11)),
            "original_SDK_returned_frames":len(stack),
            "authentic_color9_bbox_before":bbox(before,9),
            "authentic_color9_bbox_after":bbox(after,9),
            "source_native_upper_color11_cells_after":int(np.count_nonzero(after[:13]==11)),
            "source_original_action_changed_pixels":{
                "last_image":ev["source_animation"]["original_before_to_final_pixel_count"],
                "all_SDK_returned_image_steps":[
                    z["original_changed_pixel_count"] for z in
                    ev["source_animation"]["original_frame_by_frame_ledger"]]
            },
            "SDK_original_levels_completed":ev["original_source_level_after"],
            "SDK_original_game_state":ev["original_source_state_after"],
        })
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    all_trials,arrays=[],{}
    results={}
    for name,word in PLANS:
        values=[]
        for rep in range(RESETS):
            trial,raw=one(name,word,rep)
            trial["source_upper_click_observations"]=native_observation(trial,raw)
            values.append(trial)
            all_trials.append(trial)
            for phase,stack in raw.items():
                arrays[f"{name}_reset{rep}_{phase}"]=stack
        results[name]={
            "frozen_source_native_actions":word,
            "source_completed_levels":[v["original_last_source_level"] for v in values],
            "source_original_states":[v["original_last_source_state"] for v in values],
            "actual_native_level2_or_WIN":[v["native_level2_or_win"] for v in values],
            "original_SDK_dispositions":[v["actual_source_disposition"] for v in values],
            "genuine_original_clicks":[{
               "replicate":v["replicate"],
               "events":[e for e in v["source_upper_click_observations"]
                         if e.get("real_original_native_action")==6],
            } for v in values],
            "source_native_after_ACTION5_observations":[{
                "replicate":v["replicate"],
                "events":[e for e in v["source_upper_click_observations"]
                      if e.get("real_original_native_action")==5]
            } for v in values],
        }
    output={
        "kind":"ORIGINAL_SP80_UPPER_SOURCE_GLYPH_COORDINATE_ACTION6_REAL_NATIVE_CONTROLS",
        "actual_original_source_glyph_and_bar_coordinates":FROZEN_COORDINATES,
        "predeclared_original_SDK_programs":PLANS,
        "native_resets_per_program":RESETS,
        "authentic_original_native_SP80_games":len(all_trials),
        "accepted_real_source_SDK_actions":sum(t["actual_native_calls"] for t in all_trials),
        "genuine_original_native_ACTION6_events":sum(
             1 for t in all_trials for e in t["source_upper_click_observations"]
             if e.get("real_original_native_action")==6),
        "native_level2_or_WIN":sum(int(t["native_level2_or_win"]) for t in all_trials),
        "native_source_dispositions":dict(Counter(t["actual_source_disposition"] for t in all_trials)),
        "per_original_program":results,
        "full_genuine_original_SDK_evidence":all_trials,
        "limits":"Upper glyphs are visible original pixels, NOT proven targets, goals or selectable objects. Native ACTION6 is a coordinate click, and source level2/WIN alone counts as progress. All complete SDK-returned original frames saved; actual pre-click pixel colors and click effect preserved. No hidden-state or F3 law inference."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_TOP_GLYPH_CLICKS "+json.dumps({
        k:v for k,v in output.items() if k!="full_genuine_original_SDK_evidence"
    },sort_keys=True))
    if len(all_trials)!=len(PLANS)*RESETS:
        raise RuntimeError("Missing original independent SDK resets")
if __name__=="__main__":main()
