"""Independent original SDK Level4 finite observed upper source-contact bracket gate.

Never reuses the experiment's measurement routine. Recomputes full original
NPZ return receipts, 64x64 source hashes, cup/strand/topology and SDK status.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage4_upper_contact_bracket import FROZEN,PARENTS,RIGHT,UPPER
from .native_sp80_multi_select import parse_plan
from .arc4_two_strand_composition_gate import compute,framehash

CONTRACT=Path("work/arc3/arc4_upper_contact_contract.json")
DEFAULT=Path("runtime/data/arc4/contact/original-upper-contact.json")
def require(ok,why):
    if not ok:raise ValueError("ORIGINAL_ARC4_CONTACT_SOURCE_WALL: "+why)
def selected(frame):
    y,x=np.nonzero(frame==9)
    return [int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None
def context():
    c=json.loads(CONTRACT.read_text(encoding="utf8"))
    require(c["schema_version"]==1 and
            c["parent_native_runs"]==[40164869118,40154160743] and
            c["parent_native_artifacts"]==[12587806520,12583637554] and
            c["expected_original_sdk_resets"]==32 and
            c["frozen_level4_root"]=="fa8fd32d3bfd2c8b3ff7765aec373512" and
            c["source_code"]=="work/arc3/native_sp80_stage4_upper_contact_bracket.py",
            "parent actual SDK evidence or root changed")
    f=c["factors"]
    require(f["lower_parents"]==[p[0] for p in PARENTS] and
            f["right_middle_actions"]==[list(x) for x in RIGHT] and
            f["upper_actions"]==[list(x) for x in UPPER] and
            f["original_sdk_entry_witnesses"]==["A","B"] and
            len(FROZEN)==16 and len({n for n,word in FROZEN})==12,
            "finite source factors drift")
    for case,word in FROZEN:
        commands=parse_plan(word)
        require(commands[-1][0]==5 and
                sum(a==6 for a,xy in commands)==4 and
                sum(a==5 for a,xy in commands)==1,
                "native original source selection/action word changed")
    require("levels_completed>=5" in c["official_progress"],
            "original SDK success oracle missing")
    return c
def verify_result(c,path):
    path=Path(path)
    require(path.is_file() and path.with_suffix(".npz").is_file(),
            "native original SDK JSON/NPZ absent")
    source=json.loads(path.read_text())
    require(source["kind"]=="ORIGINAL_ARC4_UPPER_RIGHT_EDGE_CONTACT_BRACKET" and
            source["genuine_original_sdk_level4_root"]==c["frozen_level4_root"] and
            source["frozen_cases"]==[list(x) for x in FROZEN] and
            source["original_sdk_resets"]==32,
            "frozen native source experiment changed")
    rows={(r["case"],r["witness"]):r for r in source["native_cases"]}
    require(len(rows)==32 and set(rows)=={
        (name,witness) for name,_ in FROZEN for witness in ("A","B")},
        "native A/B original game reset evidence missing")
    outcomes={};advances=0;levels=Counter()
    with np.load(path.with_suffix(".npz"),allow_pickle=False) as arrays:
        for name,word in FROZEN:
            reps=[]
            for witness in ("A","B"):
                native=rows[(name,witness)]
                cmds=parse_plan(word);receipts=native["actual_sdk_stage4_receipts"]
                require(native["source_word"]==word and
                        native["executed_native_stage4_actions"]==len(receipts) and
                        1<=len(receipts)<=len(cmds),
                        "original native action record mismatched source")
                root=arrays[name+"_"+witness+"_entry3_34"][-1]
                require(root.shape==(64,64) and
                        framehash(root)==c["frozen_level4_root"],
                        "original SDK level4 root source differs")
                previous=root
                for i,((aid,xy),receipt) in enumerate(zip(cmds,receipts),1):
                    returned=arrays[name+"_"+witness+"_stage4_"+str(i)]
                    require(returned.ndim==3 and returned.shape[1:]==(64,64) and
                            len(returned)==receipt["original_sdk_frame_stack_count"] and
                            receipt["genuine_original_action"]==aid and
                            receipt["real_native_click_xy"]==
                              (list(xy) if xy is not None else None) and
                            aid in receipt["original_legal_actions_before"] and
                            receipt["original_sdk_level_before"]>=4 and
                            receipt["source_frame_before_blake2b16"]==framehash(previous) and
                            receipt["source_frame_after_blake2b16"]==framehash(returned[-1]),
                            "actual original SDK source action/click/before-after hash drift")
                    if xy is not None:
                        x,y=xy
                        require(receipt["original_source_pixel_before_click"]==int(previous[y,x]),
                                "original SDK true clicked source pixel changed")
                    previous=returned[-1]
                final=receipts[-1]
                require(native["official_native_level"]==final["original_sdk_level_after"] and
                        native["official_native_state"]==final["original_sdk_state_after"] and
                        native["official_level5_or_WIN"]==
                           (native["official_native_level"]>=5 or native["official_native_state"]=="WIN"),
                        "official original SDK level/state contradicted by action receipts")
                advances+=int(native["official_level5_or_WIN"])
                levels[str(native["official_native_level"])]+=1
                if not native["finished_frozen_word"]:
                    require(native["official_level5_or_WIN"] and
                            native["original_sdk_source_measures"] is None,
                            "incomplete source word without true original SDK advance")
                    reps.append({"witness":witness,"early_progress":True,
                                 "level":native["official_native_level"]})
                    continue
                require(len(receipts)==len(cmds) and final["genuine_original_action"]==5,
                        "last genuine SDK pour action absent")
                pre=arrays[name+"_"+witness+"_stage4_"+str(len(cmds)-1)][-1]
                pour=arrays[name+"_"+witness+"_stage4_"+str(len(cmds))]
                m=compute(root,pre,pour)
                obs=native["original_sdk_source_measures"]
                require(obs is not None,"original source measurement absent")
                own=obs["original_sdk_pixel_observations"]
                require(own["original_source_cup_first_full_frames"]==m["cups_first"] and
                        own["original_source_cup_max_palette13_pixels"]==m["cups_max"] and
                        own["native_first_simultaneously_full_four_cups"]==m["first_four"] and
                        all((None if own["first_original_color6_at_3_upper_sites"][site] is None
                                  else own["first_original_color6_at_3_upper_sites"][site]
                                            ["native_original_frame"])==first
                                for site,first in m["site_first"].items()) and
                        all((None if own["native_first_source_border_changes"][edge] is None
                                  else own["native_first_source_border_changes"][edge]
                                            ["native_original_frame"])==first
                                for edge,first in m["border_first"].items()),
                        "independent original frame remeasurement contradicts source observations")
                require(obs["P_no_leftmost_strand"]==m["P_leftmost_absent"] and
                        obs["Q_no_rightmost_strand"]==m["Q_rightmost_absent"] and
                        obs["P_and_Q"]==m["P_and_Q"] and
                        obs["topmiddle_max_palette13"]==m["cups_max"]["top_middle"] and
                        obs["topmiddle_full"]==(m["cups_max"]["top_middle"]==45) and
                        obs["simultaneous_four_cups"]==(m["first_four"] is not None) and
                        obs["no_top_right_border_change"]==m["no_top_right_border"] and
                        obs["original_prepour_sha"]==framehash(pre) and
                        obs["original_last_frame_sha"]==framehash(pour[-1]),
                        "native measured P/Q/R/F not supported by actual original source frames")
                col={"U1":26,"U2":23,"U3":20,"U6":11}[name.split("_")[-1]]
                expected=[col,20,col+11,22]
                if name.endswith("_U2"):
                    require(expected[2]==34 and len({32,33,34}.intersection(range(expected[0],expected[2]+1)))==3,
                            "U2 selected original upper bbox lost exact source x32..34 overlap")
                if name.endswith("_U3"):
                    require(expected[2]==31 and not {32,33,34}.intersection(range(expected[0],expected[2]+1)),
                            "U3 original upper edge no longer disjoint from x32..34 source")
                require(native["selected_upper_original_bbox"]==selected(pre)==expected,
                        "upper selected object moved somewhere other than original frozen 3px interval")
                reps.append({"witness":witness,"official_level":native["official_native_level"],
                             "official_progress":native["official_level5_or_WIN"],
                             "upper_bbox":selected(pre),
                             "P":m["P_leftmost_absent"],"Q":m["Q_rightmost_absent"],
                             "topmiddle_max13":m["cups_max"]["top_middle"],
                             "four_full_frame":m["first_four"],
                             "all_cup_max13":m["cups_max"],
                             "border_times":m["border_first"],
                             "source_prepour_hash":framehash(pre)})
            require(len(reps)==2 and
                    [x["witness"] for x in reps]==["A","B"] and
                    {k:v for k,v in reps[0].items() if k!="witness"}==
                    {k:v for k,v in reps[1].items() if k!="witness"},
                    "original independent SDK A/B source trial differs")
            outcomes[name]=reps[0]
    require(advances==source["actual_official_level5_or_WIN_count"],
            "actual official original SDK Level5/WIN ledger inconsistent")
    baseline_errors=[]
    for parent,*_ in PARENTS:
        for right,P,Q,top in (("R1",True,False,45),("R2",True,True,0)):
            name=parent+"_"+right+"_U6"
            r=outcomes[name]
            if (r.get("P"),r.get("Q"),r.get("topmiddle_max13"))!=(P,Q,top):
                baseline_errors.append({"original_source_case":name,
                        "expected_original_source_control":[P,Q,top],"actual":r})
    # Source-attested U1 baselines preserve topmiddle 45/45 in both right contexts.
    # Keep failure explicit if the previous native original control no longer holds.
    for parent,*_ in PARENTS:
        for right,expectP,expectQ,expectTop in (("R1",False,False,45),
                                                 ("R2",False,True,45)):
            name=parent+"_"+right+"_U1"
            obs=outcomes[name]
            if (obs.get("P"),obs.get("Q"),obs.get("topmiddle_max13"))!=(expectP,expectQ,expectTop):
                baseline_errors.append({"original_source_case":name,
                    "expected_original_source_control":[expectP,expectQ,expectTop],"actual":obs})
    pairs=[]
    for parent,*_ in PARENTS:
        for un,_ in UPPER:
            r1=outcomes[parent+"_R1_"+un];r2=outcomes[parent+"_R2_"+un]
            pairs.append({"clean_original_parent":parent,"upper_bar":un,
                          "R1_source_control":r1,"R2_source_transfer":r2,
                          "R2_joint_P_and_Q":r2.get("P") and r2.get("Q"),
                          "R2_topmiddle_restored":r2.get("topmiddle_max13")==45,
                          "R2_four_cups_simultaneous":r2.get("four_full_frame") is not None})
    return {
      "kind":"ORIGINAL_ARC4_UPPER_SOURCE_CONTACT_NATIVE_EVIDENCE",
      "source_contract":c["id"],"native_original_sdk_resets":len(rows),
      "official_native_level5_or_WIN_count":advances,
      "official_native_levels":dict(levels),
      "state":"REPLICATION_REQUIRED" if advances else (
                "WALL_CONTROL_DRIFT" if baseline_errors else "PARTIAL"),
      "historic_original_sdk_control_drift":baseline_errors,
      "conditional_source_contact_bracket":pairs,
      "math_scope":"finite source-observation relationship from actual original SDK; no formal F3 action map",
      "next_movement":c["next_progress"] if advances else c["next_no_progress"],
      "walls":c["walls"]
    }
def main():
    p=argparse.ArgumentParser();p.add_argument("phase",choices=("pre","post"))
    p.add_argument("--result",type=Path,default=DEFAULT)
    a=p.parse_args();c=context()
    if a.phase=="pre":
        print("ARC4_CONTACT_SOURCE_PREFLIGHT "+json.dumps({
            "contract":c["id"],"original_resets":c["expected_original_sdk_resets"]},sort_keys=True))
    else:
        m=verify_result(c,a.result)
        a.result.with_suffix(".protocol.json").write_text(json.dumps(m,indent=2)+"\n")
        print("ARC4_CONTACT_NATIVE_VERIFIED "+json.dumps(m,sort_keys=True),flush=True)
if __name__=="__main__":main()
