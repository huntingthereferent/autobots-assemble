"""Original Arcade.NORMAL SP80: verified level4 entry and native source inventory.

PR #365 original run #39616395169 verified an actual official SP80
level3 -> level4 transition (not WIN), independently on A and B native
entry histories. The successful source-frozen stage3 word moves the
selected upper bar right2/down1, the other upper down1, the linked
middle assembly right4/up1, the far-left receiver up1/left10, and
the bottom catcher left3/up5, followed by a genuine ACTION5.

Source artifact #12352298969 independently returned the same newly
entered level4 64x64 board for both native witnesses. This study
replays the WHOLE exact original SDK entry, checks the official level
after EACH level's last source action, then inspects the actual stage4
source selection geometry/legal actions. Limited predeclared stage4
click/move/pour probes are genuine SDK actions, never a stage4 proxy.

Only official original SDK levels_completed>=5 or WIN establishes
new progress. There is no inferred hidden physics or image-only win.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

from .native_sp80_legal_pairs import PREFIX, legal, state, hash_frame
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_entry_source_map import STAGE2_VERIFIED_WORD
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components, scene
from .native_sp80_action5_frame_stacks import native_stack

STAGE3_WINNER = (
    "6@20,18 4 4 2 6@40,18 2 "
    "6@10,30 4 4 4 4 1 "
    "6@46,33 1 "+" ".join(["3"]*10)+" "
    "6@40,42 3 3 3 1 1 1 1 1 5"
)
# The original level4 root from artifact #12352298969 shows an
# original palette8 bar at x29..40,y20..22, a second palette8 bar
# x20..28,y32..34, and a palette9 selected bar x41..55,y32..34.
# All trial click pixels are direct readouts of that original frame;
# their actual pre-click palette is logged again after native entry.
FROZEN = (
    ("untouched_first_native_pour", "5"),
    ("upper_source_left1", "6@34,21 3 5"),
    ("upper_source_right1", "6@34,21 4 5"),
    ("upper_source_up1", "6@34,21 1 5"),
    ("upper_source_down1", "6@34,21 2 5"),
    ("middle_left_source_left1", "6@24,33 3 5"),
    ("middle_left_source_right1", "6@24,33 4 5"),
    ("middle_right_source_left1", "6@46,33 3 5"),
    ("middle_right_source_right1", "6@46,33 4 5"),
    ("middle_right_source_up1", "6@46,33 1 5"),
    ("palette15_region_click", "6@34,42 5"),
    ("background_click", "6@5,16 5"),
)
assert len(FROZEN)==12==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(word)[-1][0]==5
           and sum(a==5 for a,xy in parse_plan(word))==1
           and all(xy is not None for a,xy in parse_plan(word) if a==6)
           for _,word in FROZEN)
assert parse_plan(STAGE3_WINNER)[-1][0]==5
assert len(parse_plan(STAGE3_WINNER))==34

def run_case(case, stage1_witness, stage1_word, stage4_word):
    original=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=original.make("sp80")
    if env is None:raise RuntimeError("Original SDK SP80 game unavailable")
    obs=env.reset()
    source,shape=native_stack(obs)
    if source is None or int(getattr(obs,"levels_completed",-1))!=0:
        raise RuntimeError("Native original SDK reset failed")
    previous=np.asarray(source[-1]).copy()
    arrays={"reset":source}
    receipts=[]
    def do_step(action,xy,phase,index):
        nonlocal obs,previous
        advertised=legal(obs)
        before_level=int(getattr(obs,"levels_completed",-1))
        before_state=state(obs)
        if action not in advertised:raise RuntimeError("Real SDK action not advertised")
        kwargs={"data":{"x":int(xy[0]),"y":int(xy[1])}} if xy else {}
        pre_click=int(previous[xy[1],xy[0]]) if xy is not None else None
        before=previous.copy()
        output=env.step(getattr(GameAction,"ACTION"+str(action)),**kwargs)
        if output is None:raise RuntimeError("Null original SDK action return")
        frames,detail=native_stack(output)
        if frames is None or np.asarray(frames).shape[-2:]!=(64,64):
            raise RuntimeError("Missing genuine original source frames")
        previous=np.asarray(frames[-1]).copy()
        arrays[f"{phase}_{index}"]=frames
        after_level=int(getattr(output,"levels_completed",-1))
        row={
            "phase":phase,
            "index":index,
            "genuine_original_action":action,
            "real_native_click_xy":list(xy) if xy is not None else None,
            "original_source_pixel_before_click":pre_click,
            "original_sdk_level_before":before_level,
            "original_sdk_level_after":after_level,
            "original_sdk_state_before":before_state,
            "original_sdk_state_after":state(output),
            "original_legal_actions_before":advertised,
            "original_legal_actions_after":legal(output),
            "source_frame_before_blake2b16":hash_frame(before),
            "source_frame_after_blake2b16":hash_frame(previous),
            "original_sdk_frame_stack_count":len(frames),
            "original_source_stack_details":detail,
        }
        receipts.append(row)
        obs=output
        return row
    def enter(phase,word,target):
        actions=parse_plan(word)
        if not actions:raise RuntimeError("Empty source entrance")
        for i,(action,xy) in enumerate(actions,1):
            result=do_step(action,xy,phase,i)
            expected=target if i==len(actions) else target-1
            if result["original_sdk_level_after"]!=expected:
                raise RuntimeError(f"Original source {phase} changed level unexpectedly at {i}: {result['original_sdk_level_after']} != {expected}")
            if result["original_sdk_state_after"]!="NOT_FINISHED":
                raise RuntimeError("Original source game terminated during verified entrance")
    enter("entry0"," ".join(PREFIX),1)
    enter("entry1",stage1_word,2)
    enter("entry2",STAGE2_VERIFIED_WORD,3)
    enter("entry3",STAGE3_WINNER,4)
    root=previous.copy()
    if int(getattr(obs,"levels_completed",-1))!=4 or state(obs)!="NOT_FINISHED":
        raise AssertionError("No original native stage4")
    stage4={
        "original_sdk_entry_level":4,
        "original_sdk_entry_state":state(obs),
        "original_sdk_entry_legal_actions":legal(obs),
        "original_sdk_stage4_root_blake2b16":hash_frame(root),
        "genuine_stage4_source_grid":scene(root),
        "genuine_stage4_source_components":color_components(root),
    }
    for i,(action,xy) in enumerate(parse_plan(stage4_word),1):
        rec=do_step(action,xy,"stage4",i)
        if rec["original_sdk_level_after"]>=5 or rec["original_sdk_state_after"] in ("WIN","GAME_OVER"):
            break
    result={
        "original_independent_entry_witness":stage1_witness,
        "frozen_original_source_case":case,
        "original_verified_level3_to4_word":STAGE3_WINNER,
        "genuine_stage4_word":stage4_word,
        "native_original_stage4_entry":stage4,
        "true_original_sdk_final_level":int(getattr(obs,"levels_completed",-1)),
        "true_original_sdk_final_state":state(obs),
        "official_original_level5_or_WIN":int(getattr(obs,"levels_completed",-1))>=5 or state(obs)=="WIN",
        "genuine_original_stage4_action_ledger":[x for x in receipts if x["phase"]=="stage4"],
        "full_native_stage4_entry_receipts":{
            ph:[x for x in receipts if x["phase"]==ph]
            for ph in ("entry0","entry1","entry2","entry3")
        },
        "actual_original_frame_arrays_retained":list(arrays),
    }
    return result,arrays

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows=[];arrays={};roots=set()
    for case,word in FROZEN:
        for witness,entry in STAGE1_WITNESSES:
            item,frames=run_case(case,witness,entry,word)
            roots.add(item["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            rows.append(item)
            for step,stack in frames.items():
                arrays[f"{case}_{witness}_{step}"]=stack
            print("ORIGINAL_SP80_STAGE4_SOURCE_CASE "+json.dumps({
                "case":case,
                "witness":witness,
                "entry4":item["native_original_stage4_entry"]["original_sdk_entry_level"],
                "stage4_source_root":item["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"],
                "sdk_final_level":item["true_original_sdk_final_level"],
                "sdk_final_state":item["true_original_sdk_final_state"],
                "official_advance_to_level5":item["official_original_level5_or_WIN"],
                "stage4_real_action_ledger":item["genuine_original_stage4_action_ledger"],
            },sort_keys=True),flush=True)
    if len(rows)!=24 or len(roots)!=1:
        raise AssertionError("Independent genuine SDK stage4 source roots differ or are missing")
    for case,_ in FROZEN:
        matched=[x for x in rows if x["frozen_original_source_case"]==case]
        if len(matched)!=2 or matched[0]["true_original_sdk_final_level"]!=matched[1]["true_original_sdk_final_level"] or matched[0]["true_original_sdk_final_state"]!=matched[1]["true_original_sdk_final_state"]:
            raise AssertionError("Original source independent level4 trial differs: "+case)
    advances=[
        {"case":x["frozen_original_source_case"],
         "witness":x["original_independent_entry_witness"],
         "stage4_sdk_word":x["genuine_stage4_word"],
         "official_level":x["true_original_sdk_final_level"],
         "official_state":x["true_original_sdk_final_state"]}
        for x in rows if x["official_original_level5_or_WIN"]
    ]
    summary={
        "kind":"AUTHENTIC_ORIGINAL_SP80_STAGE4_ENTRY_AND_SOURCE_INVENTORY",
        "source_original_level4_witness_run":39616395169,
        "source_original_level4_winning_case":"catch_left3_up5",
        "genuine_independently_reset_sp80_games":len(rows),
        "original_stage3_to4_word":STAGE3_WINNER,
        "frozen_stage4_native_source_probes":FROZEN,
        "same_original_stage4_root_blake2b16":next(iter(roots)),
        "genuine_stage4_entry_original_source_grid":rows[0]["native_original_stage4_entry"]["genuine_stage4_source_grid"],
        "genuine_stage4_entry_source_components":rows[0]["native_original_stage4_entry"]["genuine_stage4_source_components"],
        "official_source_level5_or_WIN_count":len(advances),
        "original_sdk_level5_progress_cases":advances,
        "source_original_final_level_counts":dict(Counter(str(x["true_original_sdk_final_level"]) for x in rows)),
        "source_original_final_state_counts":dict(Counter(str(x["true_original_sdk_final_state"]) for x in rows)),
        "actual_original_sdk_entrance_and_stage4_receipts":rows,
        "limits":"Only native original SDK official level>=5 or WIN counts as progress. Stage4 source bars/colors are pixels, not decoded physics or inferred object identities. Complete SDK source returned frames preserved in NPZ.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_STAGE4_INVENTORY_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("genuine_stage4_entry_original_source_grid","genuine_stage4_entry_source_components","frozen_stage4_native_source_probes","actual_original_sdk_entrance_and_stage4_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
