"""Original SP80 rooted A/B prospective parity holdout.

READ-ONLY 544 genuine original ACTION5 arrays showed 13 full-input
image collisions with different successor stacks, but zero collisions
after augmenting the visible root by stage4 action-index PARITY.
This is a bounded empirically observed quotient, NOT a global theorem.
Freeze same-object and two-object selection round trips, varying
action count while seeking the exact same complete native pre-pour frame.
New original SDK resets test whether (visible source image, index%2)
continues to predict the complete returned source animation.

The F3-48 rooted/nonrooted mathematical model remains distinct from
native SP80 six-action alphabet and no proof of conjugacy is claimed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter,defaultdict
from hashlib import blake2b
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_rooted_ab_boundary_split import UP_A
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

S="6@18,42";U="6@34,21";R="6@46,33";L="6@34,42"
HOLDOUT=(
 ("root_control",()),
 ("left1_control",("3",)),
 ("same_reclick1",(S,)),
 ("same_reclick2",(S,S)),
 ("same_reclick3",(S,S,S)),
 ("upper_return",(U,S)),
 ("right_return",(R,S)),
 ("lower_return",(L,S)),
 ("upper_return_extra",(U,S,S)),
 ("right_return_extra",(R,S,S)),
 ("upper_return_twice",(U,S,U,S)),
 ("right_return_twice",(R,S,R,S)),
)
assert len(HOLDOUT)==12==len({x[0] for x in HOLDOUT})
assert len(STAGE1_WITNESSES)==2
ROOT_HASH="dd0b9861faae399ad607560e9181be42"
EXPECTED={
  0:"36aff6ecd29ebe7974d63efac50b72a0",
  1:"4d9af990a458c0a7350bd8b65870ae3f"
}
def digest(a):return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();theory=f3_calibration()
    rows=[];stacks={};roots=set()
    for case,commands in HOLDOUT:
        word=" ".join((UP_A,*commands,"5"));allactions=parse_plan(word)
        n=len(allactions)
        assert all(a!=6 or xy is not None for a,xy in allactions)
        for witness,entry in STAGE1_WITNESSES:
            sdk,raw=run_case(case,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            pre=raw[f"stage4_{n-1}"][-1];pour=raw[f"stage4_{n}"]
            if pour.ndim!=3 or pour.shape[1:]!=(64,64):
                raise AssertionError("Require original SDK 64x64 stack")
            prehash=hash_frame(pre);posthash=digest(pour)
            root_match=prehash==ROOT_HASH
            candidate=EXPECTED[(n-1)%2] if root_match else None
            row={
              "case":case,"witness":witness,
              "actual_stage4_word":word,
              "extra_native_commands":list(commands),
              "stage4_native_pour_index":n,
              "action_count_before_pour":n-1,
              "before_pour_count_parity":(n-1)%2,
              "full_real_native_prepour_image_digest":prehash,
              "matches_predeclared_visible_root":root_match,
              "true_original_sdk_next_pour_full_stack_digest":posthash,
              "predicted_next_stack_from_frozen_parity_hypothesis":candidate,
              "parity_hypothesis_predicts_native_stack":
                  (posthash==candidate) if root_match else None,
              "actual_original_frame0_bottom_x10_to16":pour[0,63,10:17].tolist(),
              "actual_original_prepour_bottom_x10_to16":pre[63,10:17].tolist(),
              "actual_original_sdk_final_level":sdk["true_original_sdk_final_level"],
              "actual_original_sdk_final_state":sdk["true_original_sdk_final_state"],
              "original_level5_or_WIN":sdk["official_original_level5_or_WIN"],
              "complete_original_sdk_stage4_action_receipts":sdk["genuine_original_stage4_action_ledger"],
            }
            rows.append(row)
            stacks[f"{case}_{witness}_pre"]=pre
            stacks[f"{case}_{witness}_original_ACTION5_stack"]=pour
            print("SP80_ROOTED_PARITY_HOLDOUT_CASE "+json.dumps({
              "case":case,"witness":witness,
              "index":n,"parity":(n-1)%2,
              "same_source_root":root_match,
              "next_stack":posthash,
              "candidate_match":row["parity_hypothesis_predicts_native_stack"],
              "next_border":row["actual_original_frame0_bottom_x10_to16"],
              "level":row["actual_original_sdk_final_level"]},sort_keys=True),flush=True)
    if len(rows)!=24 or len(roots)!=1:raise AssertionError("Missing independent original SDK resets")
    for name,_ in HOLDOUT:
        a,b=[x for x in rows if x["case"]==name]
        for k in ("full_real_native_prepour_image_digest",
                  "true_original_sdk_next_pour_full_stack_digest",
                  "parity_hypothesis_predicts_native_stack",
                  "actual_original_frame0_bottom_x10_to16",
                  "actual_original_sdk_final_level","actual_original_sdk_final_state"):
            if a[k]!=b[k]:
                raise AssertionError("Independent original SDK witness disagreement "+name)
    controls={r["case"]:r for r in rows if r["witness"]==STAGE1_WITNESSES[0][0]}
    if not controls["root_control"]["parity_hypothesis_predicts_native_stack"] or not controls["left1_control"]["parity_hypothesis_predicts_native_stack"]:
        raise AssertionError("Historical frozen A/B positive control changed")
    same=[r for r in rows if r["matches_predeclared_visible_root"]]
    tested=[r for r in same if r["case"] not in ("root_control","left1_control")]
    result={
       "kind":"ORIGINAL_SP80_ROOTED_AB_SOURCE_PLUS_ACTION_PARITY_HOLDOUT",
       "antecedent_action_collision_runs":[40239498741,40239771729,40240600114],
       "genuine_original_normal_sdk_games":len(rows),
       "verified_original_stage4_root":next(iter(roots)),
       "original_source_same_image_hash":ROOT_HASH,
       "frozen_preexisting_parity_to_full_animation":EXPECTED,
       "all_original_source_matched_games":len(same),
       "previously_untested_same_source_matched_games":len(tested),
       "source_matched_new_controls_parity_successes":sum(bool(r["parity_hypothesis_predicts_native_stack"]) for r in tested),
       "source_matched_new_controls_parity_failures":[r["case"] for r in tested if not r["parity_hypothesis_predicts_native_stack"]],
       "original_level5_or_WIN_cases":[r["case"] for r in rows if r["original_level5_or_WIN"]],
       "official_sdk_level_counts":dict(Counter(str(r["actual_original_sdk_final_level"]) for r in rows)),
       "mathematical_F3_48_rooted_certificate_separate":theory,
       "precommitted_original_action_suffixes":HOLDOUT,
       "complete_original_sdk_native_source_receipts":rows,
       "limits":"Input image plus parity is a sample-bound candidate, not global native state or F3 correspondence. Preserve rooted word and official SDK progression separately."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**stacks)
    print("SP80_ROOTED_PARITY_HOLDOUT_SUMMARY "+json.dumps({
       k:v for k,v in result.items() if k not in
       ("precommitted_original_action_suffixes","complete_original_sdk_native_source_receipts")
       },sort_keys=True),flush=True)
if __name__=="__main__":main()
