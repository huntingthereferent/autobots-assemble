"""SK48 public A/B: are two ways of advancing the hidden phase equivalent?

Native sources: repeated no-visible-change directional ACTION2, and
directional action followed by ACTION7. Compare whole continuation traces
over all 64 three-direction suffixes. ACTION7-only is zero-phase control.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from hashlib import sha256
from itertools import product
from collections import defaultdict,Counter
import numpy as np,json,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
histories={
 0:[(),(7,),(7,7)],
 1:[(2,),(1,7),(4,7)],
 2:[(2,2),(1,7,1,7),(4,7,4,7)],
 3:[(2,2,2),(1,7,1,7,1,7),(4,7,4,7,4,7)],
}
root=None;native=0;retries=0
def step(n):
 global native
 native+=1
 return g.step(GameAction.from_id(n),data={})
def h(o):
 return "%d:%s:%s"%(o.levels_completed,o.state.name,sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:20])
def entry(path):
 global root,retries
 for k in range(8):
  o=step(0)
  if o.levels_completed==0:break
  retries+=1
 else:raise RuntimeError("native RESET not acknowledged")
 for z in L1:o=step(z)
 if root is None:root=h(o)
 if h(o)!=root:raise RuntimeError("native L2 entry drift")
 for z in path:o=step(z)
 return o
count_conflicts=[];summary=Counter();example=[];t0=time.monotonic()
for i,suffix in enumerate(product((1,2,3,4),repeat=3),1):
 group_trace={}
 for count,variants in histories.items():
  sources=[]
  for path in variants:
   before=entry(path)
   if h(before)!=root:
    count_conflicts.append({"kind":"root mismatch","suffix":suffix,"count":count,"source":path,"frame":h(before)})
    continue
   trace=[]
   for z in suffix:trace.append(h(step(z)))
   sources.append(trace)
  if not sources:continue
  if any(trace!=sources[0] for trace in sources[1:]):
   count_conflicts.append({"kind":"continuation mismatch","suffix":suffix,"count":count,
                           "sources":[list(x) for x in variants],"traces":sources})
  group_trace[count]=tuple(sources[0])
 if len(group_trace)==4:
  sig=defaultdict(list)
  for count,trace in group_trace.items():sig[trace].append(count)
  partition=tuple(sorted(tuple(v) for v in sig.values()))
  summary[str(partition)]+=1
  if i in (1,16,32,48,64):
   print("CROSS_SOURCE_AB",i,"PARTITION",partition,"CONFLICTS",len(count_conflicts),
         "NATIVE_CALLS",native,"SECONDS",round(time.monotonic()-t0,1),flush=True)
  if i in (1,16,32,48,64):
   example.append({"suffix":suffix,"trajectories":{str(k):v for k,v in group_trace.items()}})
out=F/"sk48_l2_directional_phase_cross_source_ab.json"
report={"source_variants":{str(k):[list(v) for v in vv] for k,vv in histories.items()},
  "tested_suffixes":64,"suffix_length":3,
  "native_no_private_engine":True,"same_phase_counterexamples":count_conflicts,
  "continuation_partition_counts":dict(summary),"native_calls":native,
  "reset_retries":retries,"examples":example,
  "elapsed_seconds":round(time.monotonic()-t0,2)}
out.write_text(json.dumps(report,indent=2),encoding="utf-8")
print("CROSS_SOURCE_RESULT","COUNTEREXAMPLES",len(count_conflicts),
      "PARTITIONS",dict(summary),"SAVED",out,flush=True)
