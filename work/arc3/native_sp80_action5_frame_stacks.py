"""Genuine original SP80 action-frame stack audit, especially ACTION5.

Prior source workers faithfully retained the LAST 64x64 image from
each original obs.frame payload. Their full-frame before/after color
maps are valid observations, but do not establish whether the SDK
returned multiple intermediate animation frames within an action.

This experiment independently saves the EXACT array of ALL original
SDK frames returned by reset, by each witnessed real stage1-entry
action (454545) and by each real stage1 action. There is no duplicate
game simulation or inferred unreturned animation.

Native ACTION6 is a COMPLEX ACTION: every use supplies both x and y.
The official SDK level counter and WIN/GAME_OVER remain authoritative.
Two original independently reset trials per predeclared program.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
import numpy as np

from .native_sp80_legal_pairs import PREFIX, state, legal, hash_frame
from .native_sp80_multi_select import parse_plan

PLANS=(
    ("native5_unmoved","5"),
    ("lower_contact","1 1 1 5"),
    ("upper_contact","1 1 1 1 1 3 3 3 5"),
    ("click_lower_commit","6@32,25 5"),
    ("click_upper_commit","6@12,17 5"),
    ("click_lower_upper_commit","6@32,25 6@12,17 5"),
    ("click_upper_lower_commit","6@12,17 6@32,25 5"),
    ("click_lower_move3_commit","6@32,25 3 3 3 5"),
    ("click_lower_upper_move2_commit","6@32,25 6@12,17 4 4 5"),
    ("click_background_commit","6@50,40 5"),
    ("lower_contact_click_control","1 1 1 6@24,37"),
    ("click_lower_upper_repeat_click_control","6@32,25 6@12,17 6@12,17"),
)
RESETS=2
assert len(PLANS)==len(set(n for n,_ in PLANS))==12
assert RESETS==2
assert all(len(parse_plan(word))>=1 for _,word in PLANS)
assert all(a!=6 or xy is not None for _,word in PLANS
           for a,xy in parse_plan(word))


def native_stack(obs):
    """Preserve entire actual SDK obs.frame stack; never interpolate frames."""
    payload=getattr(obs,"frame",None)
    if payload is None:
        return None,{"frame_status":"MISSING","source_shape":None}
    a=np.asarray(payload)
    shape=list(a.shape)
    if a.ndim==2 and a.shape==(64,64):
        b=a[np.newaxis,:,:]
    elif a.ndim==3 and a.shape[1:]==(64,64) and a.shape[0]>0:
        b=a
    else:
        return None,{"frame_status":"NONSTANDARD",
                     "source_shape":shape,"source_size":int(a.size)}
    if np.any(b<0) or np.any(b>15) or not np.all(b==np.floor(b)):
        raise ValueError("Original native frame outside exact ARC palette")
    b=b.astype(np.uint8,copy=True)
    return b,{"frame_status":"COMPLETE","source_shape":shape,
               "full_64x64_sdk_frames":len(b),
               "original_native_payload_bytes_sha256":sha256(
                   np.ascontiguousarray(a).tobytes()).hexdigest()}


def changed(a,b):
    y,x=np.nonzero(a!=b)
    return [{"xy":[int(xx),int(yy)],"before":int(a[yy,xx]),
             "after":int(b[yy,xx])} for yy,xx in zip(y,x)]


def frame_record_before_after(prev_last,stack):
    """A sequence of REAL returned frames, not an invented animation."""
    segments=[]
    old=prev_last
    for i,frame in enumerate(stack):
        differences=changed(old,frame)
        segments.append({
            "sdk_returned_frame_index":i,
            "original_before_frame_hash":hash_frame(old),
            "original_after_frame_hash":hash_frame(frame),
            "original_changed_pixel_count":len(differences),
            "original_changed_colors":dict(Counter(
                str(z["before"])+"->"+str(z["after"]) for z in differences)),
            "original_changed_xy_before_after_colors":differences,
        })
        old=frame
    last=stack[-1]
    transient=0
    if len(stack)>1:
        transient=int(np.count_nonzero(
            np.any(stack[:-1]!=prev_last,axis=0) & (last==prev_last)))
    return {
        "true_original_returned_frames":len(stack),
        "actual_source_intermediate_frame_count":max(0,len(stack)-1),
        "original_frame_by_frame_ledger":segments,
        "original_before_to_final_pixel_count":int(
            np.count_nonzero(prev_last!=last)),
        "original_transient_pixels_returning_to_old_color":transient,
    }


def one(name,program,repeat):
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=arcade.make("sp80")
    if env is None:raise RuntimeError("Official original SP80 unavailable")
    obs=env.reset()
    stack,info=native_stack(obs)
    if stack is None:raise RuntimeError("No complete original native reset frames")
    raw={"reset":stack}
    prev=stack[-1]
    events=[]
    native_calls=0

    def take(native_action,coords,phase,phase_step):
        nonlocal obs,prev,native_calls
        if native_action not in legal(obs):
            return {"disposition":"UNKNOWN_ACTION_WITHDRAWN",
                    "phase":phase,"step":phase_step},False
        kwargs={"data":{"x":int(coords[0]),"y":int(coords[1])}} if coords else {}
        if native_action==6 and coords is None:
            raise AssertionError("Source native ACTION6 must always have coordinates")
        pre_pixel=int(prev[coords[1],coords[0]]) if coords else None
        result=env.step(getattr(GameAction,"ACTION"+str(native_action)),**kwargs)
        native_calls+=1
        if result is None:
            return {"disposition":"UNKNOWN_NULL_NATIVE_RESPONSE",
                    "phase":phase,"step":phase_step,
                    "native_action":native_action},False
        frames,shape=native_stack(result)
        source_state=state(result)
        source_level=int(getattr(result,"levels_completed",-1))
        entry={
            "phase":phase,"phase_action_number":phase_step,
            "native_action_id":native_action,
            "native_click_xy":list(coords) if coords else None,
            "actual_native_pre_click_pixel":pre_pixel,
            "original_source_level_after":source_level,
            "original_source_state_after":source_state,
            "original_win_levels":int(getattr(result,"win_levels",-1)),
            "original_full_source_shape":shape,
            "genuine_sdk_call_index":native_calls,
        }
        if frames is None:
            entry["disposition"]="NATIVE_TERMINAL_"+source_state if source_state in ("WIN","GAME_OVER") else "UNKNOWN_NONSTANDARD_NATIVE_FRAMES"
        else:
            raw[phase+"_"+str(phase_step)]=frames
            entry["source_animation"]=frame_record_before_after(prev,frames)
            prev=frames[-1]
        events.append(entry)
        obs=result
        return entry,frames is not None

    for i,letter in enumerate(PREFIX,1):
        e,valid=take(int(letter),None,"entry",i)
        if not valid or e["original_source_state_after"] in ("WIN","GAME_OVER"):
            raise RuntimeError("Genuine original stage1 entry failed, no invented continuation")
    if int(getattr(obs,"levels_completed",-1))!=1 or state(obs)!="NOT_FINISHED":
        raise RuntimeError("Authentic original SP80 level1 witness absent")

    boundary=None
    for i,(action,coords) in enumerate(parse_plan(program),1):
        e,valid=take(action,coords,"context",i)
        if not valid:
            boundary=e.get("disposition","UNKNOWN_NONSTANDARD_NATIVE_FRAMES")
            break
        if state(obs) in ("WIN","GAME_OVER"):
            boundary="NATIVE_TERMINAL_"+state(obs)
            break
        if int(getattr(obs,"levels_completed",-1))!=1:
            boundary="NATIVE_LEVEL_CHANGED"
            break

    summary={
        "name":name,"source_native_program":program,"replicate":repeat,
        "actual_native_calls":native_calls,
        "original_last_source_level":int(getattr(obs,"levels_completed",-1)),
        "original_last_source_state":state(obs),
        "native_level2_or_win":bool(
            int(getattr(obs,"levels_completed",-1))>=2 or state(obs)=="WIN"),
        "actual_source_disposition":boundary or "COMPLETE",
        "real_sdk_observation_ledger":events,
        "original_reset_frame_info":info,
        "source_original_final_frame_hash":hash_frame(prev),
    }
    return summary,raw


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    trials,source_arrays=[],{}
    for name,program in PLANS:
        for replicate in range(RESETS):
            trial,frames=one(name,program,replicate)
            trials.append(trial)
            for phase,original in frames.items():
                source_arrays[name+"_reset"+str(replicate)+"_"+phase]=original
    overview={}
    for name,program in PLANS:
        rows=[t for t in trials if t["name"]==name]
        outcome=[]
        for trial in rows:
            interesting=[e for e in trial["real_sdk_observation_ledger"]
                         if e["phase"]=="context" and e["native_action_id"] in (5,6)]
            outcome.append({
                "native_actions":trial["actual_native_calls"],
                "last_native_level":trial["original_last_source_level"],
                "last_native_state":trial["original_last_source_state"],
                "source_actions_5_or6":[{
                    "action":e["native_action_id"],
                    "step":e["phase_action_number"],
                    "coordinates":e["native_click_xy"],
                    "sdk_payload_shape":e["original_full_source_shape"],
                    "returned_frames":e.get("source_animation",{}).get("true_original_returned_frames"),
                    "intermediate_frames":e.get("source_animation",{}).get("actual_source_intermediate_frame_count"),
                    "net_native_changed_pixels":e.get("source_animation",{}).get("original_before_to_final_pixel_count"),
                    "transient_native_pixels":e.get("source_animation",{}).get("original_transient_pixels_returning_to_old_color"),
                } for e in interesting]
            })
        overview[name]={"program":program,"real_native_reset_outcomes":outcome}
    all_events=[e for t in trials for e in t["real_sdk_observation_ledger"]]
    source_valid=[e for e in all_events if "source_animation" in e]
    five=[e for e in source_valid if e["phase"]=="context"
          and e["native_action_id"]==5]
    payload={
        "kind":"ORIGINAL_SP80_ALL_NATIVE_SDK_RETURNED_ANIMATION_FRAMES",
        "native_plans_precommitted":PLANS,
        "actual_independent_resets":len(trials),
        "source_native_calls":sum(t["actual_native_calls"] for t in trials),
        "actual_source_valid_action_responses":len(source_valid),
        "all_original_returned_valid_64x64_frames_in_actions":sum(
            e["source_animation"]["true_original_returned_frames"] for e in source_valid),
        "native_action5_observations":len(five),
        "action5_total_original_returned_frames":sum(
            e["source_animation"]["true_original_returned_frames"] for e in five),
        "action5_responses_with_extra_returned_frames":sum(
            e["source_animation"]["true_original_returned_frames"]>1 for e in five),
        "official_real_game_level2_or_WIN":sum(t["native_level2_or_win"] for t in trials),
        "sdk_dispositions":dict(Counter(t["actual_source_disposition"] for t in trials)),
        "per_program":overview,
        "authentic_native_source_records":trials,
        "limits":"Only actual SDK returned obs.frame pixels. If SDK supplies one image, unreturned internal animation is UNKNOWN; never imply no animation exists. All ACTION6 coordinates explicit. Original source WIN/level counters alone prove success. No source F3 mapping or simulation.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(payload,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**source_arrays)
    print("SP80_ACTION5_FRAME_STACKS "+json.dumps(
        {k:v for k,v in payload.items() if k!="authentic_native_source_records"},
        sort_keys=True))
    if len(trials)!=len(PLANS)*RESETS:
        raise RuntimeError("Missing authentic original native SDK trials")


if __name__=="__main__":
    main()
