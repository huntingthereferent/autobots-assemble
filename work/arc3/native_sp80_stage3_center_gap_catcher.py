"""Genuine original SP80 stage3: catcher height at the center-gap spill contrast.

Direct source observation in authentic SDK runs:
#39562263772 has four visually changed cup groups with bottom right2
but source bottom y59..62 transitions at frame30 with x59..61
new source-color6 at y58. With bottom catcher right1 and the lower
receiver moved up1/left10, #39557242249 and #39557791993 instead
show source all-four frame27 and bottom event frame28, with x35..37
at y58. Both officially remain stage3.

Prior upward-catcher #39563486480 ONLY varied right2/3/4 horizontal
displacements, not the right1 x41..52 catcher. Test the actual
right1 x41..52 catcher at multiple native vertical positions to see
whether its center-gap stream changes without losing the fourth cup.
No substitute flow model or image-only WIN. The ORIGINAL SDK level4/WIN
is the sole advancement criterion.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np

from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import real_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import color_components
from .native_sp80_legal_pairs import hash_frame

UPPER_DOWN1="6@20,18 4 4 2 6@40,18 2"
UPPER_DOWN2="6@20,18 4 4 2 6@40,18 2 2"
MIDDLE="6@10,30 4 4 4 4"
MIDDLE_UP1=MIDDLE+" 1"
MIDDLE_DOWN1=MIDDLE+" 2"
RECEIVER_LEFT10="6@46,33 "+" ".join(["3"]*10)
RECEIVER_UP1="6@46,33 1 "+" ".join(["3"]*10)
CUPS=((8,16),(26,34),(38,46),(50,58))

def bottom(right=1, vertical=0, first=False):
    assert right in (1,2) and -5<=vertical<=3
    vs=[1]*(-vertical) if vertical<0 else [2]*vertical
    hs=[4]*right
    return " ".join(["6@40,42",*map(str,vs+hs if first else hs+vs)])

def program(*,upper=UPPER_DOWN1,middle=MIDDLE,receiver=RECEIVER_UP1,right=1,vertical=0,first=False):
    return " ".join((upper,middle,receiver,bottom(right,vertical,first),"5"))

# Negative vertical counts are original ACTION1 up; positive are ACTION2
# down. Freeze all source words before starting actual original SDK games.
FROZEN=(
    *( (f"base_right1_up{h}",program(vertical=-h)) for h in range(6) ),
    *( (f"base_right1_down{h}",program(vertical=h)) for h in range(1,4) ),
    ("upfirst_right1_up2",program(vertical=-2,first=True)),
    ("upfirst_right1_up4",program(vertical=-4,first=True)),
    ("receiver_held_right1_up1",program(receiver=RECEIVER_LEFT10,vertical=-1)),
    ("receiver_held_right1_up3",program(receiver=RECEIVER_LEFT10,vertical=-3)),
    ("other_upper_down2_right1_up1",program(upper=UPPER_DOWN2,vertical=-1)),
    ("other_upper_down2_right1_up3",program(upper=UPPER_DOWN2,vertical=-3)),
    ("linked_middle_up1_right1_up2",program(middle=MIDDLE_UP1,vertical=-2)),
    ("linked_middle_down1_right1_up2",program(middle=MIDDLE_DOWN1,vertical=-2)),
    ("original_right2_parent",program(right=2,vertical=0,receiver=RECEIVER_LEFT10)),
    ("original_right2_up2",program(right=2,vertical=-2,receiver=RECEIVER_LEFT10)),
)
assert len(FROZEN)==19==len(set(n for n,_ in FROZEN))
assert len(STAGE1_WITNESSES)==2
assert all(
    len(parse_plan(word))<=36
    and parse_plan(word)[-1][0]==5
    and sum(action==5 for action,_ in parse_plan(word))==1
    and all(xy is not None for action,xy in parse_plan(word) if action==6)
    for _,word in FROZEN
)

def source_metrics(pre,returned):
    if pre.shape!=(64,64) or returned.ndim!=3 or returned.shape[1:]!=(64,64):
        raise AssertionError("Authentic original SDK 64x64 returned frames required")
    first_four=None;first_bottom=None
    first_cup=[None]*4;highest=0
    arrivals={str(y):None for y in (20,29,35,41,47,52,56,58)}
    episodes=[];prior_changed=False
    for t,frame in enumerate(returned):
        new_blue=(pre!=6)&(frame==6)
        for y in (20,29,35,41,47,52,56,58):
            xs=np.flatnonzero(new_blue[y])
            if xs.size and arrivals[str(y)] is None:
                arrivals[str(y)]={"original_animation_frame":t,
                                  "new_palette6_x":list(map(int,xs))}
        counts=[
            int(np.count_nonzero((pre[53:59,lo:hi+1]==11)&
                                    (frame[53:59,lo:hi+1]==13)))
            for lo,hi in CUPS
        ]
        for i,v in enumerate(counts):
            if v==45 and first_cup[i] is None:first_cup[i]=t
        completed=sum(v==45 for v in counts)
        highest=max(highest,completed)
        if completed==4 and first_four is None:first_four=t
        changed=bool(np.any(pre[59:63,2:62]!=frame[59:63,2:62]))
        if changed and not prior_changed:episodes.append(t)
        prior_changed=changed
        if changed and first_bottom is None:
            different=(pre[59:63,2:62]!=frame[59:63,2:62])
            first_bottom={
                "source_frame":t,
                "actual_test_bottom_changed_pixel_count":int(different.sum()),
                "new_palette6_at_y58":list(map(int,np.flatnonzero(new_blue[58]))),
                "new_palette6_at_y56":list(map(int,np.flatnonzero(new_blue[56]))),
            }
    components=[
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(pre)
        if c["palette"] in (4,8,9) and 15<=c["bbox"][1]<=55
    ]
    return {
        "original_prepour_frame_blake2b16":hash_frame(pre),
        "original_pour_final_frame_blake2b16":hash_frame(returned[-1]),
        "original_SDK_pour_animation_frame_count":len(returned),
        "original_source_prepour_selected_components":components,
        "original_native_cup_first_full_frames":first_cup,
        "source_max_simultaneously_full_cups":highest,
        "source_first_simultaneous_four_cups_frame":first_four,
        "source_first_bottom_test_region_color_change":first_bottom,
        "source_tested_bottom_color_change_episodes":episodes,
        "original_first_new_palette6_by_source_row":arrivals,
        "observation_only":"A palette13 cup group and tested bottom y59..62 region are not the original SDK's win predicate or complete leak diagnostic.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    records=[];arrays={};roots=set()
    for case,word in FROZEN:
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            native,stacks=real_trial(witness,entry,case,word)
            roots.add(native["original_verified_stage3_root"]["original_source_sha256"])
            animation=stacks.get("stage3_"+str(n))
            prior=stacks.get("stage3_"+str(n-1),stacks["entry2_11"])[-1]
            metrics=source_metrics(prior,animation) if animation is not None else None
            rec={
                "prospective_source_case":case,
                "independent_original_native_witness":witness,
                "genuine_original_sdk_action_word":word,
                "official_source_level":native["official_original_final_level"],
                "official_source_state":native["official_original_final_state"],
                "actual_source_level4_or_WIN":native["official_original_level4_or_WIN"],
                "genuine_source_trial_disposition":native["trial_disposition"],
                "original_sdk_frame_observation":metrics,
                "actual_native_source_actions":[
                    {k:v for k,v in event.items() if k!="full_original_source_frame_ledger"}
                    for event in native["original_stage3_intervention_events"]
                ],
            }
            records.append(rec)
            for k,stack in stacks.items():
                arrays[f"{case}_{witness}_{k}"]=stack
            print("ORIGINAL_SP80_CENTER_GAP_CATCHER_CASE "+json.dumps({
                "case":case,"witness":witness,
                "level":rec["official_source_level"],
                "state":rec["official_source_state"],
                "observed":metrics,
            },sort_keys=True),flush=True)
    if len(records)!=38 or len(roots)!=1:
        raise AssertionError("True original SDK independent stage3 source witnesses missing")
    winners=[
        {"case":r["prospective_source_case"],
         "witness":r["independent_original_native_witness"],
         "original_sdk_action_word":r["genuine_original_sdk_action_word"],
         "official_level":r["official_source_level"],
         "official_state":r["official_source_state"]}
        for r in records if r["actual_source_level4_or_WIN"]
    ]
    visual_four_clean=[
        {"case":r["prospective_source_case"],"witness":r["independent_original_native_witness"]}
        for r in records if r["original_sdk_frame_observation"] is not None
        and r["original_sdk_frame_observation"]["source_first_simultaneous_four_cups_frame"] is not None
        and r["original_sdk_frame_observation"]["source_first_bottom_test_region_color_change"] is None
    ]
    summary={
        "kind":"GENUINE_ORIGINAL_SP80_STAGE3_CENTER_GAP_CATCHER_HEIGHT",
        "genuine_native_antecedent_runs":[39557242249,39557791993,39562263772,39563486480],
        "independent_original_sdk_resets":len(records),
        "prospectively_frozen_original_actions":FROZEN,
        "original_verified_stage3_entry_blake2b16":next(iter(roots)),
        "official_source_level4_or_WIN_count":len(winners),
        "original_sdk_actual_progress_witnesses":winners,
        "source_visual_only_four_cups_no_test_bottom":visual_four_clean,
        "true_original_sdk_level_counts":dict(Counter(str(r["official_source_level"]) for r in records)),
        "true_original_sdk_state_counts":dict(Counter(str(r["official_source_state"]) for r in records)),
        "genuine_original_native_receipts":records,
        "boundaries":"Only original SDK official levels_completed>=4 or WIN proves level advancement. Screen pixels not inferred physics, source mechanics or equivalence. All native raw frames stored in NPZ; no other research lanes or license edits.",
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(a.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_CENTER_GAP_CATCHER_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("prospectively_frozen_original_actions","genuine_original_native_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
