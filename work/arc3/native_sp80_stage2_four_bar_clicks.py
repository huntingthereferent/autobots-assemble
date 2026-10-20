"""Genuine original SP80 level2 clickable-bar inventory and first legal moves.

Actual original SDK source level2 was reached with the independently
verified stage0 454545 + stage1 witness A. A new original stage2 screen
shows four color8/9 bars with actual native pixels:
 U (12,21) color8 16x4; M (44,29) color8 20x4;
 L (12,33) color8 24x4; F (40,41) color9 24x4.
Upper white (8,5) color11, background (62,50) color12.
These pixel locations are source observations, not decoded goals.

FROZEN independent stage2 programs test genuine SDK ACTION6 clicks,
moving a clicked bar once/twice right or once left, changing click
order, and native ACTION5. Only official levels_completed>=3 or WIN
constitutes progress. Save every genuine SDK obs.frame and source
native click color and terminal state, no hidden-state inferences.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_action5_frame_stacks import native_stack,frame_record_before_after
from .native_sp80_legal_pairs import PREFIX,state,legal,hash_frame
from .native_sp80_multi_select import parse_plan

SELECTABLE_PIXEL_CONTROLS=(
 ("upper_color8",(12,21,8)),("middle_color8",(44,29,8)),
 ("lower_color8",(12,33,8)),("first_selected_color9",(40,41,9)),
 ("top_white_glyph",(8,5,11)),("background",(62,50,12)),
)
PROGRAMS=(
 ("upper_click_commit","6@12,21 5"),
 ("middle_click_commit","6@44,29 5"),
 ("lower_click_commit","6@12,33 5"),
 ("first_click_commit","6@40,41 5"),
 ("upper_glyph_click_control","6@8,5 5"),
 ("background_click_control","6@62,50 5"),
 ("upper_one_right","6@12,21 4 5"),
 ("middle_one_right","6@44,29 4 5"),
 ("lower_one_right","6@12,33 4 5"),
 ("first_one_right","6@40,41 4 5"),
 ("upper_one_left","6@12,21 3 5"),
 ("middle_one_left","6@44,29 3 5"),
 ("lower_one_left","6@12,33 3 5"),
 ("first_one_left","6@40,41 3 5"),
 ("upper_two_right","6@12,21 4 4 5"),
 ("middle_two_right","6@44,29 4 4 5"),
 ("lower_two_right","6@12,33 4 4 5"),
 ("first_two_right","6@40,41 4 4 5"),
 ("upper_then_middle","6@12,21 6@44,29 5"),
 ("middle_then_lower","6@44,29 6@12,33 5"),
)
RESETS=2
assert len(PROGRAMS)==20 and len({n for n,_ in PROGRAMS})==20
assert RESETS==2
assert all(parse_plan(w)[-1][0]==5 and
   all(a!=6 or xy is not None for a,xy in parse_plan(w))
   for _,w in PROGRAMS)

def bbox(img,c):
    y,x=np.nonzero(img==c)
    return [int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None


def four_band_observations(img):
    bands=(("upper",20,24),("middle",28,32),("lower",32,36),("first",40,44))
    ans={}
    for name,low,high in bands:
        piece=img[low:high]
        y,x=np.nonzero(np.isin(piece,[8,9]))
        ans[name]={
            "real_original_bar_bbox":(
                [int(x.min()),int(y.min()+low),int(x.max()),int(y.max()+low)]
                if len(x) else None),
            "original_native_selected_color9_pixels":int(np.count_nonzero(piece==9)),
            "original_native_unselected_color8_pixels":int(np.count_nonzero(piece==8)),
        }
    return ans


def play_source(name,program,replicate):
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=arcade.make("sp80")
    if env is None:raise RuntimeError("Real original SP80 SDK not available")
    obs=env.reset()
    stack,info=native_stack(obs)
    if stack is None or int(getattr(obs,"levels_completed",-1))!=0:
        raise RuntimeError("Original native reset not level0")
    prev=stack[-1];source={"reset":stack};events=[];admission="COMPLETE"
    def step(action,xy,phase,index):
        nonlocal obs,prev
        before_level=int(getattr(obs,"levels_completed",-1))
        permitted=legal(obs)
        if action not in permitted:
            return False,"UNKNOWN_UNADVERTISED_ACTION"
        if action==6 and xy is None:
            raise ValueError("Actual source ACTION6 always requires native coordinates")
        clicked_color=int(prev[xy[1],xy[0]]) if xy else None
        kwargs={"data":{"x":int(xy[0]),"y":int(xy[1])}} if xy else {}
        result=env.step(getattr(GameAction,"ACTION"+str(action)),**kwargs)
        if result is None:return False,"UNKNOWN_NULL_SOURCE_RESPONSE"
        frames,frame_info=native_stack(result)
        event={
          "phase":phase,"phase_step":index,"real_source_action":action,
          "original_SDK_click_xy":list(xy) if xy else None,
          "actual_source_preclick_color":clicked_color,
          "source_level_before":before_level,
          "source_level_after":int(getattr(result,"levels_completed",-1)),
          "source_SDK_state_after":state(result),
          "native_source_legal_before":permitted,
          "native_source_legal_after":legal(result),
          "original_native_response_shape":frame_info,
        }
        if frames is not None:
            event["original_true_SDK_returned_frames"]=len(frames)
            event["actual_source_image_ledger"]=frame_record_before_after(prev,frames)
            if phase=="stage2":
                event["original_pre_action_bars"]=four_band_observations(prev)
                event["original_post_action_bars"]=four_band_observations(frames[-1])
                event["original_before_selected_color9_bbox"]=bbox(prev,9)
                event["original_after_selected_color9_bbox"]=bbox(frames[-1],9)
            source[phase+"_"+str(index)]=frames
            prev=frames[-1]
        else:event["source_frame_admission"]="UNKNOWN_NONSTANDARD_OR_TERMINAL"
        events.append(event)
        obs=result
        return frames is not None,("NATIVE_LEVEL_CHANGED" if int(getattr(obs,"levels_completed",-1))!=before_level
               else "SDK_TERMINAL_"+state(obs) if state(obs) in ("WIN","GAME_OVER")
               else "NATIVE_ACCEPTED" if frames is not None else "UNKNOWN_NATIVE_RESPONSE")
    for i,a in enumerate(PREFIX,1):
        ok,result=step(int(a),None,"entry",i)
        if not ok or state(obs) in ("WIN","GAME_OVER"):
            raise RuntimeError("Original stage1 source entry failed")
    if int(getattr(obs,"levels_completed",-1))!=1:
        raise AssertionError("True SDK stage0->1 witness missing")
    witness=STAGE1_WITNESSES[0][1]
    for i,(a,xy) in enumerate(parse_plan(witness),1):
        ok,result=step(a,xy,"witness",i)
        if not ok or (i<len(parse_plan(witness)) and
             int(getattr(obs,"levels_completed",-1))!=1):
            raise RuntimeError("Original real stage1 witness failed early")
    if int(getattr(obs,"levels_completed",-1))!=2 or state(obs)!="NOT_FINISHED":
        raise RuntimeError("Original source stage2 not reached by actual witness")
    original_stage2_root=prev.copy()
    actual_root_color={}
    for label,(x,y,expected) in SELECTABLE_PIXEL_CONTROLS:
        observed=int(original_stage2_root[y,x])
        actual_root_color[label]={"xy":[x,y],"source_pixel":observed,
                                  "expected_from_prior_native_archive":expected}
        if observed!=expected:raise AssertionError("Prior source stage2 pixels changed")
    count=0
    for i,(a,xy) in enumerate(parse_plan(program),1):
        ok,reason=step(a,xy,"stage2",i)
        if ok:count+=1
        if not ok or reason.startswith("SDK_TERMINAL") or reason=="NATIVE_LEVEL_CHANGED":
            admission=reason
            break
    return {
       "source_original_program_name":name,
       "source_frozen_stage2_actions":program,
       "fresh_source_original_reset":replicate,
       "original_stage2_root_frame_sha":hash_frame(original_stage2_root),
       "genuine_original_stage2_initial_pixel_controls":actual_root_color,
       "genuine_sdk_stage2_native_actions_accepted":count,
       "official_SDK_final_level":int(getattr(obs,"levels_completed",-1)),
       "official_SDK_final_state":state(obs),
       "real_sdk_level3_or_win":bool(int(getattr(obs,"levels_completed",-1))>=3 or state(obs)=="WIN"),
       "source_disposition":admission,
       "true_native_all_original_action_events":events,
       "real_original_final_native_frame_sha":hash_frame(prev),
    },source


def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    trials,arrays=[],{}
    for name,program in PROGRAMS:
        for rep in range(RESETS):
            trial,raw=play_source(name,program,rep)
            trials.append(trial)
            for phase,frame in raw.items():
                arrays[f"{name}_rep{rep}_{phase}"]=frame
    by={}
    for name,word in PROGRAMS:
        rows=[t for t in trials if t["source_original_program_name"]==name]
        by[name]={
          "original_precommitted_stage2_actions":word,
          "source_sdk_level_after":[t["official_SDK_final_level"] for t in rows],
          "source_SDK_state_after":[t["official_SDK_final_state"] for t in rows],
          "true_native_level3_or_WIN":[t["real_sdk_level3_or_win"] for t in rows],
          "actual_source_admissions":[t["source_disposition"] for t in rows],
          "original_click_color_and_selected_bar_changes":[[
              {"clicked_xy":e["original_SDK_click_xy"],
               "real_original_clicked_color":e["actual_source_preclick_color"],
               "selected_color9_before":e["original_before_selected_color9_bbox"],
               "selected_color9_after":e["original_after_selected_color9_bbox"],
               "real_source_last_frame_change":e["actual_source_image_ledger"]["original_before_to_final_pixel_count"]}
              for e in t["true_native_all_original_action_events"]
              if e["phase"]=="stage2" and e["real_source_action"]==6
          ] for t in rows],
        }
    payload={
      "kind":"AUTHENTIC_ORIGINAL_SP80_STAGE2_FOUR_BAR_COORDINATE_SELECTION",
      "frozen_original_source_root_pixel_checks":SELECTABLE_PIXEL_CONTROLS,
      "prospectively_frozen_native_stage2_programs":PROGRAMS,
      "fresh_original_game_resets_per_program":RESETS,
      "total_genuine_independent_original_SP80_games":len(trials),
      "actual_source_SDK_action_responses":sum(len(t["true_native_all_original_action_events"]) for t in trials),
      "source_stage2_level3_or_WIN":sum(int(t["real_sdk_level3_or_win"]) for t in trials),
      "real_native_dispositions":dict(Counter(t["source_disposition"] for t in trials)),
      "per_original_stage2_native_program":by,
      "all_full_original_SDK_source_trials":trials,
      "limits":"All source state from original public Arcade.NORMAL SDK. Correct ACTION6 x,y. Real native level3/WIN alone constitutes progress. UI upper-color11 pixel not assumed goal. Full SDK returned obs.frame stacks NPZ+JSON preserved.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(payload,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_STAGE2_SELECTABLE_BAR_CLICKS "+json.dumps({
       k:v for k,v in payload.items() if k not in
       ("per_original_stage2_native_program","all_full_original_SDK_source_trials")
    },sort_keys=True))
    print("SP80_STAGE2_SELECTABLE_BAR_SUMMARY "+json.dumps({
        k:{"levels":v["source_sdk_level_after"],"states":v["source_SDK_state_after"],
           "clicks":v["original_click_color_and_selected_bar_changes"]}
        for k,v in by.items()
    },sort_keys=True))
    if len(trials)!=len(PROGRAMS)*RESETS:raise AssertionError("Incomplete original stage2 native reset count")
if __name__=="__main__":main()
