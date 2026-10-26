"""Original SDK SP80: same full visible state, next-action divergent bottom pixel.

Read-only archival comparison found 13 distinct original full 64x64
source grids shared by differently rooted action histories, where
the genuine next ACTION5 returned stacks split at precisely one
bottom-row pixel (palette14 versus palette0 at y63).
Freeze three independently observed SPLITS and one COLLISION control.
Re-run each source history via genuine normal SDK from separately reset
games; preserve F3-48 exact rooted A/B certificate separately.

This establishes an observational projection limitation if reproduced,
not that private state or SP80 is mathematically the 48-world F3 family.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

UP_A=("6@46,33 3 6@24,33 2 2 2 3 3 "
      "6@34,42 3 3 3 1 1 6@18,42")
FROZEN=(
 ("collision_middle_return",
     BASE+" 6@15,48 4 3 6@18,36 5",
     BASE+" 6@15,48 3 4 6@18,36 5",
     "ae687e1565f7c888212c03ba8bdf6145",None),
 ("split_source_reclick_vs_left",
     UP_A+" 5",
     UP_A+" 3 5",
     "dd0b9861faae399ad607560e9181be42",[10,63]),
 ("split_middle_left_order",
     UP_A+" 1 6@27,36 3 5",
     UP_A+" 1 3 6@27,36 3 5",
     "ac83be8a4366818ec13fe9bdd7e1fdcd",[12,63]),
 ("split_extra_lower_left",
     BASE+" 3 3 5",
     BASE+" 3 3 3 5",
     "7c91036015471174098509f96fba3b70",[15,63]),
)
assert len(FROZEN)==4 and len(STAGE1_WITNESSES)==2
assert all(parse_plan(p)[-1][0]==5 and sum(a==5 for a,xy in parse_plan(p))==1
           for case,a,b,d,pixel in FROZEN for p in (a,b))

def sdk_word(name,source_witness,source_entry,word):
    n=len(parse_plan(word))
    trial,stack=run_case(name,source_witness,source_entry,word)
    pre=stack[f"stage4_{n-1}"][-1];frames=stack[f"stage4_{n}"]
    if frames.ndim!=3 or frames.shape[1:]!=(64,64) or len(frames)!=32:
        raise AssertionError("Require complete authentic 32x64x64 SDK original animation")
    receipt=trial["genuine_original_stage4_action_ledger"][-1]
    assert receipt["genuine_original_action"]==5
    row={
      "entry_witness":source_witness,"predeclared_native_history":name,
      "actual_original_stage4_word":word,
      "original_prepour_visible_blake2b16":hash_frame(pre),
      "original_next_ACTION5_frame_stack_digest":__hash_stack(frames),
      "original_next_ACTION5_final_frame_digest":hash_frame(frames[-1]),
      "real_sdk_official_level":trial["true_original_sdk_final_level"],
      "real_sdk_official_state":trial["true_original_sdk_final_state"],
      "real_sdk_level5_or_WIN":trial["official_original_level5_or_WIN"],
      "original_sdk_actions":trial["genuine_original_stage4_action_ledger"],
      "original_stage_entry_verification":trial["native_original_stage4_entry"],
    }
    return row,pre,frames,stack

def __hash_stack(s):
    from hashlib import blake2b
    return blake2b(np.ascontiguousarray(s).tobytes(),digest_size=16).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();records=[];pairs=[];arrays={}
    certificate=f3_calibration()
    for case,aword,bword,expected_pre,expected_xy in FROZEN:
        for witness,entry in STAGE1_WITNESSES:
            pair=[]
            for label,word in (("A",aword),("B",bword)):
                row,pre,frames,stacks=sdk_word(case+"_"+label,witness,entry,word)
                if row["original_prepour_visible_blake2b16"]!=expected_pre:
                    raise AssertionError("Precommitted original source pre-image failed for "+case)
                pair.append((row,pre,frames))
                records.append(row)
                for key,v in stacks.items():
                    if key=="entry3_34" or key.startswith("stage4_"):
                        arrays[f"{case}_{label}_{witness}_{key}"]=v
            a,pre_a,fa=pair[0];b,pre_b,fb=pair[1]
            if not np.array_equal(pre_a,pre_b):
                raise AssertionError("Native A/B pre-action source images not identical")
            if len(fa)!=len(fb):raise AssertionError("Native returned frame counts differ")
            ys,xs=np.nonzero(np.any(fa!=fb,axis=0))
            pixels=[[int(x),int(y)] for y,x in zip(ys,xs)]
            if expected_xy is None:
                if pixels:raise AssertionError("Positive rooted-collision control split")
            elif pixels!=[expected_xy]:
                raise AssertionError("Grounded boundary split did not reproduce "+str(pixels))
            differing_times=[int(t) for t in range(len(fa)) if np.any(fa[t]!=fb[t])]
            observed={
               "pair":case,"entry_witness":witness,
               "pre_src_pixel_digest":expected_pre,
               "rooted_same_full_visible_prepour":True,
               "native_next_action":"ACTION5",
               "two_different_original_returned_frame_stack_digests":[
                   a["original_next_ACTION5_frame_stack_digest"],
                   b["original_next_ACTION5_frame_stack_digest"]],
               "exact_source_divergence_xy":pixels,
               "first_distinct_returned_frame":differing_times[0] if differing_times else None,
               "different_original_returned_frame_indices":differing_times,
               "source_palette_A_B_at_difference":[
                   [int(fa[0,y,x]),int(fb[0,y,x])] for x,y in pixels],
               "official_sdk_levels":[a["real_sdk_official_level"],
                                      b["real_sdk_official_level"]],
               "official_sdk_states":[a["real_sdk_official_state"],
                                      b["real_sdk_official_state"]],
               "official_level5_or_WIN":[a["real_sdk_level5_or_WIN"],
                                          b["real_sdk_level5_or_WIN"]]
            }
            pairs.append(observed)
            print("SP80_NATIVE_ROOTED_AB_SPLIT "+json.dumps(observed,sort_keys=True),flush=True)
    assert len(records)==16 and len(pairs)==8
    for case,*_ in FROZEN:
        r=[x for x in pairs if x["pair"]==case]
        if len(r)!=2 or {k:v for k,v in r[0].items() if k!="entry_witness"} !={
            k:v for k,v in r[1].items() if k!="entry_witness"}:
            raise AssertionError("Original SDK independent stage entry disagreement "+case)
    result={
      "kind":"GENUINE_ORIGINAL_SP80_ROOTED_AB_VISIBLE_PROJECTION_SPLIT",
      "original_independently_reset_sdk_games":len(records),
      "native_same_visible_root_pairs":len(pairs),
      "source_divergent_pairs":sum(bool(p["exact_source_divergence_xy"]) for p in pairs),
      "source_collision_pairs":sum(not p["exact_source_divergence_xy"] for p in pairs),
      "mathematically_checked_F3_48_rooted_reference":certificate,
      "official_original_level5_or_WIN":[r["predeclared_native_history"] for r in records if r["real_sdk_level5_or_WIN"]],
      "official_sdk_level_histogram":dict(Counter(str(r["real_sdk_official_level"]) for r in records)),
      "exact_unchanged_source_preimage_F3_distinction":"Native visible-frame collision/split is not a proof of F3 native representation.",
      "predeclared_source_case_words":FROZEN,
      "actual_original_paired_A_B_findings":pairs,
      "complete_original_SDK_action_source_evidence":records,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_NATIVE_ROOTED_AB_SPLIT_SUMMARY "+json.dumps({
       k:v for k,v in result.items() if k not in
       ("predeclared_source_case_words","actual_original_paired_A_B_findings",
        "complete_original_SDK_action_source_evidence")},sort_keys=True),flush=True)
if __name__=="__main__":main()
