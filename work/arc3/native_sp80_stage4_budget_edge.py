"""True original SP80 SDK last-action A/B time controls.

Previous genuine run #40256224122 froze original Level4 four-cup
geometry, varied only same-object ACTION6 selections, and showed the
entire genuine next POUR animation outside y63 IDENTICAL through
Stage4 action92 (including 8 frames of four fully filled source cups);
zero official level5/WIN. This finishes the two remaining meaningful
budget-edge timings: actual POUR at action99 and actual POUR at 100.

No synthetic physics or post-GAME_OVER continuation. F3-48 exact
rooted math remains separately certified and untouched.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from hashlib import blake2b
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_four_cup_followup import BASE
from .native_sp80_stage4_time_shift import case
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan

EXPECTED_INTERIOR="50e4ed1e4451fb5afe58bbb87122d88b"
CASES=((77,99),(78,100))
assert len(parse_plan(BASE))==21
assert all(len(parse_plan(BASE+" "+" ".join(["6@15,48"]*n)+" 5"))==index
           for n,index in CASES)
def hd(a):return blake2b(np.ascontiguousarray(a).tobytes(),digest_size=16).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();proof=f3_calibration()
    rows=[];art={}
    for n,final_action in CASES:
        word=BASE+" "+" ".join(["6@15,48"]*n)+" 5"
        for witness,stage1 in STAGE1_WITNESSES:
            row=case("final_clock_"+str(final_action),n,witness,stage1,word)
            pre=row.pop("native_prepour")
            animation=row.pop("native_pour")
            assert hd(pre[:63])==EXPECTED_INTERIOR
            assert row["true_original_stage4_prepour_action_index"]==final_action-1
            row["same_pre_pour_geometry_as_previously_verified_action22_to92"]=True
            row["authentic_source_pour_nonclock_frame_stack_digest"]=hd(animation[:,:63])
            row["authentic_native_action5_frame_count"]=len(animation)
            art[f"clock{final_action}_{witness}_native_prepour"]=pre
            art[f"clock{final_action}_{witness}_native_pour"]=animation
            rows.append(row)
            print("SP80_NATIVE_STAGE4_BUDGET_EDGE_CASE "+json.dumps({
                "case":final_action,"entry":witness,
                "actual_level":row["native_stage4_official_sdk_final_level"],
                "actual_state":row["native_stage4_official_sdk_final_state"],
                "official_level5_or_WIN":row["official_original_level5_or_WIN"],
                "real_returned_original_pour_frames":len(animation),
                "interior_pour":row["authentic_source_pour_nonclock_frame_stack_digest"],
                "full_original_cups":row["native_stage4_four_cup_source_observations"]["same_sdk_frame_full_four_cups"],
                "real_source_clock_before_action14":
                    int(np.count_nonzero(pre[63]==14)),
            },sort_keys=True),flush=True)
    assert len(rows)==4
    for n,final_action in CASES:
        r=[x for x in rows if x["delay_same_native_selected_object_reclicks"]==n]
        assert len(r)==2
        for key in ("native_stage4_official_sdk_final_level",
                    "native_stage4_official_sdk_final_state",
                    "original_sdk_action5_native_full_animation_digest",
                    "native_stage4_four_cup_source_observations"):
            if r[0][key]!=r[1][key]:
                raise AssertionError("True independent original native source witnesses differ")
    summary={
      "kind":"ORIGINAL_NATIVE_SP80_LEVEL4_LAST_TWO_ACTION_BUDGET_TIME_AB",
      "genuine_original_sdk_reset_games":len(rows),
      "precommitted_action5_indices":[99,100],
      "original_prior_geometry_timing_run":40256224122,
      "frozen_geometry_source_interior_digest":EXPECTED_INTERIOR,
      "true_original_sdk_level_histogram":
           dict(Counter(str(r["native_stage4_official_sdk_final_level"]) for r in rows)),
      "true_original_sdk_state_histogram":
           dict(Counter(str(r["native_stage4_official_sdk_final_state"]) for r in rows)),
      "genuine_level5_or_WIN":[r["prospective_source_condition"]
            for r in rows if r["official_original_level5_or_WIN"]],
      "separate_F3_rooted_math_calibration":proof,
      "actual_original_native_source_results":rows,
      "scope":"Only official SDK level>=5/WIN is progress. Original SDK stops after GAME_OVER and no hidden engine state can be claimed from source image."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**art)
    print("SP80_NATIVE_STAGE4_BUDGET_EDGE_SUMMARY "+json.dumps({
       k:v for k,v in summary.items() if k!="actual_original_native_source_results"
    },sort_keys=True),flush=True)

if __name__=="__main__":main()
