"""Original SP80 SDK rooted history: is an invisible LEFT displacement reversible?

Original source paired run #40239498741 reproduced same complete visible
64x64 pre-ACTION5 image after LEFT0 vs LEFT1 but next output differs only
at bottom (x10,y63). All six genuine next SDK actions preserved the split.
Predeclare bounded LEFT repetitions and LEFT/RIGHT inverse attempts.
Compare exact input image roots and next native full-frame responses.
An abstract F3 A/B certificate is checked separately; no native-F3 map.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_rooted_ab_boundary_split import UP_A
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

# 3 = original SDK move LEFT; 4 = move RIGHT on the selected native
# left-middle object. No modeled motion or hidden position is assumed.
EXTRA=(
 ("L0",()),
 ("L1",(3,)),
 ("L2",(3,3)),
 ("L3",(3,3,3)),
 ("L4",(3,3,3,3)),
 ("L5",(3,3,3,3,3)),
 ("L6",(3,3,3,3,3,3)),
 ("L1_R1",(3,4)),
 ("L2_R2",(3,3,4,4)),
 ("L3_R3",(3,3,3,4,4,4)),
 ("R1_L1",(4,3)),
 ("L1_R1_L1",(3,4,3)),
 ("L2_R1",(3,3,4)),
 ("R1_L2",(4,3,3)),
)
assert len(EXTRA)==14==len({k for k,_ in EXTRA})
assert len(STAGE1_WITNESSES)==2

def hashstack(stack):
    from hashlib import blake2b
    return blake2b(np.ascontiguousarray(stack).tobytes(),digest_size=16).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    mathproof=f3_calibration()
    rows=[];arr={};roots=set();direct={}
    for name,actions in EXTRA:
        word=UP_A+(" "+" ".join(map(str,actions)) if actions else "")+" 5"
        n=len(parse_plan(word))
        for witness,entry in STAGE1_WITNESSES:
            sdk,source=run_case(name,witness,entry,word)
            roots.add(sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"])
            pre=source[f"stage4_{n-1}"][-1]
            frames=source[f"stage4_{n}"]
            if pre.shape!=(64,64) or frames.ndim!=3 or frames.shape[1:]!=(64,64):
                raise AssertionError("Only complete original SDK returned arrays allowed")
            ledger=sdk["genuine_original_stage4_action_ledger"]
            assert ledger[-1]["genuine_original_action"]==5
            assert all(r["original_sdk_level_before"]==4 for r in ledger)
            record={
                "native_frozen_case":name,
                "independent_original_entry":witness,
                "extra_genuine_native_action_suffix":list(actions),
                "actual_original_stage4_word":word,
                "real_original_prepour_source_digest":hash_frame(pre),
                "real_original_prepour_border_row63_palette":pre[63,0:22].tolist(),
                "original_action5_full_native_frames_digest":hashstack(frames),
                "real_original_action5_frame_count":len(frames),
                "real_original_action5_early_border_row63_palette":frames[0,63,0:22].tolist(),
                "real_original_action5_last_border_row63_palette":frames[-1,63,0:22].tolist(),
                "true_official_level":sdk["true_original_sdk_final_level"],
                "true_official_state":sdk["true_original_sdk_final_state"],
                "true_original_sdk_level5_or_WIN":sdk["official_original_level5_or_WIN"],
                "all_true_original_sdk_action_receipts":ledger,
            }
            rows.append(record);direct[(name,witness)]=(pre,frames)
            arr[f"{name}_{witness}_pre"]=pre
            arr[f"{name}_{witness}_original_ACTION5_stack"]=frames
            print("SP80_ROOTED_LEFT_INVERSE_CASE "+json.dumps({
                "case":name,"witness":witness,
                "pre_root":record["real_original_prepour_source_digest"],
                "next_output":record["original_action5_full_native_frames_digest"],
                "new_border_x8_18":record["real_original_action5_early_border_row63_palette"][8:19],
                "sdk_level":record["true_official_level"],
                "sdk_state":record["true_official_state"]},sort_keys=True),flush=True)
    if len(rows)!=28 or len(roots)!=1:
        raise AssertionError("True independent original stage4 resets missing")
    for name,_ in EXTRA:
        a,b=[r for r in rows if r["native_frozen_case"]==name]
        if any(a[k]!=b[k] for k in (
            "real_original_prepour_source_digest","real_original_prepour_border_row63_palette",
            "original_action5_full_native_frames_digest",
            "real_original_action5_early_border_row63_palette",
            "real_original_action5_last_border_row63_palette",
            "true_official_level","true_official_state")):
            raise AssertionError("Two independent original source history witness mismatch: "+name)
    groups=defaultdict(list)
    for name,_ in EXTRA:
        root=next(r["real_original_prepour_source_digest"] for r in rows
                  if r["native_frozen_case"]==name)
        groups[root].append(name)
    comparisons=[]
    for root,names in sorted(groups.items()):
        for i,a in enumerate(names):
            for b in names[i+1:]:
                for witness,_ in STAGE1_WITNESSES:
                    pa,fa=direct[(a,witness)];pb,fb=direct[(b,witness)]
                    assert np.array_equal(pa,pb)
                    if len(fa)!=len(fb):raise AssertionError("Native animation length varies")
                    y,x=np.nonzero(np.any(fa!=fb,axis=0))
                    differences=[[int(xx),int(yy)] for yy,xx in zip(y,x)]
                    first=next((t for t in range(len(fa)) if
                                np.any(fa[t]!=fb[t])),None)
                    comparisons.append({
                        "root":root,"A":a,"B":b,"witness":witness,
                        "same_full_source_preimage":True,
                        "full_original_sdk_pour_equal":not differences,
                        "next_A_B_exact_changed_pixels":differences,
                        "first_next_sdk_frame_split":first})
    # Frozen prior positive control: L0 and L1 have one identical source
    # root but next SDK frame differs at exactly one original bottom pixel.
    controls=[r for r in comparisons if r["A"]=="L0" and r["B"]=="L1"]
    assert len(controls)==2
    assert all(r["next_A_B_exact_changed_pixels"]==[[10,63]] for r in controls)
    result={
        "kind":"TRUE_ORIGINAL_SP80_ROOTED_A_B_INVISIBLE_LEFT_REVERSIBILITY",
        "original_normal_sdk_reset_games":len(rows),
        "same_verified_original_stage4_root":next(iter(roots)),
        "F3_48_rooted_calibration_separate_from_native":mathproof,
        "frozen_source_suffixes":EXTRA,
        "distinct_observed_full_prepour_image_roots":len(groups),
        "pre_action_source_root_groups":dict(groups),
        "same_full_visible_root_distinct_history_pair_comparisons":comparisons,
        "true_original_sdk_level5_or_WIN":[r["native_frozen_case"] for r in rows
                                            if r["true_original_sdk_level5_or_WIN"]],
        "native_level_histogram":dict(Counter(str(r["true_official_level"]) for r in rows)),
        "full_native_original_action_receipts":rows,
        "limit":"Only original SDK source observations and F3 finite math separately. Visible image alone is not a hidden-state certificate."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arr)
    print("SP80_ROOTED_LEFT_INVERSE_SUMMARY "+json.dumps({
        k:v for k,v in result.items() if k not in
        ("frozen_source_suffixes","same_full_visible_root_distinct_history_pair_comparisons",
         "full_native_original_action_receipts")},sort_keys=True),flush=True)
if __name__=="__main__":main()
