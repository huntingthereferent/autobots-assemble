"""SP80 genuine rooted A/B holdout: same original full visible frame,
SAME action count, DIFFERENT original action word, same next SDK action.

Before these tests, a read-only audit of 11,054 archived original
Stage4 action returns (394 distinct full visible grids) found no same
full visible image at two prior action counts differing by an EVEN
positive number. Thus the earlier image+count-parity no-collision
observation is not independently tested across different same-parity
counts. We test alternative rooted words AT THE SAME COUNT instead.

Three previously observed source-matched roots are frozen here:
  length1: an actual LEFT movement vs selecting same source bar again
  length2: LEFT LEFT vs RIGHT LEFT
  length3: LEFT LEFT LEFT vs LEFT RIGHT LEFT vs RIGHT LEFT LEFT
All A/B histories are rooted at the genuinely original SDK Level4
stage entry, with original F3 48-world root calibration separate.
No substitution of ARC palettes for private game physics or F3 states.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import blake2b
import json
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_rooted_ab_boundary_split import UP_A
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

# Same root from independent *earlier* original SDK source artifacts.
# The words are native action labels; not the mathematical A/B alphabet.
FROZEN_GROUPS=(
 ("one_step", "dd0b9861faae399ad607560e9181be42", (
     ("left1","3"),
     ("reclick_same","6@18,42"),
   ), ("1","2","3","4","5","6@34,21")),
 ("two_step","e42fc1e7f5256e19b53468c75724fc50",(
     ("left2","3 3"),
     ("right_then_left","4 3"),
   ), ("3","5","6@34,21")),
 ("three_step","e1e7f0020d5afe14ecce1d476491d548",(
     ("left3","3 3 3"),
     ("left_right_left","3 4 3"),
     ("right_left_left","4 3 3"),
   ), ("3","5","6@34,21"))
)
assert len(FROZEN_GROUPS)==3 and len(STAGE1_WITNESSES)==2
assert len(parse_plan(UP_A))==15
assert sum(len(paths)*len(futures) for _,_,paths,futures in FROZEN_GROUPS)*2==54
for group,root,paths,futures in FROZEN_GROUPS:
    assert len({len(parse_plan(word)) for name,word in paths})==1
    assert len({name for name,word in paths})==len(paths)
    assert len({s for s in futures})==len(futures)
    assert all(len(parse_plan(s))==1 for s in futures)
    assert len(root)==32

def hash_array(data):
    return blake2b(np.ascontiguousarray(data).tobytes(),digest_size=16).hexdigest()

def native(source_word, follow, source_witness, stage1_word, case):
    prefix=UP_A+" "+source_word
    before_index=len(parse_plan(prefix))
    true_word=prefix+" "+follow
    sdk,raw=run_case(case,source_witness,stage1_word,true_word)
    before=raw[f"stage4_{before_index}"][-1]
    returned=raw[f"stage4_{before_index+1}"]
    if before.shape!=(64,64) or returned.ndim!=3 or returned.shape[1:]!=(64,64):
        raise AssertionError("Require actual original SDK 64x64 source")
    last=sdk["genuine_original_stage4_action_ledger"][-1]
    if last["genuine_original_action"]!=parse_plan(follow)[0][0]:
        raise AssertionError("Actual final action not the prospectively frozen label")
    if last["genuine_original_action"]==6 and last["original_source_pixel_before_click"]!=8:
        raise AssertionError("Expected source palette8 bar on actual original selection")
    detail={
        "source_witness":source_witness,
        "frozen_stage4_word":true_word,
        "actual_prepour_action_count":before_index,
        "actual_before_full_visible_root":hash_frame(before),
        "actual_next_action":last["genuine_original_action"],
        "actual_next_click":last["real_native_click_xy"],
        "true_native_returned_frames":len(returned),
        "true_native_returned_stack_digest":hash_array(returned),
        "original_sdk_levels_completed":sdk["true_original_sdk_final_level"],
        "original_sdk_state":sdk["true_original_sdk_final_state"],
        "official_original_level5_or_WIN":sdk["official_original_level5_or_WIN"],
        "actual_full_genuine_stage4_ledger":sdk["genuine_original_stage4_action_ledger"],
        "original_independently_verified_stage4_root":
            sdk["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"],
    }
    return detail,before,returned

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    math=f3_calibration()
    receipts=[];comparison=[];saved={};entry_roots=set()
    for group,root,paths,futures in FROZEN_GROUPS:
        for future in futures:
            for witness,stage1_word in STAGE1_WITNESSES:
                observations=[]
                for label,word in paths:
                    detail,before,returned=native(word,future,witness,
                        stage1_word,group+"_"+label+"_"+future)
                    detail.update({"frozen_group":group,"path_label":label,
                                   "frozen_followup":future})
                    if detail["actual_before_full_visible_root"]!=root:
                        raise AssertionError("Original source root changed for "+
                                             group+" "+label+" "+future)
                    receipts.append(detail)
                    observations.append((detail,before,returned))
                    entry_roots.add(detail["original_independently_verified_stage4_root"])
                    saved[f"{group}_{label}_{witness}_{future}_pre"]=before
                    saved[f"{group}_{label}_{witness}_{future}_native_next"]=returned
                baseline_label,baseline_pre,baseline_frames=observations[0]
                assert all(np.array_equal(pre,baseline_pre) and
                           d["actual_prepour_action_count"]==
                           baseline_label["actual_prepour_action_count"]
                           for d,pre,st in observations[1:])
                for alternative,other_pre,other_frames in observations[1:]:
                    if len(baseline_frames)!=len(other_frames):
                        yx=None;first=None;same=False
                    else:
                        yy,xx=np.nonzero(np.any(baseline_frames!=other_frames,axis=0))
                        yx=[[int(x),int(y)] for y,x in zip(yy,xx)]
                        first=next((int(i) for i in range(len(baseline_frames))
                                   if np.any(baseline_frames[i]!=other_frames[i])),None)
                        same=len(yx)==0
                    row={
                        "root_group":group,
                        "independent_original_entry":witness,
                        "identical_source_state_at_equal_native_action_index":True,
                        "precommitted_next_action":future,
                        "native_A_path":baseline_label["path_label"],
                        "native_B_path":alternative["path_label"],
                        "native_pre_action_stage4_action_count":
                            alternative["actual_prepour_action_count"],
                        "original_next_frame_stack_identical":same,
                        "first_different_native_frame":first,
                        "exact_spatial_differences":yx,
                        "source_next_array_hashes":[
                            baseline_label["true_native_returned_stack_digest"],
                            alternative["true_native_returned_stack_digest"]],
                        "real_sdk_official_levels":[
                            baseline_label["original_sdk_levels_completed"],
                            alternative["original_sdk_levels_completed"]],
                        "original_sdk_official_states":[
                            baseline_label["original_sdk_state"],
                            alternative["original_sdk_state"]],
                    }
                    comparison.append(row)
                    print("SP80_ROOTED_SAME_PARITY_AB "+json.dumps(row,sort_keys=True),flush=True)
    if len(receipts)!=54 or len(entry_roots)!=1 or len(comparison)!=30:
        raise AssertionError("Missing original SDK source rooted comparison")
    for group,root,paths,futures in FROZEN_GROUPS:
        for future in futures:
            pairs=[r for r in comparison if
                   r["root_group"]==group and
                   r["precommitted_next_action"]==future]
            by_witness={}
            for r in pairs:
                by_witness.setdefault(r["independent_original_entry"],[]).append(r)
            if len(by_witness)!=2:
                raise AssertionError("Missing independent source entry witnesses")
            canonical=[]
            for v in by_witness.values():
                canonical.append([{k:x for k,x in p.items() if
                    k!="independent_original_entry"} for p in v])
            if canonical[0]!=canonical[1]:
                raise AssertionError("Two native entry witnesses disagree "+group+" "+future)
    result={
      "kind":"ORIGINAL_SP80_ROOTED_AB_SAME_VISIBLE_STATE_AND_SAME_ACTION_COUNT",
      "genuine_original_sdk_games":len(receipts),
      "original_verified_level4_entry":next(iter(entry_roots)),
      "F3_48_exact_rooted_obstruction_calibration":math,
      "frozen_equal_count_paired_histories":FROZEN_GROUPS,
      "native_identical_root_same_index_action_comparisons":comparison,
      "source_pairs_with_different_next_arrays":
          sum(not r["original_next_frame_stack_identical"] for r in comparison),
      "original_native_levels_histogram":
          dict(Counter(str(r["original_sdk_levels_completed"]) for r in receipts)),
      "official_level5_or_WIN_cases":[r["frozen_stage4_word"] for r in receipts
              if r["official_original_level5_or_WIN"]],
      "full_original_sdk_receipts":receipts,
      "epistemic_limit":"Same visible state and same action count tested directly; no archived same-visible-state at different index with same parity was available. F3 model and canonical agent unchanged. Original native level>=5/WIN is progression."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**saved)
    print("SP80_ROOTED_SAME_PARITY_SUMMARY "+json.dumps({
       k:v for k,v in result.items()
       if k not in ("frozen_equal_count_paired_histories",
                    "native_identical_root_same_index_action_comparisons",
                    "full_original_sdk_receipts")},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
