"""Authentic SP80 SDK public observation audit across an actual stage3 success
and stage4 four-cup source-negative cases.

We do not decode game physics, infer hidden objectives, or treat 180 visual
cup pixels as a win. Six independent original NORMAL SDK resets (three
predeclared stage4 continuations x two source entry witnesses) retain
official SDK state, levels, available actions, public observation fields,
and full returned 64x64 image stacks across every genuine action.
"""
from __future__ import annotations
import argparse
from collections import Counter
from enum import Enum
import json
from pathlib import Path
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from .native_sp80_legal_pairs import PREFIX, legal, state, hash_frame
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_entry_source_map import STAGE2_VERIFIED_WORD
from .native_sp80_stage4_entry_inventory import STAGE3_WINNER
from .native_sp80_stage4_four_cup_followup import BASE, read_pour
from .native_sp80_multi_select import parse_plan
from .native_sp80_action5_frame_stacks import native_stack

FROZEN=(
 ("untouched_level4","5"),
 ("four_cup_visual",BASE+" 5"),
 ("four_cup_repeat",BASE+" 5 5"),
)
assert len(STAGE1_WITNESSES)==2 and len(FROZEN)==3
assert parse_plan(STAGE3_WINNER)[-1][0]==5
assert all(sum(a==5 for a,xy in parse_plan(w)) in (1,2)
           and parse_plan(w)[-1][0]==5
           and all(xy is not None for a,xy in parse_plan(w) if a==6)
           for _,w in FROZEN)

WATCH=("levels_completed","state","game_state","game_id","score",
       "total_score","is_terminal","is_done","done","won","is_win",
       "remaining_time","time_remaining","action_count","actions_taken",
       "available_actions","legal_actions","metadata","info","message",
       "levels_total","total_levels")
def safe_primitive(v):
    if v is None or type(v) in (bool,int,float,str):
        if type(v)==str and len(v)>200:return {"length":len(v),"type":"long string"}
        return v
    if isinstance(v,Enum):return {"name":v.name,"value":safe_primitive(v.value)}
    if isinstance(v,(list,tuple,set)) and len(v)<40:
        x=[safe_primitive(z) for z in v]
        if all(z is None or isinstance(z,(str,int,float,bool)) or
            isinstance(z,dict) and "name" in z for z in x):return x
    return {"public_type":type(v).__name__}

def sdk_surface(obs):
    names=set()
    try:names|={k for k in vars(obs) if not k.startswith("_")}
    except TypeError:pass
    for cls in type(obs).__mro__:
        names.update(k for k in getattr(cls,"__annotations__",{}) if not k.startswith("_"))
    names|={x for x in WATCH if hasattr(obs,x)}
    # Only render a bounded predeclared set of public scalar SDK fields.
    fields={}
    for name in WATCH:
        if not hasattr(obs,name):continue
        try:
            value=getattr(obs,name)
            if not callable(value):fields[name]=safe_primitive(value)
        except Exception as error:
            fields[name]={"read_exception_type":type(error).__name__}
    frames,detail=native_stack(obs)
    if frames is None:raise AssertionError("Actual original SDK frame absent")
    return {
        "public_result_type":type(obs).__name__,
        "public_attribute_names":sorted(names),
        "public_documented_and_optional_fields":fields,
        "official_state":state(obs),
        "official_levels_completed":int(getattr(obs,"levels_completed",-1)),
        "actual_available_actions":legal(obs),
        "source_frame_stack_detail":detail,
        "native_final_64x64_hash":hash_frame(frames[-1]),
    },frames

