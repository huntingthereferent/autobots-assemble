"""Native SP80 source-image rooted A/B: every immediate SDK action.

Original run #40239498741: same 64x64 visible state but different
ACTION5 returned source frame at precisely x10,y63. The only
difference was prior ACTION3 after reselecting left-middle.
This experiment freezes those two histories at that exact visible
root and applies each genuine currently advertised original SDK
ACTION1..ACTION6 once, without invented followup conditions.

Separately certify F3-48 mathematical rooted A/B relations; neither
a palette pixel nor an SDK action is claimed to be an F3 generator.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_rooted_ab_boundary_split import UP_A
from .native_sp80_stage4_rooted_ab_collision import f3_calibration
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

PARENT={"A":UP_A,"B":UP_A+" 3"}
EXPECTED_PRE="dd0b9861faae399ad607560e9181be42"
ACTIONS={
    "ACTION1_UP":"1","ACTION2_DOWN":"2","ACTION3_LEFT":"3",
    "ACTION4_RIGHT":"4","ACTION5_POUR":"5",
    "ACTION6_SELECT_UPPER":"6@34,21",
}
assert len(ACTIONS)==6 and len(STAGE1_WITNESSES)==2
assert all(len(parse_plan(command))==1 for command in ACTIONS.values())
def digest(arr):
    from hashlib import blake2b
    return blake2b(np.ascontiguousarray(arr).tobytes(),digest_size=16).hexdigest()

def perform(label,word,witness,entry,command):
    prefix=PARENT[label]
    pindex=len(parse_plan(prefix))
    trial,stacks=run_case("rooted_action_"+label,witness,entry,prefix+" "+command)
    pre=stacks["entry3_34"][-1] if pindex==0 else stacks[f"stage4_{pindex}"][-1]
    stack=stacks[f"stage4_{pindex+1}"]
    assert stack.ndim==3 and stack.shape[1:]==(64,64)
    assert hash_frame(pre)==EXPECTED_PRE
    receipt=trial["genuine_original_stage4_action_ledger"][-1]
    assert receipt["genuine_original_action"]==parse_plan(command)[-1][0]
    if receipt["genuine_original_action"]==6:
        assert receipt["original_source_pixel_before_click"]==8
    row={
      "history_label":label,"entry_witness":witness,"native_next_action":word,
      "native_stage4_word":prefix+" "+command,
      "exact_original_visible_source_before":hash_frame(pre),
      "true_sdk_action":receipt["genuine_original_action"],
      "true_sdk_action6_click_xy":receipt["real_native_click_xy"],
      "true_sdk_returned_frame_count":len(stack),
      "true_sdk_returned_all_frames_digest":digest(stack),
      "true_sdk_returned_last_frame_digest":hash_frame(stack[-1]),
      "actual_native_level":trial["true_original_sdk_final_level"],
      "actual_native_state":trial["true_original_sdk_final_state"],
      "official_level5_or_WIN":trial["official_original_level5_or_WIN"],
      "complete_original_stage4_source_action_receipts":trial["genuine_original_stage4_action_ledger"],
    }
    return row,pre,stack

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    certificates=f3_calibration()
    pairs=[];rows=[];arrays={}
    for name,command in ACTIONS.items():
        for witness,entry in STAGE1_WITNESSES:
            results=[]
            for history in ("A","B"):
                row,pre,stack=perform(history,name,witness,entry,command)
                results.append((row,pre,stack))
                rows.append(row)
                arrays[f"{name}_{history}_{witness}_pre"]=pre
                arrays[f"{name}_{history}_{witness}_returned"]=stack
            a,pa,xa=results[0];b,pb,xb=results[1]
            if not np.array_equal(pa,pb):
                raise AssertionError("Original SDK identical visible input split")
            if len(xa)==len(xb):
                y,x=np.nonzero(np.any(xa!=xb,axis=0))
                diffs=[[int(xx),int(yy)] for yy,xx in zip(y,x)]
                split_idx=next((int(t) for t in range(len(xa)) if
                         np.any(xa[t]!=xb[t])),None)
            else:
                diffs=None;split_idx=None
            result={
                "frozen_real_sdk_action":name,
                "original_independent_entry":witness,
                "genuine_same_full_visible_root":True,
                "next_native_frames_identical":bool(len(xa)==len(xb) and not diffs),
                "native_returned_frame_counts":[len(xa),len(xb)],
                "first_sdk_returned_frame_divergence":split_idx,
                "all_spatial_native_divergences_xy":diffs,
                "pixel_palette_pairs_in_first_returned_frame":
                    [[int(xa[0,yy,xx]),int(xb[0,yy,xx])]
                        for xx,yy in diffs] if diffs is not None else None,
                "official_levels":[a["actual_native_level"],b["actual_native_level"]],
                "official_states":[a["actual_native_state"],b["actual_native_state"]],
            }
            pairs.append(result)
            print("SP80_SAME_ROOT_SIX_ACTIONS_PAIR "+json.dumps(result,sort_keys=True),flush=True)
    assert len(rows)==24 and len(pairs)==12
    for name in ACTIONS:
        one,two=[r for r in pairs if r["frozen_real_sdk_action"]==name]
        if {k:v for k,v in one.items() if k!="original_independent_entry"}!={
           k:v for k,v in two.items() if k!="original_independent_entry"}:
            raise AssertionError("Two independent original SDK entry histories disagree")
    report={
       "kind":"GENUINE_NATIVE_SP80_VISIBLE_ROOTED_AB_EACH_SINGLE_LEGAL_ACTION",
       "original_independent_sdk_games":len(rows),
       "source_root_pixel_digest":EXPECTED_PRE,
       "frozen_A_B_different_paths_same_visible_root":PARENT,
       "all_six_original_legal_actions":ACTIONS,
       "mathematical_F3_rooted_relation_calibration":certificates,
       "genuine_native_A_B_action_pair_findings":pairs,
       "official_level5_or_WIN":[r["native_next_action"] for r in rows if r["official_level5_or_WIN"]],
       "official_level_histogram":dict(Counter(str(r["actual_native_level"]) for r in rows)),
       "full_original_action_and_frame_receipts":rows,
       "scope":"Public original SDK source frames only; equal visible inputs need not mean equal full hidden state. Original mathematical model and agent unchanged.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**arrays)
    print("SP80_SAME_ROOT_SIX_ACTIONS_SUMMARY "+json.dumps({
        k:v for k,v in report.items() if k not in
        ("genuine_native_A_B_action_pair_findings","full_original_action_and_frame_receipts")
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
