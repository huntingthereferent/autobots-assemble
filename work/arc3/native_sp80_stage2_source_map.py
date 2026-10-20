"""Read an authentic original SP80 stage2 screen and one source pour.

No imitation puzzle, engine physics, guessed goals, or F3 correspondence.
The grid is *printed as observed*, with symbols 0..F for source palette
indices. Any semantics attached later must cite source tests separately.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np

from .native_sp80_stage2_click_inventory import trial
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_multi_select import parse_plan

def color_components(frame):
    # These are measured same-color connected screen regions, not object labels.
    out=[]
    for color in np.unique(frame):
        pixels=np.asarray(frame==color)
        seen=np.zeros(pixels.shape,dtype=np.uint8)
        for y in range(64):
            for x in range(64):
                if not pixels[y,x] or seen[y,x]:continue
                q=[(y,x)];seen[y,x]=1;xs=[];ys=[]
                while q:
                    cy,cx=q.pop();xs.append(cx);ys.append(cy)
                    for ny,nx in ((cy+1,cx),(cy-1,cx),(cy,cx+1),(cy,cx-1)):
                        if 0<=ny<64 and 0<=nx<64 and pixels[ny,nx] and not seen[ny,nx]:
                            seen[ny,nx]=1;q.append((ny,nx))
                if len(xs)>1:
                    out.append({
                        "palette":int(color),"pixels":len(xs),
                        "bbox":[min(xs),min(ys),max(xs),max(ys)]
                    })
    return sorted(out,key=lambda e:(e["palette"],-e["pixels"],e["bbox"]))
def sha(frame):
    return hashlib.sha256(np.asarray(frame,dtype=np.uint8).tobytes()).hexdigest()
def scene(frame):
    colors=np.asarray(frame,dtype=np.uint8)
    if colors.shape!=(64,64):raise AssertionError("Not authentic 64x64 frame")
    chars="0123456789ABCDEF"
    if int(colors.max())>15:raise AssertionError("Original palette exceeds 16")
    return ["".join(chars[int(z)] for z in row) for row in colors]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rec=[]
    for name,word in STAGE1_WITNESSES:
        result,raw=trial(name,word,"original_stage2_first_pour","5",0)
        if result["source_genuine_level2_entry"]["source_original_level"]!=2:
            raise RuntimeError("Genuine SDK stage2 did not materialize")
        key="witness_"+str(len(parse_plan(word)))
        pre=np.asarray(raw[key][-1])
        pour=np.asarray(raw["stage2_1"])
        frames=[]
        for i,frame in enumerate(pour):
            changed=pre!=frame
            ys,xs=np.nonzero(changed)
            frames.append({
                "source_frame_index":i,
                "source_sha256":sha(frame),
                "changed_original_source_pixels":int(changed.sum()),
                "changed_bbox":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None,
                "observed_palette_changes":dict(Counter("%d>%d"%(int(a),int(b)) for a,b in
                                          zip(pre[changed],frame[changed]))),
            })
        item={
            "source_native_entry_witness":name,
            "verified_source_level":result["source_genuine_level2_entry"]["source_original_level"],
            "source_game_pre_pour_sha256":sha(pre),
            "source_original_pre_pour_ascii_palette":scene(pre),
            "original_source_connected_same_palette_regions":color_components(pre),
            "native_first_pour_frames":frames,
            "native_SDK_end_level":result["original_source_final_level"],
            "native_SDK_end_state":result["original_source_final_state"],
            "original_SDK_pour_frame_count":int(len(pour)),
            "original_source_action_records":result["full_original_SDK_action_records"],
        }
        rec.append(item)
        print("ORIGINAL_SP80_STAGE2_SOURCE_MAP_BEGIN "+name)
        for y,row in enumerate(item["source_original_pre_pour_ascii_palette"]):
            print("%02d %s"%(y,row))
        print("ORIGINAL_SP80_STAGE2_SOURCE_MAP_END "+name)
        print("ORIGINAL_SOURCE_MAP_REGIONS "+name+" "+json.dumps(item["original_source_connected_same_palette_regions"],sort_keys=True))
        print("ORIGINAL_SOURCE_MAP_POUR "+name+" "+json.dumps({
            "native_SDK_end_level":item["native_SDK_end_level"],
            "native_SDK_end_state":item["native_SDK_end_state"],
            "original_SDK_pour_frame_count":item["original_SDK_pour_frame_count"],
            "first_pour_frames_changed":[f["changed_original_source_pixels"] for f in frames],
            "source_pre_pour_sha256":item["source_game_pre_pour_sha256"],
        },sort_keys=True))
    if len(rec)!=2:raise RuntimeError("Missing independent original source witness")
    out={"kind":"OBSERVED_ORIGINAL_SP80_STAGE2_ASCII_SOURCE_IMAGES_AND_POUR","full_native_witness_records":rec,
         "limits":"Hex palette is the unmodified original SDK frame value; pixel components only; no inferred cups, spouts, spill predicate or physics. First native pour accepted only with genuine source stage2 entry."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    print("ORIGINAL_SP80_STAGE2_SOURCE_MAP_SUMMARY "+json.dumps({
        "two_independently_witnessed_original_stage2_entries":len(rec),
        "same_original_stage2_screen": rec[0]["source_game_pre_pour_sha256"]==rec[1]["source_game_pre_pour_sha256"],
        "source_after_first_pour_levels":[r["native_SDK_end_level"] for r in rec],
    },sort_keys=True))
if __name__=="__main__":main()
