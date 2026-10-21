"""True original SP80 level4: test if lower two source emitters are selectable.

Genuine SDK source-level4 entry from merged PR #367 has native palette6
regions x20..22/y56..58 and x44..46/y56..58, each immediately above
native palette4 x20..22/y59..61 and x44..46/y59..61. The overlooked
L-shaped palette15 object was proven movable in PR #372 and produced
the visually complete four-cup contact, but native SDK stayed level4
amid original frame12 left-border palette flash. Nearby L and middle
moves did not remove this signal (PRs #374 and #375).

Before speculating about an emitter's behavior, click each visible
lower source palette6/4 region, record the ACTUAL native selection
image before/after click and one genuine move. Compare original L
positive control and original empty-background negative control.
This is source click inventory, not an inferred hidden game entity
map. Only genuine original SDK level>=5/WIN means advancement.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

PROBES=(
    ("left_emitter_blue",(21,57),6,1),
    ("left_emitter_stem",(21,60),4,3),
    ("right_emitter_blue",(45,57),6,1),
    ("right_emitter_stem",(45,60),4,4),
    ("lower_L_positive",(34,42),15,3),
    ("background_negative",(6,47),12,3),
)
assert len(STAGE1_WITNESSES)==2

FROZEN=tuple(
    (f"{name}_{suffix}",f"6@{xy[0]},{xy[1]}"+(f" {move}" if suffix=="move" else "")+" 5")
    for name,xy,palette,move in PROBES for suffix in ("click","move")
)
assert len(FROZEN)==12==len({n for n,_ in FROZEN})
assert all(parse_plan(word)[-1][0]==5 and sum(a==5 for a,xy in parse_plan(word))==1 for _,word in FROZEN)

def selection(frame):
    mask=np.ascontiguousarray(frame==9).astype(np.uint8)
    components=[
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(frame) if c["palette"] in (9,15)
    ]
    return {
        "actual_original_palette9_mask_sha256":hashlib.sha256(mask.tobytes()).hexdigest(),
        "actual_original_selected_pixel_count":int(mask.sum()),
        "native_selected_source_regions":components,
        "source_blake2b16":hash_frame(frame),
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    rows=[];raw={};roots=set()
    indexed={name:(xy,palette,move) for name,xy,palette,move in PROBES}
    for case,program in FROZEN:
        name=case.rsplit("_",1)[0]
        xy,palette,move=indexed[name]
        n=len(parse_plan(program))
        for witness,entry in STAGE1_WITNESSES:
            sdk,stacks=run_case(case,witness,entry,program)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=stacks["entry3_34"][-1]
            observed_source_palette=int(root[xy[1],xy[0]])
            if observed_source_palette!=palette:
                raise AssertionError(f"Original native {name} source pixel changed: {observed_source_palette}!={palette}")
            selected_after_click=stacks["stage4_1"][-1]
            after_move=stacks["stage4_2"][-1] if n==3 else None
            native_events=sdk["genuine_original_stage4_action_ledger"]
            if native_events[0]["genuine_original_action"]!=6 or native_events[0]["original_source_pixel_before_click"]!=palette:
                raise AssertionError("Genuine native SDK click/preclick mismatch")
            row={
                "frozen_native_source_case":case,
                "source_target_name":name,
                "actual_native_target_xy":xy,
                "genuine_independent_original_witness":witness,
                "original_source_expected_click_palette":palette,
                "original_source_actual_click_palette":observed_source_palette,
                "official_original_final_level":sdk["true_original_sdk_final_level"],
                "official_original_final_state":sdk["true_original_sdk_final_state"],
                "genuine_original_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "original_level4_entry_selected":selection(root),
                "original_after_click_selected":selection(selected_after_click),
                "native_click_changed_selection_mask":selection(root)["actual_original_palette9_mask_sha256"]!=selection(selected_after_click)["actual_original_palette9_mask_sha256"],
                "original_after_genuine_movement":selection(after_move) if after_move is not None else None,
                "original_native_movement_changed_frame":hash_frame(selected_after_click)!=hash_frame(after_move) if after_move is not None else None,
                "actual_native_action_click_receipts":native_events,
            }
            rows.append(row)
            for phase,frames in stacks.items():raw[f"{case}_{witness}_{phase}"]=frames
            print("ORIGINAL_SP80_EMITTER_SELECT_CASE "+json.dumps({
                "case":case,"witness":witness,
                "original_click_palette":observed_source_palette,
                "selected":row["original_after_click_selected"],
                "original_move":row["original_after_genuine_movement"],
                "original_move_changed_frame":row["original_native_movement_changed_frame"],
                "official_level":row["official_original_final_level"],
                "official_state":row["official_original_final_state"],
            },sort_keys=True),flush=True)
    if len(rows)!=24 or len(roots)!=1:raise AssertionError("Missing actual original native source entry")
    for case,_ in FROZEN:
        pair=[r for r in rows if r["frozen_native_source_case"]==case]
        if len(pair)!=2 or (
            pair[0]["official_original_final_level"]!=pair[1]["official_original_final_level"]
            or pair[0]["official_original_final_state"]!=pair[1]["official_original_final_state"]
            or pair[0]["original_after_click_selected"]!=pair[1]["original_after_click_selected"]
            or pair[0]["original_after_genuine_movement"]!=pair[1]["original_after_genuine_movement"]
        ):raise AssertionError("Actual source independent witnesses differ: "+case)
    selection_groups=defaultdict(list)
    for r in rows:
        selection_groups[r["original_after_click_selected"]["actual_original_palette9_mask_sha256"]].append(
            {"source_target":r["source_target_name"],"native_case":r["frozen_native_source_case"],
             "witness":r["genuine_independent_original_witness"]}
        )
    progresses=[
        {"case":r["frozen_native_source_case"],
         "witness":r["genuine_independent_original_witness"],
         "official_level":r["official_original_final_level"],
         "official_state":r["official_original_final_state"]}
        for r in rows if r["genuine_original_level5_or_WIN"]
    ]
    summary={
        "kind":"TRUE_ORIGINAL_SP80_STAGE4_LOWER_EMITTER_PALETTE6_4_SELECTION_INVENTORY",
        "antecedent_original_sdk_run":39624132483,
        "authentic_native_independent_resets":len(rows),
        "prospectively_frozen_native_words":FROZEN,
        "same_official_native_level4_root":next(iter(roots)),
        "native_original_level5_or_WIN_count":len(progresses),
        "genuine_official_level5_witnesses":progresses,
        "source_selection_mask_equivalence_groups":selection_groups,
        "official_sdk_level_histogram":dict(Counter(str(r["official_original_final_level"]) for r in rows)),
        "official_sdk_state_histogram":dict(Counter(str(r["official_original_final_state"]) for r in rows)),
        "actual_original_source_records":rows,
        "limit":"Only actual original SDK levels_completed>=5/WIN proves progress. Source palettes and click-selection groupings are empirical images, not decoded hidden object physics.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("ORIGINAL_SP80_EMITTER_SELECT_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k not in ("prospectively_frozen_native_words","actual_original_source_records")
    },sort_keys=True),flush=True)
if __name__=="__main__":
    main()
