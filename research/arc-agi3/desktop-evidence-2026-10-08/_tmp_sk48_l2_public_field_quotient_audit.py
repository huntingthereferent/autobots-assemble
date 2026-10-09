"""SK48 Level 2 native public A/B feature audit.

Probe multiple real replay histories and record full-frame versus field/state
projections. Keep collisions and outcome disagreement as counterexamples.
Never use private engine state or stored Level 2 action sequences.
"""
from __future__ import annotations
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from pathlib import Path
from hashlib import sha256
from collections import defaultdict,Counter
import json,numpy as np,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
a=Arcade(operation_mode=OperationMode.NORMAL);g=a.make("sk48")
nsteps=0;extra=0
def im(o):return np.asarray(o.frame[-1],dtype=np.uint8).reshape(64,64)
def h(x):return sha256(x.tobytes()).hexdigest()[:18]
def full(o):return h(im(o))
def proj(o):return h(im(o)[6:50,5:55])
def slim(o):return h(im(o)[6:50:2,5:55:2])
def enter(path=()):
 global nsteps,extra
 for i in range(6):
  o=g.step(GameAction.RESET,data={});nsteps+=1
  if o.levels_completed==0:break
  extra+=1
 else:raise RuntimeError("RESET not acknowledged")
 for z in L1:o=g.step(GameAction.from_id(z),data={});nsteps+=1
 if o.levels_completed!=1:raise RuntimeError("L2 not reached")
 for z in path:o=g.step(GameAction.from_id(z),data={});nsteps+=1
 return o
q=[()]
samples={}
for depth in range(7):
 nq=[];byfull=defaultdict(list);byproj=defaultdict(list);byslim=defaultdict(list)
 for path in q:
  o=enter(path)
  sample={"history":path,"full":full(o),"field":proj(o),"sample":slim(o),"levels":o.levels_completed}
  samples[path]=sample
  byfull[sample["full"]].append(path);byproj[sample["field"]].append(path);byslim[sample["sample"]].append(path)
  if depth<6:
   for z in (1,2,3,4):
    p=path+(z,)
    if p not in samples and len(nq)<600:nq.append(p)
 print("DEPTH",depth,"histories",len(q),"unique_full",len(byfull),"unique_field",len(byproj),"unique_sample",len(byslim),"native_actions",nsteps,"seconds",round(time.monotonic(),1),flush=True)
 if depth==0:initial=im(o).copy()
 if depth==3:
  print("INITIAL_PALETTE",dict(Counter(initial.ravel().tolist())),"INITIAL_COLOR_POSITIONS",{
    str(v):[ (int(x),int(y)) for y,x in zip(*np.where(initial[:50,:55]==v)) ][::16][:10] for v in [8,9,12,14]
   },flush=True)
 if depth>=4 or len(q)>=125:break
 q=nq[:150]
print("COMPARISON_AT_LEAST4",len(samples),flush=True)
out=F/"sk48_l2_public_field_quotient_audit.json"
out.write_text(json.dumps({"histories":[{**row,"history":list(row["history"])} for row in samples.values()],
                          "native_actions":nsteps,"reset_retries":extra,
                          "projection":"frame[y=6..49,x=5..54]"},
                          indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
