"""Native SP80 level4: preserve clean lateral fill, recover missing top-left.

Original SDK #39633965255 (PR #379) found two independently
reproduced clean lateral-left source arrangements:
 A: right-middle LEFT1, left-middle DOWN3/LEFT2, L LEFT3/UP2
 B: right-middle LEFT1, left-middle DOWN4/LEFT2, L LEFT4/UP2
Both give lateral cup palette11->13 at frame13 with no tested left
border change. Top-middle/right visually fill, but TOP-LEFT remains
zero source palette11->13 pixels. All official SDK levels stay4.

A genuinely new native contact: keep BOTH source clean lateral
arrangements fixed and alter the formerly unmodified top red bar at
genuine source x34,y21, testing its native lateral/vertical movement.
Do not repeat static L adjustments or claim colors are SDK success.
Only true original SDK levels_completed>=5 / WIN advances.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

RIGHT="6@46,33 3"
A_MID="6@24,33 2 2 2 3 3"
A_L="6@34,42 3 3 3 1 1"
B_MID="6@24,33 2 2 2 2 3 3"
B_L="6@34,42 3 3 3 3 1 1"
TARGETS=(("clean_D3L2_L3U2",A_MID,A_L),
         ("clean_D4L2_L4U2",B_MID,B_L))
TOP="6@34,21"
TEST_MOVES=(
    ("held",""),("left1","3"),("left2","3 3"),
    ("left3","3 3 3"),("right1","4"),("right2","4 4"),
    ("up1","1"),("down1","2"),
    ("left1_up1","3 1"),("left2_up1","3 3 1"),
    ("left1_down1","3 2"),("right1_up1","4 1"),
    ("right1_down1","4 2"),
)
def make(mid,l,moves):
    parts=[RIGHT,mid,l]
    if moves:parts.append(TOP+" "+moves)
    parts.append("5")
    return " ".join(parts)
FROZEN=tuple(
    (f"{name}_top_{label}",make(mid,l,moves))
    for name,mid,l in TARGETS for label,moves in TEST_MOVES
)
assert len(FROZEN)==26==len({n for n,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(parse_plan(w)[-1][0]==5 and sum(a==5 for a,xy in parse_plan(w))==1
           and all(xy is not None for a,xy in parse_plan(w) if a==6)
           for _,w in FROZEN)
CUPS={
    "lateral_left":(5,35,10,43),
    "top_left":(17,5,25,10),
    "top_middle":(35,5,43,10),
    "top_right":(47,5,55,10),
}
def selected(frame):
    return [{"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
            for c in color_components(frame)
            if c["palette"] in (9,15) and 15<=c["bbox"][1]<=55]

def source_readout(root,pre,frames):
    if root.shape!=(64,64) or pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Original SDK frame dimensions mismatch")
    first={k:None for k in CUPS}
    max13={k:0 for k in CUPS}
    first_simult_four=None
    first_left_border=None
    episodes=[];last_border=False
    new6_top_left=None
    for t,f in enumerate(frames):
        nfull=0
        for k,(x0,y0,x1,y1) in CUPS.items():
            rootmask=root[y0:y1+1,x0:x1+1]==11
            if int(rootmask.sum())!=45:raise AssertionError("Original game source cup root changed")
            n=int(np.count_nonzero(rootmask&(f[y0:y1+1,x0:x1+1]==13)))
            max13[k]=max(max13[k],n)
            if n==45 and first[k] is None:first[k]=t
            nfull+=int(n==45)
        if nfull==4 and first_simult_four is None:first_simult_four=t
        new6=(pre!=6)&(f==6)
        if new6_top_left is None and new6[11:30,14:29].any():
            ys,xs=np.nonzero(new6[11:30,14:29])
            new6_top_left={"frame":t,"original_source_yx":[[int(y+11),int(x+14)] for y,x in zip(ys,xs)][:100]}
        diff=pre[2:62,2:5]!=f[2:62,2:5]
        active=bool(diff.any())
        if active and not last_border:episodes.append(t)
        last_border=active
        if active and first_left_border is None:
            first_left_border={"frame":t,"actual_native_changed_pixels":int(diff.sum()),
                               "source_palette1_to14":int(np.count_nonzero(
                                   (pre[2:62,2:5]==1)&(f[2:62,2:5]==14)
                               ))}
    return {
        "original_native_prepour_hash":hash_frame(pre),
        "original_native_postpour_hash":hash_frame(frames[-1]),
        "native_returned_animation_count":len(frames),
        "source_first_full_cup_frames":first,
        "source_max_palette13_cup_pixels":max13,
        "first_native_four_simultaneous_full_visual_frame":first_simult_four,
        "first_native_left_border_color_change":first_left_border,
        "native_left_border_change_episodes":episodes,
        "first_native_new_palette6_above_top_left":new6_top_left,
        "real_original_prepour_selected_regions":selected(pre),
        "source_only":"Cup colors and border changes are only original pixel observations. Only official SDK level>=5/WIN is progress.",
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    receipts=[];raw={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,stacks=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            root=stacks["entry3_34"][-1]
            pre=stacks["stage4_"+str(n-1)][-1]
            poured=stacks["stage4_"+str(n)]
            observed=source_readout(root,pre,poured)
            native_actions=[
                {"sdk_index":x["index"],"source_action":x["genuine_original_action"],
                 "native_click_xy":x["real_native_click_xy"],
                 "original_click_palette":x["original_source_pixel_before_click"],
                 "real_selected_after":selected(stacks["stage4_"+str(x["index"])][-1]),
                 "original_frame_after_hash":x["source_frame_after_blake2b16"]}
                for x in sdk["genuine_original_stage4_action_ledger"]
                if x["genuine_original_action"] in (1,2,3,4,6)
            ]
            rec={
                "prospective_original_source_case":case,
                "independent_actual_native_witness":witness,
                "true_sdk_stage4_source_word":word,
                "official_original_final_level":sdk["true_original_sdk_final_level"],
                "official_original_final_state":sdk["true_original_sdk_final_state"],
                "original_sdk_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "original_native_cup_and_boundary_observations":observed,
                "true_original_selected_action_receipts":native_actions,
                "actual_original_sdk_full_action_receipts":sdk["genuine_original_stage4_action_ledger"],
            }
            receipts.append(rec)
            for key,stack in stacks.items():raw[f"{case}_{witness}_{key}"]=stack
            print("ORIGINAL_SP80_CLEAN_LATERAL_TOP_CASE "+json.dumps({
                "case":case,"witness":witness,
                "original_sdk_level":rec["official_original_final_level"],
                "official_sdk_state":rec["official_original_final_state"],
                "native_source":observed,
            },sort_keys=True),flush=True)
    if len(receipts)!=52 or len(roots)!=1:
        raise AssertionError("Original SDK independent witness count or roots mismatch")
    for case,_ in FROZEN:
        pair=[v for v in receipts if v["prospective_original_source_case"]==case]
        if len(pair)!=2 or (
            pair[0]["official_original_final_level"]!=pair[1]["official_original_final_level"]
            or pair[0]["official_original_final_state"]!=pair[1]["official_original_final_state"]
            or pair[0]["original_native_cup_and_boundary_observations"]!=pair[1]["original_native_cup_and_boundary_observations"]
            or pair[0]["true_original_selected_action_receipts"]!=pair[1]["true_original_selected_action_receipts"]
        ):raise AssertionError("Source A/B original independent mismatch: "+case)
    winners=[{"case":v["prospective_original_source_case"],
              "witness":v["independent_actual_native_witness"],
              "word":v["true_sdk_stage4_source_word"],
              "official_level":v["official_original_final_level"],
              "official_state":v["official_original_final_state"]}
             for v in receipts if v["original_sdk_level5_or_WIN"]]
    four=[{"case":v["prospective_original_source_case"],
           "witness":v["independent_actual_native_witness"],
           "left_border":v["original_native_cup_and_boundary_observations"]["first_native_left_border_color_change"]}
          for v in receipts if v["original_native_cup_and_boundary_observations"]["first_native_four_simultaneous_full_visual_frame"] is not None]
    summary={
        "kind":"TRUE_ORIGINAL_SP80_LEVEL4_CLEAN_LATERAL_MISSING_TOP_LEFT_RECOVERY",
        "actual_native_antecedent_run":39633965255,
        "genuine_original_independent_resets":len(receipts),
        "frozen_original_stage4_native_words":FROZEN,
        "original_same_level4_entry_blake2b16":next(iter(roots)),
        "original_official_level5_or_WIN_count":len(winners),
        "native_original_level5_witnesses":winners,
        "original_visual_four_cup_cases":four,
        "original_sdk_final_level_histogram":dict(Counter(str(v["official_original_final_level"]) for v in receipts)),
        "original_sdk_final_state_histogram":dict(Counter(str(v["official_original_final_state"]) for v in receipts)),
        "source_full_actual_original_receipts":receipts,
        "limits":"Only original Arcade.NORMAL SDK level>=5/WIN is advancement. No inferred hidden physics or proxy success. All native SDK frame stacks preserved NPZ.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("ORIGINAL_SP80_CLEAN_LATERAL_TOP_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k not in ("frozen_original_stage4_native_words","source_full_actual_original_receipts")
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
