from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib
from collections import deque,Counter,defaultdict
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]; acts=[1,2,3,4,5,7]
def fresh(h=()):
 e=a.make('ar25'); r=None
 for z in SOL+list(h): r=e.step(GameAction.from_id(z),data={})
 return e,r,r.frame[0].copy()
def a5sig(h):
 e,r,A=fresh(h); rr=e.step(GameAction.from_id(5),data={});B=rr.frame[0]
 D=np.argwhere(A!=B); c=Counter((int(A[tuple(p)]),int(B[tuple(p)])) for p in D)
 return tuple(sorted((p,n) for p,n in c.items() if p!=(11,12)))
DOM=(((0,9),7),((9,0),6))
# Recreate exact whole-state frontier and identify rare departures from dominant class.
seen={}; q=deque([()])
while q and len(seen)<90:
 h=q.popleft(); e,r,A=fresh(h); k=A.tobytes()
 if k in seen: continue
 seen[k]=h
 if len(h)<5:
  for z in acts:
   e2,r2,B=fresh(h); rr=e2.step(GameAction.from_id(z),data={})
   if rr.state.name=="NOT_FINISHED" and rr.levels_completed==2:q.append(h+(z,))
dom=[h for h in seen.values() if a5sig(h)==DOM]
rare=[]; same=[]
for h in dom:
 for z in acts:
  e,r,A=fresh(h); rr=e.step(GameAction.from_id(z),data={})
  if rr.state.name!="NOT_FINISHED" or rr.levels_completed!=2:continue
  nh=h+(z,); s=a5sig(nh)
  (same if s==DOM else rare).append((nh,s))
# exact whole-state dedup rare departures
uniq={}
for h,s in rare:
 e,r,A=fresh(h); uniq.setdefault(A.tobytes(),(h,s))
print("DOM_PARENTS",len(dom),"RARE_EDGES",len(rare),"RARE_WHOLE_STATES",len(uniq))
for i,(h,s) in enumerate(list(uniq.values())[:30]): print("R",i,h,s)
# recurse 100 witnessed edges ONLY from exact rare returned whole states
front=list(uniq.values()); walls=0; classmaps=Counter(); newrare={}
for h,ps in front:
 for z in acts:
  e,r,A=fresh(h); rr=e.step(GameAction.from_id(z),data={}); walls+=1
  if rr.levels_completed>2:
   print("SOLVED_L3",SOL+list(h)+[z],"WALL",walls); raise SystemExit
  if rr.state.name=="NOT_FINISHED":
   nh=h+(z,); ns=a5sig(nh); classmaps[(ps,ns)]+=1
   if ns!=DOM:
    e2,r2,B=fresh(nh);newrare.setdefault(B.tobytes(),(nh,ns))
  if walls>=100:break
 if walls>=100:break
print("WALLS",walls,"NEW_RARE_WHOLE",len(newrare))
for (p,n),ct in classmaps.most_common(20):print("MAP",p,"=>",n,ct)
# append compact evidence doc
doc="\n\n### Level 3 rare-departure recursion\n"
doc+=f"- Dominant A5-varying class after removing witnessed 11->12 preservation: {DOM}.\n"
doc+=f"- Exact reconstructed frontier supplied {len(dom)} dominant whole-state parents.\n"
doc+=f"- Their simple-action continuations produced {len(rare)} rare departure edges collapsing to {len(uniq)} exact rare returned whole states.\n"
doc+=f"- Recursed through {walls} witnessed continuations from those rare whole states; no closure if this note is present.\n"
doc+=f"- {len(newrare)} exact non-dominant returned whole states survived that block. Whole board remained recursion referent; A5 signature was diagnostic only.\n"
open(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\AR25_SOLVE_DOCUMENTATION.md","a",encoding="utf8").write(doc)
