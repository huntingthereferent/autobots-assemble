"""Independent 64x64 original-SDK source proof: cup windows in advancing vs nonadvancing pours.

Input is an authenticated ZIP's extracted original native JSON and NPZ. Derive
45-cell source cups directly from each level's actual pre-pour palette11
connected components rather than borrowing level4 cup coordinates for level3.
A/B original entrance witnesses must agree on all measured source effects.
This is screen observation, not a decoded private game success rule.
"""
from __future__ import annotations
import argparse
from collections import deque
import json
from pathlib import Path
import numpy as np

CASES=("four_cup_transient","three_cup_negative")
WITNESSES=("A","B")
NEIGHBORS=((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))

def native_masks(frame):
    if frame.shape!=(64,64):raise AssertionError("Authentic original SDK grid required")
    source=frame==11
    seen=np.zeros(source.shape,bool)
    objects=[]
    for y in range(64):
        for x in range(64):
            if not source[y,x] or seen[y,x]:continue
            seen[y,x]=True
            pending=deque([(y,x)])
            pixels=[]
            while pending:
                cy,cx=pending.popleft()
                pixels.append((cy,cx))
                for dy,dx in NEIGHBORS:
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<64 and 0<=nx<64 and source[ny,nx] and not seen[ny,nx]:
                        seen[ny,nx]=True;pending.append((ny,nx))
            if len(pixels)!=45:
                raise AssertionError("Unexpected authentic palette11 component size "+str(len(pixels)))
            cell=np.zeros(source.shape,bool)
            for cy,cx in pixels:cell[cy,cx]=True
            ys,xs=np.where(cell)
            objects.append({"bbox":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
                            "mask":cell})
    objects.sort(key=lambda o:(o["bbox"][1],o["bbox"][0]))
    if len(objects)!=4 or int(source.sum())!=180:
        raise AssertionError("Four original source-defined 45-pixel cup masks required")
    return objects

