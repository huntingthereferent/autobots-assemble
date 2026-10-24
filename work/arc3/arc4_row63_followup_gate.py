"""Source-independent archive checks for frozen row63 native follow-up."""
from __future__ import annotations
import argparse
import json
from hashlib import blake2b
from pathlib import Path
import numpy as np
from .native_sp80_stage4_row63_followup import (
    FROZEN,PAIRS,PARENT,original_word,
)
from .native_sp80_multi_select import parse_plan

MANIFEST=Path("work/arc3/arc4_row63_followup_contract.json")
DEFAULT=Path("runtime/data/arc4/row63/original-row63-followup.json")
CUPS={"lateral","top_left","top_middle","top_right"}

def require(ok,why):
    if not ok:raise ValueError("ORIGINAL_SDK_DRIFT_WALL: "+why)

def context():
    m=json.loads(MANIFEST.read_text(encoding="utf8"))
    require(m["schema_version"]==1 and m["parent_run_id"]==40125152426,
            "original parent source reference drift")
    require(m["source_code"]=="work/arc3/native_sp80_stage4_row63_followup.py",
            "original native source changed")
    require(m["frozen_parent"]==PARENT and m["frozen_controls"]==[list(x) for x in FROZEN]
            and m["frozen_pairs"]==[list(x) for x in PAIRS],
            "frozen original SDK action comparison changed")
    require(len(FROZEN)*m["resets_per_control"]==m["expected_original_sdk_resets"]==16,
            "native reset budget changed")
    require(any("levels_completed >=5" in w for w in m["walls"]),
            "native progress boundary missing")
    for case,history,challenge in FROZEN:
        full=parse_plan(original_word(history,challenge))
        require(full[-1][0]==5 and sum(a==5 for a,_ in full)==1,
                "actual native pour not uniquely frozen")
        require([a for a,_ in parse_plan(challenge)] in ([6],[6,3]),
                "native common challenge altered")
    return m

def _hash(arr):
    return blake2b(np.ascontiguousarray(arr).tobytes(),digest_size=16).hexdigest()

