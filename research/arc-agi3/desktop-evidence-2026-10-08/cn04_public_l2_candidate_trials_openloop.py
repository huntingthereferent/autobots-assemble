from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter

PLANS=[
{1:(0,12,5),2:(0,8,4),0:(0,7,2),3:(1,14,7)},
{1:(0,12,5),2:(0,8,4),0:(0,7,2),3:(3,16,7)},
{1:(0,12,4),2:(0,8,3),0:(0,7,1),3:(1,14,6)},
{1:(0,12,4),2:(0,8,3),0:(0,7,1),3:(3,16,6)},
{1:(0,11,4),2:(0,7,3),0:(0,6,1),3:(1,13,6)},
{1:(0,11,4),2:(0,7,3),0:(0,6,1),3:(3,15,6)},
]
START_BOX={0:(3,3),1:(12,4),2:(4,11),3:(16,16)}
CLICK={0:(3,3),1:(15,4),2:(7,11),3:(17,17)}

a=Arcade(operation_mode=OperationMode.NORMAL)
def click(e,x,y):return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def reach_l2():
 e=a.make("cn04")
 click(e,13,9)
 e.step(GameAction.from_id(5),data={})
 for _ in range(10):e.step(GameAction.from_id(3),data={})
 r=e.step(GameAction.from_id(1),data={})
 assert r.levels_completed==1 and r.state.name=="NOT_FINISHED"
 return e,r
def move_delta(e,dx,dy):
 r=None
 for _ in range(abs(dx)):
  r=e.step(GameAction.from_id(4 if dx>0 else 3),data={})
  if r.levels_completed>1 or r.state.name!="NOT_FINISHED":return r
 for _ in range(abs(dy)):
  r=e.step(GameAction.from_id(2 if dy>0 else 1),data={})
  if r.levels_completed>1 or r.state.name!="NOT_FINISHED":return r
 return r

for j,p in enumerate(PLANS):
 e,r=reach_l2()
 for idx in [0,1,2,3]:
  if idx!=0:
   click(e,*CLICK[idx])
  k,gx,gy=p[idx]
  for _ in range(k):
   r=e.step(GameAction.from_id(5),data={})
   if r.levels_completed>1 or r.state.name!="NOT_FINISHED":break
  if r.levels_completed>1 or r.state.name!="NOT_FINISHED":break
  sx,sy=START_BOX[idx]
  r=move_delta(e,gx-sx,gy-sy) or r
  if r.levels_completed>1 or r.state.name!="NOT_FINISHED":break
 print("CAND",j,"LC",r.levels_completed,"STATE",r.state.name,flush=True)
