"""Genuine original SP80 Stage4 bottom-row source clock holdout.

Offline saved-array comparison found the entire bottom row y63 identical
across every one of 11,054 original Stage4 source returns at fixed action
index n=1..32, despite very different native action words.
Precommit 42 next selections from the same actually original Stage4 root.
A: select upper native bar every step.
B: alternate middle/upper bar selections, same total index.
C: select middle bar every step.
Run each under two distinct original SDK level4-entry witnesses.
Record each exact returned bottom y63 row; test independence of
selection history at each index beyond 32 (not extrapolate an invented
formula). A/B finish with the same upper bar selected; compare their
entire native pre-pour 64x64 frames and common subsequent ACTION5.
This is a visible clock test, not an F3 mapping or an inferred objective.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from hashlib import blake2b
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

U="6@34,21";M="6@24,33"
N=42
FROZEN=(
 ("upper_only", " ".join([U]*N)),
 ("alternate_middle_upper", " ".join([M,U]*(N//2))),
 ("middle_only", " ".join([M]*N)),
)
assert len(FROZEN)==3 and len(STAGE1_WITNESSES)==2
assert all(len(parse_plan(word))==N for case,word in FROZEN)

def hash_stack(a):
    return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    theoretical=f3_calibration()
    records=[];frames_by_case={};source_roots=set();traces={}
    for case,word in FROZEN:
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word+" 5")
            source_roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            last=max(int(k.rsplit("_",1)[1]) for k in raw if k.startswith("stage4_"))
            if last!=N+1:raise AssertionError("Actual SDK halted before frozen final POUR: "+str(last))
            receipt=sdk["genuine_original_stage4_action_ledger"]
            if len(receipt)!=N+1:
                raise AssertionError("Original normal SDK did not execute full trace")
            if not all(r["genuine_original_action"]==6 and
                r["original_source_pixel_before_click"]==8
                for r in receipt[:N]):
                raise AssertionError("Expected original source-click palette8 at each selection")
            if receipt[-1]["genuine_original_action"]!=5:
                raise AssertionError("Final native action not genuine POUR")
            root=raw["entry3_34"][-1]
            rows={0:root[63,:].tolist()}
            digests={0:hash_frame(root)}
            for i in range(1,N+2):
                grid=raw[f"stage4_{i}"][-1]
                if grid.shape!=(64,64):raise AssertionError("Original frame not 64x64")
                rows[i]=grid[63,:].tolist()
                digests[i]=hash_frame(grid)
            source_prepour=raw[f"stage4_{N}"][-1]
            final_pour=raw[f"stage4_{N+1}"]
            traces[(case,witness)]=(rows,digests,source_prepour,final_pour)
            record={
              "frozen_case":case,
              "independent_original_stage1_witness":witness,
              "actual_original_source_action_word":word+" 5",
              "native_stage4_selection_count":N,
              "original_normal_sdk_final_level":sdk["true_original_sdk_final_level"],
              "original_normal_sdk_final_state":sdk["true_original_sdk_final_state"],
              "official_original_level5_or_WIN":sdk["official_original_level5_or_WIN"],
              "full_original_visible_before_pour_digest":digests[N],
              "full_original_native_ACTION5_frames_digest":hash_stack(final_pour),
              "original_returned_sdk_action_count":last,
              "full_native_bottom_y63_per_action_index":rows,
              "full_sdk_source_action_receipts":receipt,
            }
            records.append(record)
            frames_by_case[f"{case}_{witness}_pre_pour"]=source_prepour
            frames_by_case[f"{case}_{witness}_native_pour"]=final_pour
            print("SP80_NATIVE_ROOTED_CLOCK_CASE "+json.dumps({
                "case":case,"witness":witness,
                "pre":digests[N],"pour_stack":record["full_original_native_ACTION5_frames_digest"],
                "final_level":record["original_normal_sdk_final_level"],
                "new_index_33_42_first_14":[
                    next((x for x,value in enumerate(rows[i]) if value==14),None)
                    for i in range(33,N+1)]},sort_keys=True),flush=True)
    if len(records)!=6 or len(source_roots)!=1:
        raise AssertionError("Independent original source native games missing")
    all_aligned={};violations=[]
    for i in range(N+2):
        rows=[traces[(case,witness)][0][i]
                for case,word in FROZEN for witness,entry in STAGE1_WITNESSES]
        expected=rows[0]
        all_aligned[i]=all(row==expected for row in rows)
        if not all_aligned[i]:violations.append(i)
    for case,word in FROZEN:
        one,two=[r for r in records if r["frozen_case"]==case]
        if (one["full_original_visible_before_pour_digest"]!=
            two["full_original_visible_before_pour_digest"] or
            one["full_original_native_ACTION5_frames_digest"]!=
            two["full_original_native_ACTION5_frames_digest"]):
            raise AssertionError("Independent original Stage1 witnesses disagree")
    paired=[]
    for witness,entry in STAGE1_WITNESSES:
        a=traces[("upper_only",witness)]
        b=traces[("alternate_middle_upper",witness)]
        samepre=np.array_equal(a[2],b[2])
        samenext=np.array_equal(a[3],b[3])
        paired.append({
          "entry_witness":witness,
          "same_complete_original_visible_after_42_actions":samepre,
          "same_original_ACTION5_full_returned_frames":samenext,
          "original_A_pre_image_digest":hash_frame(a[2]),
          "original_B_pre_image_digest":hash_frame(b[2]),
          "original_A_native_pour_digest":hash_stack(a[3]),
          "original_B_native_pour_digest":hash_stack(b[3]),
        })
    report={
      "kind":"TRUE_ORIGINAL_SP80_STAGE4_VISIBLE_BOTTOM_CLOCK_HISTORY_INDEPENDENCE",
      "genuine_original_sdk_games":len(records),
      "original_stage4_root":next(iter(source_roots)),
      "frozen_new_source_selection_action_count":N,
      "new_original_stage4_indices_beyond_archival_max":list(range(33,N+2)),
      "all_original_y63_row_identical_at_same_index_across_six_native_histories":len(violations)==0,
      "original_stage4_action_indices_with_y63_row_divergence":violations,
      "same_count_A_B_full_frame_and_pour_comparisons":paired,
      "original_sdk_official_level_histogram":
          dict(Counter(str(r["original_normal_sdk_final_level"]) for r in records)),
      "official_level5_or_WIN_cases":[r["frozen_case"] for r in records if r["official_original_level5_or_WIN"]],
      "F3_48_separate_exact_rooted_calibration":theoretical,
      "original_frozen_action_words":FROZEN,
      "complete_original_native_sdk_source_results":records,
      "limitation":"Even a universally observed source edge pulse is not an engine goal or hidden state proof. Only original levels_completed>=5/WIN means advancement. Source pixel index clock may saturate or change outside tested indices."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames_by_case)
    print("SP80_NATIVE_ROOTED_CLOCK_SUMMARY "+json.dumps({
       k:v for k,v in report.items()
       if k not in ("original_frozen_action_words","complete_original_native_sdk_source_results")
    },sort_keys=True),flush=True)
if __name__=="__main__":
    main()
