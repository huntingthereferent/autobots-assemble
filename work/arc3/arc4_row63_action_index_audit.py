"""Source-only test of original SDK SP80 stage4 row63 versus action ordinal.

Reads four real returned-frame NPZ archives; never executes a game or emulator.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from hashlib import sha256
import io
import json
from pathlib import Path
import zipfile
import numpy as np

ARCHIVES=("arc4-468-corrected.zip","arc4-519.zip","arc4-520.zip","arc4-521.zip")

def require(condition,why):
    if not condition:raise ValueError("ARC4_ROW63_SOURCE_WALL: "+why)

def audit(directory):
    by_index=defaultdict(list);total_frames=0;resets=0;base_patterns=set()
    for archive in ARCHIVES:
        with zipfile.ZipFile(directory/archive) as z:
            source=json.loads(z.read(next(x for x in z.namelist()
                       if x.endswith(".json") and "/" not in x and ".protocol." not in x)))
            npz=z.read(next(x for x in z.namelist()
                            if x.endswith(".npz") and "/" not in x))
            with np.load(io.BytesIO(npz),allow_pickle=False) as arrays:
                for native in source["native_cases"]:
                    case=native.get("case",native.get("control"))
                    witness=native.get("witness",native.get("native_witness"))
                    actions=native.get("native_action_receipts",native.get(
                        "genuine_stage4_action_ledger",native.get(
                            "genuine_stage4_action_receipts")))
                    prefix=case+"_"+witness+"_"
                    root=arrays[prefix+"entry3_34"][-1]
                    require(root.shape==(64,64),"missing genuine source entry frame")
                    base_patterns.add(bytes(root[63]))
                    resets+=1
                    for i,receipt in enumerate(actions,1):
                        original=arrays[prefix+"stage4_"+str(i)]
                        require(original.ndim==3 and original.shape[1:]==(64,64),
                                "genuine SDK returned frames absent")
                        row=bytes(original[-1,63])
                        require(all(bytes(frame[63])==row for frame in original),
                                "row63 changed within the native returned animation")
                        prefix_zeros=row.count(0)
                        require(row==bytes([0])*prefix_zeros+bytes([14])*(64-prefix_zeros),
                                "row63 is not contiguous original source 0/14 strip")
                        by_index[i].append((row,receipt["genuine_original_action"]))
                        total_frames+=len(original)
    require(len(base_patterns)==1,"original SDK root row63 varied")
    observations=[]
    for i,pairs in sorted(by_index.items()):
        distinct={p for p,_ in pairs}
        require(len(distinct)==1,"original row63 differs at equal SDK stage4 action index")
        pattern=next(iter(distinct))
        observations.append({
            "stage4_action_index":i,
            "source_returns":len(pairs),
            "row63_palette0_prefix":pattern.count(0),
            "row63_palette14_suffix":pattern.count(14),
            "distinct_original_actions":sorted({a for _,a in pairs}),
            "row63_sha256":sha256(pattern).hexdigest(),
        })
    return {
        "kind":"ORIGINAL_ARC4_ROW63_ACTION_INDEX_FORENSIC_AUDIT",
        "original_source_archives":len(ARCHIVES),
        "original_native_resets":resets,
        "per_action_returns_checked":sum(x["source_returns"] for x in observations),
        "returned_animation_frames_checked":total_frames,
        "distinct_stage4_indices":len(observations),
        "one_row63_pattern_per_action_index_within_archives":True,
        "no_within_action_return_row63_change":True,
        "row63_palette0_prefix_by_source_action_index":[
            x["row63_palette0_prefix"] for x in observations],
        "per_index_source_observations":observations,
        "boundary":"Observational correspondence in original archived SDK frames only. Does not establish a global deterministic HUD formula, internal engine state, or that row63 is never relevant outside these trials.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    report=audit(args.directory)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print("ARC4_ROW63_INDEX_AUDIT "+json.dumps(report,sort_keys=True),flush=True)

if __name__=="__main__":main()
