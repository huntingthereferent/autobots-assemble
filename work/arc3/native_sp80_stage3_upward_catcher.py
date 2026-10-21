"""Original SDK SP80 stage3: intercept right-hand fourth-cup overshoot above rim.

This is a bounded original-game continuation of source-native trial
#39562263772. The genuine original SDK 3-cup clean vs 4-cup overflowing
pair differs first at x38..40,y17..19, frame9, then new source-color6
spreads along right-side rows and appears at x59..61,y56..58 shortly
before source bottom boundary changes at frame30. The publicly
documented stage4 constraint is simultaneous full cups without spill.
This trial does NOT implement those published physics or claim private
engine correspondence. It moves a real existing selectable bottom bar
UP toward that observed late right source stream, rather than revisiting
the saturated right/down-only scans.

Only actual original Arcade.NORMAL SDK level>=4 or WIN means progress.
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

UPPER="6@20,18 4 4 2 6@40,18 2"
MID="6@10,30 4 4 4 4"
RECEIVER="6@46,33 "+" ".join(["3"]*10)
RECEIVER_UP="6@46,33 1 "+" ".join(["3"]*10)
CUPS=((8,16),(26,34),(38,46),(50,58))
ROWS=(19,29,35,41,47,52,56,58)

def bottom(right,up,up_first=False):
    assert 1<=right<=4 and 0<=up<=4
    order=([1]*up+[4]*right) if up_first else ([4]*right+[1]*up)
    return "6@40,42 "+" ".join(map(str,order))

def word(b,lower=RECEIVER):
    return " ".join((UPPER,MID,lower,b,"5"))

FROZEN=(
    ("parent_right2_up0",word(bottom(2,0))),
    ("prior_right3_up0",word(bottom(3,0))),
    ("prior_right4_up0",word(bottom(4,0))),
    *(
        (f"bottom_right{r}_up{u}",word(bottom(r,u)))
        for r in (2,3,4) for u in (1,2,3,4)
    ),
    ("upfirst_right3_up2",word(bottom(3,2,True))),
    ("upfirst_right4_up2",word(bottom(4,2,True))),
    ("receiver_up1_right3_up2",word(bottom(3,2),RECEIVER_UP)),
    ("receiver_up1_right4_up2",word(bottom(4,2),RECEIVER_UP)),
)
assert len(FROZEN)==19==len({name for name,_ in FROZEN})
assert len(STAGE1_WITNESSES)==2
assert all(
    parse_plan(s)[-1][0]==5
    and sum(a==5 for a,xy in parse_plan(s))==1
    and len(parse_plan(s))<=40
    and all(xy is not None for a,xy in parse_plan(s) if a==6)
    for name,s in FROZEN
)

def observe(pre,frames):
    if pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
        raise AssertionError("Only genuine original SDK 64x64 source frames")
    first_four=None
    first_boundary=None
    cup_frames=[None]*4
    first_new_blue={str(y):None for y in ROWS}
    for t,frame in enumerate(frames):
        if frame.shape!=(64,64): raise AssertionError("Invalid SDK frame")
        new_blue=(pre!=6)&(frame==6)
        for y in ROWS:
            key=str(y)
            # All new source pixels in that row, not inferred streams.
            pixels=np.flatnonzero(new_blue[y])
            if first_new_blue[key] is None and pixels.size:
                first_new_blue[key]={"frame":t,"actual_new_palette6_x":list(map(int,pixels))}
        counts=[
            int(np.count_nonzero(
                (pre[53:59,l:r+1]==11)&(frame[53:59,l:r+1]==13)
            )) for l,r in CUPS
        ]
        for k,n in enumerate(counts):
            if n==45 and cup_frames[k] is None: cup_frames[k]=t
        if first_four is None and all(n==45 for n in counts): first_four=t
        diff=(pre[59:63,2:62]!=frame[59:63,2:62])
        if first_boundary is None and diff.any():
            first_boundary={
                "frame":t,
                "changed_original_sdk_bottom_pixels":int(diff.sum()),
                "new_source_palette6_at_y58":list(map(int,np.flatnonzero(new_blue[58]))),
            }
    components=[
        {"bbox":c["bbox"],"palette":c["palette"],"pixels":c["pixels"]}
        for c in color_components(pre) if c["palette"] in (4,8,9)
        and 15<=c["bbox"][1]<=55
    ]
    return {
        "pre_original_source_blake2b16":hash_frame(pre),
        "post_original_source_blake2b16":hash_frame(frames[-1]),
        "actual_original_source_frame_count":len(frames),
        "native_prepour_palette4_8_9_components":components,
        "per_cup_first_full_visual_frame":cup_frames,
        "first_four_simultaneously_full_visual_frame":first_four,
        "first_tested_source_bottom_boundary_event":first_boundary,
        "no_observed_tested_bottom_change":first_boundary is None,
        "first_actual_source_color6_arrival_at_rows":first_new_blue,
        "limits":"Source pixel changes only, NOT engine physics or verified flow contact/cup semantics; only SDK levels>=4/WIN prove stage success.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    rows=[];raw={};roots=set()
    for name,program in FROZEN:
        parts=parse_plan(program)
        for witness,entry in STAGE1_WITNESSES:
            sdk,stacks=real_trial(witness,entry,name,program)
            roots.add(sdk["original_verified_stage3_root"]["original_source_sha256"])
            last=stacks.get("stage3_"+str(len(parts)))
            previous=stacks.get("stage3_"+str(len(parts)-1),stacks["entry2_11"])[-1]
            measured=observe(previous,last) if last is not None else None
            record={
                "frozen_actual_native_case":name,
                "original_independent_entry_witness":witness,
                "source_original_sdk_word":program,
                "official_source_final_level":sdk["official_original_final_level"],
                "official_source_final_state":sdk["official_original_final_state"],
                "actual_native_level4_or_WIN":sdk["official_original_level4_or_WIN"],
                "original_sdk_disposition":sdk["trial_disposition"],
                "source_native_measured_animation":measured,
                "native_action_receipts":[
                    {k:v for k,v in event.items() if k!="full_original_source_frame_ledger"}
                    for event in sdk["original_stage3_intervention_events"]
                ],
            }
            rows.append(record)
            for key,stack in stacks.items():raw[f"{name}_{witness}_{key}"]=stack
            print("ORIGINAL_SP80_CATCH_ABOVE_RIM_CASE "+json.dumps({
                "case":name,"witness":witness,
                "original_sdk_level":record["official_source_final_level"],
                "original_sdk_state":record["official_source_final_state"],
                "source":measured,
            },sort_keys=True),flush=True)
    if len(rows)!=38 or len(roots)!=1:
        raise AssertionError("Actual source independent reset witnesses missing")
    progress=[
        {"case":row["frozen_actual_native_case"],
         "witness":row["original_independent_entry_witness"],
         "word":row["source_original_sdk_word"]}
        for row in rows if row["actual_native_level4_or_WIN"]
    ]
    four_no_boundary=[
        {"case":row["frozen_actual_native_case"],"witness":row["original_independent_entry_witness"]}
        for row in rows if row["source_native_measured_animation"] is not None
        and row["source_native_measured_animation"]["first_four_simultaneously_full_visual_frame"] is not None
        and row["source_native_measured_animation"]["no_observed_tested_bottom_change"]
    ]
    summary={
        "kind":"REAL_ORIGINAL_SP80_STAGE3_UPWARD_RIGHT_CATCH",
        "antecedent_native_first_arrival_run":39562263772,
        "original_sdk_independently_reset_games":len(rows),
        "precommitted_source_words":FROZEN,
        "original_stage3_root_blake2b16":next(iter(roots)),
        "actual_original_sdk_level4_or_WIN_count":len(progress),
        "native_official_progress_witnesses":progress,
        "source_only_four_visual_cups_no_test_bottom_change":four_no_boundary,
        "native_sdk_level_histogram":dict(Counter(str(r["official_source_final_level"]) for r in rows)),
        "native_sdk_state_histogram":dict(Counter(str(r["official_source_final_state"]) for r in rows)),
        "original_source_full_receipts":rows,
        "limitations":"Only actual original SDK official level>=4 or WIN proves progress. Native source color counts are partial feedback not success predicate. All SDK frames NPZ retained, no new engine or alterations to other lanes/rights.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("ORIGINAL_SP80_UPWARD_CATCH_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k not in ("precommitted_source_words","original_source_full_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
