"""Original SDK SP80 stage3: empirical equivalence of click selection regions.

Source run #39560139856 disproved treating two 27px red mid-sections
as independently selectable; x10 and x22 can select a linked 54px
middle assembly around the 9px spout marker. Before composing any
more routing words, explicitly enumerate observed selection outcomes
of coordinate-bearing ACTION6 from freshly reset ORIGINAL level3 and
the displacement under one actual ACTION4. Do not infer object identity
from visually disconnected color components alone.

All observations are original arc_agi.Arcade(OperationMode.NORMAL)
source frames. No substitute game, guessed physics or proxy win.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import hashlib,json
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

# Source grid target coordinates are from two independently verified
# true SDK stage3 entry screens; marker/empty are negative controls.
PROBES=(
    ("upper_selected_red",(20,18)),
    ("upper_other_red",(40,18)),
    ("middle_left_red",(10,30)),
    ("middle_right_red",(22,30)),
    ("middle_dark_marker",(18,30)),
    ("lower_right_red",(46,33)),
    ("bottom_right_red",(40,42)),
    ("far_background",(3,3)),
)
assert len(PROBES)==8==len({name for name,xy in PROBES})
assert len(STAGE1_WITNESSES)==2

def components(frame,palette):
    return [
        {"bbox":c["bbox"],"pixels":c["pixels"]}
        for c in color_components(frame) if c["palette"]==palette
    ]

def selected_mask_sha(frame):
    mask=(frame==9).astype(np.uint8)
    return hashlib.sha256(mask.tobytes()).hexdigest()

def original_selected(frame):
    return {
        "selected_pixel_count":int(np.count_nonzero(frame==9)),
        "selected_original_palette9_components":components(frame,9),
        "movable_spout_palette4_components":components(frame,4),
        "native_selected_mask_sha256":selected_mask_sha(frame),
        "original_frame_blake2b16":hash_frame(frame),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    rows=[];raw={};roots=set()
    for name,xy in PROBES:
        word=f"6@{xy[0]},{xy[1]} 4"
        for witness,entry in STAGE1_WITNESSES:
            sdk,stacks=real_trial(witness,entry,name,word)
            roots.add(sdk["original_verified_stage3_root"]["original_source_sha256"])
            before=stacks["entry2_11"][-1]
            after_click=stacks["stage3_1"][-1]
            after_move=stacks["stage3_2"][-1]
            events=sdk["original_stage3_intervention_events"]
            if len(events)!=2 or events[0]["original_action"]!=6 or events[1]["original_action"]!=4:
                raise AssertionError("Native click and move not both admitted")
            if sdk["official_original_final_level"]!=3:
                raise AssertionError("Original level not 3 after non-pour probe")
            reading={
                "preclick_source":original_selected(before),
                "postclick_source":original_selected(after_click),
                "postmovement_source":original_selected(after_move),
                "original_true_pixel_at_click":events[0]["actual_source_preclick_palette"],
                "native_click_retained_selected_changed":selected_mask_sha(before)!=selected_mask_sha(after_click),
                "original_after_move_frame_changed":hash_frame(after_click)!=hash_frame(after_move),
                "original_source_move_changed_pixel_count":int(np.count_nonzero(after_click!=after_move)),
            }
            record={
                "precommitted_source_probe":name,
                "original_click_xy":list(xy),
                "independent_original_sdk_witness":witness,
                "genuine_sdk_word":word,
                "true_original_sdk_final_level":sdk["official_original_final_level"],
                "true_original_sdk_final_state":sdk["official_original_final_state"],
                "original_sdk_level4_or_WIN":sdk["official_original_level4_or_WIN"],
                "source_selection_and_motion":reading,
                "genuine_original_sdk_action_receipts":[
                    {k:v for k,v in e.items() if k!="full_original_source_frame_ledger"}
                    for e in events
                ],
            }
            rows.append(record)
            for phase,stack in stacks.items():
                raw[f"{name}_{witness}_{phase}"]=stack
            print("ORIGINAL_SP80_SELECTION_CLASS_CASE "+json.dumps({
                "case":name,"witness":witness,
                "official_level":record["true_original_sdk_final_level"],
                "source":reading,
            },sort_keys=True),flush=True)
    if len(rows)!=16 or len(roots)!=1:
        raise AssertionError("Actual independent native source reset witnesses missing")
    groups=defaultdict(list)
    for entry in rows:
        groups[entry["source_selection_and_motion"]["postclick_source"]["native_selected_mask_sha256"]].append(
            {"clicked_region":entry["precommitted_source_probe"],
             "witness":entry["independent_original_sdk_witness"]}
        )
    grouped=sorted(
        ({"source_selection_mask_sha256":k,"actual_clicks":v} for k,v in groups.items()),
        key=lambda item:item["source_selection_mask_sha256"]
    )
    advances=[{"case":r["precommitted_source_probe"],"witness":r["independent_original_sdk_witness"]}
              for r in rows if r["original_sdk_level4_or_WIN"]]
    summary={
        "kind":"TRUE_ORIGINAL_SP80_STAGE3_NATIVE_SELECTION_EQUIVALENCE",
        "source_antecedent_trial":39560139856,
        "actual_original_sdk_games":len(rows),
        "predeclared_probe_coordinates":PROBES,
        "identical_independent_stage3_source_root_blake2b16":next(iter(roots)),
        "genuine_source_level4_or_WIN_count":len(advances),
        "official_level_histogram":dict(Counter(str(r["true_original_sdk_final_level"]) for r in rows)),
        "official_state_histogram":dict(Counter(str(r["true_original_sdk_final_state"]) for r in rows)),
        "source_click_selection_mask_equivalence_classes":grouped,
        "all_original_native_selection_receipts":rows,
        "limits":"Same observed postclick selected mask groups source-equivalent selection frames under these probes; this is not a proof of a private engine object model. Only SDK official level>=4/WIN means game progress. Native full frames retained in NPZ.",
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(a.out.with_suffix(".npz"),**raw)
    print("ORIGINAL_SP80_SELECTION_CLASS_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k!="all_original_native_selection_receipts"
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
