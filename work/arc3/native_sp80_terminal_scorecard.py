"""Independent original ARC SP80 terminal state and scorecard audit.

Official ARC documentation: WIN is objective success; GAME_OVER is
termination without a WIN report. Neither a cleared visible boundary
nor an empty terminal frame can substitute for native state/score.
Measure state, levels_completed, win_levels, available native actions,
frame admission, and optional official SDK scorecard records directly.

This is a read-only bounded source experiment (no game source edits,
no bot policy, no source F3 math changes, no win assertion).
Do not log SDK API keys, GUIDs, scorecard IDs or other credentials.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction, GameState

from .native_sp80_stage_transfer import frame_view, hash_grid

PREFIX="454545"
TRIALS=(
    ("stage0_all4_34", "", "4"*34),
    ("stage1_all4_48", PREFIX, "4"*48),
    ("stage1_late5_at39", PREFIX, "4"*38+"5"+"4"*9),
    ("stage1_early5_block", PREFIX, "5"*8+"4"*40),
)
RESETS=2
assert all(set(prefix+word)<={"4","5"} for _,prefix,word in TRIALS)
assert len(TRIALS)==4 and all(len(word) in (34,48) for _,_,word in TRIALS)
assert TRIALS[2][2][38]=="5" and TRIALS[2][2].count("5")==1


def native_state(obs):
    state=getattr(obs,"state",None)
    return str(getattr(state,"name",state))


def basic_obs(obs):
    arr,info=frame_view(obs)
    actions=sorted({int(getattr(a,"value",a)) for a in (
        getattr(obs,"available_actions",None) or [])})
    return {
        "native_state":native_state(obs),
        "levels_completed":int(getattr(obs,"levels_completed",-1)),
        "win_levels":int(getattr(obs,"win_levels",-1)),
        "legal_original_native_actions":actions,
        "frame_info":info,
        "frame_hash":hash_grid(arr) if arr is not None else None,
    },arr


def safe_scorecard(arcade):
    """Read authoritative public SDK object; emit only selected numerical fields."""
    try:
        obj=arcade.get_scorecard()
    except Exception as exc:
        return {"availability":"SDK_ERROR","class":type(exc).__name__}
    if obj is None:
        return {"availability":"UNAVAILABLE"}
    if hasattr(obj,"model_dump"):
        data=obj.model_dump(mode="json")
    elif isinstance(obj,dict):
        data=obj
    elif hasattr(obj,"dict"):
        data=obj.dict()
    else:
        return {"availability":"UNSERIALIZABLE","class":type(obj).__name__}
    if not isinstance(data,dict):
        return {"availability":"NON_DICTIONARY"}
    selected={}
    for key in ("score","total_environments","total_environments_completed",
                "total_levels","total_levels_completed","total_actions"):
        val=data.get(key)
        if isinstance(val,(float,int,bool)):
            selected[key]=val
    envs=data.get("environments")
    if isinstance(envs,list):
        selected["selected_environment_data"]=[]
        for env in envs:
            if not isinstance(env,dict):continue
            env_data={}
            for key in ("level_count","levels_completed","actions","resets","completed"):
                if isinstance(env.get(key),(int,float,bool)):
                    env_data[key]=env[key]
            runs=env.get("runs")
            if isinstance(runs,list):
                env_data["runs"]=[]
                for run in runs:
                    if not isinstance(run,dict):continue
                    row={}
                    for key in ("state","score","levels_completed","actions",
                                "resets","completed"):
                        val=run.get(key)
                        if isinstance(val,(int,float,str,bool)):row[key]=val
                    if row:env_data["runs"].append(row)
            if env_data:selected["selected_environment_data"].append(env_data)
    return {"availability":"PRESENT","public_numeric_and_state_only":selected}


def play_one(label,prefix,word,replicate):
    # Fresh arcade and game per run prevent accidental scorecard carry-over.
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=arcade.make("sp80")
    if env is None:
        raise RuntimeError("Original native SP80 SDK environment missing")
    obs=env.reset()
    root,frame=basic_obs(obs)
    if frame is None:raise RuntimeError("Missing original native reset frame")
    frames=[frame]
    ledger=[{"native_action_index":0,"phase":"ORIGINAL_RESET","observation":root}]
    target_stage=1 if prefix else 0
    stage_entry_witnessed=target_stage==0
    native_actions=0
    terminal=None
    interrupted=None
    full_word=prefix+word
    for step,letter in enumerate(full_word,1):
        before=obs
        legal=set(ledger[-1]["observation"]["legal_original_native_actions"])
        action_id=int(letter)
        phase="ACTUAL_STAGE1_ENTRY" if step<=len(prefix) else "CONTEXT"
        context_step=step-len(prefix) if phase=="CONTEXT" else None
        if action_id not in legal:
            interrupted="UNKNOWN_NATIVE_ACTION_WITHDRAWN"
            break
        try:
            obs=env.step(getattr(GameAction,"ACTION"+letter))
            native_actions+=1
        except Exception as exc:
            interrupted="UNKNOWN_NATIVE_SDK_EXCEPTION_"+type(exc).__name__
            break
        observed,frame=basic_obs(obs)
        record={
            "native_action_index":step,"context_action_step":context_step,
            "native_action_id":action_id,"phase":phase,
            "observation":observed,
        }
        ledger.append(record)
        if frame is not None:frames.append(frame)
        if phase=="ACTUAL_STAGE1_ENTRY" and step==len(prefix):
            stage_entry_witnessed=(observed["levels_completed"]==1
                and observed["native_state"]=="NOT_FINISHED")
        if observed["native_state"] in ("WIN","GAME_OVER"):
            terminal={
                "reported_sdk_state":observed["native_state"],
                "native_action_index":step,
                "context_action_attempt":context_step,
                "levels_completed":observed["levels_completed"],
                "win_levels":observed["win_levels"],
                "full_original_frame_available":frame is not None,
                "classification":(
                    "WIN_REPORTED" if observed["native_state"]=="WIN"
                    else "TERMINATED_WITHOUT_WIN_REPORT"
                )
            }
            break
        if frame is None:
            interrupted="UNKNOWN_NONSTANDARD_FRAME_BEFORE_TERMINAL"
            break
        if phase=="ACTUAL_STAGE1_ENTRY" and step==len(prefix) and not stage_entry_witnessed:
            interrupted="UNKNOWN_STAGE1_ENTRY_FAILED"
            break
        if phase=="CONTEXT" and observed["levels_completed"]!=target_stage:
            interrupted="NATIVE_LEVEL_CHANGED_WITHOUT_FULL_TARGET_STAGE_ADMISSION"
            break
    return {
        "label":label,"replicate":replicate,
        "original_stage_requested":target_stage,
        "entry_witnessed":stage_entry_witnessed,
        "native_actions_executed":native_actions,
        "total_requested_native_actions":len(full_word),
        "valid_full_64x64_frames_saved":len(frames),
        "last_observation":ledger[-1]["observation"],
        "first_original_terminal":terminal,
        "interruption":interrupted,
        "postgame_source_scorecard":safe_scorecard(arcade),
        "original_sdk_action_evidence":ledger,
    },np.stack(frames)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    trials,raw=[],{}
    for label,prefix,word in TRIALS:
        for replicate in range(RESETS):
            record,frames=play_one(label,prefix,word,replicate)
            trials.append(record)
            raw[f"{label}_reset{replicate}"]=frames
    counts=Counter()
    for t in trials:
        counts["native_reset_count"]+=1
        counts["native_actions_executed"]+=t["native_actions_executed"]
        state=t["first_original_terminal"]
        if state:
            counts["terminal_"+state["reported_sdk_state"]]+=1
        else:
            counts["no_explicit_native_terminal_report"]+=1
    summary={
        "kind":"SP80_ORIGINAL_NATIVE_TERMINAL_AND_SCORECARD_DIAGNOSTIC",
        "official_contract":"WIN is objective success. GAME_OVER means terminated without a WIN report.",
        "source_game":"sp80",
        "native_control_labels":[t[0] for t in TRIALS],
        "two_independently_reset_runs_per_control":RESETS,
        "summary_counts":dict(counts),
        "trial_terminal_and_scorecards":[{
            "label":t["label"],"replicate":t["replicate"],
            "entry_witnessed":t["entry_witnessed"],
            "native_actions_executed":t["native_actions_executed"],
            "first_original_terminal":t["first_original_terminal"],
            "last_observation":t["last_observation"],
            "scorecard":t["postgame_source_scorecard"],
            "interruption":t["interruption"],
        } for t in trials],
        "full_trials":trials,
        "limits":"Only original SDK reported state/levels/scorecard; no inferred WIN from pixels. Game source, F3 mathematics, agent and terminal semantics unchanged. Sensitive GUIDs/API keys omitted.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_TERMINAL_SCORECARD "+json.dumps({
        k:v for k,v in summary.items() if k!="full_trials"},sort_keys=True))
    if not trials:raise RuntimeError("No genuine native SDK trials")


if __name__=="__main__":
    main()
