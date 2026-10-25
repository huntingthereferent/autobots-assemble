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
from .native_sp80_stage4_middle_l_compensation import FROZEN,PARENTS,MIDDLE,L_OFFSET,RIGHT_FIXED,UPPER_FIXED
from .native_sp80_multi_select import parse_plan
from .arc4_two_strand_composition_gate import compute,framehash

CONTRACT=Path("work/arc3/arc4_middle_l_compensation_contract.json")
DEFAULT=Path("runtime/data/arc4/middle-l/original-middle-l.json")
def require(ok,reason):
    if not ok:raise ValueError("ORIGINAL_ARC4_MIDDLE_L_MATH_WALL: "+reason)
def bbox(frame):
    y,x=np.nonzero(frame==9)
    require(len(x)==27,"Original selected L has not 27 genuine source pixels")
    return [int(x.min()),int(y.min()),int(x.max()),int(y.max())]
def context():
    c=json.loads(CONTRACT.read_text())
    require(c["schema_version"]==1 and c["parent_source_run"]==40170150937
            and c["parent_source_artifact"]==12589694180
            and c["original_native_level4_root"]=="fa8fd32d3bfd2c8b3ff7765aec373512"
            and c["source_code"]=="work/arc3/native_sp80_stage4_middle_l_compensation.py"
            and c["original_native_resets"]==24,
            "frozen original Level4 source provenance drift")
    f=c["factors"]
    require(f["lower_parents"]==[[n,x,y] for n,base,l,x,y in PARENTS]
            and f["middle_move"]==[list(v) for v in MIDDLE]
            and f["L_move"]==[list(v) for v in L_OFFSET]
            and f["right_middle_fixed"]==RIGHT_FIXED
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
    require(j["kind"]=="ORIGINAL_SP80_LEVEL4_NATIVE_MIDDLE_LOWER_L_RELATION"
            and j["true_original_level4_root"]==c["original_native_level4_root"]
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
            middle_word=dict(MIDDLE)[mname]
            l_word=next(a for n,a,dx in L_OFFSET if n==lname)
            dx=next(v for n,a,v in L_OFFSET if n==lname)
            lprefix=" ".join((RIGHT_FIXED,
               "6@24,33 "+base+(" "+middle_word if middle_word else ""),
               "6@34,42 "+L+(" "+l_word if l_word else "")))
            l_idx=len(parse_plan(lprefix))
            original_x=base_x
            attempted_x=original_x+dx
            witness_results=[]
            for witness in ("A","B"):
                row=cases[(name,witness)]
                cmds=parse_plan(word);led=row["actual_native_receipts"]
                require(row["frozen_original_stage4_word"]==word
                        and row["actual_source_L_action_index"]==l_idx
                        and l_idx<=len(led)<=len(cmds),
                        "source original L action index or receipt count changed")
                root=npz[f"{name}_{witness}_entry3_34"][-1]
                require(root.shape==(64,64) and framehash(root)==c["original_native_level4_root"],
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
                attempted=[attempted_x,35,attempted_x+5,40]
                baseline=[original_x,35,original_x+5,40]
                # Legal SDK action can be blocked by an obstacle; mark it explicitly.
                moved=(actualbox==attempted and dx!=0)
                blocked=(dx!=0 and actualbox==baseline)
                require(actualbox==attempted or blocked,
                        "original L bar moved to unanticipated source geometry; fail closed")
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
                    "original_L_bbox":actualbox,"L_actually_moved":moved,
                    "L_native_movement_blocked":blocked,
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
        for m,expected_lateral in (("HOLD",45),("RIGHT1",0)):
            name=p+"_"+m+"_HOLD"
            r=obs[name]
            if (r.get("all_original_cup_max13",{}).get("left_lateral")!=expected_lateral or
                r.get("all_original_cup_max13",{}).get("top_middle")!=45 or
                r.get("official_level")!=4):
                control_drift.append({"source_case":name,"observed":r})
    relations=[]
    for p,*_ in PARENTS:
        for m,_ in MIDDLE:
            relations.append({
                "clean_native_parent":p,"middle_state":m,
                "L_minus1":obs[p+"_"+m+"_LEFT1"],
                "L_hold":obs[p+"_"+m+"_HOLD"],
                "L_plus1":obs[p+"_"+m+"_RIGHT1"],
            })
    return {
        "kind":"ORIGINAL_SP80_LEVEL4_NATIVE_MIDDLE_LOWER_L_VERIFIED",
        "contract":c["id"],"real_sdk_resets":len(cases),
        "official_sdk_levels":dict(levels),
        "official_sdk_level5_or_WIN":progress,
        "state":"REPLICATION_REQUIRED" if progress else (
          "WALL_CONTROL_DRIFT" if control_drift else "PARTIAL"),
        "control_drift":control_drift,
        "blocked_native_L_actions":block,
        "finite_native_relational_results":relations,
        "math_scope":"finite observed original source L-middle adjacency and lateral cup response; no private physics, formal F3 A/B map, or visual-success promotion",
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
        print("ARC4_MIDDLE_L_PREFLIGHT "+json.dumps({"contract":c["id"],"resets":24},sort_keys=True),flush=True)
    else:
        result=inspect(c,args.result)
        args.result.with_suffix(".protocol.json").write_text(json.dumps(result,indent=2)+"\n")
        print("ARC4_MIDDLE_L_VERIFIED "+json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":main()