def _bbox(frame):
    y,x=np.nonzero(frame==9)
    return [int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None

def _diff(a,b):
    return {"full_grid_equal":bool(np.array_equal(a,b)),
            "row0_62_equal":bool(np.array_equal(a[:63],b[:63])),
            "row63_equal":bool(np.array_equal(a[63],b[63])),
            "changed_pixels":int(np.count_nonzero(a!=b)),
            "interior_changed_pixels":int(np.count_nonzero(a[:63]!=b[:63])),
            "row63_changed_pixels":int(np.count_nonzero(a[63]!=b[63]))}

def verify_result(m,out):
    out=Path(out);npz=out.with_suffix(".npz")
    require(out.is_file() and npz.is_file(),"native source JSON/NPZ missing")
    record=json.loads(out.read_text(encoding="utf8"))
    require(record.get("kind")=="ORIGINAL_ARC4_ROW63_HISTORY_COMMON_CHALLENGE"
            and record.get("frozen_parent")==PARENT
            and record.get("frozen_controls")==[list(x) for x in FROZEN]
            and record.get("frozen_pairs")==[list(x) for x in PAIRS],
            "original source return differs from predeclared contract")
    trials=record.get("native_cases")
    require(isinstance(trials,list) and len(trials)==record.get("original_sdk_resets")==16,
            "authentic native reset record absent")
    rows={(x["case"],x["witness"]):x for x in trials}
    require(len(rows)==16 and set(rows)=={(case,witness) for case,_,_ in FROZEN
                                               for witness in ("A","B")},
            "native case/witness identity changed")
    official_advances=0
    checked_pairs={}
    with np.load(npz,allow_pickle=False) as archive:
        require(len(archive.files)>=16*2,"native source frame stacks incomplete")
        for name,history,challenge in FROZEN:
            full=parse_plan(original_word(history,challenge))
            before_n=len(parse_plan(" ".join(x for x in (PARENT,history) if x)))
            challenge_n=len(parse_plan(challenge))
            for witness in ("A","B"):
                row=rows[(name,witness)]
                require(row["original_source_word"]==original_word(history,challenge)
                        and row["original_history"]==history
                        and row["common_challenge"]==challenge,
                        "native word/case mismatch")
                require(type(row["official_level"]) is int
                        and type(row["official_state"]) is str
                        and type(row["official_level5_or_WIN"]) is bool
                        and row["official_level5_or_WIN"]==
                        (row["official_level"]>=5 or row["official_state"]=="WIN"),
                        "official original game state contradicts recorded result")
                official_advances+=int(row["official_level5_or_WIN"])
                ledger=row["genuine_stage4_action_ledger"]
                require(len(ledger)==len(full) and
                        [x["genuine_original_action"] for x in ledger]==
                        [aid for aid,_ in full],
                        "native stage4 action receipts absent")
                for i,(aid,xy) in enumerate(full):
                    require(ledger[i].get("real_native_click_xy")==
                            (list(xy) if xy else None),
                            "original native coordinate receipt disagrees")
                parent=archive[name+"_"+witness+"_stage4_"+str(before_n)][-1]
                later=archive[name+"_"+witness+"_stage4_"+str(len(full)-1)][-1]
                animation=archive[name+"_"+witness+"_stage4_"+str(len(full))]
                for f in (parent,later):
                    require(f.shape==(64,64),"native pre/post challenge frame absent")
                require(animation.ndim==3 and animation.shape[1:]==(64,64),
                        "original SDK final animation absent")
                source=row["source"]
                require(source["parent_end_frame_hash"]==_hash(parent)
                        and source["challenge_end_frame_hash"]==_hash(later)
                        and source["parent_end_selected_bbox"]==_bbox(parent)
                        and source["challenge_end_selected_bbox"]==_bbox(later)
                        and source["native_parent_end_row63"]==parent[63].tolist()
                        and source["native_challenge_end_row63"]==later[63].tolist(),
                        "native source claimed frames differ from saved frame arrays")
                cups=source["source_cups"]
                require(set(cups["first_full_cup_frames"])==CUPS and
                        set(cups["maximum_original_cup13_pixels"])==CUPS,
                        "original full cup timing receipt invalid")
                for cup in CUPS:
                    t=cups["first_full_cup_frames"][cup]
                    n=cups["maximum_original_cup13_pixels"][cup]
                    require((t is None or (type(t) is int and
                            0<=t<len(animation))) and type(n) is int and 0<=n<=45
                            and (t is None)==(n<45),
                            "source cup full event contradicts maximum")
        require(official_advances==record["official_level5_or_WIN_count"],
                "official source progress falsely summarized")
        for left,right in PAIRS:
            observations=[]
            for witness in ("A","B"):
                x=next(item for item in FROZEN if item[0]==left)
                y=next(item for item in FROZEN if item[0]==right)
                pnumx=len(parse_plan(" ".join(z for z in (PARENT,x[1]) if z)))
                pnumy=len(parse_plan(" ".join(z for z in (PARENT,y[1]) if z)))
                lx=archive[left+"_"+witness+"_stage4_"+str(pnumx)][-1]
                ly=archive[right+"_"+witness+"_stage4_"+str(pnumy)][-1]
                p=_diff(lx,ly)
                require(p["row0_62_equal"] and not p["row63_equal"]
                        and _bbox(lx)==_bbox(ly),
                        "old original native row63-only match did not reproduce")
                fx=parse_plan(original_word(x[1],x[2]))
                fy=parse_plan(original_word(y[1],y[2]))
                endx=archive[left+"_"+witness+"_stage4_"+str(len(fx)-1)][-1]
                endy=archive[right+"_"+witness+"_stage4_"+str(len(fy)-1)][-1]
                stackx=archive[left+"_"+witness+"_stage4_"+str(len(fx))]
                stacky=archive[right+"_"+witness+"_stage4_"+str(len(fy))]
                observation={
                    "source_prechallenge":p,
                    "source_after_common_challenge":_diff(endx,endy),
                    "post_challenge_pairwise_interior_equal":
                        bool(len(stackx)==len(stacky) and
                             np.array_equal(stackx[:,:63],stacky[:,:63])),
                    "post_challenge_pairwise_row63_equal":
                        bool(len(stackx)==len(stacky) and
                             np.array_equal(stackx[:,63],stacky[:,63])),
                    "post_challenge_frame_counts":[len(stackx),len(stacky)],
                }
                observations.append(observation)
                recorded=record["native_pairwise_relations"][left+"_vs_"+right]
                for scope in ("source_prechallenge","source_after_common_challenge"):
                    claimed=recorded[scope]
                    for key,v in observation[scope].items():
                        require(claimed.get(key)==v,
                                "archive disagrees with source pair "+scope+" "+key)
            require(observations[0]==observations[1],
                    "original SDK witness-to-witness source pair diverged")
            checked_pairs[left+"_vs_"+right]=observations[0]
    return {
        "kind":"ORIGINAL_ARC4_ROW63_WORKSTATION_RETURN",
        "referent":m["referent"],
        "source_contract":m["id"],
        "state":"PARTIAL" if not official_advances else "REPLICATION_REQUIRED",
        "native_resets_with_receipts":len(trials),
        "official_sdk_progress_cases":official_advances,
        "native_pairwise_relations":checked_pairs,
        "next_movement":m["next_progress"] if official_advances else m["next_no_progress"],
        "walls":m["walls"],
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("phase",choices=("pre","post"))
    p.add_argument("--result",type=Path,default=DEFAULT)
    args=p.parse_args();m=context()
    if args.phase=="pre":
        print("ARC4_ROW63_PREFLIGHT "+json.dumps({"contract":m["id"],
              "expected_native_resets":m["expected_original_sdk_resets"]},sort_keys=True))
    else:
        result=verify_result(m,args.result)
        args.result.with_suffix(".protocol.json").write_text(json.dumps(result,indent=2)+"\n")
        print("ARC4_ROW63_DRIFT_RETURN "+json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
