"""SK48 A/B trailing-action quotient: independently varied held-out counts."""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from itertools import combinations,takewhile
from collections import defaultdict,Counter
from pathlib import Path
import copy,hashlib,json,numpy as np,logging
logging.disable(logging.CRITICAL)
root=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def sign(obs):return hashlib.sha256(np.asarray(obs.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:24]
results=[]
for nup,nright in ((2,4),(4,4),(4,5),(3,3),(2,5)):
 n=nup+nright
 images=defaultdict(list);trailing=defaultdict(set)
 counterexamples=[]
 for spots in combinations(range(n),nup):
  prefix=tuple(1 if i in spots else 4 for i in range(n))
  q=copy.deepcopy(root)
  for z in prefix:obs=q.step(GameAction.from_id(z),data={})
  after=sign(obs)
  trail=len(list(takewhile(lambda a:a==1,reversed(prefix))))
  images[after].append(prefix)
  trailing[trail].add(after)
  counterexamples.append((prefix,trail,after,int(obs.levels_completed)))
 broken={k:len(hashes) for k,hashes in trailing.items() if len(hashes)>1}
 alias=defaultdict(set)
 for h,items in images.items():
  for item in items:
   alias[h].add(len(list(takewhile(lambda a:a==1,reversed(item)))))
 aliases={h:sorted(list(ts)) for h,ts in alias.items() if len(ts)>1}
 summary={"up":nup,"right":nright,"total":len(counterexamples),
  "public_classes":len(images),"trailing_classes":len(trailing),
  "split_trailing":broken,"merged_trailing":aliases,
  "class_sizes":sorted(map(len,images.values()),reverse=True),
  "level_advances":sum(v[3]>0 for v in counterexamples)}
 results.append(summary)
 print("HELDOUT",summary,flush=True)
p=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_level1_trailing_up_heldout.json")
p.write_text(json.dumps({"method":"native public-frame history A/B",
                        "reference":"different counts, no original route",
                        "cases":results},indent=2),encoding="utf-8")
print("SAVED",p,flush=True)
