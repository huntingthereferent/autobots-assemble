"""Real original SP80 stage3 selection-order and next-pour response.

Native run #39560629170 measured five source-selected mask classes in
the initial stage3 scene. The source-falsified middle-piece independence
hypothesis is recorded in PR #349. The next bounded question is whether
the *same final physical source positions* with different LAST selected
group or click history changes the true SDK ACTION5 response.

Every probe first executes the same fixed original stage3 placement
word. Then exactly one or two ACTION6 clicks change selection WITHOUT
a movement. The true SDK source pre-pour selection, original source
normalized pixels, SDK receipts and complete ACTION5 frames are retained.
Equal-click-count pairings avoid confounding from the step budget.
No guessed flow engine or image-only win rules are used.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

UPPER="6@20,18 4 4 2 6@40,18 2"
MIDDLE="6@10,30 4 4 4 4"
LOWER="6@46,33 1 "+" ".join(["3"]*10)
BOTTOM="6@40,42 4"
PREFIX=" ".join((UPPER,MIDDLE,LOWER,BOTTOM))
CUPS=((8,16),(26,34),(38,46),(50,58))
# Actual post-placement clicks are selected from original SDK source
# frame position observations, NOT the old stage3 start coordinates.
PROBES=(
    ("background",(3,3)),
    ("upper_left",(30,21)),
    ("upper_right",(40,21)),
    ("linked_middle",(30,30)),
    ("lower_receiver",(16,30)),
    ("bottom_catcher",(45,42)),
)
PROBE=dict(PROBES)

def clicks(*names):
    return " ".join("6@%d,%d"%PROBE[name] for name in names)

FROZEN=(
    ("one_background",("background",)),
    ("one_upper_left",("upper_left",)),
    ("one_upper_right",("upper_right",)),
    ("one_middle",("linked_middle",)),
    ("one_lower",("lower_receiver",)),
    ("one_bottom",("bottom_catcher",)),
    ("two_middle_bottom",("linked_middle","bottom_catcher")),
    ("two_bottom_middle",("bottom_catcher","linked_middle")),
    ("two_background_middle",("background","linked_middle")),
    ("two_middle_background",("linked_middle","background")),
    ("two_upper_left_upper_right",("upper_left","upper_right")),
    ("two_upper_right_upper_left",("upper_right","upper_left")),
)
assert len(FROZEN)==12==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(1<=len(steps)<=2 for _,steps in FROZEN)

def digest(binary):
    return hashlib.sha256(np.ascontiguousarray(binary).tobytes()).hexdigest()

def source_geometry(frame):
    # Actual frame normalization used only to compare rendered bar
    # geometry, not assert hidden object position or image equivalence.
    observed=np.asarray(frame).copy()
    observed[observed==9]=8  # selected bar rendered blue
    observed[:8,:]=0  # remove step meter differences
    return digest(observed)

def source_readout(pre,returned):
    if pre.shape!=(64,64) or returned.ndim!=3 or returned.shape[1:]!=(64,64):
        raise AssertionError("Actual original source frames missing")
    first4=None
    firstedge=None
    cup_frames=[None]*4
    flow=[]
    for i,frame in enumerate(returned):
        blue=(pre!=6)&(frame==6)
        flow.append(blue.astype(np.uint8))
        counts=[
            int(np.count_nonzero(
                (pre[53:59,a:b+1]==11)&(frame[53:59,a:b+1]==13)
            )) for a,b in CUPS
        ]
        for j,count in enumerate(counts):
            if count==45 and cup_frames[j] is None:cup_frames[j]=i
        if first4 is None and all(c==45 for c in counts):
            first4=i
        edge=(pre[59:63,2:62]!=frame[59:63,2:62])
        if firstedge is None and edge.any():
            firstedge={
                "frame":i,
                "original_bottom_test_pixel_count":int(edge.sum()),
                "native_new_palette6_x_at_y58":[
                    int(x) for x in np.flatnonzero(blue[58])
                ],
            }
    comps=[
        {"bbox":c["bbox"],"pixels":c["pixels"]}
        for c in color_components(pre) if c["palette"]==9
    ]
    return {
        "genuine_original_source_prepour_blake2b16":hash_frame(pre),
        "original_prepour_normalized_appearance_sha256":source_geometry(pre),
        "original_source_selected_palette9_components":comps,
        "source_prepour_selected_mask_sha256":digest((pre==9).astype(np.uint8)),
        "actual_original_sdk_animation_frame_count":len(returned),
        "source_flow_color6_appearance_sha256":digest(np.stack(flow)),
        "source_cup_first_full_frame":cup_frames,
        "source_first_simultaneous_four_cup_frame":first4,
        "source_first_changed_tested_bottom_boundary":firstedge,
        "true_sdk_returned_final_frame_blake2b16":hash_frame(returned[-1]),
        "scope":"Comparisons are of original SDK pixels and known input counts only; not proof of private engine identity or win predicate.",
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    receipts=[];native_frames={};roots=set()
    for name,steps in FROZEN:
        word=" ".join((PREFIX,clicks(*steps),"5"))
        parsed=parse_plan(word)
        assert parsed[-1][0]==5
        assert sum(a==5 for a,xy in parsed)==1
        assert len([a for a,xy in parsed if a==6])>=len(steps)
        for witness,entry in STAGE1_WITNESSES:
            sdk,frames=real_trial(witness,entry,name,word)
            roots.add(sdk["original_verified_stage3_root"]["original_source_sha256"])
            n=len(parsed)
            pre=frames["stage3_"+str(n-1)][-1]
            pouring=frames["stage3_"+str(n)]
            readout=source_readout(pre,pouring)
            last_click_receipts=[
                {k:v for k,v in event.items()
                 if k!="full_original_source_frame_ledger"}
                for event in sdk["original_stage3_intervention_events"][n-1-len(steps):n-1]
            ]
            if len(last_click_receipts)!=len(steps) or any(x["original_action"]!=6 for x in last_click_receipts):
                raise AssertionError("Original SDK late click inputs not preserved")
            record={
                "precommitted_native_case":name,
                "original_source_last_click_names":steps,
                "native_last_click_count":len(steps),
                "independent_native_entry":witness,
                "genuine_original_sdk_action_word":word,
                "original_sdk_official_final_level":sdk["official_original_final_level"],
                "original_sdk_official_final_state":sdk["official_original_final_state"],
                "original_sdk_advanced_level4_or_WIN":sdk["official_original_level4_or_WIN"],
                "actual_original_last_click_receipts":last_click_receipts,
                "original_sdk_source_observations":readout,
            }
            receipts.append(record)
            for stage,arr in frames.items():
                native_frames[f"{name}_{witness}_{stage}"]=arr
            print("ORIGINAL_SP80_LAST_SELECTION_CASE "+json.dumps({
                "case":name,"witness":witness,
                "true_original_level":record["original_sdk_official_final_level"],
                "true_original_state":record["original_sdk_official_final_state"],
                "source":readout,
                "last_clicked_source_pixels":[x.get("actual_source_preclick_palette") for x in last_click_receipts],
            },sort_keys=True),flush=True)
    if len(receipts)!=24 or len(roots)!=1:
        raise AssertionError("Missing independent true SDK original entries")
    group=defaultdict(list)
    for r in receipts:
        obs=r["original_sdk_source_observations"]
        key=(r["native_last_click_count"],obs["original_prepour_normalized_appearance_sha256"])
        group[key].append(r)
    comparisons=[]
    for (count,render),entries in sorted(group.items(),key=lambda x:str(x[0])):
        if len(entries)<2:continue
        outcome={(r["original_sdk_official_final_level"],
                  r["original_sdk_official_final_state"],
                  r["original_sdk_source_observations"]["source_flow_color6_appearance_sha256"],
                  r["original_sdk_source_observations"]["source_first_simultaneous_four_cup_frame"],
                  json.dumps(r["original_sdk_source_observations"]["source_first_changed_tested_bottom_boundary"],sort_keys=True)
                  ) for r in entries}
        comparisons.append({
            "same_late_click_count":count,
            "matching_observed_normalized_prepour_image_sha256":render,
            "native_original_cases":[{"case":r["precommitted_native_case"],"witness":r["independent_native_entry"],
                  "actual_last_selected_mask":r["original_sdk_source_observations"]["source_prepour_selected_mask_sha256"],
                  "source_flow_sha256":r["original_sdk_source_observations"]["source_flow_color6_appearance_sha256"]}
                 for r in entries],
            "distinct_native_observed_outcomes":len(outcome),
        })
    gains=[{
        "case":r["precommitted_native_case"],"witness":r["independent_native_entry"],
        "word":r["genuine_original_sdk_action_word"]}
        for r in receipts if r["original_sdk_advanced_level4_or_WIN"]]
    result={
        "kind":"AUTHENTIC_ORIGINAL_SP80_STAGE3_LAST_SELECTION_RESPONSE",
        "antecedent_selection_class_run":39560629170,
        "original_independent_sdk_reset_games":len(receipts),
        "fixed_original_native_stage3_placement_word":PREFIX,
        "precommitted_postplacement_click_sequences":FROZEN,
        "authentic_original_level3_source_root_blake2b16":next(iter(roots)),
        "true_sdk_level4_or_WIN_count":len(gains),
        "official_source_witnesses":gains,
        "official_source_level_histogram":dict(Counter(str(r["original_sdk_official_final_level"]) for r in receipts)),
        "official_source_state_histogram":dict(Counter(str(r["original_sdk_official_final_state"]) for r in receipts)),
        "native_same_observed_geometry_and_click_budget_comparisons":comparisons,
        "original_native_sdk_records":receipts,
        "limitations":"All groupings depend on observed source normalized pixels and SDK inputs, not decoded hidden engine state. Flow6 appearance may reflect render selection; only true original SDK level>=4/WIN establishes progress. Full source frame arrays retained in NPZ.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**native_frames)
    print("ORIGINAL_SP80_LAST_SELECTION_SUMMARY "+json.dumps({
        k:v for k,v in result.items() if k not in (
            "precommitted_postplacement_click_sequences","original_native_sdk_records"
        )
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
