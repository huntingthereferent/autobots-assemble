"""SK48 Level2 one-step A/B of future after directional action + undo.

Use native public observations only. Counterfactual baseline is a separate
fresh Arcade instance; neither runtime reads _game nor uses copied objects.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import json,hashlib,numpy as np,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
def frame(o):return np.asarray(o.frame[-1],dtype=np.uint8).copy()
def h(o):return hashlib.sha256(frame(o).tobytes()).hexdigest()[:14]
def level2(g):
 for z in L1:o=g.step(GameAction.from_id(z),data={})
 return o
baseline={}
for b in (1,2,3,4):
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 initial=level2(e)
 after=e.step(GameAction.from_id(b),data={})
 baseline[b]=(h(after),after.levels_completed,after.state.name)
print("REFERENCE",baseline,flush=True)
bad=[]
for a in (1,2,3,4,7):
 for b in (1,2,3,4):
  e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
  parent=level2(e)
  e.step(GameAction.from_id(a),data={})
  restored=e.step(GameAction.ACTION7,data={})
  got=e.step(GameAction.from_id(b),data={})
  actual=(h(got),got.levels_completed,got.state.name)
  equal=(h(restored)==h(parent) and actual==baseline[b])
  print("AB",a,"UNDO",h(restored)==h(parent),"THEN",b,"PREDICTED",baseline[b][0],"OBSERVED",actual[0],"AGREE",equal,flush=True)
  if not equal:bad.append({"first":a,"next":b,"expected":baseline[b],"got":actual})
p=F/"sk48_l2_native_undo_continuation.json"
p.write_text(json.dumps({"action_pairs_tested":20,"counterexamples":bad,
 "scope":"one undo followed by one move, Level 2 entry state, fresh game per pair"},indent=2),encoding="utf-8")
print("CONCLUSION","PASS" if not bad else "BREAK","COUNTEREXAMPLES",len(bad),flush=True)
print("SAVED",p,flush=True)
