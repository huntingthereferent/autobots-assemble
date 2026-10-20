"""Finite source-feedback continuation of original SP80 stage3.

All candidates replay genuine original SDK 0->1->2->3 through existing
witnesses. Operators are selected by ACTUAL returned stage3 pour frames.
The feedback measure is only observed source palette movement, never a
substitute WIN/level oracle. Preserve all full SDK frames in NPZ.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage3_native_feedback import BANDS,real_trial

# The four source-native stage3 bottom palette11 regions in run #39463571663.
BINS=((8,16),(26,34),(38,46),(50,58))
OPS=tuple((name,xy,way,action) for name,xy,_ in BANDS
          for way,action in (("up",1),("down",2),("left",3),("right",4)))
BEAM=4
DEPTH=3
assert len(OPS)==24 and len(BINS)==4 and len(STAGE1_WITNESSES)==2

def word(plan):
    tokens=[]
    for name,way in plan:
        operators=[(xy,a) for n,xy,d,a in OPS if (n,d)==(name,way)]
        if len(operators)!=1:raise AssertionError("Unknown native action")
        (x,y),act=operators[0]
        tokens.append("6@%d,%d %d"%(x,y,act))
    return " ".join(tokens+["5"])

def feedback(root,frames):
    # Measured source 11->13 animation is not a decoded goal condition.
    bins=[max(int(np.sum((root[53:59,lo:hi+1]==11)&
                 (f[53:59,lo:hi+1]==13))) for f in frames) for lo,hi in BINS]
    path=np.zeros((64,64),dtype=bool)
    for f in frames:path|=((root==12)&(f==6))
    xs=np.nonzero(path[19:53])[1]
    return {"observed_bottom_palette11_to13_max":bins,
            "observed_full_bottom_groups":sum(c>=45 for c in bins),
            "source_flow_rightmost_x":int(xs.max()) if len(xs) else -1,
            "source_flow_distinct_columns":len(set(int(x) for x in xs)),
            "actual_original_pour_frames":len(frames)}

def record_receipts(row):
    # Complete frame-by-frame pixels are in retained raw original NPZ;
    # exclude only redundantly expanded pixel arrays from JSON metadata.
    events=[{k:v for k,v in e.items() if k!="full_original_source_frame_ledger"}
            for e in row["full_original_sdk_action_events"]]
    return {
        "witness":row["original_entry_witness"],
        "word":row["frozen_stage3_word"],
        "level":row["official_original_final_level"],
        "state":row["official_original_final_state"],
        "source_level4_or_WIN":row["official_original_level4_or_WIN"],
        "disposition":row["trial_disposition"],
        "native_entry_sha":row["original_verified_stage3_root"]["original_source_sha256"],
        "genuine_sdk_action_receipts":events}

def rank(r):
    s=r.get("observed_feedback") or {}
    return (s.get("observed_full_bottom_groups",-1),
            s.get("source_flow_rightmost_x",-1),
            s.get("source_flow_distinct_columns",-1))

def choose(rows):
    ordered=sorted(rows,key=lambda r:(tuple(-q for q in rank(r)),r["word"]))
    kept=[];last_bands=set();profiles=set()
    # Preserve independent source band relationships, not six clones of one.
    for r in ordered:
        if len(kept)>=BEAM:break
        band=r["plan"][-1][0]
        if band not in last_bands:
            kept.append(r);last_bands.add(band)
            profiles.add(tuple((r.get("observed_feedback") or {}).get("observed_bottom_palette11_to13_max",[])))
    for r in ordered:
        if len(kept)>=BEAM:break
        profile=tuple((r.get("observed_feedback") or {}).get("observed_bottom_palette11_to13_max",[]))
        if r not in kept and profile not in profiles:
            kept.append(r);profiles.add(profile)
    for r in ordered:
        if len(kept)>=BEAM:break
        if r not in kept:kept.append(r)
    return kept

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    all_rows=[];raw_arrays={};root_hashes=set();executed=set()
    def evaluate(witness,entry,plan):
        action_word=word(plan)
        key=(witness,action_word)
        if key in executed:raise AssertionError("Duplicate original SDK plan")
        executed.add(key)
        label="__".join("%s-%s"%(name,way) for name,way in plan)
        trial,frames=real_trial(witness,entry,label,action_word)
        record=record_receipts(trial)
        record["plan"]=[list(pair) for pair in plan]
        root_hashes.add(record["native_entry_sha"])
        last=frames.get("stage3_"+str(len(plan)*2+1))
        root=frames["entry2_11"][-1]
        record["observed_feedback"]=feedback(root,last) if last is not None else None
        all_rows.append(record)
        for phase,stack in frames.items():raw_arrays["%s_%s_%s"%(witness,label,phase)]=stack
        print("ORIGINAL_SP80_GUIDED_FEEDBACK "+json.dumps({
            "plan":record["plan"],"witness":witness,"level":record["level"],
            "state":record["state"],"feedback":record["observed_feedback"]},sort_keys=True),flush=True)
        return record

    wa,entrya=STAGE1_WITNESSES[0]
    frontier=[{"plan":[]}]
    verified_a=None
    for depth in range(1,DEPTH+1):
        observations=[]
        for prior in frontier:
            touched={b for b,d in prior["plan"]}
            for band,xy,direction,action in OPS:
                if band in touched:continue
                plan=[tuple(x) for x in prior["plan"]]+[(band,direction)]
                r=evaluate(wa,entrya,plan)
                observations.append(r)
                if r["source_level4_or_WIN"]:
                    verified_a=r;break
            if verified_a:break
        if verified_a:break
        frontier=choose(observations)
        print("ORIGINAL_SP80_GUIDED_LAYER "+json.dumps({
            "depth":depth,"observations":len(observations),
            "next_source_frontier":[{"word":r["word"],"feedback":r["observed_feedback"]}
                                    for r in frontier]},sort_keys=True),flush=True)
    wb,entryb=STAGE1_WITNESSES[1]
    candidates=[verified_a] if verified_a else frontier
    repeats=[evaluate(wb,entryb,[tuple(x) for x in r["plan"]]) for r in candidates]
    if len(root_hashes)!=1:raise RuntimeError("Independent original stage3 roots disagree")
    out={
       "kind":"ORIGINAL_SDK_SP80_STAGE3_SOURCE_FEEDBACK_FINITE_BEAM_SEARCH",
       "original_native_antecedent_runs":[39462922216,39463571663,39471887855],
       "finite_operator_family":OPS,"source_palette11_bin_ranges":BINS,
       "max_search_depth":DEPTH,"max_beam_width":BEAM,
       "independent_original_SDK_resets":len(all_rows),
       "source_stage3_root_hash":next(iter(root_hashes)),
       "official_original_level4_or_WIN":sum(int(r["source_level4_or_WIN"]) for r in all_rows),
       "original_official_final_levels":dict(Counter(str(r["level"]) for r in all_rows)),
       "actual_source_successes":[{"witness":r["witness"],"word":r["word"],"level":r["level"]}
                                  for r in all_rows if r["source_level4_or_WIN"]],
       "independent_B_replays":[{"word":r["word"],"level":r["level"],"state":r["state"]}
                                 for r in repeats],
       "source_native_sdk_records":all_rows,
       "limits":"Observed source palette and trajectory merely choose finite next probes. Only actual original Arcade.NORMAL SDK levels >=4 or WIN are progress. No cloned engine, physics certainty, F3 correspondence or inferred six-level finish. Every actual SDK source return frame is preserved in NPZ."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw_arrays)
    print("ORIGINAL_SP80_GUIDED_FINAL "+json.dumps({k:v for k,v in out.items()
          if k not in ("finite_operator_family","source_native_sdk_records")},sort_keys=True),flush=True)
if __name__=="__main__":main()
