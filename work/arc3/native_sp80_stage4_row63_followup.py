"""Original native SP80 row63-history follow-up under identical later actions.

Two independently observed pairs enter the same visible interior and selected
bbox but different row63. Apply ONE common re-click, or re-click+LEFT1,
then source-observe the first ACTION5. This tests propagation of a measured
difference without assuming row63 is an engine memory or a timer.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np

from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame
from .native_sp80_stage4_upper_endpoint_history import (
    PARENT, CUPS, source_observations, actual_frame_pair,
)

# Frozen as pairs of histories followed by IDENTICAL later original SDK actions.
# Every case uses a new SDK reset; no single run is reused as a witness.
FROZEN=(
    ("zero_click",       "",      "6@34,21"),
    ("roundtrip_click",  "4 3",   "6@34,21"),
    ("right_click",      "4",     "6@34,21"),
    ("detour_click",     "3 4 4", "6@34,21"),
    ("zero_click_left",      "",      "6@34,21 3"),
    ("roundtrip_click_left", "4 3",   "6@34,21 3"),
    ("right_click_left",     "4",     "6@34,21 3"),
    ("detour_click_left",    "3 4 4", "6@34,21 3"),
)
PAIRS=(
    ("zero_click","roundtrip_click"),
    ("right_click","detour_click"),
    ("zero_click_left","roundtrip_click_left"),
    ("right_click_left","detour_click_left"),
)
assert len(FROZEN)==8==len({n for n,_,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2

def original_word(history, challenge):
    return " ".join(part for part in (PARENT,history,challenge,"5") if part)

def snapshot_pair(left,right):
    assert left.shape==right.shape==(64,64)
    changed=left!=right
    ys,xs=np.nonzero(changed)
    return {
        "full_grid_equal":bool(not len(xs)),
        "row0_62_equal":bool(np.array_equal(left[:63],right[:63])),
        "row63_equal":bool(np.array_equal(left[63],right[63])),
        "changed_pixels":int(len(xs)),
        "interior_changed_pixels":int(np.count_nonzero(changed[:63])),
        "row63_changed_pixels":int(np.count_nonzero(changed[63])),
        "first_changed_pixel_xy":[int(xs[0]),int(ys[0])] if len(xs) else None,
        "left_hash":hash_frame(left),"right_hash":hash_frame(right),
    }

def selected_bbox(frame):
    yy,xx=np.nonzero(frame==9)
    if not len(xx):
        raise AssertionError("source selected upper highlight absent")
    return [int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]

def run():
    trials=[];stored={};rawpairs={};roots=set()
    for name,history,challenge in FROZEN:
        word=original_word(history,challenge)
        actions=parse_plan(word)
        before_n=len(parse_plan(" ".join(p for p in (PARENT,history) if p)))
        challenge_length=len(parse_plan(challenge))
        if (actions[-1][0]!=5 or sum(a==5 for a,_ in actions)!=1 or
                len(actions)-before_n-1!=challenge_length or
                challenge_length not in (1,2)):
            raise AssertionError("source-frozen history or later actions altered")
        for witness,entry in STAGE1_WITNESSES:
            native,frames=run_case(name,witness,entry,word)
            root=frames["entry3_34"][-1]
            parent_end=frames["stage4_"+str(before_n)][-1]
            challenge_end=frames["stage4_"+str(len(actions)-1)][-1]
            animation=frames["stage4_"+str(len(actions))]
            roots.add(hash_frame(root))
            measured=source_observations(root,challenge_end,animation)
            source={
                "parent_end_frame_hash":hash_frame(parent_end),
                "parent_end_selected_bbox":selected_bbox(parent_end),
                "challenge_end_frame_hash":hash_frame(challenge_end),
                "challenge_end_selected_bbox":selected_bbox(challenge_end),
                "challenge_action_count":challenge_length,
                "source_cups":measured,
                "native_parent_end_row63":parent_end[63].astype(int).tolist(),
                "native_challenge_end_row63":challenge_end[63].astype(int).tolist(),
            }
            stage4=native["genuine_original_stage4_action_ledger"]
            if (len(stage4)!=len(actions) or
                    [item["genuine_original_action"] for item in stage4[-challenge_length-1:]]
                    !=[action for action,_ in actions[-challenge_length-1:]]):
                raise AssertionError("original SDK challenge and pour receipt incomplete")
            trials.append({
                "case":name,"witness":witness,
                "original_source_word":word,
                "original_history":history,"common_challenge":challenge,
                "official_level":native["true_original_sdk_final_level"],
                "official_state":native["true_original_sdk_final_state"],
                "official_level5_or_WIN":native["official_original_level5_or_WIN"],
                "source":source,
                "genuine_stage4_action_ledger":stage4,
            })
            rawpairs[(name,witness)]=(parent_end.copy(),challenge_end.copy(),animation.copy())
            for key,values in frames.items():
                stored[name+"_"+witness+"_"+key]=values
            print("ARC4_ROW63_NATIVE_CASE "+json.dumps({
                "case":name,"witness":witness,
                "original_sdk_level":native["true_original_sdk_final_level"],
                "original_sdk_state":native["true_original_sdk_final_state"],
                "selected_before_challenge":source["parent_end_selected_bbox"],
                "selected_after_challenge":source["challenge_end_selected_bbox"],
                "source_cup_first_full":measured["first_full_cup_frames"],
            },sort_keys=True),flush=True)
    if len(trials)!=16 or len(roots)!=1:
        raise AssertionError("original source roots/resets not independently witnessed")
    for name,_,_ in FROZEN:
        aa,bb=[t for t in trials if t["case"]==name]
        if (aa["witness"],bb["witness"])!=("A","B") or any(
            aa[key]!=bb[key] for key in ("official_level","official_state",
                                        "official_level5_or_WIN","source")
        ):
            raise AssertionError("independent original SDK witness conflict: "+name)
    pairs={}
    for lhs,rhs in PAIRS:
        checks=[]
        for witness,_ in STAGE1_WITNESSES:
            pa,ca,fa=rawpairs[(lhs,witness)]
            pb,cb,fb=rawpairs[(rhs,witness)]
            source_pre=snapshot_pair(pa,pb)
            if (not source_pre["row0_62_equal"] or source_pre["row63_equal"]
                    or selected_bbox(pa)!=selected_bbox(pb)):
                raise AssertionError("earlier independently witnessed matched-endpoint contrast lost")
            checks.append({
                "source_prechallenge":source_pre,
                "source_after_common_challenge":snapshot_pair(ca,cb),
                "source_pour_animation":actual_frame_pair((ca,fa),(cb,fb)),
                "source_equal_official_sdk_status":next(x for x in trials if x["case"]==lhs and x["witness"]==witness)["official_level"] ==
                    next(x for x in trials if x["case"]==rhs and x["witness"]==witness)["official_level"],
            })
        if checks[0]!=checks[1]:
            raise AssertionError("independent source pair comparison differs for "+lhs+" / "+rhs)
        pairs[lhs+"_vs_"+rhs]=checks[0]
    return trials,stored,roots,pairs

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    trials,archive,roots,pairs=run()
    result={
        "kind":"ORIGINAL_ARC4_ROW63_HISTORY_COMMON_CHALLENGE",
        "referent":"Original SP80 native row63 matched-endpoint history versus later shared action response",
        "parent_run_id":40125152426,
        "original_sdk_resets":len(trials),
        "frozen_parent":PARENT,"frozen_controls":FROZEN,"frozen_pairs":PAIRS,
        "source_root_hash":next(iter(roots)),
        "official_level_histogram":dict(Counter(str(t["official_level"]) for t in trials)),
        "official_level5_or_WIN_count":sum(int(t["official_level5_or_WIN"]) for t in trials),
        "native_cases":trials,"native_pairwise_relations":pairs,
        "wall":"Frame row63 is visible source evidence, not established internal-state memory or a causal engine variable.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**archive)
    print("ARC4_ROW63_NATIVE_SUMMARY "+json.dumps({
        "official_levels":result["official_level_histogram"],
        "progress":result["official_level5_or_WIN_count"],
        "native_resets":result["original_sdk_resets"],
        "pair_results":pairs,
        "full_cups":{name:next(t["source"]["source_cups"] for t in trials if t["case"]==name)["maximum_original_cup13_pixels"]
                     for name,_,_ in FROZEN},
    },sort_keys=True),flush=True)
if __name__=="__main__":
    main()
