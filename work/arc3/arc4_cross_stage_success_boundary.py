"""Original SDK SP80 stages 3/4: native success versus visible cups and edges.

This is source-archive verification, NOT another game run and NOT an
inferred engine physics model. Artifacts are pinned by actual SHA256.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256, blake2b
import io
import json
from pathlib import Path
import zipfile
import numpy as np

# File, source payload name, expected original JSON and NPZ SHA256, trial count,
# stage, native records key and their case/witness/word/status/ledger fields.
SOURCES = (
 ("arc3-transition-original.zip","original-sp80-stage3-right-catcher-edge",
 "99a7c84a6b2d5f52e4847dbcab8510d23b5fbebcf2aa1e7e160a77b72d995273",
 "5cdb6d73a16685a19132a67ed02e3781342725672bee4f6d388d3bc28e5c5542",
 50,3,"genuine_sdk_original_action_and_frame_receipts",
 ("original_precommitted_sdk_case","real_native_entry_witness","actual_original_sdk_word",
  "original_sdk_official_final_level","true_original_sdk_action_ledger")),
 ("arc4-clean-lateral-original.zip","original-sp80-stage4-clean-lateral-top",
 "c408f491013da2b000606ee9276ffcb5ecc6da12d080123e6c2a3365d13e3e",
 "aa86e920cba4ab7f061a34c5ab50e88cf8aa6a7037e9d80548c8a7fdb06fcc80",
 52,4,"source_full_actual_original_receipts",
 ("prospective_original_source_case","independent_actual_native_witness","true_sdk_stage4_source_word",
  "official_original_final_level","actual_original_sdk_full_action_receipts")),
 ("arc4-left-boundary-original.zip","original-sp80-stage4-L-left-boundary",
 "4d62f7fbf1c9b07d04d784dd0ee709e9bd8791df52ed04535216b6720b2230bc",
 "936565fe05e529e046f400c0037eebe7cc92802826d04770896aba165fa85ccc",
 48,4,"complete_true_original_sdk_source_records",
 ("predeclared_native_source_case","genuine_original_independent_witness","true_original_sdk_stage4_word",
  "actual_original_sdk_final_level","genuine_sdk_stage4_action_receipts")),
 ("arc4-lower-L-original.zip","original-sp80-stage4-lower-L-piece",
 "ddaaa0d118a2ed8c8d3d8cf450ba0723535d9563a2f3ac1851197c1a456d8823",
 "1fb3bf99c9c7d5065cf99445ffcc033ceeeeed1f7f5726e8fbc78692a9bc5568",
 48,4,"complete_source_native_evidence",
 ("precommitted_original_source_case","independent_original_native_witness","real_original_sdk_level4_word",
  "official_original_sdk_final_level","actual_original_source_action_receipts")),
 ("arc4-top-edge-original.zip","original-sp80-stage4-four-top-edge",
 "9bbbad04c5165135bc3df3d40e34656c8e098b1f6a2919a8485b7e22fddcdfd7",
 "7a238259863dad33e4bb2819d2e42eb20e163557611abe934960d1ddd66dc90a",
 48,4,"genuine_original_source_action_receipts",
 ("frozen_true_original_source_case","independent_original_sdk_witness","actual_native_source_stage4_word",
  "official_original_final_level","native_original_sdk_action_ledger")),
)
CUP3=tuple((x,53,x+8,58) for x in (8,26,38,50))
CUP4=((5,35,10,43),(17,5,25,10),(35,5,43,10),(47,5,55,10))
EDGES3={"bottom":(slice(59,63),slice(2,62))}
EDGES4={
 "left":(slice(2,62),slice(2,5)),
 "top":(slice(2,5),slice(2,62)),
 "right":(slice(2,62),slice(59,62)),
 "bottom":(slice(59,63),slice(2,62)),
}

def require(ok,message):
 if not ok:raise ValueError("ARC4_CROSS_STAGE_WALL: "+message)
def frame_hash(arr):
 return blake2b(np.ascontiguousarray(arr).tobytes(),digest_size=16).hexdigest()

def analyze(folder):
 records=[];archives=[]
 for filename,base,json_hash,npz_hash,budget,stage,recordkey,fields in SOURCES:
  path=folder/filename
  require(path.is_file(),"original GitHub Actions artifact missing: "+filename)
  with zipfile.ZipFile(path) as z:
   jbytes=z.read(base+".json");nbytes=z.read(base+".npz")
   require(sha256(jbytes).hexdigest()==json_hash and
           sha256(nbytes).hexdigest()==npz_hash,
           "original SDK archive SHA-256 mismatch: "+filename)
   report=json.loads(jbytes);trials=report[recordkey]
   require(len(trials)==budget,"original SDK native trial count changed")
   counted=set()
   with np.load(io.BytesIO(nbytes),allow_pickle=False) as stacks:
    for trial in trials:
     case,witness,word,level,ledger=(trial[k] for k in fields)
     require(witness in ("A","B") and (case,witness) not in counted,
             "original SDK A/B native trial duplicates")
     counted.add((case,witness))
     tokens=word.split();index=len(tokens)
     require(tokens[-1]=="5" and len(ledger)>=index,
             "original native ACTION5 receipt missing")
     last=ledger[-1]
     actionkey="original_action" if stage==3 else "genuine_original_action"
     levelkey="official_source_level_after" if stage==3 else "original_sdk_level_after"
     hashkey="actual_source_after_sha" if stage==3 else "source_frame_after_blake2b16"
     require(last[actionkey]==5 and last[levelkey]==level,
             "official original SDK transition contradicted by action ledger")
     prefix=case+"_"+witness+"_"
     stack=stacks[prefix+"stage"+str(stage)+"_"+str(index)]
     pre=stacks[prefix+"stage"+str(stage)+"_"+str(index-1)][-1]
     require(stack.ndim==3 and stack.shape[1:]==(64,64) and
             pre.shape==(64,64),"actual original SDK source frames absent")
     require(frame_hash(stack[-1])==last[hashkey],
             "original SDK native action last source hash mismatch")
     root=pre if stage==3 else stacks[prefix+"entry3_34"][-1]
     cups=CUP3 if stage==3 else CUP4
     masks=[root[y0:y1+1,x0:x1+1]==11 for x0,y0,x1,y1 in cups]
     require(all(int(mask.sum())==45 for mask in masks),
             "original source cup root changed: "+case)
     first=[None]*4;maxima=[0]*4;first_all=None
     for t,frame in enumerate(stack):
      simultaneous=0
      for i,(x0,y0,x1,y1) in enumerate(cups):
       count=int(np.count_nonzero(masks[i] & (frame[y0:y1+1,x0:x1+1]==13)))
       maxima[i]=max(maxima[i],count)
       if count==45:
        simultaneous+=1
        if first[i] is None:first[i]=t
      if first_all is None and simultaneous==4:first_all=t
     borders={}
     for edge,(ys,xs) in (EDGES3 if stage==3 else EDGES4).items():
      borders[edge]=next((t for t,frame in enumerate(stack)
                          if np.any(pre[ys,xs]!=frame[ys,xs])),None)
     observed=trial.get("genuine_original_frame_evidence") or trial.get(
      "original_native_cup_and_boundary_observations") or trial.get(
      "original_source_actual_frame_measures") or trial.get(
      "original_returned_source_visuals")
     if isinstance(observed,dict):
      for key in ("original_first_four_visually_full_cup_frame",
                  "first_native_four_simultaneous_full_visual_frame",
                  "first_native_frame_all_cups_ever_full",
                  "first_all_four_cups_simultaneous_source_frame"):
       if key in observed:
        require(observed[key]==first_all,
                "original measured four-cup event disagrees with actual saved NPZ")
        break
     records.append({
      "archive":filename,"stage":stage,"case":case,"witness":witness,
      "official_level":level,"simultaneous_four_frame":first_all,
      "first_full_cup_frames":first,"maximum_palette13_in_cups":maxima,
      "original_frame_count":len(stack),"first_border_change":borders,
      "original_prepour_hash":frame_hash(pre),"original_pour_final_hash":frame_hash(stack[-1]),
      "original_stage4_root":frame_hash(root) if stage==4 else None,
     })
    require(len(counted)==budget and
            all({w for n,w in counted if n==name}=={"A","B"}
                for name,_ in counted),"missing original SDK A/B reset")
   archives.append({"source":filename,"original_resets":budget,
                    "json_sha256":json_hash,"npz_sha256":npz_hash})
 original4={r["original_stage4_root"] for r in records if r["stage"]==4}
 require(len(original4)==1,"different original SDK stage4 roots")
 stage4_root=next(iter(original4))
 progressed=[r for r in records if r["stage"]==3 and r["official_level"]>=4]
 require(len(progressed)==2 and {r["witness"] for r in progressed}=={"A","B"} and
         all(r["original_pour_final_hash"]==stage4_root for r in progressed),
         "original SDK stage3 native advance does not bridge to source stage4 root")
 counts={}
 for stage,level in ((3,3),(3,4),(4,4)):
  group=[r for r in records if r["stage"]==stage and r["official_level"]==level]
  counts["stage"+str(stage)+"_level"+str(level)]={
   "original_sdk_resets":len(group),
   "simultaneously_full_four_cups":sum(r["simultaneous_four_frame"] is not None for r in group),
   "any_border_change":sum(any(v is not None for v in r["first_border_change"].values())
                           for r in group),
  }
 four4=[r for r in records if r["stage"]==4 and r["simultaneous_four_frame"] is not None]
 boundary_classes=dict(Counter(",".join(k for k,v in r["first_border_change"].items()
                                      if v is not None) or "none" for r in four4))
 return {
  "kind":"SP80_CROSS_STAGE_NATIVE_VISUAL_VS_OFFICIAL_BOUNDARY",
  "original_archives":archives,
  "total_original_sdk_resets":len(records),
  "original_stage4_root_blake2b16":stage4_root,
  "genuine_stage3_successes_bridge_to_stage4_root":True,
  "official_vs_visual":counts,
  "stage4_four_full_border_patterns":boundary_classes,
  "all_source_cases":records,
  "walls":[
   "Visual completion of four original cup masks is not a sufficient original SDK success criterion in stage3 or stage4.",
   "Distinct original levels have distinct source frames, positions, and requirements; associations across levels are not a causal intervention.",
   "Native border-pixel differences are measured witnesses, not inferred internal physics or a decoded engine objective.",
   "Original archive provenance is limited to pinned authentic GitHub Actions artifacts and saved SDK frames; no new game reset was made.",
  ],
 }

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--directory",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 args=p.parse_args()
 report=analyze(args.directory)
 args.out.parent.mkdir(parents=True,exist_ok=True)
 args.out.write_text(json.dumps(report,indent=2)+"\n")
 print("ARC4_CROSS_STAGE_BOUNDARY "+json.dumps({
  "original_sdk_resets":report["total_original_sdk_resets"],
  "official_vs_visual":report["official_vs_visual"],
  "stage4_four_full_border_patterns":report["stage4_four_full_border_patterns"],
  "stage4_root":report["original_stage4_root_blake2b16"],
  "success_bridge":report["genuine_stage3_successes_bridge_to_stage4_root"],
 },sort_keys=True),flush=True)

if __name__=="__main__":main()
