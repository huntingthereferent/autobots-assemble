"""SK48 native inverse A/B category: projected source branches, 4-action holdout."""
import json,random,logging,time
from pathlib import Path
from itertools import product
from hashlib import sha256
import numpy as np
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
evidence=json.loads((F/"sk48_l2_directional_phase_cross_source_ab.json").read_text())
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
atoms=[tuple(x) for x in evidence["source_variants"]["1"]]
assert atoms==[(2,),(1,7),(4,7)]
groups={k:[{"symbol":list(b),"path":[a for j in b for a in atoms[j]]}
  for b in product(range(3),repeat=k)] for k in range(4)}
rng=random.Random(481015)
all4=list(product((1,2,3,4),repeat=4))
special=[(x,)*4 for x in (1,2,3,4)]+[(1,2,3,4),(4,3,2,1),(1,4,1,4),(4,1,4,1)]
probes=special+rng.sample([x for x in all4 if x not in special],12)
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;root=None;retry=0
def move(a):
 global calls
 o=g.step(GameAction.from_id(a),data={});calls+=1;return o
def state(o):
 return (int(o.levels_completed),o.state.name,sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:20])
def replay(path,suffix):
 global root,retry
 for _ in range(8):
  o=move(0)
  if o.levels_completed==0:break
  retry+=1
 else:raise RuntimeError("RESET UNKNOWN")
 for a in L1:
  o=move(a)
  if o.levels_completed>=1:break
 assert o.levels_completed==1
 if root is None:root=state(o)
 assert state(o)==root
 for a in path:o=move(a)
 pre=state(o);trajectory=[]
 for a in suffix:trajectory.append(state(move(a)))
 return pre,trajectory
start=time.monotonic()
refs={k:[replay([2]*k,p)[1] for p in probes] for k in groups}
assert len({repr(v) for v in refs.values()})==4
print("REAL_AB_HOLDOUT_REFERENCES","4 classes",len(probes),"suffixes",flush=True)
data=[];failed=[];summary={}
for k,variants in groups.items():
 valid=0
 for j,c in enumerate(variants):
  p=c["path"];pre=replay(p,())[0]
  if pre!=root:
   match=[];different=list(range(len(probes)))
  else:
   actual=[replay(p,s)[1] for s in probes]
   match=[z for z in refs if refs[z]==actual]
   different=[i for i,x in enumerate(actual) if x!=refs[k][i]]
  item={"depth":k,"symbol":c["symbol"],"history":p,
    "root_preserved":pre==root,"matched_categories":match,
    "first_counterexample":list(probes[different[0]]) if different else None}
  data.append(item)
  if match==[k]:valid+=1
  else:failed.append(item)
 summary[k]={"tested":len(variants),"agreed":valid,"split":len(variants)-valid}
 print("REAL_AB_INVERSE_BRANCH",k,summary[k],"SDK_CALLS",calls,
  "SECONDS",round(time.monotonic()-start,1),flush=True)
out=F/"SK48_AB_REAL_CATEGORY_INVERSE_BRANCH_HOLDOUT_2026-10-08.json"
obj={"source":"native SK48 category, 3 observed phase1 alternative witnesses",
 "projection":"compose witnessed phase1 alternatives without saved win paths",
 "older_horizon":3,"new_holdout_horizon":4,
 "suffixes":[list(x) for x in probes],"summary":summary,
 "branches":data,"counterexamples":failed,
 "native_calls":calls,"reset_retries":retry,
 "not_unseen_game":True,"no_native_fractal_claim":True}
out.write_text(json.dumps(obj,indent=2),encoding="utf-8")
print("REAL_AB_INVERSE_COMPLETE","SUCCESS",
 sum(x["agreed"] for x in summary.values()),"OF",len(data),
 "COUNTEREXAMPLES",len(failed),"SAVED",out,flush=True)
