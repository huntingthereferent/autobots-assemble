"""ARC4 source-pinned row63 timeline reconstructed from saved original SDK frames.

No new native movements and no hidden engine assumptions: this audit verifies
exactly when returned screen row63 changes during predeclared movement words.
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path
import numpy as np

EXPECTED_COUNTS={"one_left":1,"three_horizontal":3,"three_vertical":3,
                 "five_horizontal":5,"five_vertical":5,
                 "seven_horizontal":7,"seven_vertical":7}
WITNESSES=("A","B")

def first14(row):
    xs=np.flatnonzero(row==14)
    return int(xs[0]) if len(xs) else None

def extract(record,arrays):
    name=record["case"];witness=record["witness"]
    ledger=record["native_action_receipts"]
    selections=[i for i,r in enumerate(ledger)
      if r["genuine_original_action"]==6 and r["real_native_click_xy"]==[34,21]]
    if len(selections)!=1:raise AssertionError("Exact original upper source click not found")
    upper=ledger[selections[0]+1:]
    movements=upper[:-1]
    if len(movements)!=EXPECTED_COUNTS[name] or upper[-1]["genuine_original_action"]!=5:
        raise AssertionError("Unexpected original SDK action sequence")
    if any(x["genuine_original_action"] not in (1,2,3,4) for x in movements):
        raise AssertionError("Non-movement in native upper history")
    frames=[]
    for number,receipt in enumerate(upper,1):
        key=name+"_"+witness+"_stage4_"+str(receipt["index"])
        arr=arrays[key]
        if arr.ndim!=3 or arr.shape[1:]!=(64,64):raise AssertionError("Bad source stack")
        before=arr[-1,63,:]
        pixels=[int(v) for v in before.tolist()]
        frames.append({"upper_action_number":number,
          "native_action":receipt["genuine_original_action"],
          "stage4_receipt_index":receipt["index"],
          "original_native_stack_length":int(len(arr)),
          "first_palette14_x_at_y63":first14(before),
          "original_source_row63":pixels,
          "official_level":receipt["original_sdk_level_after"],
          "official_state":receipt["original_sdk_state_after"]})
    return {"case":name,"witness":witness,
            "upper_native_movement_count":len(movements),
            "source_steps":frames,
            "source_prepour_row63":frames[-2]["original_source_row63"],
            "source_final_pour_row63":frames[-1]["original_source_row63"],
            "first_prepour_palette14_x":frames[-2]["first_palette14_x_at_y63"],
            "first_postpour_palette14_x":frames[-1]["first_palette14_x_at_y63"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--npz",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    source=json.loads(a.json.read_text())
    if source.get("kind")!="ORIGINAL_SP80_STAGE4_SAME_SELECTED_POSITION_LENGTH_CONTROLS":
        raise ValueError("Need the verified original stage4 movement-length SDK source")
    if source.get("original_sdk_independent_resets")!=14 or source.get("official_level5_or_WIN_count")!=0:
        raise ValueError("Unexpected native source scope")
    output=[]
    with np.load(a.npz,allow_pickle=False) as frames:
        for row in source["original_sdk_records"]:
            output.append(extract(row,frames))
    if len(output)!=14:raise AssertionError("Native original witness records missing")
    grouped=defaultdict(list)
    for row in output:grouped[row["case"]].append(row)
    if set(grouped)!=set(EXPECTED_COUNTS):raise AssertionError("Missing frozen paths")
    for name,pair in grouped.items():
        if len(pair)!=2 or {r["witness"] for r in pair}!={"A","B"}:
            raise AssertionError("Missing independent original SDK witness: "+name)
        first,second=pair
        if first["source_steps"]!=second["source_steps"] or first["source_prepour_row63"]!=second["source_prepour_row63"]:
            raise AssertionError("Source native A/B source-row difference: "+name)
    # The source row is independently tested for each action position in all
    # paths long enough to reach it. This is a repeated observation only.
    per_action={}
    for index in range(1,8):
        rows=[(x["case"],x["witness"],x["source_steps"][index-1]["first_palette14_x_at_y63"],
               x["source_steps"][index-1]["original_source_row63"])
              for x in output if x["upper_native_movement_count"]>=index]
        if not rows:raise AssertionError("No source at movement index")
        observed={json.dumps(item[3]) for item in rows}
        if len(observed)!=1:
            raise AssertionError("Different source row63 at the same movement index "+str(index))
        per_action[str(index)]={"native_witnessed_histories":len(rows),
              "first_palette14_x":rows[0][2],
              "source_row63":rows[0][3]}
    final={}
    for count in (1,3,5,7):
        rows=[r for r in output if r["upper_native_movement_count"]==count]
        xs={(r["first_prepour_palette14_x"],r["first_postpour_palette14_x"]) for r in rows}
        if len(xs)!=1:raise AssertionError("Path-matched original pre/post pour sources differ")
        final[str(count)]={"verified_original_sdk_games":len(rows),
          "before_pour_first14":rows[0]["first_prepour_palette14_x"],
          "after_pour_first14":rows[0]["first_postpour_palette14_x"]}
    report={"kind":"ORIGINAL_SP80_STAGE4_ROW63_SOURCE_TIMELINE",
       "source_native_run_id":39757263041,
       "source_native_artifact_id":12415838204,
       "native_original_sdk_records":output,
       "source_row63_at_movement_number":per_action,
       "source_pre_post_pour_by_path_length":final,
       "limitation":"Only the original returned row63 palette sequence is established. No private action counter, game objective, clock, or hidden-state equivalence is inferred."}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    print("ARC4_ROW63_TIMELINE_SUMMARY "+json.dumps({
       "movements":{k:{"x":v["first_palette14_x"],"witnessed":v["native_witnessed_histories"]}
                    for k,v in per_action.items()},
       "native_pre_postpour":final,
       "independent_original_sdk_records":len(output)},sort_keys=True))

if __name__=="__main__":
    main()
