"""Original SP80 NORMAL SDK: independent validation of published full-game
6/6 sequence, with OUR OWN two original full Stage0->4 SDK entrances.

The Stage4 fifth-level public 17-action witness from
synchopate/arc-agi-crystalline/solvers/recorded_solutions.json (indices
48..64) was already replicated independently under true original SDK
in run #40383702393: levels_completed 4->5, two native entry witnesses.

This follow-up continues THAT EXACT VERIFIED stage5 root through the
third-party published last 32 native actions (indices65..96). If it
reaches WIN it is an *attributed external positive-control replication*,
not an invention of our original ARC agent. Do not modify F3 laws,
canonical ARC worker or synthetic simulations.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from .native_sp80_legal_pairs import PREFIX,legal,state,hash_frame
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_entry_source_map import STAGE2_VERIFIED_WORD
from .native_sp80_stage4_entry_inventory import STAGE3_WINNER
from .native_sp80_stage4_public_positive_ab import EXTERNAL_PUBLISHED_ACTIONS
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_action5_frame_stacks import native_stack

EXTERNAL_FINAL_SIXTH_LEVEL=(
 "4 4 4 2 2 2 2 2 6@44,20 "
 "3 3 3 3 3 3 3 2 2 2 2 "
 "6@29,32 4 4 4 1 1 "
 "6@32,47 4 1 1 1 5"
)
assert len(parse_plan(EXTERNAL_PUBLISHED_ACTIONS))==17
assert len(parse_plan(EXTERNAL_FINAL_SIXTH_LEVEL))==32
assert [xy for a,xy in parse_plan(EXTERNAL_FINAL_SIXTH_LEVEL) if a==6]==[
 (44,20),(29,32),(32,47)]
EXPECTED_STAGE4_ROOT="fa8fd32d3bfd2c8b3ff7765aec373512"
EXPECTED_STAGE5_ROOT="633788a7d98fbec041de79dd1abf49f4"

def original_game(source_witness,stage1_word):
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=arcade.make("sp80")
    if env is None:raise RuntimeError("Genuine original SP80 game unavailable")
    obs=env.reset()
    frames,_=native_stack(obs)
    if frames is None or frames.shape[-2:]!=(64,64):
        raise AssertionError("Original SDK reset not 64x64")
    assert int(getattr(obs,"levels_completed",-1))==0
    prev=frames[-1].copy()
    store={"original_reset":frames}
    history=[];stage_roots={}
    phases=(
        ("original_level1", " ".join(PREFIX),1),
        ("original_level2", stage1_word,2),
        ("original_level3", STAGE2_VERIFIED_WORD,3),
        ("original_level4", STAGE3_WINNER,4),
        ("public_attributed_level5", EXTERNAL_PUBLISHED_ACTIONS,5),
        ("public_attributed_level6", EXTERNAL_FINAL_SIXTH_LEVEL,6),
    )
    for phase,word,target in phases:
        for i,(act,xy) in enumerate(parse_plan(word),1):
            legal_before=legal(obs);before_level=int(getattr(obs,"levels_completed",-1))
            if act not in legal_before:
                raise AssertionError("Original SDK next action not legal "+phase)
            palette=int(prev[xy[1],xy[0]]) if xy is not None else None
            kwargs={"data":{"x":int(xy[0]),"y":int(xy[1])}} if xy is not None else {}
            output=env.step(getattr(GameAction,"ACTION"+str(act)),**kwargs)
            if output is None:raise AssertionError("Native original SDK returned None")
            stack,detail=native_stack(output)
            if stack is None or stack.shape[-2:]!=(64,64):
                raise AssertionError("True original SDK frame returned invalid")
            prev=stack[-1].copy()
            after=int(getattr(output,"levels_completed",-1))
            current=state(output)
            row={
               "phase":phase,"original_native_action_index":i,
               "original_sdk_action":act,
               "true_original_click_xy":list(xy) if xy is not None else None,
               "actual_native_source_pixel_before_click":palette,
               "true_original_before_level":before_level,
               "true_original_after_level":after,
               "original_sdk_after_state":current,
               "true_original_returned_frame_count":int(len(stack)),
               "source_returned_last_frame_digest":hash_frame(prev),
               "source_frame_stack_details":detail
            }
            store[f"{phase}_{i}"]=stack
            history.append(row)
            obs=output
            expected=target if i==len(parse_plan(word)) else target-1
            if after!=expected:
                raise AssertionError(f"Native SDK entered unexpected level at {phase} action{i}: {after}!={expected}")
            if i<len(parse_plan(word)) and current in ("GAME_OVER","WIN"):
                raise AssertionError("Original SDK unexpectedly terminal before phase end")
        stage_roots[phase]=hash_frame(prev)
        if phase=="original_level4" and stage_roots[phase]!=EXPECTED_STAGE4_ROOT:
            raise AssertionError("Real Stage4 root changed from already-verified source")
        if phase=="public_attributed_level5" and stage_roots[phase]!=EXPECTED_STAGE5_ROOT:
            raise AssertionError("Real original Stage5 positive root mismatch")
        print("SP80_NATIVE_FULL_GAME_PHASE "+json.dumps({
           "stage":phase,"entry":source_witness,
           "true_original_levels_completed":int(getattr(obs,"levels_completed",-1)),
           "original_state":state(obs),"source_root_digest":stage_roots[phase],
           "native_actions":len(parse_plan(word)),
        },sort_keys=True),flush=True)
    return ({
      "source_entry_witness":source_witness,
      "kind":"TRUE_ORIGINAL_SP80_NORMAL_SDK_INDEPENDENT_PUBLIC_FINAL_LEVEL_REPLAY",
      "original_SDK_full_game_level":int(getattr(obs,"levels_completed",-1)),
      "original_SDK_full_game_state":state(obs),
      "official_original_full_six_levels_or_WIN":
          int(getattr(obs,"levels_completed",-1))>=6 or state(obs)=="WIN",
      "original_stage4_root":stage_roots["original_level4"],
      "original_stage5_root":stage_roots["public_attributed_level5"],
      "final_original_source_root_digest":stage_roots["public_attributed_level6"],
      "public_external_SDK_level5_word":EXTERNAL_PUBLISHED_ACTIONS,
      "public_external_SDK_level6_word":EXTERNAL_FINAL_SIXTH_LEVEL,
      "native_actual_action_receipts":history,
      "root_digest_per_verified_stage":stage_roots,
    },store)

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();f3=f3_calibration()
    rows=[];all_frames={}
    for witness,word in STAGE1_WITNESSES:
        report,stacks=original_game(witness,word)
        rows.append(report)
        for key,value in stacks.items():
            if (key=="original_reset" or key.startswith("public_attributed_") or
                key in ("original_level4_"+str(len(parse_plan(STAGE3_WINNER))),)):
                all_frames[f"{witness}_{key}"]=value
        print("SP80_TRUE_NATIVE_FULL_GAME_STATUS "+json.dumps({
           "entry":witness,"final_level":report["original_SDK_full_game_level"],
           "final_state":report["original_SDK_full_game_state"],
           "official_WIN":report["official_original_full_six_levels_or_WIN"],
           "final_frame_digest":report["final_original_source_root_digest"],
        },sort_keys=True),flush=True)
    if len(rows)!=2:raise AssertionError("Missing distinct independent original entry histories")
    for key in ("original_SDK_full_game_level","original_SDK_full_game_state",
                "official_original_full_six_levels_or_WIN","final_original_source_root_digest",
                "root_digest_per_verified_stage"):
        if rows[0][key]!=rows[1][key]:raise AssertionError("Two actual SDK entry histories disagreed "+key)
    report={
        "kind":"ORIGINAL_SP80_COMPLETE_SIX_LEVELS_EXTERNAL_PUBLIC_TRACE_INDEPENDENT_REPLAY",
        "source_public_comparator_url":"https://github.com/synchopate/arc-agi-crystalline/blob/main/solvers/recorded_solutions.json",
        "source_public_last_level_action_indices":[65,96],
        "genuine_original_independent_full_game_resets":len(rows),
        "official_six_of_six_WIN":bool(rows[0]["official_original_full_six_levels_or_WIN"]),
        "original_sdk_final_level":rows[0]["original_SDK_full_game_level"],
        "original_sdk_final_state":rows[0]["original_SDK_full_game_state"],
        "separate_exact_F3_math_rooted_certificate":f3,
        "all_original_sdk_source_and_action_receipts":rows,
        "limit":"External published source of two final action words is acknowledged. Only actual original Arcade.NORMAL SDK final level/state can demonstrate WIN. No canonical agent or F3 law altered.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**all_frames)
    print("SP80_TRUE_NATIVE_FULL_GAME_SUMMARY "+json.dumps({
       k:v for k,v in report.items() if k!="all_original_sdk_source_and_action_receipts"
    },sort_keys=True),flush=True)

if __name__=="__main__":main()
