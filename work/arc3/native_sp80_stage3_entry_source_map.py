"""Read genuine original SDK stage3 entry after the independently witnessed
stage2->3 native winning word. Read-only; no guessed future goal.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage2_click_inventory import trial as original_trial
from .native_sp80_multi_select import parse_plan
from .native_sp80_stage2_source_map import scene,color_components,sha
STAGE2_VERIFIED_WORD="6@12,21 4 6@44,29 3 3 6@12,33 3 3 6@40,41 4 5"
assert parse_plan(STAGE2_VERIFIED_WORD)[-1][0]==5
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rec=[];arrays={}
    step=len(parse_plan(STAGE2_VERIFIED_WORD))
    for witness,entry in STAGE1_WITNESSES:
        trial,raw=original_trial(witness,entry,"source_stage3_entry",STAGE2_VERIFIED_WORD,0)
        if trial["original_source_final_level"]!=3 or trial["original_source_final_state"]!="NOT_FINISHED":
            raise RuntimeError("No genuine independent original SDK level3 entry")
        root=raw["stage2_"+str(step)][-1]
        info={
            "independent_original_witness":witness,
            "authentic_SDK_level":trial["original_source_final_level"],
            "authentic_SDK_state":trial["original_source_final_state"],
            "source_frame_sha256":sha(root),
            "original_SDK_palette_64x64":scene(root),
            "connected_actual_original_native_color_regions":color_components(root),
            "source_available_actions":trial["stage2_native_observations"][-1]["source_original_legal_after"],
            "original_exact_action_records":trial["full_original_SDK_action_records"],
        }
        rec.append(info)
        for phase,stack in raw.items():
            arrays["%s_%s"%(witness,phase)]=stack
        print("ORIGINAL_SP80_LEVEL3_SOURCE_MAP_BEGIN "+witness)
        for y,row in enumerate(info["original_SDK_palette_64x64"]):
            print("%02d %s"%(y,row))
        print("ORIGINAL_SP80_LEVEL3_SOURCE_MAP_END "+witness)
        print("ORIGINAL_SP80_LEVEL3_COMPONENTS "+witness+" "+json.dumps(info["connected_actual_original_native_color_regions"],sort_keys=True))
    if len(rec)!=2:raise AssertionError("Missing one original entry witness")
    out={
        "kind":"REAL_ORIGINAL_SP80_SDK_LEVEL3_ENTRY_FROM_TWO_NATIVE_SUCCESS_WORDS",
        "authentic_native_level2_to3_word":STAGE2_VERIFIED_WORD,
        "original_first_two_source_witnesses":STAGE1_WITNESSES,
        "original_independent_game_resets":len(rec),
        "same_actual_stage3_screen":rec[0]["source_frame_sha256"]==rec[1]["source_frame_sha256"],
        "official_original_sdk_final_levels":[r["authentic_SDK_level"] for r in rec],
        "true_full_source_native_records":rec,
        "limits":"Source screen and official levels only. No asserted engine physics, stage4 objective, six-level WIN, or F3 correspondence. All intermediate returned source frames archived."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("ORIGINAL_SP80_LEVEL3_ENTRY_SUMMARY "+json.dumps({k:v for k,v in out.items() if k!="true_full_source_native_records"},sort_keys=True))
if __name__=="__main__":main()
