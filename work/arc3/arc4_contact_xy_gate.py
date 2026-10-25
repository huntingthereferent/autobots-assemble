"""Independent original SDK 64x64 frame gate: Level4 finite 2D upper contact.

Import finite source-domain factor list but never import experiment measurements.
Cup, side-strand and boundary predicates are derived independently using
existing source-independent original SDK NPZ observer.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np

from .native_sp80_stage4_contact_xy import FROZEN,PARENTS,UPPER,VERTICAL
from .native_sp80_multi_select import parse_plan
from .arc4_two_strand_composition_gate import compute,framehash

CONTRACT=Path("work/arc3/arc4_contact_xy_contract.json")
DEFAULT=Path("runtime/data/arc4/contact-xy/original-contact-xy.json")

def require(ok,reason):
    if not ok:raise ValueError("ORIGINAL_ARC4_CONTACT_XY_MATH_WALL: "+reason)

def geometry(frame):
    y,x=np.nonzero(frame==9)
    if len(x)==0:return None
    return [int(x.min()),int(y.min()),int(x.max()),int(y.max())]

def context():
    c=json.loads(CONTRACT.read_text(encoding="utf8"))
    require(c["schema_version"]==1 and
            c["parent_original_run_id"]==40165524676 and
            c["parent_root"]=="fa8fd32d3bfd2c8b3ff7765aec373512" and
            c["expected_genuine_sdk_resets"]==24 and
            c["source_code"]=="work/arc3/native_sp80_stage4_contact_xy.py",
            "frozen native source and parent evidence drift")
    f=c["frozen_factors"]
    require(f["lower_parents"]==[p[0] for p in PARENTS] and
            f["right_middle_fixed"]=="6@46,33 3 3" and
            f["top_last_vertical"]==[list(x) for x in VERTICAL] and
            f["top_left_actions"]==[list(x) for x in UPPER] and
            f["native_original_entry_witnesses"]==["A","B"],
            "finite action factors changed without renewed admission")
    require(len(FROZEN)==12 and len(set(n for n,w in FROZEN))==12,
            "finite case count changed")
    for name,program in FROZEN:
        actions=parse_plan(program)
        require(actions[-1][0]==5 and
                sum(a==5 for a,xy in actions)==1 and
                sum(a==6 for a,xy in actions)==4,
                "original SDK frozen action word illegal")
    require("levels_completed>=5" in c["official_progress"],
            "original SDK native advancement boundary missing")
    return c

def verify_result(contract,out):
    out=Path(out)
    require(out.is_file() and out.with_suffix(".npz").is_file(),
            "real original SDK source JSON/NPZ missing")
    record=json.loads(out.read_text(encoding="utf8"))
    require(record["kind"]=="ORIGINAL_ARC4_UPPER_CONTACT_XY_VERTICAL_BRACKET" and
            record["frozen_stage4_source_words"]==[list(r) for r in FROZEN] and
            record["original_sdk_native_resets"]==24 and
            record["original_level4_source_root_blake2b16"]==contract["parent_source_root"],
            "native source identity/protocol does not match frozen factors")
    cases={(r["case"],r["witness"]):r for r in record["original_native_cases"]}
    require(len(cases)==24 and set(cases)=={
        (name,witness) for name,_ in FROZEN for witness in ("A","B")},
        "actual independent original source A/B cases missing")
    checked={};official=0;status_hist=Counter();no_motion=[]
    with np.load(out.with_suffix(".npz"),allow_pickle=False) as arrays:
        for name,word in FROZEN:
            witness_results=[]
            for witness in ("A","B"):
                source=cases[(name,witness)]
                actions=parse_plan(word)
                ledger=source["original_sdk_stage4_action_ledger"]
                require(source["frozen_stage4_source_word"]==word and
                        source["original_sdk_executed_actions"]==len(ledger) and
                        len(ledger)>1 and len(ledger)<=len(actions),
                        "native original SDK action word or receipts changed")
                root=arrays[name+"_"+witness+"_entry3_34"][-1]
                require(root.shape==(64,64) and
                        framehash(root)==contract["parent_source_root"],
                        "true native SDK did not enter exact observed Level4")
                previous=root
                for index,((aid,xy),entry) in enumerate(zip(actions,ledger),1):
                    frames=arrays[name+"_"+witness+"_stage4_"+str(index)]
                    require(frames.ndim==3 and frames.shape[1:]==(64,64) and
                            frames.shape[0]==entry["original_sdk_frame_stack_count"],
                            "original SDK returned animation stack missing")
                    require(entry["genuine_original_action"]==aid and
                            entry["real_native_click_xy"]==
                            (list(xy) if xy is not None else None) and
                            entry["source_frame_before_blake2b16"]==framehash(previous) and
                            entry["source_frame_after_blake2b16"]==framehash(frames[-1]) and
                            aid in entry["original_legal_actions_before"],
                            "native original source action/frame/legal source receipt drift")
                    require(entry["original_sdk_level_before"]>=4 and
                            entry["original_sdk_level_after"]>=4,
                            "original Level4 SDK replay unexpectedly downgraded")
                    if xy is not None:
                        x,y=xy
                        require(entry["original_source_pixel_before_click"]==
                                int(previous[y,x]),
                                "actual SDK selected source pixel different")
                    previous=frames[-1]
                ended=ledger[-1]
                require(source["original_sdk_official_level"]==ended["original_sdk_level_after"]
                        and source["original_sdk_official_state"]==ended["original_sdk_state_after"]
                        and source["official_level5_or_WIN"]==
                           (source["original_sdk_official_level"]>=5
                             or source["original_sdk_official_state"]=="WIN"),
                        "original SDK native status not independently witnessed")
                official+=int(source["official_level5_or_WIN"])
                status_hist[str(source["original_sdk_official_level"])]+=1
                if not source["original_sdk_complete_source_word"]:
                    require(source["official_level5_or_WIN"] and
                            source["original_sdk_native_visual_measurements"] is None,
                            "unwitnessed early original SDK stop")
                    witness_results.append({"witness":witness,"early_official_progress":True,
                                            "official_level":source["original_sdk_official_level"]})
                    continue
                require(len(ledger)==len(actions) and ended["genuine_original_action"]==5,
                        "native original ACTION5 absent")
                pre=arrays[name+"_"+witness+"_stage4_"+str(len(ledger)-1)][-1]
                frames=arrays[name+"_"+witness+"_stage4_"+str(len(ledger))]
                measured=compute(root,pre,frames)
                obs=source["original_sdk_native_visual_measurements"]
                require(obs is not None,"source recorded native pour without visual frames")
                m=obs["original_source_measurements"]
                require(m["original_source_cup_first_full_frames"]==measured["cups_first"]
                        and m["original_source_cup_max_palette13_pixels"]==measured["cups_max"]
                        and m["native_first_simultaneously_full_four_cups"]==measured["first_four"]
                        and all((None if m["first_original_color6_at_3_upper_sites"][k] is None
                            else m["first_original_color6_at_3_upper_sites"][k]
                              ["native_original_frame"])==val
                            for k,val in measured["site_first"].items())
                        and all((None if m["native_first_source_border_changes"][k] is None
                            else m["native_first_source_border_changes"][k]
                              ["native_original_frame"])==val
                            for k,val in measured["border_first"].items()),
                        "source-independent frame/cup/strand/border math differs from native report")
                require(obs["P_leftmost_suppressed"]==measured["P_leftmost_absent"]
                        and obs["Q_rightmost_suppressed"]==measured["Q_rightmost_absent"]
                        and obs["P_and_Q"]==measured["P_and_Q"]
                        and obs["R_topmiddle_cup_full"]==(measured["cups_max"]["top_middle"]==45)
                        and obs["R_four_cups_simultaneously_full"]==
                            (measured["first_four"] is not None)
                        and obs["top_right_border_unchanged"]==
                            measured["no_top_right_border"]
                        and obs["source_original_prepour_hash"]==framehash(pre)
                        and obs["source_original_pour_last_hash"]==framehash(frames[-1]),
                        "observed finite source predicates falsified by actual SDK NPZ")
                prior_bbox=geometry(arrays[name+"_"+witness+"_stage4_"+str(len(ledger)-2)][-1]) \
                    if name.endswith(("UP1","DOWN1")) else geometry(pre)
                bbox=geometry(pre)
                require(source["original_source_selected_before_vertical"]==prior_bbox
                        and source["original_source_selected_before_pour"]==bbox,
                        "original selected-upper geometry was not witnessed")
                # Actual selected source bar 12x3 object, bounded 2D geometry.
                upper=name.split("_")[-2]
                vertical=name.split("_")[-1]
                expected_x=23 if upper=="U2" else 20
                expected_y={"HOLD":20,"UP1":17,"DOWN1":23}[vertical]
                require(bbox==[expected_x,expected_y,expected_x+11,expected_y+2],
                        "native selected upper 2D source contact geometry diverged")
                require(prior_bbox==[expected_x,20,expected_x+11,22],
                        "native source upper pre-vertical x-y baseline diverged")
                changed=prior_bbox!=bbox
                if name.endswith(("UP1","DOWN1")) and not changed:
                    no_motion.append((name,witness))
                witness_results.append({"witness":witness,
                    "official_level":source["original_sdk_official_level"],
                    "official_progress":source["official_level5_or_WIN"],
                    "P":measured["P_leftmost_absent"],
                    "Q":measured["Q_rightmost_absent"],
                    "P_and_Q":measured["P_and_Q"],
                    "topmiddle_max13":measured["cups_max"]["top_middle"],
                    "topmiddle_full":measured["cups_max"]["top_middle"]==45,
                    "four_cups_frame":measured["first_four"],
                    "top_right_border_change":[measured["border_first"][s] for s in ("top","right")],
                    "selected_before_vertical":prior_bbox,
                    "selected_before_pour":bbox,
                    "vertical_selected_geometry_changed":changed,
                })
            require({x["witness"] for x in witness_results}=={"A","B"} and
                    {k:v for k,v in witness_results[0].items() if k!="witness"}==
                    {k:v for k,v in witness_results[1].items() if k!="witness"},
                    "independent original native SDK A/B source mismatch")
            checked[name]=witness_results[0]
    require(official==record["official_sdk_level5_or_WIN_count"],
            "original SDK official advance count contradictory")
    baseline_walls=[]
    for parent,mid,l in PARENTS:
        for upper,expectP,expectQ,expectMiddle in (
            ("U2",False,True,45),("U3",False,True,0)):
            case=parent+"_"+upper+"_HOLD"
            measured=checked[case]
            if (measured.get("P"),measured.get("Q"),
                measured.get("topmiddle_max13"))!=(expectP,expectQ,expectMiddle):
                baseline_walls.append({
                    "case":case,
                    "native_observed":measured,
                    "expected_original_source_control":[expectP,expectQ,expectMiddle]})
    results=[]
    for parent,*_ in PARENTS:
        group={u+"_"+v:checked[parent+"_"+u+"_"+v]
               for u,_ in UPPER for v,_ in VERTICAL}
        results.append({
            "lower_parent":parent,
            "finite_original_upper_xy_cases":group,
            "original_contact_overlap_U2":group["U2_HOLD"],
            "original_disjoint_U3":group["U3_HOLD"],
            "U2_up1":group["U2_UP1"],
            "U2_down1":group["U2_DOWN1"],
            "U3_up1":group["U3_UP1"],
            "U3_down1":group["U3_DOWN1"],
        })
    disposition="REPLICATION_REQUIRED" if official else (
        "WALL_BASELINE_DRIFT" if baseline_walls else "PARTIAL")
    return {
        "kind":"ORIGINAL_SP80_LEVEL4_SOURCE_XY_CONTACT_WORKSTATION_RETURN",
        "source_contract":contract["id"],
        "native_original_sdk_resets":len(cases),
        "official_native_level5_or_WIN_count":official,
        "official_native_level_histogram":dict(status_hist),
        "state":disposition,
        "baseline_walls":baseline_walls,
        "blocked_vertical_geometry":sorted([list(x) for x in no_motion]),
        "source_predicate_results":results,
        "mathematical_scope":"Finite original SDK U2 right-edge34 versus U3 right-edge31 source overlap; actual native UP1/DOWN1 changes vertical y17/y23, no formal F3 A/B action map",
        "next_movement":contract["next_if_level5"] if official else contract["next_if_no_level5"],
        "walls":contract["walls"],
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("phase",choices=("pre","post"))
    parser.add_argument("--result",type=Path,default=DEFAULT)
    args=parser.parse_args()
    c=context()
    if args.phase=="pre":
        print("ARC4_CONTACT_XY_PREFLIGHT "+json.dumps({
            "contract":c["id"],"expected_genuine_sdk_resets":c["expected_genuine_sdk_resets"]
        },sort_keys=True),flush=True)
    else:
        verdict=verify_result(c,args.result)
        args.result.with_suffix(".protocol.json").write_text(json.dumps(verdict,indent=2)+"\n",encoding="utf8")
        print("ARC4_CONTACT_XY_GATE "+json.dumps(verdict,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
