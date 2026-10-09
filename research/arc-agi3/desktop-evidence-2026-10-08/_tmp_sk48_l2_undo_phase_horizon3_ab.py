"""SK48 native public A/B horizon three after 0-3 undo cycles.

8 representative histories (two per cycle count), every 4^3 suffix.
The cycle-count classes are accepted only if same-count distinct action
histories agree for each native continuation.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from itertools import product
from hashlib import sha256
from collections import defaultdict,Counter
import json,numpy as np,logging,time
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
game=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
groups={0:[(),()],1:[(1,),(3,)],2:[(1,1),(2,4)],
        3:[(1,1,1),(2,3,1)]}
def key(o):
 return (int(o.levels_completed),o.state.name,sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:22])
parent=None;native_calls=0;extra=0
def step(z):
 global native_calls
 native_calls+=1
 return game.step(z,data={})
def enter(hist):
 global parent,extra
 for trial in range(8):
  o=step(GameAction.RESET)
  if o.levels_completed==0:break
  extra+=1
 else:raise RuntimeError("RESET not acknowledged")
 for z in L1:o=step(GameAction.from_id(z))
 if parent is None:parent=key(o)
 if key(o)!=parent:raise RuntimeError("Level2 entry replay mismatch")
 for z in hist:
  step(GameAction.from_id(z))
  o=step(GameAction.ACTION7)
  if key(o)!=parent:raise RuntimeError(("undo did not recover public referent",hist))
 return o
outcomes={};start=time.monotonic()
for num,suffix in enumerate(product((1,2,3,4),repeat=3),1):
 obs={}
 for count,history_set in groups.items():
  views=[]
  for hist in history_set:
   enter(hist)
   for a in suffix:o=step(GameAction.from_id(a))
   views.append(key(o))
  obs[count]=views
 outcomes["".join(map(str,suffix))]=obs
 if num%16==0:
  unique_count=len({(count,obs[count][0]) for count in groups})
  print("HORIZON3_PROGRESS",num,"OF",64,"NATIVE",native_calls,
        "SECONDS",round(time.monotonic()-start,1),flush=True)
same_count_fail=[]
partitions=Counter()
for suffix,obs in outcomes.items():
 for count,v in obs.items():
  if v[0]!=v[1]:same_count_fail.append({"suffix":suffix,"count":count,"results":v})
 sig_to_counts=defaultdict(list)
 for count in groups:sig_to_counts[obs[count][0]].append(count)
 partitions[tuple(sorted(tuple(v) for v in sig_to_counts.values()))]+=1
print("PHASE3_PARTITIONS",dict((str(k),v) for k,v in partitions.items()),
      "SAME_COUNT_BREAKS",len(same_count_fail),"CALLS",native_calls,"TIME",round(time.monotonic()-start,2),flush=True)
for err in same_count_fail[:5]:print("AB_SAMECOUNT_BREAK",err,flush=True)
out=F/"sk48_l2_undo_phase_horizon3_ab.json"
out.write_text(json.dumps({"game":"sk48","method":"native single game RESET+L1+rollback history+3 action suffix",
   "no_private_access":True,"tested_suffixes":64,"histories_tested":8,
   "same_cycle_count_counterexamples":same_count_fail,
   "signature_partition_counts":{str(k):v for k,v in partitions.items()},
   "native_calls":native_calls,"reset_retries":extra,
   "outcomes":outcomes},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
