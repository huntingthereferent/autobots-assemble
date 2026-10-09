"""Test depth-four native SK48 histories created by inverting observed A/B category."""
import json,logging,time
from itertools import product
from pathlib import Path
from collections import Counter,defaultdict
from hashlib import sha256
import numpy as np
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
atoms=[[2],[1,7],[4,7]]
suffixes=[(1,)*5,(2,)*5,(3,)*5,(4,)*5,
(1,2,3,4,1),(4,3,2,1,4),(2,4,1,3,2),(3,1,4,2,3)]
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
calls=0;root=None
def move(a):
 global calls
 o=g.step(GameAction.from_id(a),data={});calls+=1;return o
def value(o):
 return (int(o.levels_completed),o.state.name,
 sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:20])
def run(seq,tail):
 global root
 for _ in range(8):
  o=move(0)
  if o.levels_completed==0:break
 else:raise RuntimeError("RESET failed")
 for a in L1:
  o=move(a)
  if o.levels_completed>=1:break
 assert o.levels_completed==1
 if root is None:root=value(o)
 assert value(o)==root
 for a in seq:o=move(a)
 before=value(o);tr=[]
 for a in tail:tr.append(value(move(a)))
 return before,tuple(tr)
start=time.monotonic();groups=defaultdict(list);visible=Counter();records=[]
for j,word in enumerate(product(range(3),repeat=4),1):
 history=[a for i in word for a in atoms[i]]
 before,_=run(history,())
 traces=tuple(run(history,s)[1] for s in suffixes)
 groups[(before,traces)].append(word);visible[before]+=1
 records.append({"source":list(word),"actions":history,"state":before,
  "future_hash":sha256(repr(traces).encode()).hexdigest()[:16]})
 if j%27==0:
  print("DEPTH4_SCAN",j,"VISIBLE",len(visible),
    "CLASSES",len(groups),"CALLS",calls,"SEC",round(time.monotonic()-start,1),flush=True)
classes=[{"count":len(v),"examples":[list(t) for t in v[:6]],
 "state":k[0],"future_hash":sha256(repr(k[1]).encode()).hexdigest()[:16]}
 for k,v in sorted(groups.items(),key=lambda x:-len(x[1]))]
out=F/"SK48_AB_INVERSE_DEPTH4_NATIVE_BOUNDARY_2026-10-08.json"
out.write_text(json.dumps({"source":"native SK48 inverse category projected branches",
 "depth":4,"total":81,"probe_horizon":5,"probes":[list(s) for s in suffixes],
 "visible_classes":len(visible),"continuation_classes":len(groups),
 "classes":classes,"witnesses":records,
 "native_calls":calls,"elapsed_s":round(time.monotonic()-start,1),
 "provenance":"current game, no private engine, finite horizon only"},indent=2))
print("DEPTH4_DONE","CLASSES",len(groups),"SIZES",[len(v) for v in groups.values()],
 "SAVED",out,flush=True)
