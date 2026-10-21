"""Original SDK SP80 level4: first TOP/RIGHT edge contact from clean FOUR cups.

Authentic native run #39636174534 isolated two original level4
source words with all 4 cup11->13 windows full, NO observed LEFT
border change, but native TOP y2..4 source border changes 171
palette1->14 pixels at returned frame21 and right edge 9 pixels.
Both independently reset original SDK witnesses stay level4.

Hold each source-proven clean L+left-middle+top arrangement and vary
the previously fixed RIGHT-MIDDLE selectable 45px red bar (original
source click 46,33) in a bounded native matrix. Track genuine
SDK status and returned original 64x64 source animations, first
palette6 arrival near x56..58/y5..7, each cup and ALL 4 borders.
No hidden fluid model, no image-only success claim.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

RIGHT_CLICK="6@46,33"
UPPER="6@34,21 3"
PARENTS=(
    ("cleanD3L2_L3U2","6@24,33 2 2 2 3 3","6@34,42 3 3 3 1 1"),
    ("cleanD4L2_L4U2","6@24,33 2 2 2 2 3 3","6@34,42 3 3 3 3 1 1"),
)
RIGHT_WORDS=(
    ("parent_left1","3"),
    ("bar_left2","3 3"),("bar_left3","3 3 3"),
    ("bar_right1","4"),
    ("bar_up1_left1","1 3"),("bar_down1_left1","2 3"),
    ("bar_left1_up1","3 1"),("bar_left1_up2","3 1 1"),
    ("bar_left1_down1","3 2"),("bar_left1_down2","3 2 2"),
    ("bar_left2_up1","3 3 1"),("bar_left2_down1","3 3 2"),
)
FROZEN=tuple(
    (f"{parent}_right_{name}",
     " ".join((RIGHT_CLICK+" "+moves,mid,L,UPPER,"5")))
    for parent,mid,L in PARENTS for name,moves in RIGHT_WORDS
)
assert len(FROZEN)==24==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(word)[-1][0]==5
           and sum(action==5 for action,xy in parse_plan(word))==1
           and all(xy is not None for action,xy in parse_plan(word) if action==6)
           for _,word in FROZEN)
CUPS={
    "lateral_left":(5,35,10,43),
    "top_left":(17,5,25,10),
    "top_middle":(35,5,43,10),
    "top_right":(47,5,55,10),
}
EDGES={
    "left":(slice(2,62),slice(2,5)),
    "right":(slice(2,62),slice(59,62)),
    "top":(slice(2,5),slice(2,62)),
    "bottom":(slice(59,62),slice(2,62)),
}
def selected(frame):
    return [
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(frame)
        if c["palette"] in (9,15) and 15<=c["bbox"][1]<=56
    ]

def source_metrics(root,pre,frames):
    if root.shape!=(64,64) or pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Actual original SDK source frames 64x64 required")
    first={k:None for k in CUPS}
    max13={k:0 for k in CUPS}
    first_four=None
    borders={k:None for k in EDGES}
    episodes={k:[] for k in EDGES}
    prev={k:False for k in EDGES}
    first_right_blue={str(y):None for y in (5,6,7,8,10,14,17,20,23)}
    for t,f in enumerate(frames):
        filled=0
        new_blue=(pre!=6)&(f==6)
        for y in (5,6,7,8,10,14,17,20,23):
            xs=np.flatnonzero(new_blue[y,47:62])+47
            if xs.size and first_right_blue[str(y)] is None:
                first_right_blue[str(y)]={"original_frame":t,"actual_new_source_palette6_x":list(map(int,xs))}
        for name,(x0,y0,x1,y1) in CUPS.items():
            original=root[y0:y1+1,x0:x1+1]==11
            if int(original.sum())!=45:raise AssertionError("Original SDK source cup geometry drift")
            n=int(np.count_nonzero(original&(f[y0:y1+1,x0:x1+1]==13)))
            max13[name]=max(max13[name],n)
            if n==45 and first[name] is None:first[name]=t
            filled+=int(n==45)
        if filled==4 and first_four is None:first_four=t
        for name,(ys,xs) in EDGES.items():
            diff=pre[ys,xs]!=f[ys,xs]
            active=bool(diff.any())
            if active and not prev[name]:episodes[name].append(t)
            prev[name]=active
            if active and borders[name] is None:
                transitions,n=np.unique(np.stack((
                    pre[ys,xs][diff],f[ys,xs][diff]
                ),axis=1),axis=0,return_counts=True)
                borders[name]={
                    "native_animation_frame":t,
                    "original_source_changed_pixels":int(diff.sum()),
                    "native_palette_transitions":[[int(v[0]),int(v[1]),int(c)] for v,c in zip(transitions,n)]
                }
    return {
        "original_source_prepour_blake2b16":hash_frame(pre),
        "original_source_pour_final_blake2b16":hash_frame(frames[-1]),
        "original_sdk_returned_animation_frames":len(frames),
        "original_cup_first_full_frame":first,
        "original_cup_max_palette13_pixels":max13,
        "first_all_four_cups_simultaneous_source_frame":first_four,
        "first_source_border_color_change":borders,
        "source_border_change_episode_frames":episodes,
        "source_first_new_palette6_right_upper_by_row":first_right_blue,
        "true_source_prepour_selected_components":selected(pre),
        "qualification":"Original source pixel colors/edges are observations not a native WIN or private physics rule.",
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    rows=[];arrays={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,frames=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=frames["entry3_34"][-1]
            pre=frames["stage4_"+str(n-1)][-1]
            obs=source_metrics(root,pre,frames["stage4_"+str(n)])
            receipts=[
                {"original_step":event["index"],"source_action":event["genuine_original_action"],
                 "native_click_xy":event["real_native_click_xy"],
                 "preclick_native_palette":event["original_source_pixel_before_click"],
                 "real_native_selected_component_after":selected(frames["stage4_"+str(event["index"])][-1]),
                 "native_source_after_hash":event["source_frame_after_blake2b16"]}
                for event in sdk["genuine_original_stage4_action_ledger"]
                if event["genuine_original_action"] in (1,2,3,4,6)
            ]
            record={
                "frozen_true_original_source_case":case,
                "independent_original_sdk_witness":witness,
                "actual_native_source_stage4_word":word,
                "official_original_final_level":sdk["true_original_sdk_final_level"],
                "official_original_final_state":sdk["true_original_sdk_final_state"],
                "actual_original_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "original_native_cup_and_border_observations":obs,
                "real_original_selected_object_step_receipts":receipts,
                "native_original_sdk_action_ledger":sdk["genuine_original_stage4_action_ledger"],
            }
            rows.append(record)
            for phase,stack in frames.items():arrays[f"{case}_{witness}_{phase}"]=stack
            print("ORIGINAL_SP80_CLEAN_FOUR_TOP_EDGE_CASE "+json.dumps({
                "case":case,"witness":witness,
                "sdk_level":record["official_original_final_level"],
                "sdk_state":record["official_original_final_state"],
                "source":obs,
            },sort_keys=True),flush=True)
    if len(rows)!=48 or len(roots)!=1:raise AssertionError("Original independent SDK histories missing")
    for case,_ in FROZEN:
        pair=[x for x in rows if x["frozen_true_original_source_case"]==case]
        if len(pair)!=2 or (
            pair[0]["official_original_final_level"]!=pair[1]["official_original_final_level"]
            or pair[0]["official_original_final_state"]!=pair[1]["official_original_final_state"]
            or pair[0]["original_native_cup_and_border_observations"]!=pair[1]["original_native_cup_and_border_observations"]
            or pair[0]["real_original_selected_object_step_receipts"]!=pair[1]["real_original_selected_object_step_receipts"]
        ):raise AssertionError("True original SDK A/B disagreement: "+case)
    winning=[{"case":r["frozen_true_original_source_case"],
              "witness":r["independent_original_sdk_witness"],
              "original_native_stage4_word":r["actual_native_source_stage4_word"],
              "official_level":r["official_original_final_level"],
              "official_state":r["official_original_final_state"]}
             for r in rows if r["actual_original_level5_or_WIN"]]
    four=[{"case":r["frozen_true_original_source_case"],
           "witness":r["independent_original_sdk_witness"],
           "original_first_edge_changes":r["original_native_cup_and_border_observations"]["first_source_border_color_change"]}
          for r in rows if r["original_native_cup_and_border_observations"]["first_all_four_cups_simultaneous_source_frame"] is not None]
    result={
        "kind":"GENUINE_ORIGINAL_SP80_STAGE4_CLEAN_FOUR_CUP_TOP_RIGHT_EDGE_CONTACT",
        "real_original_antecedent_run":39636174534,
        "original_sdk_independent_reset_games":len(rows),
        "frozen_original_source_words":FROZEN,
        "genuine_level4_source_root_blake2b16":next(iter(roots)),
        "original_official_level5_or_WIN_count":len(winning),
        "actual_original_level5_witnesses":winning,
        "native_four_cup_source_cases_with_edge_events":four,
        "official_sdk_final_level_counts":dict(Counter(str(r["official_original_final_level"]) for r in rows)),
        "official_sdk_final_state_counts":dict(Counter(str(r["official_original_final_state"]) for r in rows)),
        "genuine_original_source_action_receipts":rows,
        "scope":"Only original SDK official level>=5/WIN qualifies. Real source colors and border changes are not the native success predicate or decoded physics. Full actual original SDK frames preserved NPZ.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_CLEAN_FOUR_TOP_EDGE_SUMMARY "+json.dumps({
        k:v for k,v in result.items()
        if k not in ("frozen_original_source_words","genuine_original_source_action_receipts")
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
