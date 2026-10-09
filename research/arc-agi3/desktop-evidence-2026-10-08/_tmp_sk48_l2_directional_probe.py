"""SK48 Level 2 public-only action/phase trace on deterministic probe programs."""
import json,numpy as np,hashlib,logging
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
logging.disable(logging.CRITICAL)
f=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((f/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
def mat(o):return np.asarray(o.frame[-1],dtype=np.uint8).reshape(64,64).copy()
def digest(o):return hashlib.sha256(mat(o).tobytes()).hexdigest()[:16]
def go():
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 for z in L1:o=e.step(GameAction.from_id(z),data={})
 assert o.levels_completed==1
 return e,o
programs={"all_right":[4]*12,"all_up":[1]*12,"all_noop_down":[2]*12,
          "all_left":[3]*12,"mix_right_up":[4,1]*6,
          "mix_up_right":[1,4]*6,"mix_left_right":[3,4]*6}
out={}
for name,seq in programs.items():
 e,o=go();records=[];old=mat(o)
 for k,z in enumerate(seq,1):
  o=e.step(GameAction.from_id(z),data={})
  new=mat(o)
  yy,xx=np.where(new!=old)
  changed=int(len(yy))
  row={"k":k,"action":z,"hash":digest(o),"changed":changed,
       "box":[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())] if changed else None,
       "top_goal":new[25,30:54].tolist(),
       "lower_reference":new[57,23:51].tolist(),
       "levels":int(o.levels_completed)}
  records.append(row)
  old=new
  if o.levels_completed>=2:break
 print("PROGRAM",name,"DISTINCT",len(set(r["hash"] for r in records)),
  "PIXELS",[r["changed"] for r in records],
  "LEVELS",[r["levels"] for r in records],
  "GOALS",[r["top_goal"] for r in records[-1:]],flush=True)
 out[name]=records
path=f/"sk48_l2_public_directional_probe_2026-10-08.json"
path.write_text(json.dumps({"method":"native public SDK frame-only controls","programs":out},indent=2),encoding="utf-8")
print("SAVED",path,flush=True)
