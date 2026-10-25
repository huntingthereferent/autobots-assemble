"""Independent source-native SP80 Level4 middle/L relational verifier.

Uses real SDK archived NPZ frame arrays and action-click receipts, but DOES
NOT call the experiment's measurement function. Reports blocked native moves
as observed nonmovement and never upgrades source cup filling to SDK victory.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage4_middle_height_spill import FROZEN,PARENTS,MIDDLE,HEIGHT,RIGHT_FIXED,UPPER_FIXED
from .native_sp80_multi_select import parse_plan
from .arc4_two_strand_composition_gate import compute,framehash

CONTRACT=Path("work/arc3/arc4_middle_height_spill_contract.json")
DEFAULT=Path("runtime/data/arc4/height-spill/original-height-spill.json")
def require(ok,reason):
    if not ok:raise ValueError("ORIGINAL_ARC4_MIDDLE_L_MATH_WALL: "+reason)
def bbox(frame):
    y,x=np.nonzero(frame==9)
    require(len(x)==27,"Original selected L has not 27 genuine source pixels")
    return [int(x.min()),int(y.min()),int(x.max()),int(y.max())]
def context():
    c=json.loads(CONTRACT.read_text())
    require(c["schema_version"]==1 and c["original_parent_run"]==40171009741
            and c["original_parent_artifact"]==12588949682
            and c["original_level4_root"]=="fa8fd32d3bfd2c8b3ff7765aec373512"
            and c["source_code"]=="work/arc3/native_sp80_stage4_middle_height_spill.py"
            and c["original_sdk_resets"]==24,
            "frozen original Level4 source provenance drift")
    f=c["factors"]
    require(f["lower_parents"]==[[n,x,y] for n,base,l,x,y in PARENTS]
            and f["middle_L_couplings"]==[list(v) for v in MIDDLE]
            and f["middle_vertical"]==[list(v) for v in HEIGHT]
            and f["right_middle"]==RIGHT_FIXED
            and f["upper"]==UPPER_FIXED
            and f["original_sdk_entry_witnesses"]==["A","B"]
            and len(FROZEN)==12 and len({n for n,w in FROZEN})==12,
            "native original finite source matrix changed")
    for name,word in FROZEN:
        cmds=parse_plan(word)
        require(cmds[-1][0]==5 and sum(a==5 for a,xy in cmds)==1
                and sum(a==6 for a,xy in cmds)==4,
                "original SDK click+pour alphabet drift")
    require("levels_completed>=5" in c["official_success"],
            "native official Level5 oracle missing")
    return c
def inspect(c,path):
    path=Path(path)
    require(path.is_file() and path.with_suffix(".npz").is_file(),
            "missing original SDK native source arrays")
    j=json.loads(path.read_text())
    require(j["kind"]=="ORIGINAL_SP80_LEVEL4_NATIVE_MIDDLE_HEIGHT_SPILL_RELATION"
            and j["true_original_level4_root"]==c["original_level4_root"]
            and j["frozen_source_words"]==[list(v) for v in FROZEN]
            and j["original_sdk_resets"]==24,
            "frozen Level4 genuine original source experiment identity drift")
    cases={(v["case"],v["witness"]):v for v in j["native_cases"]}
    require(len(cases)==24 and set(cases)=={
        (n,w) for n,_ in FROZEN for w in ("A","B")},
        "original SDK independent A/B source coverage lost")
    parents={n:(base,l,x,y) for n,base,l,x,y in PARENTS}
    obs={};levels=Counter();progress=0;block=[]
    with np.load(path.with_suffix(".npz"),allow_pickle=False) as npz:
        for name,word in FROZEN:
            parent=next(p for p in parents if name.startswith(p+"_"))
            mname,lname=name[len(parent)+1:].split("_")
            base,L,base_x,bar_y=parents[parent]
            mid_word,L_word=next((mid,l) for n,mid,l in MIDDLE if n==mname)
            height_word,dy=next((w,dy) for n,w,dy in HEIGHT if n==lname)
            mid_prefix=" ".join((RIGHT_FIXED,
                "6@24,33 "+base+(" "+mid_word if mid_word else "")+
                (" "+height_word if height_word else "")))
            mid_idx=len(parse_plan(mid_prefix))
            l_prefix="6@34,42 "+L+(" "+L_word if L_word else "")
            l_idx=mid_idx+len(parse_plan(l_prefix))
            expected_mid_x=14 if mname=="BASELINE" else 17
            expected_L_x=base_x if mname=="BASELINE" else base_x+3
            expected_mid_y=bar_y+dy
            witness_results=[]
            for witness in ("A","B"):
                row=cases[(name,witness)]
                cmds=parse_plan(word);led=row["actual_native_receipts"]
                require(row["frozen_original_stage4_word"]==word
                        and row["actual_source_middle_action_index"]==mid_idx
                        and row["actual_source_L_action_index"]==l_idx
                        and l_idx<=len(led)<=len(cmds),
                        "source original L action index or receipt count changed")
                root=npz[f"{name}_{witness}_entry3_34"][-1]
                require(root.shape==(64,64) and framehash(root)==c["original_level4_root"],
                        "source SDK Level4 exact entry frame not reproduced")
                previous=root
                for i,((aid,xy),receipt) in enumerate(zip(cmds,led),1):
                    frames=npz[f"{name}_{witness}_stage4_{i}"]
                    require(frames.ndim==3 and frames.shape[1:]==(64,64)
                            and len(frames)==receipt["original_sdk_frame_stack_count"]
                            and receipt["genuine_original_action"]==aid
                            and receipt["real_native_click_xy"]==(list(xy) if xy is not None else None)
                            and aid in receipt["original_legal_actions_before"]
                            and receipt["original_sdk_level_before"]>=4
                            and receipt["source_frame_before_blake2b16"]==framehash(previous)
                            and receipt["source_frame_after_blake2b16"]==framehash(frames[-1]),
                            "original source action receipt/hashes/legality mismatch")
                    if xy is not None:
                        xx,yy=xy
                        require(receipt["original_source_pixel_before_click"]==int(previous[yy,xx]),
                                "real original SDK native click source palette disagrees")
                    previous=frames[-1]
                middlebox=bbox(npz[f"{name}_{witness}_stage4_{mid_idx}"][-1])
                Lbox=bbox(npz[f"{name}_{witness}_stage4_{l_idx}"][-1])
                require(row["actual_selected_middle_bbox"]==middlebox
                        and row["actual_selected_L_bbox"]==Lbox,
                        "saved native source-selected middle/L bboxes differ from NPZ")
                require(Lbox==[expected_L_x,35,expected_L_x+5,40],
                        "original source compensated lower L geometry changed")
                expected_middle=[expected_mid_x,expected_mid_y,
                                 expected_mid_x+8,expected_mid_y+2]
                default_middle=[expected_mid_x,bar_y,expected_mid_x+8,bar_y+2]
                blocked=(dy!=0 and middlebox==default_middle)
                moved=(dy!=0 and middlebox==expected_middle)
                require(middlebox==expected_middle or blocked,
                        "real selected middle bar source geometry outside predeclared interval")
                if blocked:block.append([name,witness])
                after=led[-1]
                require(row["official_original_sdk_level"]==after["original_sdk_level_after"]
                    and row["official_original_sdk_state"]==after["original_sdk_state_after"]
                    and row["official_original_level5_or_WIN"]==
                       (row["official_original_sdk_level"]>=5 or row["official_original_sdk_state"]=="WIN"),
                    "original SDK game success predicate contradicts saved native receipt")
                progress+=int(row["official_original_level5_or_WIN"])
                levels[str(row["official_original_sdk_level"])]+=1
                if not row["original_word_complete"]:
                    require(row["official_original_level5_or_WIN"]
                            and row["measured_original_source"] is None,
                            "unverified SDK early exit without native progression")
                    witness_results.append({"witness":witness,"early_progress":True,
                                            "official_level":row["official_original_sdk_level"]})
                    continue
                require(len(led)==len(cmds) and after["genuine_original_action"]==5,
                        "source native last ACTION5/animation missing")
                pre=npz[f"{name}_{witness}_stage4_{len(cmds)-1}"][-1]
                pour=npz[f"{name}_{witness}_stage4_{len(cmds)}"]
                independently=compute(root,pre,pour)
                stored=row["measured_original_source"]
                require(stored is not None,"source original metrics missing")
                original=stored["genuine_original_source_metrics"]
                require(original["original_source_cup_first_full_frames"]==independently["cups_first"]
                    and original["original_source_cup_max_palette13_pixels"]==independently["cups_max"]
                    and original["native_first_simultaneously_full_four_cups"]==independently["first_four"]
                    and all((None if original["first_original_color6_at_3_upper_sites"][name] is None
                               else original["first_original_color6_at_3_upper_sites"][name]["native_original_frame"])==first
                            for name,first in independently["site_first"].items())
                    and all((None if original["native_first_source_border_changes"][name] is None
                               else original["native_first_source_border_changes"][name]["native_original_frame"])==first
                            for name,first in independently["border_first"].items()),
                    "full original source native NPZ cup / strand / border independent remeasurement differs")
                regions={}
                for x in (5,8,11,14,17,20):
                    regions[f"x{x}_{x+2}"]=next(
                       (i for i,frame in enumerate(pour)
                        if np.any((pre[5:8,x:x+3]!=6)&(frame[5:8,x:x+3]==6))),
                       None)
                require(regions==stored["source_upper_left_new6_first_by_3px_band"]
                        and stored["source_upper_left_offcup_wider_detected"]==
                          any(regions[name] is not None for name in ("x5_7","x8_10","x11_13","x14_16"))
                        and stored["native_cup_max_palette13"]==independently["cups_max"]
                        and stored["native_four_cups_together"]==(independently["first_four"] is not None)
                        and stored["lateral_cup_full"]==(independently["cups_max"]["left_lateral"]==45)
                        and stored["topmiddle_cup_full"]==(independently["cups_max"]["top_middle"]==45)
                        and stored["prepour_original_hash"]==framehash(pre)
                        and stored["final_original_hash"]==framehash(pour[-1]),
                        "full native SDK independent source-region or cup predicate mismatch")
                witness_results.append({
                    "witness":witness,"official_level":row["official_original_sdk_level"],
                    "official_progress":row["official_original_level5_or_WIN"],
                    "real_middle_bbox":middlebox,"real_lower_L_bbox":Lbox,
                    "middle_vertical_genuinely_moved":moved,
                    "middle_vertical_blocked":blocked,
                    "upper_left_offcup_first":regions,
                    "all_original_cup_max13":independently["cups_max"],
                    "all_four_together_frame":independently["first_four"],
                    "top_edge_first":independently["border_first"]["top"],
                    "right_edge_first":independently["border_first"]["right"],
                })
            require(len(witness_results)==2
                    and [v["witness"] for v in witness_results]==["A","B"]
                    and {k:v for k,v in witness_results[0].items() if k!="witness"}==
                        {k:v for k,v in witness_results[1].items() if k!="witness"},
                    "independent original SDK A/B actual native frame witnesses disagree")
            obs[name]=witness_results[0]
    require(progress==j["official_level5_or_WIN_count"],
            "original SDK level5 count cannot be independently substantiated")
    control_drift=[]
    for p,*_ in PARENTS:
        for coupling,source_band in (("BASELINE","x11_13"),
                                     ("COMPENSATED","x14_16")):
            key=p+"_"+coupling+"_HOLD"
            r=obs[key]
            spill=r.get("upper_left_offcup_first",{})
            if (r.get("all_original_cup_max13",{}).get("left_lateral")!=45
                or r.get("all_original_cup_max13",{}).get("top_middle")!=45
                or r.get("all_four_together_frame") is None
                or spill.get(source_band) is None
                or r.get("official_level")!=4):
                control_drift.append({"source_case":key,"original_observed":r})
    relations=[]
    for p,*_ in PARENTS:
        for coupling,mid,l in MIDDLE:
            relations.append({
                "source_clean_parent":p,"finite_coupling":coupling,
                "source_up1":obs[p+"_"+coupling+"_UP1"],
                "source_hold":obs[p+"_"+coupling+"_HOLD"],
                "source_down1":obs[p+"_"+coupling+"_DOWN1"],
            })
    return {
        "kind":"ORIGINAL_SP80_LEVEL4_MIDDLE_HEIGHT_SPILL_VERIFIED",
        "contract":c["id"],"real_sdk_resets":len(cases),
        "official_sdk_levels":dict(levels),
        "official_sdk_level5_or_WIN":progress,
        "state":"REPLICATION_REQUIRED" if progress else (
          "WALL_CONTROL_DRIFT" if control_drift else "PARTIAL"),
        "control_drift":control_drift,
        "blocked_original_middle_vertical_actions":block,
        "finite_original_middle_y_spill_relations":relations,
        "math_scope":"finite original source middle-bar y-dependence of spill x14..16 under independently restored four-cup lower-L x-coupling; no formal F3 generator map or inferred physics",
        "next_movement":c["next_progress"] if progress else c["next_no_progress"],
        "walls":c["walls"],
    }
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("phase",choices=("pre","post"))
    ap.add_argument("--result",type=Path,default=DEFAULT)
    args=ap.parse_args()
    c=context()
    if args.phase=="pre":
        print("ARC4_MIDDLE_HEIGHT_PREFLIGHT "+json.dumps({"contract":c["id"],"resets":24},sort_keys=True),flush=True)
    else:
        result=inspect(c,args.result)
        args.result.with_suffix(".protocol.json").write_text(json.dumps(result,indent=2)+"\n")
        print("ARC4_MIDDLE_HEIGHT_VERIFIED "+json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":main()
