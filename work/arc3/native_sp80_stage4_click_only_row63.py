"""Genuine original SP80 stage4: matched click-only controls for the y63 signal.

No extra native movement is introduced. Preserve the frozen D3 lower source
word and real upper LEFT1→ACTION5. Extra source ACTION6 clicks are varied
and every actual pre-pour 64x64 difference and SDK outcome is retained.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_top_left_source_contrast import source_report
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

LOWER="6@46,33 3 6@24,33 2 2 2 3 3 6@34,42 3 3 3 1 1"
LAST_UPPER="6@34,21 3 5"
FROZEN=(
    ("original_no_extra_click",""),
    ("right_object_click","6@46,33"),
    ("background_click","6@5,16"),
    ("upper_object_click","6@34,21"),
    ("double_right_click","6@46,33 6@46,33"),
    ("double_background_click","6@5,16 6@5,16"),
    ("right_then_background_click","6@46,33 6@5,16"),
)

def first14(row):
    x=np.flatnonzero(row==14)
    return int(x[0]) if len(x) else None

def source_diff(before,after):
    coords=np.argwhere(before!=after)
    return {"pixel_count":int(len(coords)),
            "inside_y0_62":int(np.count_nonzero(before[:63]!=after[:63])),
            "last_y63":int(np.count_nonzero(before[63]!=after[63])),
            "differences":[{"xy":[int(x),int(y)],"before":int(before[y,x]),"after":int(after[y,x])}
                           for y,x in coords[:100]],
            "differences_truncated":len(coords)>100}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    opts=p.parse_args()
    rows=[];stacks={};pair_frames={};roots=set()
    for label,extra in FROZEN:
        native_word=" ".join(v for v in (LOWER,extra,LAST_UPPER) if v)
        actions=parse_plan(native_word)
        expected_extra=len(parse_plan(extra)) if extra else 0
        if actions[-1][0]!=5 or sum(a==5 for a,xy in actions)!=1:
            raise AssertionError("Exactly one native terminal ACTION5 required")
        for witness,entry in STAGE1_WITNESSES:
            native,actual=run_case(label,witness,entry,native_word)
            root=actual["entry3_34"][-1]
            pre=actual["stage4_"+str(len(actions)-1)][-1]
            animation=actual["stage4_"+str(len(actions))]
            obs=source_report(root,pre,animation)
            roots.add(obs["root_hash"])
            receipts=native["genuine_original_stage4_action_ledger"]
            extra_index=len(parse_plan(LOWER))
            extra_receipts=receipts[extra_index:extra_index+expected_extra]
            if len(extra_receipts)!=expected_extra or any(x["genuine_original_action"]!=6 for x in extra_receipts):
                raise AssertionError("Additional original SDK controls must be click only")
            if len(receipts)!=len(actions):raise AssertionError("Source action was not fully admitted")
            clicks=[]
            for item in extra_receipts:
                state_image=actual["stage4_"+str(item["index"])][-1]
                clicks.append({
                    "native_click_xy":item["real_native_click_xy"],
                    "real_pixel_before_click":item["original_source_pixel_before_click"],
                    "native_legal_actions_before":item["original_legal_actions_before"],
                    "native_state_after_click":item["original_sdk_state_after"],
                    "first_row63_palette14_x_after_click":first14(state_image[63]),
                    "source_image_after_click_hash":hash_frame(state_image),
                })
            row={
                "control":label,"witness":witness,"native_exact_word":native_word,
                "source_added_click_receipts":clicks,
                "original_sdk_level":native["true_original_sdk_final_level"],
                "original_sdk_state":native["true_original_sdk_final_state"],
                "official_level5_or_WIN":native["official_original_level5_or_WIN"],
                "source_measurement":obs,
                "native_first_row63_palette14_before_pour":first14(pre[63]),
                "native_first_row63_palette14_after_pour":first14(animation[-1,63]),
                "source_prepour_row63":[int(i) for i in pre[63]],
                "source_original_stage4_action_ledger":receipts,
            }
            rows.append(row)
            pair_frames[(label,witness)]=(pre.copy(),animation[-1].copy())
            for k,arr in actual.items():stacks[label+"_"+witness+"_"+k]=arr
            print("ARC4_CLICK_ONLY_CASE "+json.dumps({
                "case":label,"witness":witness,
                "source_clicks":clicks,
                "native_level":row["original_sdk_level"],"native_state":row["original_sdk_state"],
                "pre_row63_first14":row["native_first_row63_palette14_before_pour"],
                "source_cup_times":obs["source_first_full_cups"],
            },sort_keys=True),flush=True)
    if len(roots)!=1 or len(rows)!=len(FROZEN)*2:
        raise AssertionError("Independent original SDK entry count/root differs")
    diffs={}
    for label,_ in FROZEN:
        pair=[v for v in rows if v["control"]==label]
        if len(pair)!=2 or {x["witness"] for x in pair}!={"A","B"}:
            raise AssertionError("Independent native A/B witnesses absent")
        for field in ("source_added_click_receipts","original_sdk_level","original_sdk_state",
                      "source_measurement","native_first_row63_palette14_before_pour",
                      "native_first_row63_palette14_after_pour","source_prepour_row63"):
            if pair[0][field]!=pair[1][field]:
                raise AssertionError("Source SDK A/B discrepancy "+label+" "+field)
        if label=="original_no_extra_click":continue
        independent=[]
        for witness,_ in STAGE1_WITNESSES:
            base_pre,base_final=pair_frames[("original_no_extra_click",witness)]
            other_pre,other_final=pair_frames[(label,witness)]
            independent.append({"pre_pour":source_diff(base_pre,other_pre),
                                "post_pour":source_diff(base_final,other_final)})
        if independent[0]!=independent[1]:raise AssertionError("Original frame delta A/B disagrees")
        diffs[label]=independent[0]
    result={
        "kind":"ORIGINAL_SP80_STAGE4_SOURCE_ROW63_CLICK_ONLY_CONTROLS",
        "original_sdk_independent_resets":len(rows),
        "source_frozen_click_only_controls":FROZEN,
        "official_native_level_counts":dict(Counter(str(x["original_sdk_level"]) for x in rows)),
        "official_level5_or_WIN_count":sum(int(x["official_level5_or_WIN"]) for x in rows),
        "real_source_records":rows,"native_original_frame_deltas_vs_base":diffs,
        "limitations":"Original SDK accepted clicks and screen pixels only; a background click may affect selection, so interpretations are restricted to matched visible geometry. No decoded counter or win rule."
    }
    opts.out.parent.mkdir(parents=True,exist_ok=True)
    opts.out.write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(opts.out.with_suffix(".npz"),**stacks)
    print("ARC4_CLICK_ONLY_SUMMARY "+json.dumps({
        "source_resets":result["original_sdk_independent_resets"],
        "level5_or_WIN":result["official_level5_or_WIN_count"],
        "level_histogram":result["official_native_level_counts"],
        "cases":{name:{
            "added_native_clicks":len(next(v["source_added_click_receipts"] for v in rows if v["control"]==name)),
            "first14_before":next(v["native_first_row63_palette14_before_pour"] for v in rows if v["control"]==name),
            "first14_after":next(v["native_first_row63_palette14_after_pour"] for v in rows if v["control"]==name),
            "pre_differences":diffs[name]["pre_pour"] if name in diffs else None,
            "cup_times":next(v["source_measurement"]["source_first_full_cups"] for v in rows if v["control"]==name)}
            for name,_ in FROZEN}
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