def run_original(case,witness,stage1,stage4):
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=arcade.make("sp80")
    if env is None:raise RuntimeError("True original SP80 missing")
    obs=env.reset()
    before,returned=sdk_surface(obs)
    if before["official_levels_completed"]!=0:raise AssertionError("Original reset not level0")
    stacks={"reset":returned}; ledger=[]; observations={"reset":before}
    def one(phase,index,action,xy):
        nonlocal obs
        pre,pre_frames=sdk_surface(obs)
        if action not in legal(obs):raise RuntimeError("Original SDK action not advertised")
        kwargs={"data":{"x":int(xy[0]),"y":int(xy[1])}} if xy else {}
        result=env.step(getattr(GameAction,"ACTION"+str(action)),**kwargs)
        if result is None:raise RuntimeError("Native SDK null action return")
        post,stack=sdk_surface(result)
        stacks[f"{phase}_{index}"]=stack
        rec={"phase":phase,"index":index,"native_action":action,
            "original_action6_xy":list(xy) if xy else None,
            "actual_original_clicked_palette":int(pre_frames[-1][xy[1],xy[0]]) if xy else None,
            "actual_native_before":pre,"actual_native_after":post}
        ledger.append(rec);obs=result
        return rec
    for phase,word,target in (
        ("entry0"," ".join(PREFIX),1),
        ("entry1",stage1,2),
        ("entry2",STAGE2_VERIFIED_WORD,3),
        ("entry3",STAGE3_WINNER,4)):
        actions=parse_plan(word)
        for index,(a,xy) in enumerate(actions,1):
            rec=one(phase,index,a,xy)
            if rec["actual_native_after"]["official_levels_completed"]!=(
                    target if index==len(actions) else target-1):
                raise AssertionError("Verified official native entry diverged: "+phase)
    root=stacks[f"entry3_{len(parse_plan(STAGE3_WINNER))}"][-1]
    if hash_frame(root)!="fa8fd32d3bfd2c8b3ff7765aec373512":
        raise AssertionError("Native Level4 root outside original witness")
    actions=parse_plan(stage4)
    pours=[]
    for index,(a,xy) in enumerate(actions,1):
        rec=one("stage4",index,a,xy)
        if a==5:
            previous=stacks[f"stage4_{index-1}"][-1] if index>1 else root
            observation=read_pour(root,previous,stacks[f"stage4_{index}"])
            pours.append({"native_sdk_action_index":index,
                 "official_before":rec["actual_native_before"],
                 "official_after":rec["actual_native_after"],
                 "actual_native_source_cups":observation})
        if (rec["actual_native_after"]["official_levels_completed"]>=5 or
            rec["actual_native_after"]["official_state"] in ("WIN","GAME_OVER")):
            break
    result={"predeclared_case":case,"independent_native_entry":witness,
            "original_sdk_stage4_word":stage4,
            "original_stage3_last_action":next(r for r in ledger
                if r["phase"]=="entry3" and r["index"]==len(parse_plan(STAGE3_WINNER))),
            "original_sdk_stage4_pour_observations":pours,
            "official_final_state":state(obs),
            "official_final_levels_completed":int(getattr(obs,"levels_completed",-1)),
            "official_level5_or_WIN":int(getattr(obs,"levels_completed",-1))>=5 or state(obs)=="WIN",
            "native_stage4_root_digest":hash_frame(root),
            "entire_true_sdk_action_ledger":ledger}
    return result,stacks

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();rows=[];allframes={}
    for case,word in FROZEN:
        for witness,entry in STAGE1_WITNESSES:
            result,frames=run_original(case,witness,entry,word)
            rows.append(result)
            for phase,stack in frames.items():allframes[f"{case}_{witness}_{phase}"]=stack
            stage3=result["original_stage3_last_action"]
            print("SP80_SDK_OBSERVATION_CONTRAST "+json.dumps({
                "case":case,"witness":witness,"level":result["official_final_levels_completed"],
                "state":result["official_final_state"],
                "public_field_names":stage3["actual_native_after"]["public_attribute_names"],
                "successful_level3_pre":stage3["actual_native_before"]["public_documented_and_optional_fields"],
                "successful_level3_post":stage3["actual_native_after"]["public_documented_and_optional_fields"],
                "level4_pours":[{
                    "level_before":r["official_before"]["official_levels_completed"],
                    "level_after":r["official_after"]["official_levels_completed"],
                    "state_before":r["official_before"]["official_state"],
                    "state_after":r["official_after"]["official_state"],
                    "public_fields_before":r["official_before"]["public_documented_and_optional_fields"],
                    "public_fields_after":r["official_after"]["public_documented_and_optional_fields"],
                    "four_cup_source_frames":r["actual_native_source_cups"]["same_sdk_frame_full_four_cups"],
                } for r in result["original_sdk_stage4_pour_observations"]]
            },sort_keys=True),flush=True)
    if len(rows)!=6:raise AssertionError("Missing genuine original SDK reset games")
    for case,_ in FROZEN:
        a,b=[r for r in rows if r["predeclared_case"]==case]
        if any(a[k]!=b[k] for k in
           ("original_stage3_last_action","original_sdk_stage4_pour_observations",
            "official_final_state","official_final_levels_completed")):
            raise AssertionError("Independent source witness diverges: "+case)
    report={
       "kind":"GENUINE_NATIVE_SP80_SDK_PUBLIC_OBSERVATION_AND_PROGRESSION_CONTRAST",
       "predeclared_source_cases":FROZEN,
       "independent_original_normal_sdk_resets":len(rows),
       "official_level5_or_WIN_cases":[r["predeclared_case"] for r in rows if r["official_level5_or_WIN"]],
       "final_level_histogram":dict(Counter(str(r["official_final_levels_completed"]) for r in rows)),
       "source_root_digest":"fa8fd32d3bfd2c8b3ff7765aec373512",
       "full_real_sdk_observation_and_frame_receipts":rows,
       "limits":"No hidden engine introspection; only actual original observation outputs, SDK levels and returned 64x64 frames. Original F3-48 mathematics unmodified.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**allframes)
    print("SP80_SDK_OBSERVATION_SUMMARY "+json.dumps({k:v for k,v in report.items() if
         k not in ("predeclared_source_cases","full_real_sdk_observation_and_frame_receipts")},sort_keys=True),flush=True)
if __name__=="__main__":main()
