"""Independent finite original-SDK Level4 action-order square verifier.

Checks full genuine source frames, original game action/legality/click pixels,
source-derived cup/edge/strand observations and exact order pair. Uses the
source audit's independent metric implementation, not the experiment's.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np

from .native_sp80_stage4_operator_order import FROZEN,PARENTS,RIGHT,UPPER,ORDERS
from .native_sp80_multi_select import parse_plan
from .arc4_two_strand_composition_gate import compute,framehash

CONTRACT=Path("work/arc3/arc4_operator_order_contract.json")
DEFAULT=Path("runtime/data/arc4/order/original-order-native.json")

def require(ok,why):
    if not ok: raise ValueError("ORIGINAL_ARC4_ORDER_MATH_WALL: "+why)

def bbox(frame):
    ys,xs=np.nonzero(frame==9)
    return [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None

def difference(a,b):
    changed=np.argwhere(a!=b)
    if not len(changed):return None
    return {"first_coordinate":[int(v) for v in changed[0]],
            "pixels_changed":int(len(changed)),
            "first_values":[int(a[tuple(changed[0])]),int(b[tuple(changed[0])])]}

def context():
    c=json.loads(CONTRACT.read_text())
    require(c["schema_version"]==1 and
            c["antecedent_native_run"]==40158241960 and
            c["parent_root_blake2b16"]=="fa8fd32d3bfd2c8b3ff7765aec373512" and
            c["expected_original_sdk_resets"]==32 and
            c["source_code"]=="work/arc3/native_sp80_stage4_operator_order.py",
            "original source archive or Level4 wall drift")
    factors=c["factors"]
    require(factors["clean_lower_parents"]==[n for n,mid,l in PARENTS] and
            factors["right_middle_move"]==[list(v) for v in RIGHT] and
            factors["upper_move"]==[list(v) for v in UPPER] and
            factors["order"]==list(ORDERS) and
            factors["independent_native_entries"]==["A","B"] and
            len(FROZEN)==16==len({n for n,word in FROZEN}),
            "prospectively fixed finite intervention family changed")
    for name,word in FROZEN:
        actions=parse_plan(word)
        require(actions[-1][0]==5 and
                sum(a==5 for a,xy in actions)==1 and
                sum(a==6 for a,xy in actions)==5,
                "source-native level4 word lacks exactly five actual click actions")
    require("levels_completed>=5" in c["official_progress"],
            "genuine original SDK progress predicate disappeared")
    return c

def inspect(c,source):
    path=Path(source)
    require(path.is_file() and path.with_suffix(".npz").is_file(),
            "native original SDK JSON/NPZ evidence missing")
    report=json.loads(path.read_text())
    require(report["kind"]=="ORIGINAL_SP80_LEVEL4_NATIVE_ORDER_RU_VS_UR" and
            report["original_sdk_resets"]==32 and
            report["original_sdk_level4_root_blake2b16"]==c["parent_root_blake2b16"] and
            report["frozen_original_stage4_words"]==[list(v) for v in FROZEN],
            "frozen original SDK controls or source run changed")
    cases={(v["case"],v["witness"]):v for v in report["native_cases"]}
    require(len(cases)==32 and
            set(cases)=={(n,w) for n,word in FROZEN for w in ("A","B")},
            "source-original A/B case ledger incomplete")
    data={};advances=0;level_hist=Counter()
    with np.load(path.with_suffix(".npz"),allow_pickle=False) as stacks:
        for name,word in FROZEN:
            duplicates=[]
            for witness in ("A","B"):
                row=cases[(name,witness)];actions=parse_plan(word)
                ledger=row["original_stage4_action_ledger"]
                require(row["frozen_original_stage4_word"]==word and
                        row["native_stage4_source_actions"]==len(ledger) and
                        1<=len(ledger)<=len(actions),
                        "source SDK action-operator word mismatch")
                root=stacks[name+"_"+witness+"_entry3_34"][-1]
                require(root.shape==(64,64) and
                        framehash(root)==c["parent_root_blake2b16"],
                        "original SDK Level4 exact root absent")
                previous=root
                for i,((aid,xy),receipt) in enumerate(zip(actions,ledger),1):
                    returned=stacks[name+"_"+witness+"_stage4_"+str(i)]
                    require(returned.ndim==3 and returned.shape[1:]==(64,64) and
                            len(returned)==receipt["original_sdk_frame_stack_count"],
                            "genuine original native returned full 64x64 source stack absent")
                    require(receipt["genuine_original_action"]==aid and
                            receipt["real_native_click_xy"]==
                             (list(xy) if xy is not None else None)
                            and receipt["source_frame_before_blake2b16"]==framehash(previous)
                            and receipt["source_frame_after_blake2b16"]==framehash(returned[-1])
                            and aid in receipt["original_legal_actions_before"]
                            and receipt["original_sdk_level_before"]>=4,
                            "real original SDK legal-action/click/source-frame hash disagrees")
                    if xy is not None:
                        x,y=xy
                        require(receipt["original_source_pixel_before_click"]==
                                int(previous[y,x]),"native click not independently reproduced")
                    previous=returned[-1]
                end=ledger[-1]
                require(end["original_sdk_level_after"]==row["official_original_level"] and
                        end["original_sdk_state_after"]==row["official_original_state"] and
                        row["official_level5_or_WIN"]==
                            (row["official_original_level"]>=5 or
                             row["official_original_state"]=="WIN"),
                        "original SDK official level5/WIN witness drift")
                advances+=int(row["official_level5_or_WIN"])
                level_hist[str(row["official_original_level"])]+=1
                if not row["native_full_frozen_action_word"]:
                    require(row["official_level5_or_WIN"] and row["source_observed"] is None,
                            "original native word illegally shortened without true progress")
                    duplicates.append({"witness":witness,"early_progress":True,
                                       "official_level":row["official_original_level"]})
                    continue
                require(len(ledger)==len(actions) and end["genuine_original_action"]==5,
                        "original source last ACTION5/pour not recorded")
                pre=stacks[name+"_"+witness+"_stage4_"+str(len(actions)-1)][-1]
                animation=stacks[name+"_"+witness+"_stage4_"+str(len(actions))]
                obs=compute(root,pre,animation)
                src=row["source_observed"]
                require(src is not None,"missing native source cup/strand observation")
                m=src["actual_original_source"]
                require(m["original_source_cup_first_full_frames"]==obs["cups_first"] and
                        m["original_source_cup_max_palette13_pixels"]==obs["cups_max"] and
                        m["native_first_simultaneously_full_four_cups"]==obs["first_four"] and
                        all((None if m["first_original_color6_at_3_upper_sites"][key] is None
                              else m["first_original_color6_at_3_upper_sites"][key]
                               ["native_original_frame"])==index
                            for key,index in obs["site_first"].items()) and
                        all((None if m["native_first_source_border_changes"][key] is None
                              else m["native_first_source_border_changes"][key]
                               ["native_original_frame"])==index
                            for key,index in obs["border_first"].items()),
                        "raw original source NPZ contradicts reported native visual metrics")
                require(src["four_cups_together"]==(obs["first_four"] is not None) and
                        src["topmiddle_max13"]==obs["cups_max"]["top_middle"] and
                        src["leftmost_strand_absent"]==obs["P_leftmost_absent"] and
                        src["rightmost_strand_absent"]==obs["Q_rightmost_absent"] and
                        src["top_and_right_edge_unchanged"]==obs["no_top_right_border"] and
                        src["original_prepour_hash"]==framehash(pre) and
                        src["original_postpour_hash"]==framehash(animation[-1]) and
                        row["selected_upper_after_common_terminal_click"]==bbox(pre),
                        "native visual/source-sha/source-selected bbox math not witnessed")
                require(ledger[-2]["genuine_original_action"]==6,
                        "final native action prior to pour not the common selection click")
                expect_x=30 if "_U1_" in name else 16
                require(ledger[-2]["real_native_click_xy"]==[expect_x,21],
                        "final common original click coordinates changed")
                expected_box=[26,20,37,22] if expect_x==30 else [11,20,22,22]
                require(bbox(pre)==expected_box,
                        "WALL_TERMINAL_SELECTION: native clicked object differs from controlled upper bar")
                duplicates.append({
                    "witness":witness,"official_level":row["official_original_level"],
                    "official_state":row["official_original_state"],
                    "original_terminal_frame":pre.copy(),
                    "native_animation":animation.copy(),
                    "source_metrics":obs,
                    "source_selected_bbox":bbox(pre),
                    "last_source_hash":framehash(animation[-1]),
                })
            require(len(duplicates)==2 and
                    {x["witness"] for x in duplicates}=={"A","B"},
                    "independent source witness count changed")
            if "early_progress" not in duplicates[0]:
                a,b=duplicates
                require(a["official_level"]==b["official_level"] and
                        a["official_state"]==b["official_state"] and
                        np.array_equal(a["original_terminal_frame"],b["original_terminal_frame"]) and
                        np.array_equal(a["native_animation"],b["native_animation"]) and
                        a["source_metrics"]==b["source_metrics"],
                        "independent original source A/B replay disagreements")
            else:
                require(duplicates[0]==duplicates[1] or
                        all(x.get("early_progress") for x in duplicates),
                        "new level5 advancement needs native independent replication")
            data[name]=duplicates[0]

    require(advances==report["official_native_level5_or_WIN"],
            "official SDK level histogram/count mismatched saved originals")
    squares=[]
    for parent,mid,l in PARENTS:
        for rn,ra in RIGHT:
            for un,ua,terminal in UPPER:
                ru=data[f"{parent}_{rn}_{un}_RU"]
                ur=data[f"{parent}_{rn}_{un}_UR"]
                if "early_progress" in ru or "early_progress" in ur:
                    squares.append({"clean_parent":parent,"right":rn,"upper":un,
                         "status":"REPLICATION_REQUIRED_EARLY_NATIVE_PROGRESS",
                         "official_levels":[ru["official_level"],ur["official_level"]]})
                    continue
                a,b=ru["original_terminal_frame"],ur["original_terminal_frame"]
                pa,pb=ru["native_animation"],ur["native_animation"]
                equal_len=len(pa)==len(pb)
                first_animation_diff=(
                     difference(pa,pb) if equal_len else
                     {"kind":"frame_count","counts":[len(pa),len(pb)]}
                )
                same_projection=bool(np.array_equal(a[:63],b[:63]))
                same_full=bool(np.array_equal(a,b))
                same_animation=equal_len and first_animation_diff is None
                same_official=(ru["official_level"]==ur["official_level"] and
                               ru["official_state"]==ur["official_state"])
                squares.append({
                    "clean_parent":parent,"right":rn,"upper":un,
                    "native_action_pair":["RU","UR"],
                    "same_full_prepour_original_frame":same_full,
                    "same_prepour_observation_rows0_62":same_projection,
                    "prepour_source_counterexample":difference(a,b),
                    "first_returned_animation_difference":first_animation_diff,
                    "same_original_all_pour_frames":same_animation,
                    "same_original_official_game_outcome":same_official,
                    "native_level_RU":ru["official_level"],"native_level_UR":ur["official_level"],
                    "native_cup_max_RU":ru["source_metrics"]["cups_max"],
                    "native_cup_max_UR":ur["source_metrics"]["cups_max"],
                    "native_first_four_RU":ru["source_metrics"]["first_four"],
                    "native_first_four_UR":ur["source_metrics"]["first_four"],
                    "native_P_Q_RU":[ru["source_metrics"]["P_leftmost_absent"],
                                     ru["source_metrics"]["Q_rightmost_absent"]],
                    "native_P_Q_UR":[ur["source_metrics"]["P_leftmost_absent"],
                                     ur["source_metrics"]["Q_rightmost_absent"]],
                    "selected_upper_bbox_RU":ru["source_selected_bbox"],
                    "selected_upper_bbox_UR":ur["source_selected_bbox"],
                    "returned_animation_frame_counts":[len(pa),len(pb)],
                })
    require(len(squares)==8,"missing original finite action-order commuting squares")
    count=lambda key:sum(bool(s.get(key)) for s in squares)
    result={
      "kind":"ORIGINAL_SP80_LEVEL4_NATIVE_ORDER_MATHEMATICAL_WORKSTATION_RETURN",
      "source_contract":c["id"],
      "native_original_sdk_resets":len(cases),
      "official_native_level5_or_WIN_count":advances,
      "official_native_level_histogram":dict(level_hist),
      "state":"REPLICATION_REQUIRED" if advances else "PARTIAL",
      "finite_action_order_comparisons":squares,
      "observed_same_full_prepour":count("same_full_prepour_original_frame"),
      "observed_same_prepour_projection":count("same_prepour_observation_rows0_62"),
      "observed_identical_full_native_pours":count("same_original_all_pour_frames"),
      "observed_same_official_outcomes":count("same_original_official_game_outcome"),
      "math_admission":"Exact finite source-native partial commuting diagram; no total operator law or F3-to-SDK map",
      "next_movement":c["next_if_progress"] if advances else c["next_if_no_progress"],
      "walls":c["walls"],
    }
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("phase",choices=("pre","post"))
    p.add_argument("--result",type=Path,default=DEFAULT)
    a=p.parse_args();c=context()
    if a.phase=="pre":
        print("ARC4_ORDER_FINITE_PREFLIGHT "+json.dumps({
            "contract":c["id"],"source_root":c["parent_root_blake2b16"],
            "expected_native_resets":c["expected_original_sdk_resets"]},sort_keys=True),flush=True)
    else:
        result=inspect(c,a.result)
        a.result.with_suffix(".protocol.json").write_text(json.dumps(result,indent=2)+"\n")
        print("ARC4_NATIVE_ORDER_VERIFIED "+json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__": main()
