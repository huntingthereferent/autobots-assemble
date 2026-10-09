"""Native check depth-five A/B inverse branch frontier on SK48."""
from itertools import product
from pathlib import Path
from collections import Counter
from hashlib import sha256
import json,logging,random,time,numpy as np
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
P=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
A=((2,),(1,7),(4,7))
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
c=0;root=None
def step(z):
 global c
 o=g.step(GameAction.from_id(z),data={});c+=1;return o
def state(o):
 return (int(o.levels_completed),o.state.name,
  sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:20])
def run(h,t):
 global root
 for _ in range(8):
  o=step(0)
  if o.levels_completed==0:break
 else:raise RuntimeError("native reset UNKNOWN")
 for z in P:
  o=step(z)
  if o.levels_completed>=1:break
 assert o.levels_completed==1
 if root is None:root=state(o)
 assert state(o)==root
 for z in h:o=step(z)
 before=state(o);trace=[]
 for z in t:trace.append(state(step(z)))
 return before,trace
rng=random.Random(158);paths=list(product(range(3),repeat=5))
front=Counter();beg=time.monotonic();representatives={}
for j,word in enumerate(paths,1):
 h=[z for i in word for z in A[i]]
 s,_=run(h,());front[s]+=1
 representatives.setdefault(s,word)
 if j%81==0:
  print("DEPTH5_FRONT",j,"OF",len(paths),"VISIBLE",len(front),
    "CALLS",c,"SECONDS",round(time.monotonic()-beg,1),flush=True)
# Holdout sample, explicitly not exhaustive: new SIX-action horizon.
sample=[(0,)*5,(1,)*5,(2,)*5]+rng.sample(
 [p for p in paths if p not in ((0,)*5,(1,)*5,(2,)*5)],21)
suffixes=[(1,)*6,(2,)*6,(3,)*6,(4,)*6,
          (1,2,3,4,1,2),(4,3,2,1,4,3)]
futures=Counter();records=[]
for word in sample:
 h=[z for i in word for z in A[i]]
 before,empty=run(h,())
 trace=tuple(tuple(run(h,t)[1]) for t in suffixes)
 signature=sha256(repr((before,trace)).encode()).hexdigest()[:20]
 futures[signature]+=1
 records.append({"word":list(word),"before":before,
     "signature":signature})
out=F/"SK48_AB_INVERSE_DEPTH5_FRONTIER_2026-10-08.json"
out.write_text(json.dumps({"native_public_only":True,"depth":5,
 "all_paths_tested_for_visible_state":len(paths),
 "visible_classes":len(front),
 "class_populations":{repr(k):v for k,v in front.items()},
 "six_action_holdout_sample_count":len(sample),
 "six_action_holdout_fingerprints":dict(futures),
 "sampled_records":records,"native_calls":c,
 "important":"24 futures sampled, NOT all 243 six-step continuations"},indent=2))
print("DEPTH5_RESULT","PATHS",len(paths),"VISIBLE",len(front),
 "SAMPLED_FUTURE",len(sample),"CLASSES",len(futures),
 "CALLS",c,"SAVED",out,flush=True)
