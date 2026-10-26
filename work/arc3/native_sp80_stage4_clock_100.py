"""Original SDK SP80: test bottom-row 64-pixel clock exhaustion and rooted
same-visible-input collisions at equal index parity.

Prospective heldout prediction from genuine source:
at original Stage4 action indices 0..43, first 14 on y63 exactly
round(64*n/100), with full row14 at n0. A display of width64
cannot represent boundary >=64. Therefore near n100 is a FINITE
boundary that may produce an identical full-frame state at n and n+2,
or official SDK terminal status may prevent such an input. Neither
outcome is presumed.

Two distinct actual SDK action histories (upper-only and alternating
middle/upper selection) are repeated 104 times each, with both
independently verified original Stage0→4 SDK entry witnesses.
Authentic status at every action, exact visible frames and source
bottom rows, and exact next SDK action labels/clicks are retained.
F3-48 rooted mathematics is independently calibrated, never mapped
to the native game six-label action alphabet.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from hashlib import blake2b
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

N=104
UPPER="6@34,21";MIDDLE="6@24,33"
FROZEN=(
  ("upper_only", " ".join([UPPER]*N)),
  ("alternating_middle_upper", " ".join([MIDDLE,UPPER]*(N//2))),
)
assert len(FROZEN)==2 and len(STAGE1_WITNESSES)==2
assert all(len(parse_plan(w))==N for case,w in FROZEN)

def stack_digest(a):
    return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()

def bottom_observation(frame,index):
    row=frame[63]
    first=next((int(i) for i,x in enumerate(row) if x==14),None)
    n14=int(np.count_nonzero(row==14))
    if int(np.count_nonzero((row!=0)&(row!=14))):
        raise AssertionError("Native bottom-row has unhandled colors")
    pred=min(64,round(64*index/100))
    return {"first_palette14_x":first,
            "palette14_pixels":n14,
            "all_zero":n14==0,
            "predicted_first14_at_64pct":pred if pred<64 else None,
            "candidate_matches":first==(pred if pred<64 else None),
            "full_row_digest":stack_digest(row)}

def test_case(name,witness,entry,word):
    sdk,raw=run_case(name,witness,entry,word+" 5")
    ledger=sdk["genuine_original_stage4_action_ledger"]
    root=raw["entry3_34"][-1]
    length=len(ledger)
    native={0:root}
    returned={}
    for i in range(1,length+1):
        stack=raw.get(f"stage4_{i}")
        if stack is None or stack.ndim!=3 or stack.shape[1:]!=(64,64):
            raise AssertionError("Every actually returned original SDK frame required")
        native[i]=stack[-1];returned[i]=stack
    measurements={}
    for i,frame in native.items():
        measurements[i]=bottom_observation(frame,i)
    for i,rec in enumerate(ledger,1):
        if rec["index"]!=i:
            raise AssertionError("Native SDK action ledger index mismatch")
        if i<=N and rec["genuine_original_action"]!=6:
            raise AssertionError("Original source action6 selection missing")
    hypotheses=[
        {"native_action_index":i,"observation":measurements[i],
         "original_native_status":ledger[i-1]["original_sdk_state_after"],
         "true_original_sdk_level":ledger[i-1]["original_sdk_level_after"]}
        for i in range(90,length+1)]
    collisions=[]
    # First n: true source from native after action n. Compare actual
    # SDK step n+1 against m+1 ONLY if common action and true click coordinates match.
    for n in range(90,length):
        for m in range(n+2,length):
            if (m-n)%2:continue
            if not np.array_equal(native[n],native[m]):continue
            aa=ledger[n];bb=ledger[m]
            if (aa["genuine_original_action"]!=bb["genuine_original_action"]
                or aa["real_native_click_xy"]!=bb["real_native_click_xy"]):
                continue
            collisions.append({
                "rooted_indices_with_identical_original_complete_visible_frames":[n,m],
                "identical_true_next_sdk_action":aa["genuine_original_action"],
                "identical_true_next_action6_click":aa["real_native_click_xy"],
                "source_visible_root_hash":hash_frame(native[n]),
                "two_original_next_source_animation_hashes":[
                    stack_digest(returned[n+1]),stack_digest(returned[m+1])],
                "same_entire_returned_original_sdk_next_frame_array":
                    bool(np.array_equal(returned[n+1],returned[m+1])),
                "original_next_official_levels":[
                    aa["original_sdk_level_after"],bb["original_sdk_level_after"]],
                "original_next_official_states":[
                    aa["original_sdk_state_after"],bb["original_sdk_state_after"]],
            })
    rec={
        "predeclared_true_original_sdk_case":name,
        "independent_native_stage_entry":witness,
        "original_stage4_prospective_action_count":N,
        "actual_original_sdk_stage4_action_count":length,
        "official_original_final_level":sdk["true_original_sdk_final_level"],
        "official_original_final_state":sdk["true_original_sdk_final_state"],
        "official_original_level5_or_WIN":sdk["official_original_level5_or_WIN"],
        "actual_original_stage4_entry_root_hash":
            sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"],
        "source_clock_all_tested_indices_match_precommitted_formula":
            all(x["candidate_matches"] for x in measurements.values()),
        "first_genuine_original_formula_mismatch":next(
            (i for i in measurements if not measurements[i]["candidate_matches"]),None),
        "first_native_action_index_bottom_row_all_zero":next(
            (i for i in measurements if measurements[i]["all_zero"]),None),
        "rooted_even_distance_same_visible_input_pairs":collisions,
        "measured_actual_sdk_index90_to_end":hypotheses,
        "last_original_sdk_action_receipts":ledger[-12:],
        "all_actual_native_stage4_action_receipts":ledger,
    }
    retained={
        f"{name}_{witness}_level4_entry":root,
    }
    for i in sorted(native):
        if i>=90:retained[f"{name}_{witness}_after_stage4_{i}"]=native[i]
    for i in sorted(returned):
        if i>=90:retained[f"{name}_{witness}_returned_action_{i}"]=returned[i]
    return rec,measurements,retained

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    f3=f3_calibration()
    records=[];preserved={};rows={}
    for case,word in FROZEN:
        for witness,entry in STAGE1_WITNESSES:
            rec,measure,frames=test_case(case,witness,entry,word)
            records.append(rec);preserved.update(frames);rows[(case,witness)]=measure
            print("SP80_CLOCK_100_NATIVE_CASE "+json.dumps({
                "case":case,"entry":witness,
                "actual_actions":rec["actual_original_sdk_stage4_action_count"],
                "sdk_level":rec["official_original_final_level"],
                "sdk_state":rec["official_original_final_state"],
                "first_zero_row":rec["first_native_action_index_bottom_row_all_zero"],
                "first_candidate_mismatch":rec["first_genuine_original_formula_mismatch"],
                "even_distance_complete_visible_root_collisions":
                    rec["rooted_even_distance_same_visible_input_pairs"],
                "heldout_clock":rec["measured_actual_sdk_index90_to_end"],
            },sort_keys=True),flush=True)
    assert len(records)==4
    for case,word in FROZEN:
        a,b=[r for r in records if r["predeclared_true_original_sdk_case"]==case]
        for key in ("actual_original_sdk_stage4_action_count",
                    "official_original_final_level","official_original_final_state",
                    "source_clock_all_tested_indices_match_precommitted_formula",
                    "first_native_action_index_bottom_row_all_zero",
                    "first_genuine_original_formula_mismatch",
                    "rooted_even_distance_same_visible_input_pairs"):
            if a[key]!=b[key]:
                raise AssertionError("True original SDK entry witnesses disagree: "+case+" "+key)
    common=sorted(set(rows[("upper_only",STAGE1_WITNESSES[0][0])])&
                   set(rows[("alternating_middle_upper",STAGE1_WITNESSES[0][0])]))
    divergent_indices=[i for i in common if
        len({tuple(rows[(c,w)][i]["full_row_digest"] for c,w in [("upper_only",STAGE1_WITNESSES[0][0])])})>1]
    # Fully explicit test across every original native game at each shared action index.
    divergent_indices=[i for i in common if len({
        rows[(c,w)][i]["full_row_digest"]
        for c,_ in FROZEN for w,_ in STAGE1_WITNESSES
        if i in rows[(c,w)]
    })>1]
    summary={
        "kind":"TRUE_ORIGINAL_SP80_STAGE4_CLOCK_EXHAUSTION_ROOTED_AB_TEST",
        "precommitted_bottom_clock_candidate":"first14_x=round(64*n/100) clipped at full zero row",
        "true_original_normal_sdk_resets":len(records),
        "genuine_original_stage4_root_digest":records[0]["actual_original_stage4_entry_root_hash"],
        "shared_action_index_source_y63_row_divergence":divergent_indices,
        "source_even_distance_identical_full_visible_state_pairs":
            [dict(p,case=r["predeclared_true_original_sdk_case"],
                    entry=r["independent_native_stage_entry"])
             for r in records for p in r["rooted_even_distance_same_visible_input_pairs"]],
        "official_native_level5_or_WIN":[r["predeclared_true_original_sdk_case"] for r in records
                                         if r["official_original_level5_or_WIN"]],
        "true_original_level_histogram":dict(Counter(str(r["official_original_final_level"]) for r in records)),
        "original_status_histogram":dict(Counter(r["official_original_final_state"] for r in records)),
        "F3_48_rooted_math_independent_calibration":f3,
        "original_sdk_stage4_all_action_receipts_and_clock":records,
        "limits":"If SDK stops before 104 actions no late even-count input exists: do not invent one. Official original level>=5/WIN is only advancement. No private engine inference."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**preserved)
    print("SP80_CLOCK_100_NATIVE_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k!="original_sdk_stage4_all_action_receipts_and_clock"
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
