"""Genuine original SP80 stage0 ACTION5: actual SDK level-change response contrast.

From prior true original native 454545 witnessed level0 -> level1
only on the final source action. The SDK returned 22, 28 and 20
real 64x64 images on successive ACTION5 calls. These are prior
observations, NOT a universal clock rule or a known win criterion.

Prospectively replay distinct legitimate original stage0 action
histories with independent fresh source resets. Save EVERY real
SDK obs.frame returned image and per-image XY/native-color events.
Label advancing vs nonadvancing only by the official SDK's change in
levels_completed and terminal state. Stop on first genuine change,
WIN, GAME_OVER, or unknown/nonstandard response.

No synthetic SP80, hidden mechanics, autonomous solver, mathematical
F3-48 source-action identity, or unobserved animation reconstruction.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

from .native_sp80_legal_pairs import state,legal,hash_frame
from .native_sp80_action5_frame_stacks import (
    native_stack,frame_record_before_after
)

WORDS=(
    ("known_advancing_454545","454545"),
    ("stop_before_advancing_45454","45454"),
    ("known_prefix_plus_45","45454545"),
    ("reversed_545454","545454"),
    ("alt_4454545","4454545"),
    ("alt_5445454","5445454"),
    ("alt_454544","454544"),
    ("alt_454455","454455"),
    ("alt_454554","454554"),
    ("alt_4545445","4545445"),
    ("alt_5454454","5454454"),
    ("alt_444555","444555"),
    ("alt_555444","555444"),
    ("alt_44454545","44454545"),
)
RESETS=2
assert len(WORDS)==len({n for n,_ in WORDS})==14
assert RESETS==2
assert all(word and set(word)<={"4","5"} for _,word in WORDS)


def native_source_image_counts(a):
    return {
        "native_color6_count":int(np.count_nonzero(a==6)),
        "native_color9_count":int(np.count_nonzero(a==9)),
        "native_color11_count":int(np.count_nonzero(a==11)),
        "native_color14_count":int(np.count_nonzero(a==14)),
    }


def stage0_original_trial(name,word,replicate):
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env=arcade.make("sp80")
    if env is None:raise RuntimeError("Original SDK SP80 unavailable")
    obs=env.reset()
    root,meta=native_stack(obs)
    if root is None:raise RuntimeError("Native reset has no complete original frames")
    if int(getattr(obs,"levels_completed",-1))!=0:
        raise RuntimeError("Native root is not original level0")
    raw={"reset":root}
    previous=root[-1]
    events=[]
    disposition=None
    for step,letter in enumerate(word,1):
        aid=int(letter)
        before_level=int(getattr(obs,"levels_completed",-1))
        before_state=state(obs)
        advertised=legal(obs)
        if aid not in advertised:
            events.append({"original_word_step":step,"native_action":aid,
                          "admission":"UNKNOWN_ACTION_WITHDRAWN",
                          "SDK_advertised_before":advertised})
            disposition="UNKNOWN_ACTION_WITHDRAWN"
            break
        pre_snapshot=previous.copy()
        response=env.step(getattr(GameAction,"ACTION"+letter))
        if response is None:
            events.append({"original_word_step":step,"native_action":aid,
                           "admission":"UNKNOWN_NULL_SDK_RESPONSE"})
            disposition="UNKNOWN_NULL_SDK_RESPONSE"
            break
        after_level=int(getattr(response,"levels_completed",-1))
        after_state=state(response)
        stack,shape=native_stack(response)
        advanced=after_level>before_level or after_state=="WIN"
        event={
            "original_word_step":step,
            "native_action":aid,
            "pre_SDK_level":before_level,
            "post_SDK_level":after_level,
            "pre_SDK_state":before_state,
            "post_SDK_state":after_state,
            "SDK_win_levels":int(getattr(response,"win_levels",-1)),
            "SDK_available_before":advertised,
            "SDK_available_after":legal(response),
            "native_SDK_level_increase":after_level>before_level,
            "native_SDK_WIN":after_state=="WIN",
            "SDK_source_response":shape,
            "source_preimage_hash":hash_frame(pre_snapshot),
            "source_preimage_palette_counts":native_source_image_counts(pre_snapshot),
            "prior_ACTION5_count":sum(int(x.get("native_action")==5) for x in events),
        }
        if stack is None:
            event["source_frame_admission"]="UNKNOWN_NONSTANDARD_NATIVE_RESPONSE"
            disposition=("SDK_TERMINAL_"+after_state
                         if after_state in ("WIN","GAME_OVER") else
                         "UNKNOWN_NONSTANDARD_NATIVE_RESPONSE")
        else:
            raw["action_"+str(step)]=stack
            event["actual_SDK_frame_sequence"]=frame_record_before_after(previous,stack)
            event["native_color_counts_per_actual_returned_frame"]=[
                native_source_image_counts(frame) for frame in stack]
            event["native_last_frame_hash"]=hash_frame(stack[-1])
            event["source_frame_admission"]="ADMITTED_ALL_RETURNED_IMAGES"
            previous=stack[-1]
        events.append(event)
        obs=response
        if after_state in ("WIN","GAME_OVER"):
            disposition="SDK_TERMINAL_"+after_state
            break
        if after_level!=before_level:
            disposition="SDK_LEVEL_CHANGED"
            break
        if stack is None:break
    final_level=int(getattr(obs,"levels_completed",-1))
    return {
        "name":name,"frozen_original_word":word,"replicate":replicate,
        "genuine_original_native_reset_frame_count":len(root),
        "SDK_native_level_at_end":final_level,
        "SDK_native_state_at_end":state(obs),
        "genuine_level0_to_level1_or_higher":final_level>=1,
        "SDK_NATIVE_WIN":state(obs)=="WIN",
        "source_disposition":disposition or "COMPLETE",
        "genuine_source_action_records":events,
        "actual_SDK_action_count":sum(
            "pre_SDK_level" in e for e in events),
        "original_native_last_image_hash":hash_frame(previous),
        "native_original_level0_ACTION5_observations":[{
            "original_word_step":e["original_word_step"],
            "prior_ACTION5_count":e.get("prior_ACTION5_count"),
            "native_frames":e.get("actual_SDK_frame_sequence",{}).get("true_original_returned_frames"),
            "native_SDK_level_increase":e.get("native_SDK_level_increase"),
            "SDK_win":e.get("native_SDK_WIN"),
        } for e in events if e["native_action"]==5],
    },raw


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    records,raw={},{}
    all_records=[]
    for name,word in WORDS:
        for replicate in range(RESETS):
            record,frames=stage0_original_trial(name,word,replicate)
            all_records.append(record)
            raw.update({f"{name}_reset{replicate}_{phase}":arr
                       for phase,arr in frames.items()})
    emitted=[e for r in all_records for e in r["genuine_source_action_records"]
             if "actual_SDK_frame_sequence" in e]
    action5=[e for e in emitted if e["native_action"]==5]
    positive=[e for e in action5 if e["native_SDK_level_increase"] or e["native_SDK_WIN"]]
    negative=[e for e in action5 if not(e["native_SDK_level_increase"] or e["native_SDK_WIN"])]
    byword={}
    for name,word in WORDS:
        group=[r for r in all_records if r["name"]==name]
        byword[name]={
            "frozen_native_actions":word,
            "genuine_resets":len(group),
            "original_native_progress":[r["SDK_native_level_at_end"] for r in group],
            "native_SDK_state":[r["SDK_native_state_at_end"] for r in group],
            "source_disposition":[r["source_disposition"] for r in group],
            "genuine_SDK_action_counts":[r["actual_SDK_action_count"] for r in group],
            "native_ACTION5_frame_length_by_trial":[{
                "replicate":r["replicate"],
                "observations":r["native_original_level0_ACTION5_observations"],
            } for r in group],
        }
    result={
        "kind":"ORIGINAL_SP80_GENUINE_STAGE0_ACTION5_PROGRESS_VS_NONPROGRESS",
        "frozen_native_words":WORDS,
        "independently_reset_original_games_per_word":RESETS,
        "original_SDK_resets":len(all_records),
        "true_source_action_responses":sum(r["actual_SDK_action_count"] for r in all_records),
        "actual_valid_original_SDK_returned_full_frame_actions":len(emitted),
        "actual_returned_full_64x64_source_images":sum(
            e["actual_SDK_frame_sequence"]["true_original_returned_frames"] for e in emitted),
        "original_stage0_ACTION5_with_frame_stacks":len(action5),
        "real_source_level_advancing_ACTION5_count":len(positive),
        "real_source_nonadvancing_ACTION5_count":len(negative),
        "native_level0_ACTION5_frame_lengths_if_ADVANCED":dict(Counter(
            str(e["actual_SDK_frame_sequence"]["true_original_returned_frames"])
            for e in positive)),
        "native_level0_ACTION5_frame_lengths_if_NO_PROGRESS":dict(Counter(
            str(e["actual_SDK_frame_sequence"]["true_original_returned_frames"])
            for e in negative)),
        "all_native_level0_progress_resets":sum(int(
            r["genuine_level0_to_level1_or_higher"]) for r in all_records),
        "original_SDK_dispositions":dict(Counter(r["source_disposition"] for r in all_records)),
        "per_frozen_word":byword,
        "full_native_source_trial_evidence":all_records,
        "limits":"Original SP80 Arcade.NORMAL true SDK, complete ordered obs.frame stacks. Progress labels use source SDK levels_completed and state, NOT frame count or colors. This stage0 0->1 witness is not evidence of a level1->2 solution or universal timing cause. Preserve all source counterexamples and UNKNOWN responses; no source F3-48 mathematical mapping.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_STAGE0_ADVANCE_CONTRAST "+json.dumps({
        k:v for k,v in result.items()
        if k not in ("full_native_source_trial_evidence",)
    },sort_keys=True))
    if len(all_records)!=len(WORDS)*RESETS:
        raise RuntimeError("Missing genuine original SP80 reset")


if __name__=="__main__":
    main()
