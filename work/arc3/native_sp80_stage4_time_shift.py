"""Original SP80: geometry-held Stage4 time-shift A/B experiment.

Exact positive comparator: successful original Stage3->4 native ACTION5
holds all 180 original cup pixels at palette13 for 2 frames.
Original Stage4 four-cup negative comparator holds all 180 for 8
frames, yet official levels_completed stays4.
Hence transient/sustained visual cup fill is not a win certificate.

Freeze the verified Stage4 four-cup native setup BASE and vary ONLY
the number of repeated genuine SDK ACTION6 clicks on the *already*
selected palette8/9 source at x15,y48 before a single native ACTION5.
Use independently reset original SDK entry witnesses at each delay.
The 100-action GAME_OVER boundary is proven by original run
#40250466381; all frozen words remain below that limit.

Compare complete pre-pour images excluding clock row y63; declare
whether the geometry ACTUALLY remained identical. Compare complete
native pour 32-frame stacks and four-cup source occupancy, but only
official SDK levels_completed>=5/WIN constitutes progress. The exact
F3-48 mathematical rooted source is calibrated independently, not
assumed to identify the game.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from hashlib import blake2b
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE,read_pour
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

NOPS=(1,2,3,8,24,48,70)
SELECT="6@15,48"
assert len(NOPS)==7 and len(STAGE1_WITNESSES)==2
assert len(parse_plan(BASE))==21
WORDS=tuple((f"same_geometry_wait_{n}",BASE+" "+" ".join([SELECT]*n)+" 5")
            for n in NOPS)
assert all(len(parse_plan(word))<100 for name,word in WORDS)

def frame_digest(a):
    return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()

def success_frame_occupancy(success_pre,success_frames):
    orig=(success_pre==11)
    if int(orig.sum())!=180:
        raise AssertionError("Original successful Stage3 has different native cup mask")
    times=[int(t) for t,f in enumerate(success_frames)
           if np.count_nonzero(orig & (f==13))==180]
    return times

def case(name,delay,witness,entry,word):
    sdk,raw=run_case(name,witness,entry,word)
    stage3_pre=raw["entry3_33"][-1]
    stage3_animation=raw["entry3_34"]
    positive_times=success_frame_occupancy(stage3_pre,stage3_animation)
    if positive_times!=[27,28]:
        raise AssertionError("Real original prior Stage3->4 win positive control changed")
    n=len(parse_plan(word))
    assert n==len(parse_plan(BASE))+delay+1
    root=raw["entry3_34"][-1]
    before=raw[f"stage4_{n-1}"][-1]
    animation=raw[f"stage4_{n}"]
    assert animation.ndim==3 and animation.shape[1:]==(64,64)
    ledger=sdk["genuine_original_stage4_action_ledger"]
    assert len(ledger)==n and ledger[-1]["genuine_original_action"]==5
    source_clicks=ledger[len(parse_plan(BASE)):-1]
    if len(source_clicks)!=delay or any(
       evt["genuine_original_action"]!=6 or
       evt["real_native_click_xy"]!=[15,48] or
       evt["original_source_pixel_before_click"] not in (8,9) or
       evt["original_sdk_level_before"]!=4 or
       evt["original_sdk_level_after"]!=4
       for evt in source_clicks):
        raise AssertionError("True original SDK same selected source reclick receipts changed")
    observed=read_pour(root,before,animation)
    return {
        "prospective_source_condition":name,
        "delay_same_native_selected_object_reclicks":delay,
        "independent_original_entry":witness,
        "exact_original_stage4_action_word":word,
        "stage3_success_actual_native_fourcup_frames":positive_times,
        "stage3_transition_original_levels":[
             ledger[0]["original_sdk_level_before"],sdk["native_original_stage4_entry"]["original_sdk_entry_level"]],
        "true_original_stage4_prepour_action_index":n-1,
        "actual_native_prepour_full_frame_digest":hash_frame(before),
        "actual_native_prepour_without_clock_row_digest":frame_digest(before[:63]),
        "actual_native_prepour_clock_row_digest":frame_digest(before[63]),
        "original_sdk_action5_native_full_animation_digest":frame_digest(animation),
        "original_native_action5_frame_count":int(len(animation)),
        "native_stage4_four_cup_source_observations":observed,
        "native_stage4_official_sdk_final_level":sdk["true_original_sdk_final_level"],
        "native_stage4_official_sdk_final_state":sdk["true_original_sdk_final_state"],
        "official_original_level5_or_WIN":sdk["official_original_level5_or_WIN"],
        "authentic_sdk_native_reclick_action_receipts":source_clicks,
        "native_sdk_actual_last_pour_receipt":ledger[-1],
        "original_sdk_stage4_root_hash":
            sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"],
        "native_prepour":before,"native_pour":animation
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    proof=f3_calibration()
    rows=[];arrays={}
    for (name,word),delay in zip(WORDS,NOPS):
        for witness,entry in STAGE1_WITNESSES:
            data=case(name,delay,witness,entry,word)
            frame=data.pop("native_prepour")
            pour=data.pop("native_pour")
            rows.append(data)
            arrays[f"{name}_{witness}_original_prepour"]=frame
            arrays[f"{name}_{witness}_original_ACTION5"]=pour
            print("SP80_LEVEL4_TIME_SHIFT_CASE "+json.dumps({
                "condition":name,"entry":witness,
                "pre_action_index":data["true_original_stage4_prepour_action_index"],
                "geometry_outside_clock":data["actual_native_prepour_without_clock_row_digest"],
                "original_full_pour_digest":data["original_sdk_action5_native_full_animation_digest"],
                "stage3_win_full_cups":data["stage3_success_actual_native_fourcup_frames"],
                "stage4_full_cups":data["native_stage4_four_cup_source_observations"]["same_sdk_frame_full_four_cups"],
                "official_level":data["native_stage4_official_sdk_final_level"],
                "official_state":data["native_stage4_official_sdk_final_state"],
            },sort_keys=True),flush=True)
    assert len(rows)==14
    assert len({r["original_sdk_stage4_root_hash"] for r in rows})==1
    for name,word in WORDS:
        one,two=[r for r in rows if r["prospective_source_condition"]==name]
        for key in ("actual_native_prepour_full_frame_digest",
                    "original_sdk_action5_native_full_animation_digest",
                    "native_stage4_four_cup_source_observations",
                    "native_stage4_official_sdk_final_level",
                    "native_stage4_official_sdk_final_state"):
            if one[key]!=two[key]:
                raise AssertionError("Independent original stage1 source witnesses differ "+name)
    # Exact A/B geometry check, never assume "no-op" preserves full
    # source interior merely from syntactic repetition.
    per_witness=[]
    for witness,entry in STAGE1_WITNESSES:
        conditions=[r for r in rows if r["independent_original_entry"]==witness]
        geometry_set={r["actual_native_prepour_without_clock_row_digest"] for r in conditions}
        per_witness.append({
            "independent_entry":witness,
            "number_of_distinct_prepour_geometry_away_from_clock":len(geometry_set),
            "all_delays_match_original_nonclock_prepour_image":len(geometry_set)==1,
        })
    report={
        "kind":"AUTHENTIC_ORIGINAL_SP80_STAGE4_FOURCUP_GEOMETRY_HELD_ACTION_CLOCK_AB",
        "new_genuine_independent_original_sdk_games":len(rows),
        "original_stage4_parent":BASE,
        "precommitted_original_sdk_wait_click_counts":NOPS,
        "verified_previous_original_gameover_at_action100":40250466381,
        "independent_source_geometry_checks":per_witness,
        "original_sdk_level5_or_WIN_conditions":[r["prospective_source_condition"]
           for r in rows if r["official_original_level5_or_WIN"]],
        "native_sdk_level_histogram":dict(Counter(str(r["native_stage4_official_sdk_final_level"]) for r in rows)),
        "native_sdk_state_histogram":dict(Counter(r["native_stage4_official_sdk_final_state"] for r in rows)),
        "exact_separate_F3_rooted_certificate":proof,
        "complete_true_original_sdk_game_observations":rows,
        "limitation":"The source Stage3 full-cup positive comparator and Stage4 source negative are two different original levels. Time-shift effects are only claims when source nonclock pre-pour frames are exactly identical. Official progress is level>=5/WIN, not image metrics."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_LEVEL4_TIME_SHIFT_SUMMARY "+json.dumps({
        k:v for k,v in report.items() if k!="complete_true_original_sdk_game_observations"
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
