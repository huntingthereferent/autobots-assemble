"""SK48 native public A/B: continuation closure of 35 same-multiset prefixes.

Search for counterexamples to public-frame quotient by probing the same
native actions from each history, including ACTION7/undo.
"""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from itertools import combinations
from collections import defaultdict,Counter
from pathlib import Path
import copy,hashlib,json,numpy as np,logging
logging.disable(logging.CRITICAL)
root=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
def signature(o):
 frame=np.asarray(o.frame[-1],dtype=np.uint8)
 return hashlib.sha256(frame.tobytes()).hexdigest()[:24]
rows=[];views=defaultdict(list)
for up in combinations(range(7),3):
 prefix=tuple(1 if i in up else 4 for i in range(7))
 env=copy.deepcopy(root)
 for z in prefix: before=env.step(GameAction.from_id(z),data={})
 visible=signature(before)
 continuations={}
 for z in (1,2,3,4,7):
  q=copy.deepcopy(env)
  after=q.step(GameAction.from_id(z),data={})
  continuations[str(z)]={"frame":signature(after),"level":after.levels_completed,"state":after.state.name}
 row={"history":prefix,"visible":visible,
      "trailing_up":len(prefix)-len(tuple(reversed(prefix)))+0, # overwritten directly below
      "continuations":continuations}
 row["trailing_up"]=len(list(__import__("itertools").takewhile(lambda t:t==1,reversed(prefix))))
 rows.append(row);views[visible].append(row)
print("VISIBLE_CLASSES",[(key,len(v),v[0]["trailing_up"]) for key,v in views.items()],flush=True)
failures=[]
for current,group in views.items():
 for z in ("1","2","3","4","7"):
  bins=defaultdict(list)
  for row in group:
   next_state=row["continuations"][z]
   bins[(next_state["frame"],next_state["level"],next_state["state"])].append(row["history"])
  print("CLASS",current,"SIZE",len(group),"MOVE",z,"FUTURE_CLASSES",len(bins),
        "SPLIT_SIZES",sorted(map(len,bins.values()),reverse=True),flush=True)
  if len(bins)>1:
   example=[{"result_frame":key[0],"histories":[list(h) for h in histories[:3]],"size":len(histories)} for key,histories in bins.items()]
   failures.append({"public":current,"action":int(z),"branches":example})
print("COUNTEREXAMPLES",len(failures),flush=True)
for x in failures[:8]: print("AB_BREAK",x,flush=True)
p=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_level1_public_horizon1_undo.json")
p.write_text(json.dumps({"history_length":7,"input_prefix_multiset":{"ACTION1":3,"ACTION4":4},
                         "all_prefixes":len(rows),"public_classes":len(views),
                         "actions":[1,2,3,4,7],"counterexample_count":len(failures),
                         "counterexamples":failures,"observations":rows},indent=2),encoding="utf-8")
print("SAVED",p,flush=True)
