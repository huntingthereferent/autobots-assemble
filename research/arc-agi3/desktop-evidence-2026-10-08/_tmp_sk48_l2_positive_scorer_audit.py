"""Audit positive SK48 Level2 witness against public-sensor beam scorer.

Positive saved native Level 2 path is used only as a regression oracle:
find where heuristic loses necessary contraction actions. No solver writes.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from _sk48_public_goal_sensor import frame,features
import numpy as np,json,logging
logging.disable(logging.CRITICAL)
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
L1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
REF=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4)
milestones=json.loads((F/"sk48_l2_goal_seed444_checkpoint.json").read_text())["milestones"]
best={int(m["depth"]):m["best_score"] for m in milestones}
g=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
for z in L1:o=g.step(GameAction.from_id(z),data={})
rows=[]
for i,z in enumerate(REF,1):
 o=g.step(GameAction.from_id(z),data={})
 a=frame(o);f=features(a)
 b=max(f["candidates"],key=lambda q:(q["matched_prefix"],len(q["attached_row"])),default=None)
 prefix=b["matched_prefix"] if b else 0
 seq=b["attached_row"] if b else ()
 y=b["head"][1] if b else 42
 body=int(np.count_nonzero(a[y+2,5:55]==1))
 score=round(1000*prefix+12*len(seq)-5*max(len(seq)-prefix,0)-.18*abs(y-18)+.3*body,2)
 item={"step":i,"action":z,"witness_score":score,"best_beam":best.get(i),
       "beam_gap":round(best.get(i,score)-score,2),"prefix":prefix,
       "seq":seq,"head_y":y}
 rows.append(item)
 print("POSITIVE_REGRESSION",item,flush=True)
out=F/"sk48_l2_goal_beam_positive_regression.json"
out.write_text(json.dumps({"method":"positive reference witness used for scorer audit only",
 "reference_level2_action_count":len(REF),"score_comparison":rows},indent=2),encoding="utf-8")
print("SAVED",out,flush=True)
