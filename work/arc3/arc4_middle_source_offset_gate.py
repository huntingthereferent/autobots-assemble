"""Independent native SP80 Level4 source proof: middle-bar adjacency intervention.

Audit raw original SDK return stacks, native level/event receipts, original
clicked pixels, source-selected left-middle bbox and measured spill pixels.
The experiment's measurement routine is NOT imported.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_stage4_middle_source_offset import FROZEN,PARENTS,MIDDLE_MOVES,RIGHT_FIXED,UPPER_FIXED
from .native_sp80_multi_select import parse_plan
from .arc4_two_strand_composition_gate import compute,framehash

CONTRACT=Path("work/arc3/arc4_middle_source_offset_contract.json")
DEFAULT=Path("runtime/data/arc4/mid-source/original-mid-source.json")
def require(cond,message):
    if not cond:raise ValueError("ARC4_ORIGINAL_SDK_MIDDLE_SOURCE_MATH_WALL: "+message)
def selected_bbox(frame):
    yy,xx=np.nonzero(frame==9)
    require(len(xx)==27,"source selected left-middle 27-pixel bar not found")
    return [int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]
def context():
    c=json.loads(CONTRACT.read_text(encoding="utf8"))
    require(c["schema_version"]==1 and
            c["parent_original_run"]==40166014281 and
            c["parent_original_artifact"]==12588047670 and
            c["source_root"]=="fa8fd32d3bfd2c8b3ff7765aec373512" and
            c["frozen_original_sdk_resets"]==16 and
            c["source_code"]=="work/arc3/native_sp80_stage4_middle_source_offset.py",
            "original SDK source-parent and finite fixed protocol drift")
    f=c["factors"]
    require(f["clean_lower_parents"]==[p[0] for p in PARENTS] and
            f["middle_extra_actions"]==[list(x) for x in MIDDLE_MOVES] and
            f["right_middle_fixed"]==RIGHT_FIXED and
            f["upper_fixed"]==UPPER_FIXED and
            f["independent_original_native_entries"]==["A","B"] and
            len(FROZEN)==8 and len({n for n,w in FROZEN})==8,
            "native original source factor family is not frozen")
    for _,w in FROZEN:
        acts=parse_plan(w)
        require(acts[-1][0]==5 and
                sum(a==5 for a,xy in acts)==1 and
                sum(a==6 for a,xy in acts)==4,
                "genuine original SDK click/pour program drift")
    require("levels_completed>=5" in c["actual_native_progress"],
            "genuine SDK official advance oracle absent")
    return c
def inspect(c,path):
    path=Path(path)
    require(path.is_file() and path.with_suffix(".npz").is_file(),"original SDK saved native JSON/NPZ missing")
    data=json.loads(path.read_text(encoding="utf8"))
    require(data["kind"]=="ORIGINAL_SP80_LEVEL4_NATIVE_LEFT_MIDDLE_SOURCE_ADJACENCY"
            and data["native_level4_root"]==c["source_root"]
            and data["frozen_words"]==[list(x) for x in FROZEN]
            and data["original_native_sdk_resets"]==16,
            "original SDK native study was changed after freezing")
    records={(v["case"],v["witness"]):v for v in data["original_native_cases"]}
    require(len(records)==16 and set(records)=={
        (n,w) for n,p in FROZEN for w in ("A","B")},
        "independent real original SDK A/B resets incomplete")
    parent={p:(base,l,y) for p,base,l,y in PARENTS}
    outcomes={};level=Counter();advances=0;control_drift=[]
    with np.load(path.with_suffix(".npz"),allow_pickle=False) as arrays:
        for name,word in FROZEN:
            pname,movename=name.rsplit("_",1)
            base,l,expected_y=parent[pname]
            expected_x={"LEFT1":11,"HOLD":14,"RIGHT1":17,"RIGHT2":20}[movename]
            mid_index=len(parse_plan(" ".join(p for p in (
              RIGHT_FIXED,"6@24,33 "+base+(
                " "+dict(MIDDLE_MOVES)[movename] if dict(MIDDLE_MOVES)[movename] else "")
            ) if p)))
            witness_records=[]
            for witness in ("A","B"):
                raw=records[(name,witness)]
                require(raw["frozen_original_stage4_word"]==word and
                        raw["original_native_mid_last_action_index"]==mid_index,
                        "actual original selected middle index/action word disagrees")
                actions=parse_plan(word)
                led=raw["actual_native_stage4_action_ledger"]
                require(len(led)==raw["original_native_actions_executed"] and
                        mid_index<=len(led)<=len(actions),
                        "original source native stage4 ledger length changed")
                root=arrays[f"{name}_{witness}_entry3_34"][-1]
                require(root.shape==(64,64) and framehash(root)==c["source_root"],
                        "genuine original SDK Level4 root changed")
                previous=root
                for i,((action,xy),receipt) in enumerate(zip(actions,led),1):
                    frames=arrays[f"{name}_{witness}_stage4_{i}"]
                    require(frames.ndim==3 and frames.shape[1:]==(64,64)
                            and len(frames)==receipt["original_sdk_frame_stack_count"]
                            and receipt["genuine_original_action"]==action
                            and receipt["real_native_click_xy"]==
                              (list(xy) if xy is not None else None)
                            and action in receipt["original_legal_actions_before"]
                            and receipt["original_sdk_level_before"]>=4
                            and receipt["source_frame_before_blake2b16"]==framehash(previous)
                            and receipt["source_frame_after_blake2b16"]==framehash(frames[-1]),
                            "actual SDK original source action/level/hash receipt fails")
                    if xy is not None:
                        x,y=xy
                        require(receipt["original_source_pixel_before_click"]==int(previous[y,x]),
                                "original native click source pixel differs")
                    previous=frames[-1]
                mid=arrays[f"{name}_{witness}_stage4_{mid_index}"][-1]
                bbox=selected_bbox(mid)
                require(raw["original_native_mid_selected_bbox"]==bbox and
                        bbox==[expected_x,expected_y,expected_x+8,expected_y+2],
                        "source selected middle bar did not genuinely move to expected 9x3 position")
                after=led[-1]
                require(raw["official_original_sdk_level"]==after["original_sdk_level_after"]
                        and raw["official_original_sdk_state"]==after["original_sdk_state_after"]
                        and raw["official_original_sdk_level5_or_WIN"]==
                          (raw["official_original_sdk_level"]>=5 or
                           raw["official_original_sdk_state"]=="WIN"),
                        "original SDK official success oracle contradicted by source")
                advances+=int(raw["official_original_sdk_level5_or_WIN"])
                level[str(raw["official_original_sdk_level"])]+=1
                if not raw["original_native_frozen_word_complete"]:
                    require(raw["official_original_sdk_level5_or_WIN"] and
                            raw["original_native_observation"] is None,
                            "original SDK incomplete action program without advancement")
                    witness_records.append({"witness":witness,"advance_before_pour":True,
                                            "official_level":raw["official_original_sdk_level"]})
                    continue
                require(len(led)==len(actions) and after["genuine_original_action"]==5,
                        "native final actual SDK ACTION5 missing")
                pre=arrays[f"{name}_{witness}_stage4_{len(actions)-1}"][-1]
                pour=arrays[f"{name}_{witness}_stage4_{len(actions)}"]
                metrics=compute(root,pre,pour)
                obs=raw["original_native_observation"]
                require(obs is not None,"original SDK native observation missing")
                original=obs["genuine_source_measurements"]
                require(original["original_source_cup_first_full_frames"]==metrics["cups_first"]
                        and original["original_source_cup_max_palette13_pixels"]==metrics["cups_max"]
                        and original["native_first_simultaneously_full_four_cups"]==metrics["first_four"]
                        and all((None if original["first_original_color6_at_3_upper_sites"][key] is None
                                 else original["first_original_color6_at_3_upper_sites"][key]
                                 ["native_original_frame"])==t
                                for key,t in metrics["site_first"].items())
                        and all((None if original["native_first_source_border_changes"][key] is None
                                else original["native_first_source_border_changes"][key]
                                ["native_original_frame"])==t
                                for key,t in metrics["border_first"].items()),
                        "independent source full cup and offcup source palette event disagreement")
                require(obs["all_four_cups_simultaneous"]==(metrics["first_four"] is not None)
                        and obs["topmiddle_max13"]==metrics["cups_max"]["top_middle"]
                        and obs["top_left_max13"]==metrics["cups_max"]["top_left"]
                        and obs["leftmost_x11_13_new6"]==
                           (metrics["site_first"]["leftmost_outside_cup"] is not None)
                        and obs["selected_upper_original_prepour_hash"]==framehash(pre)
                        and obs["original_sdk_pour_last_hash"]==framehash(pour[-1]),
                        "derived genuine source-native observation contradicts NPZ")
                sites={}
                for x in (5,8,11,14,17,20):
                    idx=next((i for i,f in enumerate(pour)
                              if np.any((pre[5:8,x:x+3]!=6)&(f[5:8,x:x+3]==6))),None)
                    sites[f"x{x}_{x+2}"]=idx
                require(obs["first_new_palette6_upper_left_by_column"]==sites
                        and obs["upper_left_offcup_any_x5_16"]==
                           any(sites[k] is not None for k in
                               ("x5_7","x8_10","x11_13","x14_16")),
                        "source observed upper-left overflow shifted but verifier missed it")
                witness_records.append({
                    "witness":witness,"middle_bbox":bbox,
                    "sdk_level":raw["official_original_sdk_level"],
                    "official_advance":raw["official_original_sdk_level5_or_WIN"],
                    "first_native_source_upper_left_by_column":sites,
                    "any_upper_left_outside_cup":obs["upper_left_offcup_any_x5_16"],
                    "original_cup_topmiddle_max13":metrics["cups_max"]["top_middle"],
                    "original_cup_top_left_max13":metrics["cups_max"]["top_left"],
                    "first_simultaneous_four_cups_frame":metrics["first_four"],
                    "native_top_border_frame":metrics["border_first"]["top"],
                    "native_right_border_frame":metrics["border_first"]["right"],
                })
            require(len(witness_records)==2 and [x["witness"] for x in witness_records]==["A","B"]
                    and {k:v for k,v in witness_records[0].items() if k!="witness"}==
                        {k:v for k,v in witness_records[1].items() if k!="witness"},
                    "two independent genuine SDK native replays disagreed")
            outcomes[name]=witness_records[0]
    require(data["genuine_original_level5_or_WIN_count"]==advances,
            "original SDK official level progress count differs")
    for pname,base,l,y in PARENTS:
        hold=outcomes[pname+"_HOLD"]
        if (hold.get("first_native_source_upper_left_by_column",{}).get("x11_13") is None
              or hold.get("original_cup_topmiddle_max13")!=45
              or hold.get("first_simultaneous_four_cups_frame") is None):
            control_drift.append({"case":pname+"_HOLD","actual_original_sdk_source":hold})
    comparisons=[{
      "original_lower_parent":pname,
      "measured_left_middle_control":outcomes[pname+"_HOLD"],
      "original_mid_left1":outcomes[pname+"_LEFT1"],
      "original_mid_right1":outcomes[pname+"_RIGHT1"],
      "original_mid_right2":outcomes[pname+"_RIGHT2"],
    } for pname,base,l,y in PARENTS]
    return {
      "kind":"ORIGINAL_ARC4_LEVEL4_LEFT_MIDDLE_SOURCE_ADJACENCY_VERIFIED",
      "original_sdk_source_contract":c["id"],
      "original_sdk_resets":len(records),
      "original_sdk_level_histogram":dict(level),
      "original_sdk_official_level5_or_WIN":advances,
      "state":"REPLICATION_REQUIRED" if advances else
              "WALL_CONTROL_DRIFT" if control_drift else "PARTIAL",
      "native_baseline_control_drift":control_drift,
      "finite_original_source_middle_bar_comparisons":comparisons,
      "math_scope":"Source-bound finite neighboring 9x3 object versus original x11..13 rising pixel stream; cannot infer global physics, private state, or formal F3 A/B action map.",
      "next_movement":c["next_if_progress"] if advances else c["next_if_no_progress"],
      "walls":c["walls"],
    }
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("phase",choices=("pre","post"))
    ap.add_argument("--result",type=Path,default=DEFAULT)
    args=ap.parse_args();contract=context()
    if args.phase=="pre":
        print("ARC4_MIDDLE_SOURCE_PREFLIGHT "+json.dumps({
          "source":contract["id"],"original_sdk_resets":contract["frozen_original_sdk_resets"]
        },sort_keys=True),flush=True)
    else:
        result=inspect(contract,args.result)
        args.result.with_suffix(".protocol.json").write_text(json.dumps(result,indent=2)+"\n")
        print("ARC4_MIDDLE_SOURCE_VERIFIED "+json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":main()
