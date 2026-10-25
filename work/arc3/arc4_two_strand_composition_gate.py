"""Independent original SDK NPZ/receipt gate for Level4 two-source composition.

The gate deliberately does not import the experiment's measurement function.
Recompute source predicates, cup masks, border contacts and SDK status from
saved original 64x64 source arrays and the genuine per-action ledger.
"""
from __future__ import annotations
import argparse,json
from hashlib import blake2b
from pathlib import Path
import numpy as np

from .native_sp80_stage4_two_strand_composition import FROZEN,PARENTS,RIGHT,UPPER
from .native_sp80_multi_select import parse_plan

MANIFEST=Path("work/arc3/arc4_two_strand_composition_contract.json")
DEFAULT=Path("runtime/data/arc4/two-strand/original-two-strand-native.json")
CUPS={"left_lateral":(5,35,10,43),"top_left":(17,5,25,10),
      "top_middle":(35,5,43,10),"top_right":(47,5,55,10)}
REGIONS={
    "leftmost_outside_cup":(slice(5,8),slice(11,14)),
    "upper_right_outside":(slice(5,8),slice(56,59)),
    "top_left_cup_other_side":(slice(5,8),slice(26,29)),
}
BORDERS={
    "left":(slice(2,62),slice(2,5)),
    "right":(slice(2,62),slice(59,62)),
    "top":(slice(2,5),slice(2,62)),
    "bottom":(slice(59,63),slice(2,62)),
}

def require(ok,message):
    if not ok:raise ValueError("ORIGINAL_ARC4_TWO_STRAND_SOURCE_WALL: "+message)
def framehash(frame):
    return blake2b(np.ascontiguousarray(frame).tobytes(),digest_size=16).hexdigest()

def context():
    c=json.loads(MANIFEST.read_text())
    require(c["schema_version"]==1 and c["original_sdk_resets"]==16
            and c["source_code"]=="work/arc3/native_sp80_stage4_two_strand_composition.py"
            and c["parent_root_blake2b16"]=="fa8fd32d3bfd2c8b3ff7765aec373512"
            and c["parent_original_runs"]==[39639320303,39636999616],
            "original source/parent evidence changed")
    require(c["frozen_factors"]["lower_clean_parents"]==[p[0] for p in PARENTS]
            and c["frozen_factors"]["right_middle_actions"]==[list(x) for x in RIGHT]
            and c["frozen_factors"]["upper_actions"]==[list(x) for x in UPPER]
            and c["frozen_factors"]["independent_entry_witnesses"]==["A","B"],
            "finite experimental action factors changed")
    require(len(FROZEN)==8 and len({name for name,_ in FROZEN})==8,
            "missing finite two-factor terms")
    for case,word in FROZEN:
        actions=parse_plan(word)
        require(sum(a==5 for a,_ in actions)==1 and actions[-1][0]==5
                and [a for a,_ in actions].count(6)==4,
                "original SDK click/pour action word drift")
    require("levels_completed >=5" in c["success_oracle"],
            "official original win predicate lost")
    return c

def compute(root,pre,frames):
    require(root.shape==(64,64) and pre.shape==(64,64)
            and frames.ndim==3 and frames.shape[1:]==(64,64),
            "original 64x64 SDK frames missing")
    mask={}
    for name,(x0,y0,x1,y1) in CUPS.items():
        sub=root[y0:y1+1,x0:x1+1]==11
        require(int(sub.sum())==45,"original source cup geometry changed")
        mask[name]=sub
    first={name:None for name in CUPS}
    max13={name:0 for name in CUPS}
    sites={name:None for name in REGIONS}
    edges={name:None for name in BORDERS}
    four=None
    for i,frame in enumerate(frames):
        new6=(pre!=6)&(frame==6)
        for name,(ys,xs) in REGIONS.items():
            if sites[name] is None and new6[ys,xs].any():
                sites[name]=i
        full=0
        for name,(x0,y0,x1,y1) in CUPS.items():
            filled=int(np.count_nonzero(mask[name]&
                      (frame[y0:y1+1,x0:x1+1]==13)))
            max13[name]=max(max13[name],filled)
            if filled==45:
                full+=1
                if first[name] is None:first[name]=i
        if four is None and full==4:four=i
        for name,(ys,xs) in BORDERS.items():
            if edges[name] is None and np.any(pre[ys,xs]!=frame[ys,xs]):
                edges[name]=i
    return {
        "cups_first":first,"cups_max":max13,"first_four":four,
        "site_first":sites,"border_first":edges,
        "P_leftmost_absent":sites["leftmost_outside_cup"] is None,
        "Q_rightmost_absent":sites["upper_right_outside"] is None,
        "P_and_Q":sites["leftmost_outside_cup"] is None and
                  sites["upper_right_outside"] is None,
        "no_top_right_border":edges["top"] is None and edges["right"] is None,
    }

