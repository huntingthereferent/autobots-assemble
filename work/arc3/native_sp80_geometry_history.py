"""Native SP80 stage1: separate current visible geometry from action history.

Parent true-game #177 showed ACTUAL stage1 upper color8-band actions
11111333 and 33311111 both leave color9 bbox x8..27,y16..19.
ACTION5 after either showed same 130 native XY/color changes, unlike
ACTION6 (two bottom-row clears). Reconcile REAL pre-action screen
interiors and boundary rows, then test ACTION5 under:
  - reordered native movement history with same visible geometry;
  - one prior nonterminal ACTION6 versus ACTION5;
  - balanced movement prefixes 12 or 34 (interior-restoring at root);
  - an earlier original ACTION5/6 prefix.
No claim that the full native state is identical across histories.
Record SDK WIN/GAME_OVER and actual levels_completed after EVERY step.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from hashlib import blake2b
import json
from pathlib import Path

import numpy as np

from .native_sp80_legal_pairs import one

PATHS=("11111333","33311111")
WORDS=tuple(
    [base for base in PATHS]
    + [base+suffix for base in PATHS for suffix in ("5","6","65","56","55")]
    + [prefix+base+"5" for prefix in ("12","34","56") for base in PATHS]
)
RESETS=2
assert len(WORDS)==len(set(WORDS))==18
assert all(set(word)<={"1","2","3","4","5","6"} for word in WORDS)
assert RESETS==2


def digest(arr):
    return blake2b(np.ascontiguousarray(arr).tobytes(),digest_size=16).hexdigest()


def screen_view(arr):
    p=np.argwhere(arr==9)
    bounds=([int(p[:,1].min()),int(p[:,0].min()),
             int(p[:,1].max()),int(p[:,0].max())] if len(p) else None)
    return {
        "entire_native_frame_digest":digest(arr),
        "original_native_interior_digest":digest(arr[1:63]),
        "original_native_bottom_y63_digest":digest(arr[63]),
        "native_color9_bounds_xy":bounds,
        "native_color9_pixel_count":int(len(p)),
        "native_color8_pixel_count":int(np.count_nonzero(arr==8)),
        "native_bottom_y63_clear_pixels":int(np.count_nonzero(arr[63]==0)),
    }


def effect_source(trial,frames):
    source=[]
    for row in trial["source_effects"]:
        step=row["context_step"]
        if not row.get("native_complete_frame"):
            source.append({
                "step":step,"native_action":row["native_action"],
                "disposition":row.get("status","UNKNOWN_NO_SOURCE_FRAME")
            })
            continue
        ix=6+step
        if ix>=len(frames):
            raise AssertionError("Missing source frame at admitted original SDK action")
        before,after=frames[ix-1],frames[ix]
        y,x=np.nonzero(before!=after)
        effects=[{"xy":[int(px),int(py)],
                  "before":int(before[py,px]),
                  "after":int(after[py,px])} for py,px in zip(y,x)]
        old=row["actual_original_pixel_color_changes"]
        if effects!=old:
            raise AssertionError("Recorded source native frame effects disagree with arrays")
        interior=[q for q in effects if 1<=q["xy"][1]<=62]
        bottom=[q for q in effects if q["xy"][1]==63]
        if len(effects)!=len(interior)+len(bottom):
            # Top row changes are source evidence, never silently omitted.
            other=[q for q in effects if q["xy"][1]==0]
        else:other=[]
        source.append({
            "step":step,
            "native_action":row["native_action"],
            "prior_native_ACTION5_count":trial["word"][:step-1].count("5"),
            "prior_native_ACTION6_count":trial["word"][:step-1].count("6"),
            "preaction_screen":screen_view(before),
            "postaction_screen":screen_view(after),
            "all_native_pixel_color_changes":effects,
            "native_interior_pixel_color_changes":interior,
            "native_bottom_y63_pixel_color_changes":bottom,
            "other_original_boundary_changes":other,
            "interior_changed_count":len(interior),
            "bottom_changed_count":len(bottom),
            "original_SDK_level":row["official_after_levels_completed"],
            "original_SDK_state":row["official_after_state"],
        })
    return source


def summary(trials):
    word_results={}
    group=defaultdict(list)
    for t in trials:
        last=next((r for r in reversed(t["audited_native_source_actions"])
                   if r.get("native_action") in (5,6) and r.get("preaction_screen")),None)
        word_results.setdefault(t["word"],[]).append({
            "replicate":t["replicate"],
            "valid_native_actions":t["actual_accepted_complete_native_action_frames"],
            "native_state":t["last_reported_native_state"],
            "native_levels":t["last_reported_native_level"],
            "level2_or_WIN":t["progress_to_level2_or_native_WIN"],
            "disposition":t["status"],
            "last_native_action5_or6":({
                "step":last["step"],
                "native_action":last["native_action"],
                "original_preaction_color9_bounds":last["preaction_screen"]["native_color9_bounds_xy"],
                "original_preaction_interior_hash":last["preaction_screen"]["original_native_interior_digest"],
                "original_preaction_y63_hash":last["preaction_screen"]["original_native_bottom_y63_digest"],
                "prior_ACTION5_count":last["prior_native_ACTION5_count"],
                "prior_ACTION6_count":last["prior_native_ACTION6_count"],
                "native_color8_count_before":last["preaction_screen"]["native_color8_pixel_count"],
                "native_color8_count_after":last["postaction_screen"]["native_color8_pixel_count"],
                "native_interior_changed_cells":last["interior_changed_count"],
                "native_bottom_changed_cells":last["bottom_changed_count"],
                "original_color_pairs":dict(Counter(
                    str(a["before"])+"->"+str(a["after"])
                    for a in last["all_native_pixel_color_changes"])),
            } if last else None),
        })
        if last:
            key=(last["native_action"],
                 last["preaction_screen"]["original_native_interior_digest"])
            group[key].append({
                "word":t["word"],"replicate":t["replicate"],
                "native_action_step":last["step"],
                "prior_ACTION5":last["prior_native_ACTION5_count"],
                "prior_ACTION6":last["prior_native_ACTION6_count"],
                "bottom_hash":last["preaction_screen"]["original_native_bottom_y63_digest"],
                "source_interior_effect":last["native_interior_pixel_color_changes"],
            })
    # Same source-screen INTERIOR but distinct native history/elapsed frontier.
    comparisons=[]
    for (action,interior_hash),members in group.items():
        words=set(x["word"] for x in members)
        if len(words)<2:continue
        effects={json.dumps(x["source_interior_effect"],sort_keys=True)
                 for x in members}
        comparisons.append({
            "native_action":action,"same_preaction_interior_hash":interior_hash,
            "words":sorted(words),"native_sessions":len(members),
            "distinct_original_native_interior_effects":len(effects),
            "historical_conditions":[{
                "word":x["word"],"replicate":x["replicate"],
                "prior_ACTION5":x["prior_ACTION5"],
                "prior_ACTION6":x["prior_ACTION6"],
                "preaction_y63_hash":x["bottom_hash"],
            } for x in members],
            "same_screen_interior_sufficient_in_this_group":len(effects)==1,
        })
    return {"per_word":word_results,
            "matching_preaction_interior_comparisons":comparisons}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    evidence,stacks=[],{}
    for word in WORDS:
        for replicate in range(RESETS):
            native,frames=one(word,replicate)
            native["audited_native_source_actions"]=effect_source(native,frames)
            evidence.append(native)
            stacks[f"word_{word}_reset{replicate}"]=frames
    results=summary(evidence)
    out={
        "kind":"SP80_REAL_NATIVE_ACTION5_GEOMETRY_VERSUS_HISTORY",
        "predeclared_reordered_root_paths":PATHS,
        "predeclared_all_words":WORDS,
        "independent_native_resets_per_word":RESETS,
        "original_SDK_resets":len(evidence),
        "original_native_context_actions":sum(
            x["actual_accepted_complete_native_action_frames"] for x in evidence),
        "real_SDK_level2_or_WIN":sum(
            int(x["progress_to_level2_or_native_WIN"]) for x in evidence),
        "native_dispositions":dict(Counter(x["status"] for x in evidence)),
        "observed":results,
        "original_game_trial_records":evidence,
        "limits":"Native original SP80 Arcade.NORMAL, real observed action 1–6 stage1. Identical visible interior is not identical full 64x64 or hidden state. Original SDK WIN/levels are sole objective metric. This is source discovery, not a universal history-independence proof or original F3 mathematical mapping.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**stacks)
    print("SP80_GEOMETRY_HISTORY "+json.dumps(
        {k:v for k,v in out.items() if k!="original_game_trial_records"},
        sort_keys=True))
    if len(evidence)!=len(WORDS)*RESETS:
        raise RuntimeError("Insufficient real original SDK trials")


if __name__=="__main__":
    main()
