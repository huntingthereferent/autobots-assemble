"""SK48 native A/B minimum witness family for chained-undo counterexample.

All eight ordered subsets of the previously observed (ACTION1, ACTION2,
ACTION3) action+undo cycles. Test ACTION4 after each. Reset acknowledgment
and identical public parent checked before every candidate.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from hashlib import sha256
import logging,json,numpy as np,itertools
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
arc=Arcade(operation_mode=OperationMode.NORMAL);g=arc.make("sk48")
def H(o):return sha256(np.asarray(o.frame[-1],dtype=np.uint8).tobytes()).hexdigest()[:16]
def root():
 for k in range(8):
  r=g.step(GameAction.RESET,data={})
  if r.levels_completed==0:break
 else:raise RuntimeError("RESET not acknowledged")
 for z in L1:r=g.step(GameAction.from_id(z),data={})
 assert r.levels_completed==1
 return r
base=root();reference=H(base)
direct=g.step(GameAction.ACTION4,data={})
direct_h=H(direct)
print("PARENT",reference,"FRESH_ACTION4",direct_h,flush=True)
rows=[]
for subset_mask in range(8):
 subset=tuple(a for j,a in enumerate((1,2,3)) if subset_mask & (1<<j))
 p=root()
 if H(p)!=reference:raise RuntimeError("parent replay differed")
 cycle_hashes=[]
 for action in subset:
  obs=g.step(GameAction.from_id(action),data={})
  restored=g.step(GameAction.ACTION7,data={})
  cycle_hashes.append((action,H(restored),H(restored)==reference))
  if H(restored)!=reference:break
 else:
  next4=g.step(GameAction.ACTION4,data={})
  got=H(next4)
  row={"history":list(subset),"cycle_outcomes":cycle_hashes,
       "fully_appeared_restored":True,"action4":got,"different_from_direct":got!=direct_h}
  rows.append(row)
  print("MIN_WITNESS",row,flush=True)
  continue
 row={"history":list(subset),"cycle_outcomes":cycle_hashes,
      "fully_appeared_restored":False,"action4":None,"different_from_direct":None}
 rows.append(row);print("MIN_WITNESS",row,flush=True)
valid=[r for r in rows if r["fully_appeared_restored"] and r["different_from_direct"]]
n=min((len(r["history"]) for r in valid),default=None)
minimal=[r["history"] for r in valid if len(r["history"])==n]
result={"tested":len(rows),"full_parent_sha_prefix":reference,"direct_action4_sha_prefix":direct_h,
        "minimal_witness_length":n,"minimal_witness_paths":minimal,"results":rows}
out=F/"sk48_l2_chained_undo_minimal_ab.json"
out.write_text(json.dumps(result,indent=2),encoding="utf-8")
print("AB_MINIMUM",minimal,"LENGTH",n,"SAVED",out,flush=True)