def verify_result(contract,result):
    result=Path(result)
    require(result.is_file() and result.with_suffix(".npz").is_file(),
            "missing real native JSON/NPZ")
    m=json.loads(result.read_text())
    require(m["kind"]=="ORIGINAL_SP80_STAGE4_TWO_SOURCE_STRAND_COMPOSITION"
            and m["frozen_level4_programs"]==[list(x) for x in FROZEN]
            and m["native_original_source_resets"]==16,
            "original source experiment frozen program drift")
    records={(x["case"],x["witness"]):x for x in m["original_native_cases"]}
    require(len(records)==16 and set(records)=={
        (name,witness) for name,_ in FROZEN for witness in ("A","B")},
        "source trial A/B witness coverage changed")
    controls={}
    advances=0
    with np.load(result.with_suffix(".npz"),allow_pickle=False) as arrays:
        for name,program in FROZEN:
            replay=[]
            for witness in ("A","B"):
                record=records[(name,witness)]
                require(record["frozen_original_source_word"]==program,
                        "original SDK action word changed")
                actions=parse_plan(program)
                ledger=record["genuine_original_sdk_stage4_action_ledger"]
                require(record["actual_executed_stage4_actions"]==len(ledger)
                        and 1<=len(ledger)<=len(actions),
                        "original SDK stage4 receipts missing")
                root=arrays[name+"_"+witness+"_entry3_34"][-1]
                require(framehash(root)==contract["parent_root_blake2b16"],
                        "true original SDK level4 root hash mismatch")
                previous=root
                for index,(aid,xy) in enumerate(actions[:len(ledger)],1):
                    receipt=ledger[index-1]
                    key=name+"_"+witness+"_stage4_"+str(index)
                    frames=arrays[key]
                    require(frames.ndim==3 and frames.shape[1:]==(64,64),
                            "original stage4 action return frame stack absent")
                    require(receipt["genuine_original_action"]==aid and
                            receipt["real_native_click_xy"]==
                             (list(xy) if xy is not None else None)
                            and receipt["source_frame_before_blake2b16"]==framehash(previous)
                            and receipt["source_frame_after_blake2b16"]==framehash(frames[-1])
                            and receipt["original_sdk_frame_stack_count"]==len(frames),
                            "native source per-action SHA / action / frame ledger drift")
                    require(receipt["original_sdk_level_before"]>=4
                            and receipt["original_sdk_level_after"]>=4,
                            "original Level4 source unexpectedly reverted")
                    if xy is not None:
                        x,y=xy
                        require(receipt["original_source_pixel_before_click"]==int(previous[y,x]),
                                "original SDK native selection pixel mismatch")
                    previous=frames[-1]
                last=ledger[-1]
                require(record["official_original_sdk_level"]==last["original_sdk_level_after"]
                        and record["official_original_sdk_state"]==last["original_sdk_state_after"]
                        and record["official_level5_or_WIN"]==
                            (record["official_original_sdk_level"]>=5
                             or record["official_original_sdk_state"]=="WIN"),
                        "SDK official outcome contradicts original source ledger")
                advances+=int(record["official_level5_or_WIN"])
                if not record["native_complete_frozen_program"]:
                    require(record["official_level5_or_WIN"] and
                            record["original_source_observation"] is None,
                            "unjustified truncated source program")
                    replay.append({"witness":witness,"advance_before_pour":True})
                    continue
                require(last["genuine_original_action"]==5,
                        "native source ACTION5 missing")
                pre=arrays[name+"_"+witness+"_stage4_"+str(len(ledger)-1)][-1]
                pour=arrays[name+"_"+witness+"_stage4_"+str(len(ledger))]
                x=compute(root,pre,pour)
                obs=record["original_source_observation"]
                require(obs is not None,"native source observation absent")
                o=obs["measured_original_native"]
                require(o["original_source_cup_first_full_frames"]==x["cups_first"]
                        and o["original_source_cup_max_palette13_pixels"]==x["cups_max"]
                        and o["native_first_simultaneously_full_four_cups"]==x["first_four"]
                        and all((None if o["first_original_color6_at_3_upper_sites"][k] is None
                                  else o["first_original_color6_at_3_upper_sites"][k]
                                         ["native_original_frame"])==v
                                for k,v in x["site_first"].items())
                        and all((None if o["native_first_source_border_changes"][k] is None
                                  else o["native_first_source_border_changes"][k]
                                         ["native_original_frame"])==v
                                for k,v in x["border_first"].items()),
                        "independent source NPZ measurement differs from native JSON")
                require(obs["visual_four_cups_simultaneously_full"]==(x["first_four"] is not None)
                        and obs["upper_left_source_strand_absent"]==x["P_leftmost_absent"]
                        and obs["upper_right_source_strand_absent"]==x["Q_rightmost_absent"]
                        and obs["both_tested_upstream_strands_absent"]==x["P_and_Q"]
                        and obs["no_measured_top_or_right_border_change"]==x["no_top_right_border"],
                        "native source composition predicate was not reproduced")
                replay.append({"witness":witness,**x,
                               "official_level":record["official_original_sdk_level"],
                               "official_progress":record["official_level5_or_WIN"]})
            require(replay[0]["witness"]=="A" and replay[1]["witness"]=="B"
                    and {k:v for k,v in replay[0].items() if k!="witness"}==
                        {k:v for k,v in replay[1].items() if k!="witness"},
                    "independent original A/B native source outcomes differ")
            controls[name]=replay[0]
    require(advances==m["official_original_level5_or_WIN_count"],
            "official native stage5 count doesn't match observed events")
    historic_control_mismatches=[]
    for name,record in controls.items():
        if record.get("advance_before_pour"):
            continue
        bits=name.split("_")
        # Factor arms already observed separately in original source antecedents.
        right=bits[-2];upper=bits[-1]
        if (right,upper)==("R1","U1"):
            expect=(False,False,True)
        elif (right,upper)==("R2","U1"):
            expect=(False,True,True)
        elif (right,upper)==("R1","U6"):
            expect=(True,False,True)
        else:
            continue
        observed=(record["P_leftmost_absent"],record["Q_rightmost_absent"],
                  record["first_four"] is not None)
        if observed!=expect:
            historic_control_mismatches.append({
                "case":name,"historic_control_expected":expect,
                "actual_genuine_original_sdk_observation":observed})
    pair_results=[]
    for parent,*_ in PARENTS:
        term={f:controls[parent+"_"+f] for f in
              ("R1_U1","R2_U1","R1_U6","R2_U6")}
        joint=term["R2_U6"]
        pair_results.append({
            "native_clean_parent":parent,
            "frozen_two_factor_conditions":term,
            "joint_original_P_and_Q":joint.get("P_and_Q"),
            "joint_four_cups_simultaneous":joint.get("first_four") is not None,
            "joint_tested_top_right_edge_cleared":joint.get("no_top_right_border"),
            "joint_official_sdk_level":joint["official_level"],
        })
    status=("REPLICATION_REQUIRED" if advances else
            "WALL_CONTROL_DRIFT" if historic_control_mismatches else "PARTIAL")
    return {
        "kind":"ORIGINAL_ARC4_TWO_STRAND_NATIVE_SOURCE_WORKSTATION_RETURN",
        "source_contract":contract["id"],
        "native_original_resets":len(records),
        "official_native_sdk_level5_or_WIN":advances,
        "state":status,
        "historic_control_mismatches":historic_control_mismatches,
        "source_composition_by_clean_parent":pair_results,
        "math_admission":"P and Q are source-observed finite predicates only; no F3 mathematical generator map",
        "next_movement":contract["next_progress"] if advances else contract["next_no_progress"],
        "walls":contract["walls"],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("phase",choices=("pre","post"))
    p.add_argument("--result",type=Path,default=DEFAULT)
    a=p.parse_args()
    c=context()
    if a.phase=="pre":
        print("ARC4_TWO_STRAND_NATIVE_PREFLIGHT "+json.dumps({"contract":c["id"],"resets":16}))
    else:
        verdict=verify_result(c,a.result)
        a.result.with_suffix(".protocol.json").write_text(json.dumps(verdict,indent=2)+"\n")
        print("ARC4_TWO_STRAND_NATIVE_GATE "+json.dumps(verdict,sort_keys=True))
if __name__=="__main__":main()
