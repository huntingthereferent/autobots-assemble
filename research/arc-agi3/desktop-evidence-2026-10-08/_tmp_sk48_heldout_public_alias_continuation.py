"""Held-out SK48 public-alias A/B: do visually identical frames have same next actions?"""
from arc_agi import Arcade, OperationMode
from arcengine import GameAction
from itertools import combinations,takewhile
from collections import defaultdict,Counter
from pathlib import Path
import copy,hashlib,json,numpy as np,logging
logging.disable(logging.CRITICAL)
root=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def sig(o):return hashlib.sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:20]
groups=defaultdict(list)
for ups in combinations(range(9),4):
 hist=tuple(1 if i in ups else 4 for i in range(9))
 e=copy.deepcopy(root)
 for z in hist:obs=e.step(GameAction.from_id(z),data={})
 groups[sig(obs)].append((hist,e))
breaks=[]
for parent,items in groups.items():
 vals=Counter()
 for action in (1,2,3,4,7):
  after_groups=defaultdict(list)
  for hist,e in items:
   child=copy.deepcopy(e)
   r=child.step(GameAction.from_id(action),data={})
   after_groups[(sig(r),r.levels_completed,r.state.name)].append(hist)
  vals[action]=len(after_groups)
  if len(after_groups)>1:
   examples=[{"next":k[0],"size":len(v),"example_prefix":list(v[0])} for k,v in after_groups.items()]
   breaks.append({"parent":parent,"parent_size":len(items),"action":action,"children":examples})
 print("CLASS",parent,"HISTORIES",len(items),
       "TRAIL_UPS",sorted(set(len(list(takewhile(lambda x:x==1,reversed(h)))) for h,e in items)),
       "NEXT_CLASS_COUNTS",dict(vals),flush=True)
print("BREAKS",len(breaks),flush=True)
for b in breaks[:15]:print("COUNTEREXAMPLE",b,flush=True)
output=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_heldout_public_alias_continuation.json")
output.write_text(json.dumps({"family":{"up":4,"right":5,"histories":126},
    "number_visible_classes":len(groups),"one_step_actions":[1,2,3,4,7],
    "counterexamples":breaks},indent=2),encoding="utf-8")
print("SAVED",output,flush=True)
