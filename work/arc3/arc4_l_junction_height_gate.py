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
from .native_sp80_stage4_l_junction_height import FROZEN,PARENTS,COUPLING,L_HEIGHT,RIGHT_FIXED,UPPER_FIXED
from .native_sp80_multi_select import parse_plan
from .arc4_two_strand_composition_gate import compute,framehash

CONTRACT=Path("work/arc3/arc4_l_junction_height_contract.json")
DEFAULT=Path("runtime/data/arc4/l-junction/original-l-junction.json")
def require(ok,reason):
    if not ok:raise ValueError("ORIGINAL_ARC4_MIDDLE_L_MATH_WALL: "+reason)
def bbox(frame):
    y,x=np.nonzero(frame==9)
    require(len(x)==27,"Original selected L has not 27 genuine source pixels")
    return [int(x.min()),int(y.min()),int(x.max()),int(y.max())]
def context():
    c=json.loads(CONTRACT.read_text())
    require(c["schema_version"]==1 and c["original_parent_run"]==40172934437
            and c["original_parent_artifact"]==12590867076
            and c["original_level4_root"]=="fa8fd32d3bfd2c8b3ff7765aec373512"
            and c["source_code"]=="work/arc3/native_sp80_stage4_l_junction_height.py"
            and c["expected_genuine_sdk_resets"]==24,
            "frozen original Level4 source provenance drift")
    f=c["factors"]
    require(f["lower_parents"]==[[n,x,y] for n,base,l,x,y in PARENTS]
            and f["coupling"]==[list(v) for v in COUPLING]
            and f["lower_L_vertical"]==[list(v) for v in L_HEIGHT]
            and f["right_fixed"]==RIGHT_FIXED
            and f["upper_fixed"]==UPPER_FIXED
            and f["native_entry_witnesses"]==["A","B"]
            and len(FROZEN)==12 and len({n for n,w in FROZEN})==12,
            "native original finite source matrix changed")
    for name,word in FROZEN:
        cmds=parse_plan(word)
        require(cmds[-1][0]==5 and sum(a==5 for a,xy in cmds)==1
                and sum(a==6 for a,xy in cmds)==4,
                "original SDK click+pour alphabet drift")
    require("levels_completed>=5" in c["native_progress"],
            "native official Level5 oracle missing")
    return c
def inspect(c,path):
    path=Path(path)
    require(path.is_file() and path.with_suffix(".npz").is_file(),
            "missing original SDK native source arrays")
    j=json.loads(path.read_text())
    require(j["kind"]=="ORIGINAL_SP80_LEVEL4_NATIVE_L_JUNCTION_VERTICAL"
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
            mid_word,L_extra=next((mid,l) for n,mid,l in COUPLING if n==mname)
            vertical_word,dy=next((word,dy) for n,word,dy in L_HEIGHT if n==lname)
            prefix=" ".join((RIGHT_FIXED,
                "6@24,33 "+base+(" "+mid_word if mid_word else ""),
                "6@34,42 "+L+(" "+L_extra if L_extra else "")+
                                   (" "+vertical_word if vertical_word else "")))
            l_idx=len(parse_plan(prefix))
            actual_x=base_x+(3 if mname=="COMPENSATED" else 0)
            expected_L=[actual_x,35+dy,actual_x+5,40+dy]
            baseline_L=[actual_x,35,actual_x+5,40]
            witness_results=[]
            for witness in ("A","B"):
                row=cases[(name,witness)]
                cmds=parse_plan(word);led=row["actual_native_receipts"]
                require(row["frozen_original_stage4_word"]==word
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
                selected=npz[f"{name}_{witness}_stage4_{l_idx}"][-1]
                actualbox=bbox(selected)
                require(row["actual_selected_L_bbox"]==actualbox,
                        "genuine original selected lower L does not equal saved receipt")
                moved=(actualbox==expected_L and dy!=0)
                blocked=(dy!=0 and actualbox==baseline_L)
                require(actualbox==expected_L or blocked,
                        "native original selected L not at intended or blocked source bbox")
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
                junction={}
                for y in (44,47):
                    for x in (11,14,17,20,23,26):
                        key=f"y{y}_x{x}_{x+2}"
                        junction[key]=next(
                            (i for i,frame in enumerate(pour)
                             if np.any((pre[y:y+3,x:x+3]!=6)&
                                       (frame[y:y+3,x:x+3]==6))),None)
                require(junction==stored["new_palette6_junction_arrival_tiles"],
                        "original SDK source branch tile first-arrival timing does not match NPZ")
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
                    "original_L_bbox":actualbox,"L_vertical_genuinely_moved":moved,
                    "L_vertical_blocked":blocked,
                    "upper_left_offcup_first":regions,
                    "original_source_junction_first":junction,
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
            name=p+"_"+coupling+"_HOLD"
            r=obs[name]
            if (r.get("all_original_cup_max13",{}).get("left_lateral")!=45
                or r.get("all_original_cup_max13",{}).get("top_middle")!=45
                or r.get("all_four_together_frame") is None
                or r.get("upper_left_offcup_first",{}).get(source_band) is None
                or r.get("official_level")!=4):
                control_drift.append({"case":name,"observed":r})
    relations=[]
    for p,*_ in PARENTS:
        for coupling,_,_ in COUPLING:
            relations.append({
                "source_lower_parent":p,
                "middle_L_coupling":coupling,
                "source_L_up1":obs[p+"_"+coupling+"_UP1"],
                "source_L_hold":obs[p+"_"+coupling+"_HOLD"],
                "source_L_down1":obs[p+"_"+coupling+"_DOWN1"],
            })
    return {
        "kind":"ORIGINAL_SP80_LEVEL4_NATIVE_L_JUNCTION_VERIFIED",
        "contract":c["id"],"real_sdk_resets":len(cases),
        "official_sdk_levels":dict(levels),
        "official_sdk_level5_or_WIN":progress,
        "state":"REPLICATION_REQUIRED" if progress else (
          "WALL_CONTROL_DRIFT" if control_drift else "PARTIAL"),
        "control_drift":control_drift,
        "blocked_native_L_vertical_actions":block,
        "finite_native_L_junction_relations":relations,
        "math_scope":"finite genuine SDK source first-arrival lower x20 to x14 left fork tested under L vertical junction displacement, independent parent and A/B paths; no decoded physics or F3 map",
        "next_movement":c["next_if_progress"] if progress else c["next_if_no_progress"],
        "walls":c["walls"],
    }
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("phase",choices=("pre","post"))
    ap.add_argument("--result",type=Path,default=DEFAULT)
    args=ap.parse_args()
    c=context()
    if args.phase=="pre":
        print("ARC4_L_JUNCTION_PREFLIGHT "+json.dumps({"contract":c["id"],"resets":24},sort_keys=True),flush=True)
    else:
        result=inspect(c,args.result)
        args.result.with_suffix(".protocol.json").write_text(json.dumps(result,indent=2)+"\n")
        print("ARC4_L_JUNCTION_VERIFIED "+json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":main()
