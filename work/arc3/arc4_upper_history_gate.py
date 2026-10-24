"""Fail-closed pre/post gate for original native ARC4 upper-bar contrast."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from .native_sp80_stage4_upper_endpoint_history import PARENT,FROZEN,MATCHED,STAGE1_WITNESSES,parse_plan,word

MANIFEST=Path("work/arc3/arc4_upper_history_contract.json")
RESULT=Path("runtime/data/arc4/upper-history/original-upper-history.json")
CUPS={"lateral","top_left","top_middle","top_right"}

def require(ok,why):
    if not ok:raise ValueError("ARC4 source wall: "+why)

def context():
    m=json.loads(MANIFEST.read_text())
    require(m["schema_version"]==1 and m["frozen_parent"]==PARENT,"parent/source drift")
    require([tuple(x) for x in m["frozen_controls"]]==list(FROZEN),"frozen controls drift")
    require([tuple(x) for x in m["frozen_matched_relations"]]==list(MATCHED),"relations drift")
    require(tuple(w for w,_ in STAGE1_WITNESSES)==("A","B"),"native witnesses drift")
    require(len(FROZEN)*2==m["expected_original_sdk_resets"]==16,"native budget drift")
    for name,tail in FROZEN:
        actions=parse_plan(word(tail))
        require(actions[-1][0]==5 and sum(a==5 for a,_ in actions)==1,"pour drift "+name)
    require(any("levels_completed >=5" in w for w in m["walls"]),"native success rule missing")
    return m

def verify_result(m,out):
    out=Path(out);npz=out.with_suffix(".npz")
    require(out.is_file() and npz.is_file(),"original source artifacts missing")
    r=json.loads(out.read_text())
    require(r["kind"]=="ORIGINAL_SP80_UPPER_ENDPOINT_HISTORY_DISCRIMINATOR","native kind changed")
    require(r["frozen_parent"]==m["frozen_parent"] and
            r["frozen_controls"]==m["frozen_controls"] and
            r["frozen_matched_relations"]==m["frozen_matched_relations"],"unfrozen native actions")
    cases=r["native_cases"]
    require(len(cases)==r["original_sdk_resets"]==16,"original reset count")
    progress=0;observations={}
    for name,tail in m["frozen_controls"]:
        pair=[c for c in cases if c["case"]==name]
        require(len(pair)==2 and {c["witness"] for c in pair}=={"A","B"},"missing A/B "+name)
        require(pair[0]["source"]==pair[1]["source"] and
                pair[0]["official_level"]==pair[1]["official_level"] and
                pair[0]["official_state"]==pair[1]["official_state"],"native A/B conflict")
        for c in pair:
            require(c["original_word"]==word(tail),"action history changed")
            require(type(c["official_level"]) is int and type(c["official_state"]) is str
                    and type(c["official_level5_or_WIN"]) is bool,"non-native status")
            first=c["source"]["first_full_cup_frames"];maximum=c["source"]["maximum_original_cup13_pixels"]
            require(set(first)==CUPS and set(maximum)==CUPS,"source cups missing")
            for cup in CUPS:
                t=first[cup];v=maximum[cup]
                require((t is None or (type(t) is int and
                        0<=t<c["source"]["original_frame_count"]))
                        and type(v) is int and 0<=v<=45 and
                        (t is None)==(v<45),"first cup timing differs from maxima")
            require(bool(c["native_action_receipts"]),"native action ledger absent")
            progress+=int(c["official_level5_or_WIN"])
        observations[name]=pair[0]["source"]
    require(progress==r["official_level5_or_WIN_count"],"SDK official result mismatch")
    pairs=r["actual_native_pairwise_relations"]
    require(set(pairs)=={a+"_vs_"+b for a,b in MATCHED},"source contrasts absent")
    with np.load(npz,allow_pickle=False) as frames:
        require(len(frames.files)>=16,"original SDK archives incomplete")
        for key in frames.files:
            a=frames[key]
            require(a.ndim in (2,3) and a.shape[-2:]==(64,64),"non-native frame "+key)
    return {"kind":"ARC4_UPPER_HISTORY_SOURCE_RETURN","state":"PARTIAL" if not progress else "REPLICATION_REQUIRED",
            "contract":m["id"],"native_resets_with_receipts":16,
            "official_sdk_progress_cases":progress,
            "native_control_events":observations,
            "native_matched_relations":pairs,
            "next_movement":m["next_progress"] if progress else m["next_no_progress"]}

def main():
    p=argparse.ArgumentParser();p.add_argument("phase",choices=("pre","post"))
    p.add_argument("--result",type=Path,default=RESULT);a=p.parse_args()
    m=context()
    if a.phase=="pre":
        print("ARC4_HISTORY_PREFLIGHT "+json.dumps({"contract":m["id"],"native_resets":16}),flush=True)
    else:
        receipt=verify_result(m,a.result)
        a.result.with_suffix(".protocol.json").write_text(json.dumps(receipt,indent=2)+"\n")
        print("ARC4_HISTORY_DRIFT_RETURN "+json.dumps(receipt,sort_keys=True),flush=True)
if __name__=="__main__":main()