def inspect(original_root,frames):
    if frames.ndim!=3 or frames.shape[1:]!=(64,64) or len(frames)<2:
        raise AssertionError("Original native SDK returned 64x64 source stack required")
    regions=native_masks(original_root)
    counts=[
        [int(np.count_nonzero((frame==13)&obj["mask"])) for obj in regions]
        for frame in frames
    ]
    fully=[i for i,v in enumerate(counts) if all(n==45 for n in v)]
    descriptions=[]
    for i,obj in enumerate(regions):
        hits=[t for t,record in enumerate(counts) if record[i]==45]
        descriptions.append({"original_source_bbox_xyxy":obj["bbox"],
                "native_first_full_frame":hits[0] if hits else None,
                "native_last_full_frame":hits[-1] if hits else None,
                "original_last_two_cup_palette13":[counts[-2][i],counts[-1][i]],
                "native_full_frame_indices":hits})
    return {"original_native_animation_frames":int(len(frames)),
        "source_original_palette11_cup_count":len(regions),
        "source_cups":descriptions,
        "source_four_cup_full_frame_indices":fully,
        "source_last_two_total_palette13":[int((frames[-2]==13).sum()),int((frames[-1]==13).sum())],
        "source_total_palette13_at_first_four":int((frames[fully[0]]==13).sum()) if fully else None,
        "source_final_all_cup_palette13":counts[-1],
        "source_last_frame_changed_pixels":int(np.count_nonzero(frames[-1]!=frames[-2]))}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",type=Path,required=True)
    p.add_argument("--npz",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    data=json.loads(args.json.read_text())
    if data.get("kind")!="SP80_ORIGINAL_SDK_CONFIRMED_LEVEL3_SUCCESS_VS_LEVEL4_NONADVANCE" or data.get("original_native_resets")!=4:
        raise ValueError("Original verified paired-SDK source required")
    results=[]
    with np.load(args.npz,allow_pickle=False) as archive:
        for row in data["native_original_source_rows"]:
            name=row["condition"];w=row["witness"]
            if name not in CASES or w not in WITNESSES:raise AssertionError("Unexpected original SDK run")
            n=len(next(word for label,word in data["frozen_comparison_cases"] if label==name).split())
            before3=archive[name+"_"+w+"_entry3_33"][-1]
            frames3=archive[name+"_"+w+"_entry3_34"]
            before4=archive[name+"_"+w+"_stage4_"+str(n-1)][-1]
            frames4=archive[name+"_"+w+"_stage4_"+str(n)]
            receipt3=row["genuine_stage3_success"]["original_action_receipt"]
            receipt4=row["genuine_stage4_nonadvance"]["original_action_receipt"]
            if (receipt3["sdk_level_before"],receipt3["sdk_level_after"],receipt3["genuine_original_action"])!=(3,4,5):
                raise AssertionError("Genuine advancing source receipt absent")
            if (receipt4["sdk_level_before"],receipt4["sdk_level_after"],receipt4["genuine_original_action"])!=(4,4,5):
                raise AssertionError("Genuine nonadvancing source receipt absent")
            transition3=inspect(before3,frames3)
            transition4=inspect(before4,frames4)
            stage4_root=archive[name+"_"+w+"_entry3_34"][-1]
            if not np.array_equal(stage4_root,frames3[-1]):
                raise AssertionError("Successful returned final frame did not match original stage4 root")
            if transition3["source_last_two_total_palette13"]!=row["genuine_stage3_success"]["last_two_palette13"]:
                raise AssertionError("SDK stage3 source summary mismatch")
            if transition4["source_last_two_total_palette13"]!=row["genuine_stage4_nonadvance"]["last_two_palette13"]:
                raise AssertionError("SDK stage4 source summary mismatch")
            results.append({"condition":name,"witness":w,
                "real_sdk_stage3_receipt":receipt3,"real_sdk_stage4_receipt":receipt4,
                "original_success_stage3":transition3,
                "original_nonadvance_stage4":transition4})
    if len(results)!=4:raise AssertionError("Expected four genuine SDK sessions")
    for name in CASES:
        group=[v for v in results if v["condition"]==name]
        if len(group)!=2 or {q["witness"] for q in group}!={"A","B"}:
            raise AssertionError("Missing original SDK independent entrance")
        for key in ("real_sdk_stage3_receipt","real_sdk_stage4_receipt","original_success_stage3","original_nonadvance_stage4"):
            if group[0][key]!=group[1][key]:raise AssertionError("Original source A/B mismatch "+name+" "+key)
    for row in results:
        if row["original_success_stage3"]["source_four_cup_full_frame_indices"]!=[27,28]:
            raise AssertionError("Source-derived winning cup timing differs")
        expect=list(range(25,33)) if row["condition"]=="four_cup_transient" else []
        if row["original_nonadvance_stage4"]["source_four_cup_full_frame_indices"]!=expect:
            raise AssertionError("Native stage4 cup timing differs from authenticated source")
        for phase in ("original_success_stage3","original_nonadvance_stage4"):
            if row[phase]["source_final_all_cup_palette13"]!=[0,0,0,0]:
                raise AssertionError("Native returned terminal cup state differs")
    report={"kind":"ARC4_NATIVE_SUCCESS_AND_NONADVANCE_SOURCE_DEFINED_CUPS",
        "original_source_run_id":39762841397,
        "original_source_artifact_id":12418353014,
        "independent_sdk_resets":len(results),
        "original_sdk_receipts_and_cup_timelines":results,
        "boundary":"Four simultaneous source-defined 45-pixel cups appear in both successful stage3 and nonadvancing stage4. Only original SDK level receipts establish progress; different level geometries do not imply one hidden objective."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    print("ARC4_SOURCE_DEFINED_CUP_COMPARISON "+json.dumps({
      "original_sdk_resets":len(results),
      "stage3_success":{"sdk_level_change":"3->4","four_cup_full":results[0]["original_success_stage3"]["source_four_cup_full_frame_indices"],
                        "native_animation_frames":results[0]["original_success_stage3"]["original_native_animation_frames"],
                        "cup_bboxes":[q["original_source_bbox_xyxy"] for q in results[0]["original_success_stage3"]["source_cups"]]},
      "stage4_nonadvance_four_cup":{"sdk_level_change":"4->4",
                      "four_cup_full":results[0]["original_nonadvance_stage4"]["source_four_cup_full_frame_indices"],
                      "native_animation_frames":results[0]["original_nonadvance_stage4"]["original_native_animation_frames"],
                      "cup_bboxes":[q["original_source_bbox_xyxy"] for q in results[0]["original_nonadvance_stage4"]["source_cups"]]},
      "stage4_three_cup_control":{"sdk_level_change":"4->4",
                      "four_cup_full":results[2]["original_nonadvance_stage4"]["source_four_cup_full_frame_indices"]},
      "all_A_B_source_agreement":True},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
